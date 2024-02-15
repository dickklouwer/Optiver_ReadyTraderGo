import re
import matplotlib.pyplot as plt
import numpy as np

log_file = 'autotrader.log'
DELTA_VWAP = []
BUY_PRICES = []
SELL_PRICES = []


# Open log file and loop over lines
with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'deltaVWAP\$(-?\d+)\$', line)
        if match:
            # Append integer to ask_prices list
            DELTA_VWAP.append(int(match.group(1)))

with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'BUYPRICE\$(\d+)\$', line)
        if match:
            # Append integer to ask_prices list
            BUY_PRICES.append(int(match.group(1)))

with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'SELLPRICE\$(\d+)\$', line)
        if match:
            # Append integer to ask_prices list
            SELL_PRICES.append(int(match.group(1)))

VWAP_PRICE = []

with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'New VWAP calculated:\$(-?\d+)\$', line)
        if match:
            # Append integer to ask_prices list
            VWAP_PRICE.append(int(match.group(1)))


"""
PARSING THE LOG FILE TO FIND THE ASK AND BID PRICE OF THE ETF
"""
Ask_Prices_ETF = []
Bid_Prices_ETF = []

with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'ASK PRICE ETF \$(\d+)\$', line)
        if match:
            # Append integer to ask_prices list
            Ask_Prices_ETF.append(int(match.group(1)))

with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'BID PRICE ETF \$(\d+)\$', line)
        if match:
            # Append integer to ask_prices list
            Bid_Prices_ETF.append(int(match.group(1)))

"""
CALCULATING THE MIDPOINT PRICE FOR THE ETF
"""
midpoint_prices = [(Bid_Prices_ETF[i] + Ask_Prices_ETF[i])/2 for i in range(1,len(Ask_Prices_ETF))]

"""
CALCULATING THE PRICE POINTS AND INDEX TO PLOT ON THE CHART
"""
sell_order_indices = []
sell_order_prices = []
Future_Vwap = []
with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'Future - VWAP: \$(\d+)\$', line)
        if match:
            # Append integer to ask_prices list
            Future_Vwap.append(int(match.group(1)))

for sell_price in SELL_PRICES:
    try:
        index = Ask_Prices_ETF.index(sell_price)
        sell_order_indices.append(index)
        sell_order_prices.append(sell_price)
    except ValueError:
        pass

sell_order_indices = np.array(sell_order_indices)
sell_order_prices = np.array(sell_order_prices)

buy_order_indices = []
buy_order_prices = []

for buy_price in BUY_PRICES:
    try:
        index = Bid_Prices_ETF.index(buy_price)
        buy_order_indices.append(index)
        buy_order_prices.append(buy_price)
    except ValueError:
        pass

buy_order_indices = np.array(buy_order_indices)
buy_order_prices = np.array(buy_order_prices)


"""
MAKING THE CHART
"""
PRICE_ETF = plt.figure(facecolor='lightgray')

"""
SETTING THE LINES
"""
plt.plot(Bid_Prices_ETF, color='blue')
plt.plot(Ask_Prices_ETF, color='orange', label="Midpoint Prices")
plt.plot(midpoint_prices, color='purple', label="Midpoint Prices")
plt.plot(Future_Vwap, color='grey')

plt.plot(sell_order_indices, sell_order_prices, marker='o', markersize=4, color='red', linestyle='')
plt.plot(buy_order_indices, buy_order_prices, marker='o', markersize=4, color='green', linestyle='')

"""
CHART SETTINGS
"""
plt.title("ETF PRICES")
plt.legend(['BID PRICE', 'ASK PRICE', 'MIDPOINT'])
plt.xlabel('Log Frequency')
plt.ylabel('Price')
plt.ylim(145000, 152000)
# plt.show()


# Plot ask prices using Matplotlib
# plt.plot(DELTA_VWAP, color='blue')

# plt.plot(BUY_PRICES, color='green')
# plt.plot(buy_PRICES, color='red')

# DeltaVwap = plt.figure()
# plt.plot(DELTA_VWAP, color='black')

# plt.ylim(-550, 250)

# plt.legend(['SELLS', 'BUYS'])
# plt.title('PRICE DATA')

# plt.ylabel('ASK PRICE')


# # fig2 = plt.figure()


# VWAP_Price = plt.figure()
# plt.plot(VWAP_PRICE, color='blue')
# plt.plot(midpoint_prices, color='purple', label="Midpoint Prices")

# plt.show()
# import re

# with open('autotrader.log', 'r') as f:
#     log_data = f.read()

# ask_prices = re.findall(r'ASK PRICE \$([0-9]+)\$', log_data)
# for price in ask_prices:
#     print(price)


"""
PARSING THE LOG FILE TO FIND THE ASK AND BID PRICE OF THE FUTURE
"""
Ask_Prices_FUTURE = []
Bid_Prices_FUTURE = []
Future_Vwap = []
with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'Future - VWAP: \$(\d+)\$', line)
        if match:
            # Append integer to ask_prices list
            Future_Vwap.append(int(match.group(1)))




with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'ASK PRICE FUTURE \$(-?\d+)\$', line)
        if match:
            # Append integer to ask_prices list
            Ask_Prices_FUTURE.append(int(match.group(1)))

with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'BID PRICE FUTURE \$(-?\d+)\$', line)
        if match:
            # Append integer to ask_prices list
            Bid_Prices_FUTURE.append(int(match.group(1)))

"""
    CALCULATING THE MIDPOINT PRICE FOR THE FUTURE
"""
midpoint_prices_FUTURE = [(Bid_Prices_FUTURE[i] + Ask_Prices_FUTURE[i])/2 for i in range(1,len(Ask_Prices_FUTURE))]


"""
    MAKING THE CHART
"""
PRICE_FUTURE = plt.figure(facecolor='lightgray')


"""
    SETTING THE LINES
"""
plt.plot(Bid_Prices_FUTURE, color='blue')
plt.plot(Ask_Prices_FUTURE, color='orange', label="Midpoint Prices")
plt.plot(midpoint_prices_FUTURE, color='purple', label="Midpoint Prices")
plt.plot(Future_Vwap, color='grey')


"""
    CHART SETTINGS
"""
plt.title("FUTURE PRICES")
plt.legend(['BID PRICE', 'ASK PRICE', 'MIDPOINT'])
plt.xlabel('Log Frequency')
plt.ylabel('Price')
plt.ylim(145000, 152000)

"""
    MIDPOINT PRICES OF FUTURE & ETF
"""

CORR_CHART = plt.figure(facecolor='lightgray')

plt.plot(midpoint_prices, color='blue')
plt.plot(midpoint_prices_FUTURE, color='orange', label="Midpoint Prices")

"""
    CORRELATION BETWEEN ETF AND FUTURES PRICE
"""
correlation_coefficient = np.corrcoef(midpoint_prices, midpoint_prices_FUTURE)[0,1]
print(correlation_coefficient)

# correlation_array = []

# # loop over price histories and calculate correlation for each iteration
# for i in range(len(midpoint_prices)):
#     correlation = np.corrcoef(midpoint_prices[:i+1], midpoint_prices_FUTURE[:i+1])[0, 1]
#     correlation_array.append(correlation)


# plt.title(f"Correlation: {correlation_coefficient:.2f}")
# plt.legend(['ETF MIDPOINT', 'FUTURE MIDPOINT'])
# plt.xlabel('Log Frequency')
# plt.ylabel('Price')
# plt.ylim(145000, 152000)


# correlation_plot = plt.figure(facecolor='lightgray')
# plt.plot(correlation_array)
# plt.title("Correlation between Instrument 1 and Instrument 2 over Time")
# plt.xlabel("Time")
# plt.ylabel("Correlation")
plt.show()


moment_index = 2  # Note that index 2 corresponds to the third moment, since Python uses zero-based indexing

# Extract the prices for both instruments at the given moment
price1 = midpoint_prices[moment_index]
price2 = midpoint_prices_FUTURE[moment_index]

# Calculate the correlation coefficient using the corrcoef function from NumPy
correlation_coefficient = np.corrcoef([price1, price2])


# Print the result
# print(f"The correlation coefficient at moment {moment_index} is {correlation_coefficient:.2f}")
# calculate correlation coefficient at each moment
"""
    CORRELATION CALCULATION OVER ALL THE GIVEN MOMENTS NOT WORKING YET!!!!!!!!!!
"""
# correlation_coefficients = []
# for i in range(1, len(midpoint_prices_FUTURE)):
#     # price1 = np.array(midpoint_prices[i], midpoint_prices[i+1])
#     price2 = np.array(midpoint_prices_FUTURE[i], midpoint_prices_FUTURE[i+1])
#     correlation_coefficient = np.corrcoef(price1, price2)[0,1]
#     correlation_coefficients.append(correlation_coefficient)
#
# print(correlation_coefficients)
# # plot prices and correlation coefficient
# fig, ax = plt.subplots(figsize=(10, 5))
# ax.plot(midpoint_prices, color='grey', label='Midpoint Prices')
# ax.plot(midpoint_prices_FUTURE, color='black', label='Midpoint Prices')
# ax.set_xlabel('Time')
# ax.set_ylabel('Price')
# ax.legend(loc='upper left')
#
# ax2 = ax.twinx()
# ax2.plot(correlation_coefficients, color='blue', label='Correlation Coefficient')
# ax2.set_ylabel('Correlation Coefficient')
# ax2.legend(loc='upper right')
#
# plt.text(0.5, 0.9, f"Correlation Coefficient: {correlation_coefficient:.2f}", transform=plt.gca().transAxes)
#
# plt.title('ETF Price History with Correlation Coefficient')
#
# plt.show()

