import matplotlib.pyplot as plt
import re

palette = ['#7f7f7f', '#1f77b4', '#9467bd']

log_file = 'autotrader.log'

etf_mp_prices = []
etf_spreads = []
etf_skews = []
future_bid_prices = []
future_ask_prices = []
future_skew = []

with open('autotrader.log', 'r') as file:
    for line in file:
        # Extract bid and ask prices and skew for ETF market
        etf_mp_match = re.search(r'ETFMP: (\d+)', line)
        if etf_mp_match:
            etf_mp_prices.append(int(etf_mp_match.group(1)))
        
		# Extract ETF spread
        etf_sp_match = re.search(r'ETFMP: \d+SP: (\d+)', line)
        if etf_sp_match:
            etf_spreads.append(int(etf_sp_match.group(1)))

        # Extract ETF skew
        etf_skew_match = re.search(r'ETFMP: \d+SP: \d+ASkew: ([\d\.-]+)', line)
        if etf_skew_match:
            etf_skews.append(float(etf_skew_match.group(1)))

        # # Extract bid and ask prices and skew for futures market
        # future_bid_match = re.search(r'FutureMP: \d+ BID (\d+)', line)
        # future_ask_match = re.search(r'FutureMP: \d+ ASK (\d+)', line)
        # future_skew_match = re.search(r'FutureMP: \d+ BSkew: ([\d\.-]+)', line)
        # if future_bid_match and future_ask_match and future_skew_match:
        #     future_bid_prices.append(int(future_bid_match.group(1)))
        #     future_ask_prices.append(int(future_ask_match.group(1)))
        #     future_skew.append(float(future_skew_match.group(1))))

future_mp_prices = []
future_spreads = []
future_skews = []
future_bid_prices = []
future_ask_prices = []
future_skew = []

with open('autotrader.log', 'r') as file:
    for line in file:
        # Extract bid and ask prices and skew for future market
        future_mp_match = re.search(r'FutureMP: (\d+)', line)
        if future_mp_match:
            future_mp_prices.append(int(future_mp_match.group(1)))

	# Extract future spread
        future_sp_match = re.search(r'futureMP: \d+SP: (\d+)', line)
        if future_sp_match:
            future_spreads.append(int(future_sp_match.group(1)))

        # Extract future skew
        future_skew_match = re.search(r'futureMP: \d+SP: \d+ASkew: ([\d\.-]+)', line)
        if future_skew_match:
            future_skews.append(float(etf_skew_match.group(1)))

        # # Extract bid and ask prices and skew for futures market
        # future_bid_match = re.search(r'FutureMP: \d+ BID (\d+)', line)
        # future_ask_match = re.search(r'FutureMP: \d+ ASK (\d+)', line)
        # future_skew_match = re.search(r'FutureMP: \d+ BSkew: ([\d\.-]+)', line)
        # if future_bid_match and future_ask_match and future_skew_match:
        #     future_bid_prices.append(int(future_bid_match.group(1)))
        #     future_ask_prices.append(int(future_ask_match.group(1)))
        #     future_skew.append(float(future_skew_match.group(1))))

Ask_Prices_FUTURE = []
Bid_Prices_FUTURE = []

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

Ask_Prices_etf = []
Bid_Prices_etf = []

with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'ETF ASK (\d+)', line)
        if match:
            # Append integer to ask_prices list
            Ask_Prices_etf.append(int(match.group(1)))

with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'ETF .*? BID (\d+)', line)
        if match:
            # Append integer to ask_prices list
            Bid_Prices_etf.append(int(match.group(1)))

Interspread = []

with open(log_file, 'r') as file:
    for line in file:
        # Use regular expression to find integers next to "ASK PRICE"
        match = re.search(r'Interspread: (\d+)', line)
        if match:
            # Append integer to ask_prices list
            Interspread.append(int(match.group(1)))

fig, ax1 = plt.subplots(facecolor='#f0f0f0')
ax1.set_facecolor(color='slategrey')
# Plot the ETF midpoint prices on the first y-axis
color = 'tab:grey'
ax1.set_ylabel('interspread', color=color)
ax1.plot(Interspread, label='Spread', color='gainsboro')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_ylim(-1500, 1500)
# Create a second y-axis for the spreads and skews
ax2 = ax1.twinx()

# Plot the ETF spreads and skews on the second y-axis
color = 'tab:grey'

ax2.set_xlabel('Time')
ax2.set_ylabel('Midpoint Price', color=color)
ax2.plot(Ask_Prices_etf, color='blue')
ax2.plot(Bid_Prices_etf, color='orange')
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_ylim(148000, 154000)

plt.show()


# Add a legend to the chart

# Create x-axis values for the chart
# x_values = range(len(etf_mp_prices))
# Create a figure with two y-axes
fig, ax1 = plt.subplots(facecolor='#f0f0f0')
ax1.set_facecolor(color='slategrey')
# Plot the ETF midpoint prices on the first y-axis

# Create a second y-axis for the spreads and skews


# Plot the ETF spreads and skews on the second y-axis
color = 'tab:grey'
ax1.set_ylabel('Spread/Skew', color=color)
ax1.plot(Interspread, label='Spread', color='gainsboro')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_ylim(-1250, 1250)
# Add a legend to the chart
ax1.legend()
ax2 = ax1.twinx()
ax2.set_xlabel('Time')
ax2.set_ylabel('Midpoint Price', color='blue')
ax2.plot(etf_mp_prices, color='blue')
ax2.plot(future_mp_prices, color='orange')
ax2.tick_params(axis='y', labelcolor='black')
ax2.set_ylim(145000, 155000)



# NEXT GRAPH



# Show the chart
fig, ax1 = plt.subplots(facecolor='#f0f0f0')
ax1.set_facecolor(color='slategrey')
# Plot the ETF midpoint prices on the first y-axis
color = 'tab:grey'
ax1.set_ylabel('Spread/Skew', color=color)
ax1.plot(etf_skews, label='Spread', color='gainsboro')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_ylim(-1, 1)
# Create a second y-axis for the spreads and skews
ax2 = ax1.twinx()

# Plot the ETF spreads and skews on the second y-axis
color = 'tab:grey'


ax2.set_xlabel('Time')
ax2.set_ylabel('Midpoint Price', color=color)
ax2.plot(etf_mp_prices, color='blue')
ax2.plot(future_mp_prices, color='orange')
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_ylim(148000, 154000)

# Add a legend to the chart
ax2.legend()
plt.show()