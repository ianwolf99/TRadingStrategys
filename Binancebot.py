import pandas as pd
import plotly.graph_objects as go
import time
import threading
from binance.client import Client

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

# Function to plot the chart
def plot_chart():
    while True:
        if historical_data is not None:
            fig = go.Figure()

            fig.add_trace(go.Candlestick(x=historical_data.index,
                                         open=historical_data['open'],
                                         high=historical_data['high'],
                                         low=historical_data['low'],
                                         close=historical_data['close'],
                                         name='Candlesticks'))

            fig.add_trace(go.Scatter(x=historical_data.index, y=historical_data['short_ma'],
                                     mode='lines',
                                     name=f'Short MA ({short_ma_period} periods)',
                                     line=dict(color='orange')))

            fig.add_trace(go.Scatter(x=historical_data.index, y=historical_data['medium_ma'],
                                     mode='lines',
                                     name=f'Medium MA ({medium_ma_period} periods)',
                                     line=dict(color='green')))

            fig.update_layout(title='BTC/USDT Price and Moving Averages',
                              xaxis_title='Time',
                              yaxis_title='Price')

            # Show the plot and export it as a static image
            fig.show(validate=False)
            fig.write_image('btc_chart.png')

            time.sleep(3600)  # 1 hour

# Function to execute a trade
def execute_trade(side):
    try:
        order = client.create_order(
            symbol=symbol,
            side=side,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity
        )
        print(f"Order executed: {side} {quantity} BTC at market price. Order details: {order}")
    except Exception as e:
        print(f"Error executing order: {e}")

# Function for the trading strategy
def trading_strategy():
    while True:
        if historical_data is not None:
            if historical_data['short_ma'].iloc[-1] > historical_data['medium_ma'].iloc[-1]:
                # Buy signal: Short MA above Medium MA
                print("Buying")
                # execute_trade(side=Client.SIDE_BUY)
            elif historical_data['short_ma'].iloc[-1] < historical_data['medium_ma'].iloc[-1]:
                # Sell signal: Short MA below Medium MA
                print("Selling")
                # execute_trade(side=Client.SIDE_SELL)
            time.sleep(3600)  # 1 hour

# Global variable to store the latest historical data
historical_data = fetch_historical_data()  # Fetch historical data once before starting threads
calculate_moving_averages(historical_data)  # Calculate moving averages

# Create threads for plotting and strategy execution
plot_thread = threading.Thread(target=plot_chart)
strategy_thread = threading.Thread(target=trading_strategy)

# Start the threads
plot_thread.start()
strategy_thread.start()

# Main loop for monitoring and updating orders
while True:
    try:
        # Fetch historical data
        historical_data = fetch_historical_data()

        # Calculate moving averages
        calculate_moving_averages(historical_data)

        # Sleep for a certain period (adjust as needed)
        time.sleep(3600)  # 1 hour

    except Exception as e:
        print(f"Error: {e}")
        # Handle errors or add logging as needed
