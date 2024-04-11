import pandas as pd
import numpy as np

# Load your data
bch_usd = pd.read_csv("BCH-USD.csv")
bch_usd['Date'] = pd.to_datetime(bch_usd['Date'])
bch_usd['Close'] = pd.to_numeric(bch_usd['Close'], errors='coerce')

def compute_cumulative_profit(df, sensitivity, window1, window2, fee=0.02):
    # Calculate smoothed prices
    df['1Week_Smoothed'] = df['Close'].rolling(window=int(window1)).mean()
    df['2Week_Smoothed'] = df['Close'].rolling(window=int(window2)).mean()
    df['Smoothed_Difference'] = (df['2Week_Smoothed'] - df['1Week_Smoothed']) / df['1Week_Smoothed'] * 100

    # Trading signals
    df['Signal'] = 0
    df.loc[df['Smoothed_Difference'] < -sensitivity, 'Signal'] = 1  # Buy
    df.loc[df['Smoothed_Difference'] > sensitivity, 'Signal'] = -1  # Sell

    # Calculate trades and profits
    df['Position'] = df['Signal'].replace(to_replace=0, method='ffill')
    df['Position'] = df['Position'].shift(1).fillna(0)
    df['Market Returns'] = df['Close'].pct_change()
    df['Strategy Returns'] = df['Market Returns'] * df['Position']

    # Assuming fees: Subtract transaction fees from returns when a trade occurs
    df['Trades'] = df['Position'].diff().fillna(0).abs()
    df['Strategy Returns'] -= df['Trades'] * fee

    # Cumulative profit calculation
    df['Cumulative Profit'] = (1 + df['Strategy Returns']).cumprod() - 1

    # Return the final cumulative profit
    return df['Cumulative Profit'].iloc[-1]

# Grid search setup
sensitivity_range = np.arange(0.01, 0.11, 0.01)
window1_range = range(5, 16)
window2_range = range(10, 31)

# Store the best settings found
best_profit = -np.inf
best_settings = {}

# Grid search
for sensitivity in sensitivity_range:
    for window1 in window1_range:
        for window2 in window2_range:
            if window2 > window1:  # Ensure that window2 is greater than window1
                profit = compute_cumulative_profit(bch_usd.copy(), sensitivity, window1, window2)
                if profit > best_profit:
                    best_profit = profit
                    best_settings = {'sensitivity': sensitivity, 'window1': window1, 'window2': window2, 'profit': profit}

# Output the best results
print("Best Settings:")
print(f"Sensitivity: {best_settings['sensitivity']}")
print(f"Window1: {best_settings['window1']}")
print(f"Window2: {best_settings['window2']}")
print(f"Cumulative Profit: {best_settings['profit']}")
