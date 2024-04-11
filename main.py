import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file into a DataFrame
bch_usd = pd.read_csv("BCH-USD.csv")

bch_usd = bch_usd.iloc[385:2300]
bch_usd.reset_index(drop=True, inplace=True)



sensitivity = 2
# Convert 'Date' column to datetime format if it's not already
bch_usd['Date'] = pd.to_datetime(bch_usd['Date'])
bch_usd = bch_usd[['Close', 'Date']]
# Calculate 1-week and 2-week smoothed closing prices
window1 = 5
window2 = 20
bch_usd['1Week_Smoothed'] = bch_usd['Close'].rolling(window=window1).mean()
bch_usd['2Week_Smoothed'] = bch_usd['Close'].rolling(window=window2).mean()

# Plotting the data
plt.figure(figsize=(12, 6))
plt.plot(bch_usd['Date'], bch_usd['Close'], label='Close', color='blue')
plt.plot(bch_usd['Date'], bch_usd['1Week_Smoothed'], label='1Week_Smoothed', color='red')
plt.plot(bch_usd['Date'], bch_usd['2Week_Smoothed'], label='2Week_Smoothed', color='green')

# Adding title and labels
plt.title('Bitcoin Cash (BCH) Price Analysis')
plt.xlabel('Date')
plt.ylabel('Price (USD)')

# Adding legend
plt.legend()

# Rotating x-axis labels for better readability
plt.xticks(rotation=45)

# Displaying the plot
plt.tight_layout()
#plt.show()


# Calculate the percentage difference between 1-week and 2-week smoothed prices
bch_usd['Smoothed_Difference'] = (bch_usd['2Week_Smoothed'] - bch_usd['1Week_Smoothed']) / bch_usd['1Week_Smoothed'] * 100

# Create a column to indicate if 1-week smoothing is greater than 2-week smoothing, with condition for difference less than or equal to 5%
bch_usd['1Week_Greater'] = 0
bch_usd['2Week_Greater'] = 0
bch_usd['Smoothed_Difference'] = (bch_usd['2Week_Smoothed'] - bch_usd['1Week_Smoothed']) / bch_usd['1Week_Smoothed'] * 100
# Create a column to indicate if 1-week smoothing is greater than 2-week smoothing
bch_usd.loc[bch_usd['Smoothed_Difference'] < -sensitivity, '1Week_Greater'] = 1
bch_usd.loc[bch_usd['Smoothed_Difference'] > sensitivity, '2Week_Greater'] = 1

# Define the initial capital
initial_capital = 1000
# Create a new column with the initial capital
bch_usd['Initial_Capital'] = initial_capital
bch_usd['HODL'] = 0

# Determine Buy and Sell signals
for i in range(1, len(bch_usd)):
    if bch_usd.loc[i, '1Week_Greater'] > bch_usd.loc[i, '2Week_Greater']:
        bch_usd.loc[i, 'Buy'] = 1
        bch_usd.loc[i, 'HODL'] = 1
    elif bch_usd.loc[i, '1Week_Greater'] < bch_usd.loc[i, '2Week_Greater']:
        bch_usd.loc[i, 'Sell'] = 1
        bch_usd.loc[i, 'HODL'] = -1
    else:
        bch_usd.loc[i, ['Buy', 'Sell']] = 0
        bch_usd.loc[i, 'HODL'] = 1

bch_usd['Buy/Sell'] = bch_usd['HODL'].diff().fillna(0)
bch_usd = bch_usd[['Close', 'Date','Buy/Sell','Initial_Capital']]
bch_usd['bought_price'] = 0
bch_usd['profit'] = 0

fee = 0.00

for index, row in bch_usd.iterrows():
    close_price = row['Close']
    buy_sell_signal = row['Buy/Sell']
    if(row['Buy/Sell']>0):
        bch_usd['bought_price'][index] = close_price
        bought_price = close_price
    if(row['Buy/Sell']==-2):
        bch_usd['profit'][index]  = close_price - bought_price*(1+fee)


# Calculate cumulative sum of profits
bch_usd['Cumulative_Profit'] = bch_usd['profit'].cumsum()
bch_usd['Initial_Capital']  += bch_usd['Cumulative_Profit']


# Normalize Initial_Capital and Close price to start at 100
initial_capital_normalized = (bch_usd['Initial_Capital'] / initial_capital) * 100
close_price_normalized = (bch_usd['Close'] / bch_usd['Close'].iloc[0]) * 100
non_zero_signals = bch_usd[bch_usd['Buy/Sell'] != 0]
# Plot the normalized cumulative profit and Close price
plt.figure(figsize=(10, 6))
plt.plot(bch_usd['Date'], initial_capital_normalized, label='Normalized Initial Capital', color='blue')
plt.plot(bch_usd['Date'], close_price_normalized, label='Normalized Close Price', color='red')
scaled_signals_abs = abs(non_zero_signals['Buy/Sell'] )
buy_sell_colors = ['green' if x > 0 else 'red' for x in non_zero_signals['Buy/Sell']]
plt.scatter(non_zero_signals['Date'], scaled_signals_abs* 50, label='Buy/Sell Signals', color=buy_sell_colors, marker='^')
plt.title('Normalized Initial Capital and Close Price for BCH-USD')
plt.xlabel('Date')
plt.ylabel('Normalized Value (Starts at 100)')
plt.legend()
plt.grid(True)
plt.show()

bch_usd = bch_usd[['Close', 'Date','Initial_Capital']]
print(bch_usd)