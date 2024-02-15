import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np
from ipywidgets import widgets


log_file = 'autotrader3.log'
DELTA_VWAP = []
BUY_PRICES = []
SELL_PRICES = []
hedge_order_data = []
hedge_order_prices = []

"""
PARSING THE LOG FILE TO FIND THE ASK AND BID PRICE OF THE FUTURE
"""
Ask_Prices_FUTURE = []
Bid_Prices_FUTURE = []
vwap_FUTURE = []

with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'Future ASK (\d+)', line)
        if match:
            # Append integer to ask_prices list
            Ask_Prices_FUTURE.append(int(match.group(1)))

with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'Future .*? BID (\d+)', line)
        if match:
            # Append integer to ask_prices list
            Bid_Prices_FUTURE.append(int(match.group(1)))

with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'Future - VWAP: \$(-?\d+)\$', line)
        if match:
            # Append integer to ask_prices list
            vwap_FUTURE.append(int(match.group(1)))


"""
   HEDGE ORDER CALCULATIONS -- 
"""
hedge_orders = []
with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'lots at \$(\d+) average price in cents', line)
        if match:
            # Append integer to ask_prices list
            hedge_orders.append(int(match.group(1)))

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
        match = re.search(r'BUY PRICE(\d+)', line)
        if match:
            # Append integer to ask_prices list
            BUY_PRICES.append(int(match.group(1)))

with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'SELL PRICE(\d+)', line)
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
vwap_ETF = []

with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'ETF ASK (\d+) ', line)
        if match:
            # Append integer to ask_prices list
            Ask_Prices_ETF.append(int(match.group(1)))

with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'ETF .*? BID (\d+)', line)
        if match:
            # Append integer to ask_prices list
            Bid_Prices_ETF.append(int(match.group(1)))

# print(Bid_Prices_ETF)
with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'ETF - VWAP: \$(-?\d+)\$', line)
        if match:
            # Append integer to ask_prices list
            vwap_ETF.append(int(match.group(1)))



"""
CALCULATING THE MIDPOINT PRICE FOR THE ETF
"""
midpoint_prices = [(Bid_Prices_ETF[i] + Ask_Prices_ETF[i])/2 for i in range(1,len(Ask_Prices_ETF))]

"""
CALCULATING THE PRICE POINTS AND INDEX TO PLOT ON THE CHART
"""
sell_order_indices = []
sell_order_prices = []

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

for hedge_order in hedge_orders:
    try:
        index = Ask_Prices_FUTURE.index(hedge_order)
        hedge_order_data.append((index, hedge_order))
    except ValueError:
        pass

"""
MAKING THE CHART
"""
# PRICE_ETF = plt.figure(facecolor='lightgray')
fig, ax = plt.subplots()
"""
SETTING THE LINES
"""
for index, price in hedge_order_data:
    hedgeOrders = plt.plot(index, price, marker='d', markersize=4, color='blue', linestyle='')
# sellO = ax.plot(sell_order_indices, sell_order_prices, marker='v', markersize=8, color='red', linestyle='')
# buyO = ax.plot(buy_order_indices, buy_order_prices, marker='^', markersize=8, color='green', linestyle='')

# B_ETF = ax.plot(Bid_Prices_ETF, color='blue')
# B_FUTURE = ax.plot(Bid_Prices_FUTURE, color='lightblue')
# A_FUTURE = ax.plot(Ask_Prices_FUTURE, color='red')
# A_ETF = ax.plot(Ask_Prices_ETF, color='pink', label="Midpoint Prices")
# M_PRICE = ax.plot(midpoint_prices, color='orange', label="Midpoint Prices")

sellO = plt.plot(sell_order_indices, sell_order_prices, marker='v', markersize=5, color='red', linestyle='')
buyO = plt.plot(buy_order_indices, buy_order_prices, marker='^', markersize=5, color='green', linestyle='')
B_ETF = plt.plot(Bid_Prices_ETF, color='blue')
B_FUTURE = plt.plot(Bid_Prices_FUTURE, color='lightblue')
A_FUTURE = plt.plot(Ask_Prices_FUTURE, color='red')
A_ETF = plt.plot(Ask_Prices_ETF, color='pink', label="Midpoint Prices")
M_PRICE = plt.plot(midpoint_prices, color='orange', label="Midpoint Prices")

hedgeOrders_button_ax = plt.axes([0.1, 0.9, 0.05, 0.02])
sellO_button_ax = plt.axes([0.2, 0.9, 0.05, 0.02])
buyO_button_ax = plt.axes([0.3, 0.9, 0.05, 0.02])
B_ETF_button_ax = plt.axes([0.4, 0.9, 0.05, 0.02])
A_ETF_button_ax = plt.axes([0.5, 0.9, 0.05, 0.02])
B_FUTURE_button_ax = plt.axes([0.6, 0.9, 0.05, 0.02])
A_FUTURE_button_ax = plt.axes([0.7, 0.9, 0.05, 0.02])
M_PRICE_button_ax = plt.axes([0.8, 0.9, 0.05, 0.02])

# Create a button for each plot
hedgeOrders_button = plt.Button(ax=hedgeOrders_button_ax, label='Hedge Orders')
sellO_button = plt.Button(ax=sellO_button_ax, label='Sell Orders')
buyO_button = plt.Button(ax=buyO_button_ax, label='Buy Orders')
B_ETF_button = plt.Button(ax=B_ETF_button_ax, label='Bid Prices ETF')
B_FUTURE_button = plt.Button(ax=B_FUTURE_button_ax, label='Bid Prices FUTURE')
A_FUTURE_button = plt.Button(ax=A_FUTURE_button_ax, label='Ask Prices FUTURE')
A_ETF_button = plt.Button(ax=A_ETF_button_ax, label='Ask Prices ETF')
M_PRICE_button = plt.Button(ax=M_PRICE_button_ax, label='Midpoint Prices')

# Define the toggle_visibility function


def toggle_visibility(line):
    line.set_visible(not line.get_visible())
    plt.draw()


# Connect each button to its callback function
hedgeOrders_button.on_clicked(lambda event: toggle_visibility(sellO[0]))
sellO_button.on_clicked(lambda event: toggle_visibility(sellO[0]))
buyO_button.on_clicked(lambda event: toggle_visibility(buyO[0]))
B_ETF_button.on_clicked(lambda event: toggle_visibility(B_ETF[0]))
B_FUTURE_button.on_clicked(lambda event: toggle_visibility(B_FUTURE[0]))
A_FUTURE_button.on_clicked(lambda event: toggle_visibility(A_FUTURE[0]))
A_ETF_button.on_clicked(lambda event: toggle_visibility(A_ETF[0]))
M_PRICE_button.on_clicked(lambda event: toggle_visibility(M_PRICE[0]))

# Show the legend
"""
CHART SETTINGS
"""
plt.ylim(145000, 158000)
plt.title("ALL AVAILABLE DATA")
plt.legend(['HEDGE ORDER', 'SELL ORDER', 'BUY ORDER', 'BID PRICE ETF', 'BID PRICE FUTURE', 'ASK PRICE FUTURE', 'ASK PRICE ETF', 'MIDPOINT PRICE'])
# plt.xlabel('Log Frequency')
# plt.ylabel('Price')
ax.set_ylim(145000, 158000)
# plt.show()
# """
#           FUTURE PRICE CHART.
# """




"""
    CALCULATING THE MIDPOINT PRICE FOR THE FUTURE
"""
midpoint_prices_FUTURE = [(Bid_Prices_FUTURE[i] + Ask_Prices_FUTURE[i])/2 for i in range(1,len(Ask_Prices_FUTURE))]

# """
#     MAKING THE CHART
# """
# PRICE_FUTURE = plt.figure(facecolor='lightgray')


# """
#     SETTING THE LINES
# """
# for index, price in hedge_order_data:
#     plt.plot(index, price, marker='^', markersize=8,
#              color='green', linestyle='')
# # plt.plot(sell_order_indices, hedge_order_indices, marker='v', markersize=8, color='red', linestyle='')
# # plt.plot(buy_order_indices, hedge_order_prices, marker='^', markersize=8, color='green', linestyle='')
# plt.plot(Bid_Prices_FUTURE, color='blue')
# plt.plot(Ask_Prices_FUTURE, color='orange', label="Midpoint Prices")
# # plt.plot(vwap_FUTURE, color='red')
# plt.plot(midpoint_prices_FUTURE, color='purple', label="Midpoint Prices")


# """
#     CHART SETTINGS
# """
# plt.title("FUTURE PRICE")
# plt.legend(['BID PRICE', 'ASK PRICE', 'MIDPOINT PRICE'])
# plt.xlabel('Log Frequency')
# plt.ylabel('Price')
# plt.ylim(145000, 158000)

"""
    MIDPOINT PRICES OF FUTURE & ETF
"""

CORR_CHART = plt.figure(facecolor='lightgray')

plt.plot(midpoint_prices, color='blue')
plt.plot(midpoint_prices_FUTURE, color='orange', label="Midpoint Prices")
plt.title("MIDPOINT PRICES")
plt.legend(['Midpoint Price ETF', 'Midpoint Price Future'])
plt.xlabel('Log Frequency')
plt.ylabel('Midpoint Price')
plt.ylim(145000, 158000)
plt.show()