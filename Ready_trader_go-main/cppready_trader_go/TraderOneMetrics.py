import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the files
score_board_df = pd.read_csv("score_board_1.csv")
match_events_df = pd.read_csv("match_events_1.csv")

# Filter the match events to only show TraderOne's orders
trader_one_orders = match_events_df[match_events_df["Competitor"] == "TraderOne"]

# Extract the account balance, total fees, ETF price, future price, and profit/loss from the score board
account_balance = score_board_df["AccountBalance"]
total_fees = score_board_df["TotalFees"]
etf_price = score_board_df["EtfPrice"]
future_price = score_board_df["FuturePrice"]
profit_loss = score_board_df["ProfitOrLoss"]

# Create the plot
# fig, ax = plt.subplots(figsize=(12, 8))

# # Plot the prices on the left axis
# ax.plot(score_board_df["Time"], etf_price, color="orange", label="ETF Price")
# ax.plot(score_board_df["Time"], future_price,
#         color="gray", label="Future Price")
# ax.set_ylabel("Price/PL")

# # Plot the trader one orders on the right axis
# ax2 = ax.twinx()
# ax2.plot(score_board_df["Time"], account_balance,
#          color="red", label="Account Balance")
# ax2.plot(score_board_df["Time"], total_fees, color="blue", label="Total Fees")
# ax2.set_ylabel("Account Balance/Total Fees")

# # Plot a line between the prices at which TraderOne implemented its orders
# # last_order = None
# # for i, order in trader_one_orders.iterrows():
# #     if last_order is not None:
# #         ax.plot([last_order["Time"], order["Time"]], [
# #                 last_order["Price"], order["Price"]], color="black")
# #     last_order = order

# # Add a legend and titles
# ax.legend(('ETF Price', 'Future Price'), loc="upper left")
# ax2.legend(('Account Balance', 'Total Fees Over Time'), loc="upper right")

# plt.ylim(-100000, 400000)
# plt.title("TraderOne's Account Balance over Time")

# # Show the plot
# plt.show()

fig, ax = plt.subplots(figsize=(12, 8))
ax.plot(score_board_df["Time"], (etf_price + future_price) / 2, color="orange", label="ETF Price")
last_order = None
for i, order in trader_one_orders.iterrows():
    if last_order is not None:
        ax.plot([last_order["Time"], order["Time"]], [
                last_order["Price"], order["Price"]], color="black")
    last_order = order

last_order_price = None
last_order_time = None

ax2 = ax.twinx()
ax2.plot(score_board_df["Time"], account_balance,
         color="red", label="Account Balance")
ax2.set_ylim(-20000, 400000)
last_order_price = None
last_order_time = None

# for i, order in trader_one_orders.iterrows():
#     x = order["Time"]
#     y = order["Price"]
#     if order["Side"] == "B":
#         if order["Instrument"] == 0:
#             marker = "^"
#             color = "green"
#         else:
#             marker = "v"
#             color = "blue"
#     elif order["Side"] == "S":
#         marker = "v"
#         color = "red"
#     elif order["Operation"] == "Hedge":
#         if order["Instrument"] == 0:
#             marker = "D"
#             color = "blue"
#         # else:
#         #     marker = "o"
#             # color = "orange"
#     elif order["Operation"] == "Cancel":
#         marker = "x"
#         color = "red"
#     elif order["Operation"] == "Insert":
#         marker = "+"
#         color = "green"
#         if last_order_price is not None:
#             ax2.plot([last_order_time, x], [
#                      last_order_price, y], color="black")
#         last_order_price = y
#         last_order_time = x
#     ax2.plot(x, y, marker=marker, color=color)
# ax2.set_ylabel("Order Price")

plt.ylim(-30000, 400000)
plt.show()