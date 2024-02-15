// Copyright 2021 Optiver Asia Pacific Pty. Ltd.
//
// This file is part of Ready Trader Go.
//
//     Ready Trader Go is free software: you can redistribute it and/or
//     modify it under the terms of the GNU Affero General Public License
//     as published by the Free Software Foundation, either version 3 of
//     the License, or (at your option) any later version.
//
//     Ready Trader Go is distributed in the hope that it will be useful,
//     but WITHOUT ANY WARRANTY; without even the implied warranty of
//     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//     GNU Affero General Public License for more details.
//
//     You should have received a copy of the GNU Affero General Public
//     License along with Ready Trader Go.  If not, see
//     <https://www.gnu.org/licenses/>.
#include <array>

#include <boost/asio/io_context.hpp>

#include <iostream>
#include <ready_trader_go/logging.h>

#include "autotrader.h"

#include <iostream>
#include "limits.h"
#include <chrono>
#include <thread>

using namespace ReadyTraderGo;

RTG_INLINE_GLOBAL_LOGGER_WITH_CHANNEL(LG_AT, "AUTO")

constexpr int LOT_SIZE = 5;
constexpr int POSITION_LIMIT = 100;
constexpr int ORDER_LIMIT = 10;
constexpr int MESSAGE_PER_SECOND_LIMIT = 40;
constexpr int TICK_SIZE_IN_CENTS = 100;
constexpr int MIN_BID_NEARST_TICK = (MINIMUM_BID + TICK_SIZE_IN_CENTS) / TICK_SIZE_IN_CENTS * TICK_SIZE_IN_CENTS;
constexpr int MAX_ASK_NEAREST_TICK = MAXIMUM_ASK / TICK_SIZE_IN_CENTS * TICK_SIZE_IN_CENTS;

constexpr size_t WINDOW_SIZE = 50;
const double ENTRY_THRESHOLD_MULTIPLIER = 1.25;
const double EXIT_THRESHOLD_MULTIPLIER = 0.35;

/******************************************************************************/
/***************************AUTOTRADER*****************************************/
/******************************************************************************/

AutoTrader::AutoTrader(boost::asio::io_context &context) : BaseAutoTrader(context)
{
}

void AutoTrader::DisconnectHandler()
{
    BaseAutoTrader::DisconnectHandler();
    RLOG(LG_AT, LogLevel::LL_INFO) << "execution connection lost";
}

void AutoTrader::ErrorMessageHandler(unsigned long clientOrderId,
                                     const std::string &errorMessage)
{
    RLOG(LG_AT, LogLevel::LL_INFO) << "error with order " << clientOrderId << ": " << errorMessage;
    if (clientOrderId != 0 && ((_Asks.count(clientOrderId) == 1) || (_Bids.count(clientOrderId) == 1)))
    {
        OrderStatusMessageHandler(clientOrderId, 0, 0, 0);
    }
}

void AutoTrader::HedgeFilledMessageHandler(unsigned long clientOrderId,
                                           unsigned long price,
                                           unsigned long volume)
{
    RLOG(LG_AT, LogLevel::LL_DEBUG) << "HEDGE order " << clientOrderId << " filled for " << volume
                                   << " lots at $" << price << " average price in cents";
}

void AutoTrader::OrderBookMessageHandler(Instrument instrument,
                                         unsigned long sequenceNumber,
                                         const std::array<unsigned long, TOP_LEVEL_COUNT> &askPrices,
                                         const std::array<unsigned long, TOP_LEVEL_COUNT> &askVolumes,
                                         const std::array<unsigned long, TOP_LEVEL_COUNT> &bidPrices,
                                         const std::array<unsigned long, TOP_LEVEL_COUNT> &bidVolumes)
{
    (void)sequenceNumber;

    std::chrono::steady_clock::time_point CurrentTime = std::chrono::steady_clock::now();
    if (std::chrono::duration_cast<std::chrono::milliseconds>(CurrentTime - _StartTime).count() >= 1000)
    {
        if (_MessageCounter > MESSAGE_PER_SECOND_LIMIT)
            RLOG(LG_AT, LogLevel::LL_ERROR) << "_MessageCounter: " << _MessageCounter;
      _StartTime = CurrentTime;
      _MessageCounter = 0;
    }

    if (instrument == Instrument::FUTURE)
        _Future.updateOrderBook(bidPrices, bidVolumes, askPrices, askVolumes);
    else if (instrument == Instrument::ETF)
    {
        _ETF.updateOrderBook(bidPrices, bidVolumes, askPrices, askVolumes);
        if (_ETF.getAskPrice() && _ETF.getBidPrice() && _Future.getAskPrice() && _Future.getBidPrice() && _Future.accessVWAP().getVwap())
        {
            _PairSmall.addEntry((_ETF.accessMidPrice().getMidPrice() + _Future.accessVWAP().getVwap()) / 2);
            _PairBig.addEntry((_ETF.accessMidPrice().getMidPrice() + _Future.accessVWAP().getVwap()) / 2);
            _ZScore.update(static_cast<double>(_ETF.accessMidPrice().getMidPrice()), static_cast<double>(_Future.accessMidPrice().getMidPrice()));
            if ( _MessageCounter <= 45 && _AskId != 0 && _ETF.getAskPrice() != _ETFOrderAskPrice)
                CancelSellOrder();
            if ( _MessageCounter <= 45 && _BidId != 0 && _ETF.getBidPrice() != _ETFOrderBidPrice)
                CancelBuyOrder();
            if (_MessageCounter <= 45 && _AskId != 0 && askPrices[0] && askPrices[0] == _ETFOrderAskPrice && askVolumes[0] == (unsigned long)std::abs(_Position) && askPrices[1] && askPrices[0] - askPrices[1] > 100)
                CancelSellOrder();
            if (_MessageCounter <= 45 && _BidId != 0 &&  askPrices[0] && bidPrices[0] == _ETFOrderBidPrice && bidVolumes[0] == (unsigned long)std::abs(_Position) && bidPrices[1] && bidPrices[1] - bidPrices[0] > 100)
                CancelBuyOrder();

            // Liquidate Position calls
            if (_Position < 0 && !_AskId && !_BidId && _ZScore.getZScore() < 0)
                SendBuyOrder(instrument,_ETF.getBidPrice(), -_Position);
            else if (_Position > 0 && !_AskId && !_BidId && _ZScore.getZScore() > 0)
                SendSellOrder(instrument, _ETF.getAskPrice(), _Position);
            // Increase Position calls
            else if (_MessageCounter <= 45 && !_AskId && !_BidId && _ZScore.getZScore() < _ZScore.getEntryThresholdInverted() && _ETF.accessMidPrice().getMidPrice() < _PairSmall.getAverage()) {
                unsigned long size = POSITION_LIMIT - std::abs(_Position);
                if (size) {
                    SendBuyOrder(instrument, _ETF.getBidPrice(), size);
                }
            }
            else if (_MessageCounter <= 45 && !_AskId && !_BidId && _ZScore.getZScore() > _ZScore.getEntryThreshold() && _ETF.accessMidPrice().getMidPrice() > _PairSmall.getAverage()) {
                unsigned long size = POSITION_LIMIT - std::abs(_Position);
                if (size) {
                    SendSellOrder(instrument, _ETF.getAskPrice(), POSITION_LIMIT - std::abs(_Position));
                }
            }
        }

        RLOG(LG_AT, LogLevel::LL_INFO) << "ORDER_BOOK";
        RLOG(LG_AT, LogLevel::LL_INFO) << "_Position " << _Position << "_AskId" << _AskId   << "_BidId" << _BidId;
    }
}

void AutoTrader::CancelBuyOrder() {
    RLOG(LG_AT, LogLevel::LL_INFO) << "Cancelling sell order with id: " << _BidId;
    _MessageCounter++;
    SendCancelOrder(_BidId);
    _ETFOrderBidPrice = 0;
    _BidId = 0;
}

void AutoTrader::CancelSellOrder() {
    RLOG(LG_AT, LogLevel::LL_INFO) << "Cancelling buy order with id: " << _AskId;
    _MessageCounter++;
    SendCancelOrder(_AskId);
    _ETFOrderAskPrice = 0;
    _AskId = 0;
}

void AutoTrader::SendBuyOrder(Instrument instrument, unsigned long bid_price, unsigned long size) {
    if (_ETF.getAskPrice() - bid_price > TICK_SIZE_IN_CENTS)
        bid_price += TICK_SIZE_IN_CENTS;
    _MessageCounter++;
    _BidId = _NextMessageId++;
    RLOG(LG_AT, LogLevel::LL_INFO) << instrument << " order BUY: " << _BidId << ": price:" << bid_price << " size: " << size;
    SendInsertOrder(_BidId, Side::BUY, bid_price, size, Lifespan::GOOD_FOR_DAY);
    _ETFOrderBidPrice = bid_price;
    _Bids.emplace(_BidId);
}

void AutoTrader::SendSellOrder(Instrument instrument, unsigned long ask_price, unsigned long size) {
     if (ask_price - _ETF.getBidPrice() > TICK_SIZE_IN_CENTS)
         ask_price -= TICK_SIZE_IN_CENTS;
    _MessageCounter++;
    _AskId = _NextMessageId++;
    RLOG(LG_AT, LogLevel::LL_INFO) << instrument << ": order: SELL: " << _AskId << " ask_price " << ask_price;
    SendInsertOrder(_AskId, Side::SELL, ask_price, size, Lifespan::GOOD_FOR_DAY);
    _ETFOrderAskPrice = ask_price;
    _Asks.emplace(_AskId);
}

void AutoTrader::OrderFilledMessageHandler(unsigned long clientOrderId,
                                               unsigned long price,
                                               unsigned long volume)
{
    RLOG(LG_AT, LogLevel::LL_INFO) << "order " << clientOrderId << " filled for " << volume
                                   << " lots at $" << price << " cents";


    if (_Asks.count(clientOrderId) == 1)
    {
        _Position -= (long)volume;
        _MessageCounter++;
        SendHedgeOrder(_NextMessageId++, Side::BUY, MAX_ASK_NEAREST_TICK, volume);
    }
    else if (_Bids.count(clientOrderId) == 1)
    {
        _Position += (long)volume;
        _MessageCounter++;
        SendHedgeOrder(_NextMessageId++, Side::SELL, MIN_BID_NEARST_TICK, volume);
    }
}

void AutoTrader::OrderStatusMessageHandler(unsigned long clientOrderId,
                                           unsigned long fillVolume,
                                           unsigned long remainingVolume,
                                           signed long fees)
{
    if (remainingVolume == 0)
    {
        if (clientOrderId == _AskId)
        {
            _AskId = 0;
        }
        else if (clientOrderId == _BidId)
        {
            _BidId = 0;
        }

        _Asks.erase(clientOrderId);
        _Bids.erase(clientOrderId);
    }
}

void AutoTrader::TradeTicksMessageHandler(Instrument instrument,
                                          unsigned long sequenceNumber,
                                          const std::array<unsigned long, TOP_LEVEL_COUNT> &askPrices,
                                          const std::array<unsigned long, TOP_LEVEL_COUNT> &askVolumes,
                                          const std::array<unsigned long, TOP_LEVEL_COUNT> &bidPrices,
                                          const std::array<unsigned long, TOP_LEVEL_COUNT> &bidVolumes)
{
    (void)sequenceNumber;
    if (instrument == Instrument::ETF)
        _ETF.accessVWAP().calculateVwap(bidPrices, bidVolumes, askPrices, askVolumes);
    else if (instrument == Instrument::FUTURE)
        _Future.accessVWAP().calculateVwap(bidPrices, bidVolumes, askPrices, askVolumes);
}

/******************************************************************************/
/***************************ORDERBOOK******************************************/
/******************************************************************************/

OrderBook::OrderBook(ReadyTraderGo::Instrument instrument) : _Instrument(instrument), _UpdateCount(0), _AskPrice(0), _BidPrice(0)
{
}

MidPrice& OrderBook::accessMidPrice()
{
    return (_MidPrice);

}

Vwap& OrderBook::accessVWAP()
{
    return (_Vwap);
}

unsigned long OrderBook::getUpdateCount() const
{
    return (_UpdateCount);
}

unsigned long OrderBook::getAskPrice() const
{
    return (_AskPrice);
}

unsigned long OrderBook::getBidPrice() const
{
    return (_BidPrice);
}

void OrderBook::setAskPrice(unsigned long ask_price)
{
    _AskPrice = ask_price;
}

void OrderBook::setBidPrice(unsigned long bid_price)
{
    _BidPrice = bid_price;
}

void OrderBook::updateOrderBook(const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& bidPrices,
        const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& bidVolumes,
        const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& askPrices,
        const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& askVolumes)
{
    _UpdateCount++;
    if (askPrices[0])
        setAskPrice(askPrices[0]);
    if (bidPrices[0])
        setBidPrice(bidPrices[0]);
    _Vwap.updateVwap();
    _MidPrice.updateMidPrices(getAskPrice(), getBidPrice());
    RLOG(LG_AT, LogLevel::LL_INFO) << "Update " << _Instrument << " ASK " << getAskPrice() << " BID " << getBidPrice()
        << " Best_ASK " << askPrices[0] << " Best_BID " << bidPrices[0]
        << " MID " << _MidPrice.getMidPrice() << " MID " << _MidPrice.getAverageMidPrice()
        << " VWAP " << _Vwap.getVwap() << " AverageVWAP " << _Vwap.getAverageVwap();
}

void OrderBook::updateTradeTicks(const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& bidPrices,
        const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& bidVolumes,
        const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& askPrices,
        const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& askVolumes)
{
    _Vwap.calculateVwap(bidPrices, bidVolumes, askPrices, askVolumes);
}

/******************************************************************************/
/***************************VWAP***********************************************/
/******************************************************************************/

Vwap::Vwap() : _deltaVwap(0), _CumulativeVwap(0), _VwapEntries(0), _sizeVwap(512), _Vwaps(_sizeVwap, 0)
{
}

unsigned long Vwap::getVwap() const
{
    return (_Vwaps.front());
}
unsigned long Vwap::getAverageVwap() const
{
    unsigned long Vwap = 0;
    if (_VwapEntries)
        Vwap = _CumulativeVwap / _VwapEntries;
    return (Vwap);
}

unsigned long Vwap::getVwapEntries() const
{
    return (_VwapEntries);
}

void Vwap::updateVwap()
{
    unsigned long back;
    unsigned long front;

    front = _Vwaps.at(0);
    back = _Vwaps.back();
    if (front)
    {
        _CumulativeVwap += front;
        _VwapEntries++;
    }
    _Vwaps.push_front(front);
    if (back)
    {
        _CumulativeVwap -= back;
        _VwapEntries--;
    }
    _Vwaps.pop_back();
}

void Vwap::calculateVwap(const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& bidPrices, const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& bidVolumes,
        const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& askPrices, const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& askVolumes)
{
    unsigned long totalVolume = 0;
    unsigned long totalPriceVolume = 0;

    for (size_t i = 0; i < askPrices.size() && askVolumes[i] && askPrices[i]; i++)
    {
            totalVolume += askVolumes[i];
            totalPriceVolume += askPrices[i] * askVolumes[i];
    }
    for (size_t i = 0; i < bidPrices.size() && bidVolumes[i] && bidPrices[i]; i++)
    {
            totalVolume += bidVolumes[i];
            totalPriceVolume += bidPrices[i] * bidVolumes[i];
    }
    if (totalVolume == 0 || totalPriceVolume == 0)
        return ;
    _Vwaps.front() = totalPriceVolume / totalVolume;;
}

Vwap::~Vwap()
{

}

/******************************************************************************/
/***************************MIDPRICE*******************************************/
/******************************************************************************/

MidPrice::MidPrice() : _Size(64), _Cumulative(0), _Entries(0), _MidPrices(_Size, 0)
{
}

void MidPrice::updateMidPrices(unsigned long ask, unsigned long bid)
{
    unsigned long back;
    unsigned long front;

    if (ask && bid)
        _MidPrices.front() =  (ask + bid) / 2;

    front = _MidPrices.at(0);
    back = _MidPrices.back();
    if (front)
    {
        _Cumulative += front;
        _Entries++;
    }
    _MidPrices.push_front(front);
    if (back)
    {
        _Cumulative -= back;
        _Entries--;
    }
    _MidPrices.pop_back();

}

unsigned long MidPrice::getAverageMidPrice() const
{
    unsigned long AverageMidPrice = 0;
    if (_Entries)
        AverageMidPrice = _Cumulative / _Entries;
    return (AverageMidPrice);
}

unsigned long MidPrice::getMidPrice() const
{
    return (_MidPrices.front());
}

/******************************************************************************/
/***************************ZSCORE*********************************************/
/******************************************************************************/

double ZScore::getZScore(void) const
{
    return (_ZScore);
}

double ZScore::getExitThreshold(void) const
{
    return (_ExitThreshold);
}

double ZScore::getExitThresholdInverted(void) const
{
    return (-_ExitThreshold);
}

double ZScore::getEntryThreshold(void) const
{
    return (_EntryThreshold);
}

double ZScore::getEntryThresholdInverted(void) const
{
    return (-_EntryThreshold);
}

double ZScore::calculateStandardDeviation(void) 
{
    return std::sqrt(ba::variance(_RatioStats));
}

void ZScore::update(double ETFPrice, double FuturePrice)
{
    _SpreadRatioMidPrices = ETFPrice  / FuturePrice;
    _RatioStats(_SpreadRatioMidPrices);
    calcZscore();
    updateZScoreWindow(_ZScore);
    calculateStdZScore();
    calculateThresholds();
    RLOG(LG_AT, LogLevel::LL_INFO) << "ZSCORE " << _ZScore << " AVG ZSCORE " << " TRESHOLD " << _EntryThreshold  << "EXIT TRESHOLD " << _ExitThreshold;
}

void ZScore::calcZscore()
{
    double stdDev = calculateStandardDeviation();
    _ZScore = (_SpreadRatioMidPrices - ba::mean(_RatioStats)) / stdDev; 
}

void ZScore::updateZScoreWindow(double newZScore)
{
    _ZScoreWindow.push_back(newZScore);
    if (_ZScoreWindow.size() > WINDOW_SIZE)
    {
        _ZScoreWindow.pop_front();
    }
}

double ZScore::calculateAverageZScore()
{
    double sum = std::accumulate(_ZScoreWindow.begin(), _ZScoreWindow.end(), 0.0);
    return sum / _ZScoreWindow.size();
}

void ZScore::calculateStdZScore()
{
    _AverageZScore = calculateAverageZScore();
    double mean = _AverageZScore;
    double sq_sum = std::inner_product(_ZScoreWindow.begin(), _ZScoreWindow.end(), _ZScoreWindow.begin(), 0.0,
        std::plus<double>(), [mean](double a, double b) { return (a - mean) * (b - mean); });
    _StandardDevationZScore = std::sqrt(sq_sum / _ZScoreWindow.size());
}

void ZScore::calculateThresholds(void)
{
        _ExitThreshold = _AverageZScore + EXIT_THRESHOLD_MULTIPLIER * _StandardDevationZScore;
        _EntryThreshold = _AverageZScore + ENTRY_THRESHOLD_MULTIPLIER * _StandardDevationZScore;
}

/******************************************************************************/
/***************************MOVINGAVERAGE**************************************/
/******************************************************************************/

void MovingAverage::addEntry(unsigned long entry) {
    window.push_front(entry);
    if (window.size() > windowSize) {
        sum -= window.back();
        window.pop_back();
    }
    sum += entry;
    average = sum / window.size();
    if (window.size() == windowSize) {
        calcVariance();
    }
}

double MovingAverage::calcStdDev() {
    return std::sqrt(variance);
}

double MovingAverage::calcVariance() {
    int n = window.size();

    double variance = 0.0;
    for (int i = 0; i < n; i++) {
        variance += pow(window[i] - average, 2);
    }
    variance = variance / (n - 1);
    return variance;
}
