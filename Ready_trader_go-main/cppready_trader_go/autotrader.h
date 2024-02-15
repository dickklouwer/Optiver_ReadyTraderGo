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
#ifndef CPPREADY_TRADER_GO_AUTOTRADER_H
#define CPPREADY_TRADER_GO_AUTOTRADER_H

#include <array>
#include <deque>
#include <memory>
#include <string>
#include <unordered_set>

#include <boost/asio/io_context.hpp>

#include <ready_trader_go/baseautotrader.h>
#include <ready_trader_go/types.h>

/**
 * spread stuff
*/
#include <boost/accumulators/accumulators.hpp>
#include <boost/accumulators/statistics.hpp>

namespace ba = boost::accumulators;

class MovingAverage {
public:
    MovingAverage(size_t windowSize) : windowSize(windowSize), sum(0) {}

    double getLastRatio() { return lastRatio; }
    unsigned long getAverage() { return sum / window.size(); }
    int getSize() { return window.size(); }

    double calcStdDev();
    double calcVariance();

    void addEntry(unsigned long entry);

    bool isFull() { return window.size() == windowSize; }

private:
    size_t windowSize;
    std::deque<unsigned long> window;
    double lastRatio;
    unsigned long sum = 0;
    unsigned long average = 0;
    double variance = 0;
};

class Vwap
{
    public:
        Vwap();
        unsigned long getVwap() const;
        unsigned long getAverageVwap() const;
        unsigned long getVwapEntries() const;
        void calculateVwap(const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& bidPrices,
                                            const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& bidVolumes,
                                            const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& askPrices,
                                            const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& askVolumes);
        void updateVwap();

        unsigned long getDeltaVwap() const;

        ~Vwap();


    private:
        long   _deltaVwap;
        unsigned long _CumulativeVwap;
        unsigned long _CumulativeDeltaVwap;
        unsigned long _VwapEntries;
        const unsigned long   _sizeVwap;
        std::deque<unsigned long> _Vwaps;
};

class MidPrice
{
    public:
        MidPrice();
        void updateMidPrices(unsigned long ask, unsigned long bid);
        unsigned long getAverageMidPrice() const;
        unsigned long getMidPrice() const;
    private:
        const unsigned long   _Size;
        unsigned long _Cumulative;
        unsigned long _Entries;
        std::deque<unsigned long> _MidPrices;
};

class ZScore
{
    public:
        // ZScore();
        
        void update(double ETFPrice, double FuturePrice);
        //Getters
        double getZScore(void) const;
        double getExitThreshold(void) const;
        double getExitThresholdInverted(void) const;
        double getEntryThreshold(void) const;
        double getEntryThresholdInverted(void) const;

        //Calculators
        void calcZscore(void);
        double calculateStandardDeviation(void);
        double calculateAverageZScore(void);
        void calculateStdZScore(void);
        void   calculateThresholds(void);

        void updateZScoreWindow(double newZScore);
    private:
        double _AverageZScore = 0;
        double _StandardDevationZScore = 0;
        double _ZScore = 0;

        double _ExitThreshold = 0;
        double _EntryThreshold = 0;
        double _SpreadRatioMidPrices = 0;
        std::deque<double> _ZScoreWindow;       
        ba::accumulator_set<double, ba::features<ba::tag::mean, ba::tag::count, ba::tag::variance>> _RatioStats;
};

class OrderBook
{
    public:
    OrderBook(ReadyTraderGo::Instrument instrument);
    unsigned long getUpdateCount() const;
    unsigned long getAskPrice() const;
    unsigned long getBidPrice() const;
    unsigned long getVwap() const;
    MidPrice& accessMidPrice();
    Vwap& accessVWAP();
    void setAskPrice(unsigned long ask_price);
    void setBidPrice(unsigned long bid_price);
    void updateOrderBook(const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& bidPrices,
            const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& bidVolumes,
            const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& askPrices,
            const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& askVolumes);
    void updateTradeTicks(const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& bidPrices,
            const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& bidVolumes,
            const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& askPrices,
            const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT>& askVolumes);

    private:
    ReadyTraderGo::Instrument _Instrument;
    unsigned long _UpdateCount;
    unsigned long _AskPrice;
    unsigned long _BidPrice;
    MidPrice _MidPrice;
    Vwap _Vwap;
};

class AutoTrader : public ReadyTraderGo::BaseAutoTrader
{
    public:
        explicit AutoTrader(boost::asio::io_context &context);

        // Called when the execution connection is lost.
        void DisconnectHandler() override;

        // Called when the matching engine detects an error.
        // If the error pertains to a particular order, then the client_order_id
        // will identify that order, otherwise the client_order_id will be zero.
        void ErrorMessageHandler(unsigned long clientOrderId,
                const std::string &errorMessage) override;

        // Called when one of your hedge orders is filled, partially or fully.
        //
        // The price is the average price at which the order was (partially) filled,
        // which may be better than the order's limit price. The volume is
        // the number of lots filled at that price.
        //
        // If the order was unsuccessful, both the price and volume will be zero.
        void HedgeFilledMessageHandler(unsigned long clientOrderId,
                unsigned long price,
                unsigned long volume) override;

        // Called periodically to report the status of an order book.
        // The sequence number can be used to detect missed or out-of-order
        // messages. The five best available ask (i.e. sell) and bid (i.e. buy)
        // prices are reported along with the volume available at each of those
        // price levels.
        void OrderBookMessageHandler(ReadyTraderGo::Instrument instrument,
                unsigned long sequenceNumber,
                const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT> &askPrices,
                const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT> &askVolumes,
                const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT> &bidPrices,
                const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT> &bidVolumes) override;

        // Called when one of your orders is filled, partially or fully.
        void OrderFilledMessageHandler(unsigned long clientOrderId,
                unsigned long price,
                unsigned long volume) override;

        // Called when the status of one of your orders changes.
        // The fill volume is the number of lots already traded, remaining volume
        // is the number of lots yet to be traded and fees is the total fees paid
        // or received for this order.
        // Remaining volume will be set to zero if the order is cancelled.
        void OrderStatusMessageHandler(unsigned long clientOrderId,
                unsigned long fillVolume,
                unsigned long remainingVolume,
                signed long fees) override;

        // Called periodically when there is trading activity on the market.
        // The five best ask (i.e. sell) and bid (i.e. buy) prices at which there
        // has been trading activity are reported along with the aggregated volume
        // traded at each of those price levels.
        // If there are less than five prices on a side, then zeros will appear at
        // the end of both the prices and volumes arrays.
        void TradeTicksMessageHandler(ReadyTraderGo::Instrument instrument,
                unsigned long sequenceNumber,
                const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT> &askPrices,
                const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT> &askVolumes,
                const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT> &bidPrices,
                const std::array<unsigned long, ReadyTraderGo::TOP_LEVEL_COUNT> &bidVolumes) override;

        void SendBuyOrder(ReadyTraderGo::Instrument instrument, unsigned long price, unsigned long size);
        void SendSellOrder(ReadyTraderGo::Instrument instrument, unsigned long price, unsigned long size);
        void CancelBuyOrder();
        void CancelSellOrder();


    private:
        unsigned long _NextMessageId = 1;
        unsigned long _MessageCounter = 0;

        unsigned long _AskId = 0;
        unsigned long _ETFOrderAskPrice = 0;
        std::unordered_set<unsigned long> _Asks;

        unsigned long _BidId = 0;
        unsigned long _ETFOrderBidPrice = 0;
        std::unordered_set<unsigned long> _Bids;

        signed long _Position = 0;
        MovingAverage _PairSmall = MovingAverage(4);
        MovingAverage _PairBig = MovingAverage(60);


        OrderBook _ETF = OrderBook(ReadyTraderGo::Instrument::ETF);
        OrderBook _Future = OrderBook(ReadyTraderGo::Instrument::FUTURE);
        ZScore _ZScore;

        std::chrono::steady_clock::time_point _StartTime = std::chrono::steady_clock::now();
};


#endif // CPPREADY_TRADER_GO_AUTOTRADER_H
