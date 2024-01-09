import pandas as pd
import time
from binance.client import Client
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# Replace 'your_api_key' and 'your_api_secret' with your actual Binance API key and secret
api_key = 'rywhX43ozfOXWJ5G6eqvzV7FFh0rT4CCyWqffnIGdP1wkHVqY3FGUedGo9eUmirg'
api_secret = 'y2qlhQPZd6DTLwCqPrqCKLtIwVj3Z13hmiKilBFL8UjUOy4qBWlGV6EyAkkg6J0X'
client = Client(api_key, api_secret)

symbol = 'BTCUSDT'
quantity = 0.001  # The quantity of BTC to trade

# Moving averages periods
short_ma_period = 7
medium_ma_period = 25

# Function to fetch historical data
def fetch_historical_data():
    klines = client.get_historical_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=200)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df['close'] = df['close'].astype(float)
    return df

# Function to calculate moving averages
def calculate_moving_averages(df):
    df['short_ma'] = df['close'].rolling(window=short_ma_period).mean()
    df['medium_ma'] = df['close'].rolling(window=medium_ma_period).mean()
'''
# Function to plot the chart
def plot_chart(historical_data, signals):
    fig, ax1 = plt.subplots(figsize=(14,8))

    ax1.plot(historical_data.index, historical_data['close'], label='Price', color='blue')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Price', color='blue')
    ax1.tick_params('y', colors='blue')

    ax2 = ax1.twinx()
    buy_signals = signals[signals == 'Buy']
    sell_signals = signals[signals == 'Sell']

    ax2.plot(buy_signals.index, historical_data['close'].loc[buy_signals.index], '^', markersize=10, color='g', label='Buy Signal')
    ax2.plot(sell_signals.index, historical_data['close'].loc[sell_signals.index], 'v', markersize=10, color='r', label='Sell Signal')

    ax2.plot(historical_data.index, historical_data['short_ma'], label=f'Short MA ({short_ma_period} periods)', color='orange')
    ax2.plot(historical_data.index, historical_data['medium_ma'], label=f'Medium MA ({medium_ma_period} periods)', color='green')
    ax2.set_ylabel('Moving Averages', color='black')
    ax2.tick_params('y', colors='black')

    fig.suptitle('BTC/USDT Price and Moving Averages')
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))

    plt.show()
'''
# Function to plot the chart
def plot_chart(historical_data, signals):
    fig, ax1 = plt.subplots(figsize=(14, 8))

    ax1.plot(historical_data.index, historical_data['close'], label='Price', color='blue')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Price', color='blue')
    ax1.tick_params('y', colors='blue')

    ax2 = ax1.twinx()

    buy_signals = signals[signals == 'Buy'].index
    sell_signals = signals[signals == 'Sell'].index

    ax2.plot(buy_signals, historical_data['close'].loc[buy_signals], '^', markersize=10, color='g', label='Buy Signal')
    ax2.plot(sell_signals, historical_data['close'].loc[sell_signals], 'v', markersize=10, color='r', label='Sell Signal')

    ax2.plot(historical_data.index, historical_data['short_ma'], label=f'Short MA ({short_ma_period} periods)', color='orange')
    ax2.plot(historical_data.index, historical_data['medium_ma'], label=f'Medium MA ({medium_ma_period} periods)', color='green')
    ax2.set_ylabel('Moving Averages', color='black')
    ax2.tick_params('y', colors='black')

    fig.suptitle('BTC/USDT Price and Moving Averages')
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))

    plt.show()

# Function for the trading strategy
def trading_strategy(historical_data):
    signals = []
    for i in range(1, len(historical_data)):
        if historical_data['short_ma'].iloc[i-1] <= historical_data['medium_ma'].iloc[i-1] and historical_data['short_ma'].iloc[i] > historical_data['medium_ma'].iloc[i]:
            signals.append("Buy")
        elif historical_data['short_ma'].iloc[i-1] >= historical_data['medium_ma'].iloc[i-1] and historical_data['short_ma'].iloc[i] < historical_data['medium_ma'].iloc[i]:
            signals.append("Sell")
        else:
            signals.append("Hold")
    return pd.Series(signals, index=historical_data.index[:-1])

# Function to backtest the strategy
def backtest_strategy():
    historical_data = fetch_historical_data()
    calculate_moving_averages(historical_data)

    signals = trading_strategy(historical_data)

    # Backtesting
    positions = []
    balance = 0
    total_profit = 0
    max_drawdown = 0

    for i in range(len(signals)):
        if signals[i] == 'Buy':
            positions.append((historical_data.index[i], 'Buy', historical_data['close'].iloc[i]))
            balance -= historical_data['close'].iloc[i] * quantity
        elif signals[i] == 'Sell':
            if positions:
                entry_price = positions[-1][2]
                profit = (historical_data['close'].iloc[i] - entry_price) * quantity
                total_profit += profit
                balance += historical_data['close'].iloc[i] * quantity
                drawdown = balance - total_profit
                max_drawdown = min(max_drawdown, drawdown)
                positions = []
                print(f"Trade executed: Sell at {historical_data.index[i]}, Profit: {profit}, Total Profit: {total_profit}, Balance: {balance}, Max Drawdown: {max_drawdown}")

    # Plot the chart with signals
    plot_chart(historical_data, signals)

# Run backtesting
backtest_strategy()
