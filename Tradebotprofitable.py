from flask import Flask, render_template, Response
from binance.client import Client
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import time

# Binance API configuration (replace with your own keys)
api_key = 'rywhX43ozfOXWJ5G6eqvzV7FFh0rT4CCyWqffnIGdP1wkHVqY3FGUedGo9eUmirg'
api_secret = 'y2qlhQPZd6DTLwCqPrqCKLtIwVj3Z13hmiKilBFL8UjUOy4qBWlGV6EyAkkg6J0X'
symbol = 'BTCUSDT'
timeframe = '1h'

# Initialize Binance client
client = Client(api_key, api_secret)

app = Flask(__name__)

def fetch_data():
    # Fetch historical klines
    klines = client.get_klines(symbol=symbol, interval=timeframe)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

def run_trading_logic():
    df = fetch_data()

    # Calculate RSI and signals
    df['fast_ma'] = df['close'].ewm(span=13, adjust=False).mean()
    df['slow_ma'] = df['close'].ewm(span=21, adjust=False).mean()
    df['long_signal'] = (df['fast_ma'] > df['slow_ma']) & (df['fast_ma'].shift() <= df['slow_ma'].shift())
    df['short_signal'] = (df['fast_ma'] < df['slow_ma']) & (df['fast_ma'].shift() >= df['slow_ma'].shift())

    # Trading logic
    balance = 10000  # Set your initial balance
    quantity = 1  # Set your trading quantity
    position = 0  # 0: No position, 1: Long, -1: Short

    for index, row in df.iterrows():
        if row['long_signal'] and position != 1:
            # Execute Buy Order
            order = client.create_market_buy(symbol=symbol, quantity=quantity)
            print(f"Buy Order Executed: {order}")
            position = 1

        elif row['short_signal'] and position != -1:
            # Execute Sell Order
            order = client.create_market_sell(symbol=symbol, quantity=quantity)
            print(f"Sell Order Executed: {order}")
            position = -1

    # Print final position
    if position == 1:
        print("Final Position: Long")
    elif position == -1:
        print("Final Position: Short")
    else:
        print("Final Position: No position")

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(df['close'], label='Close Price', linewidth=1)
    plt.scatter(df.index[df['long_signal']], df['close'][df['long_signal']], marker='^', color='g', label='Long Signal')
    plt.scatter(df.index[df['short_signal']], df['close'][df['short_signal']], marker='v', color='r', label='Short Signal')
    plt.title('Trading Results with Buy/Sell Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

    # Convert plot to bytes for display in Flask
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)
    plt.close()

    return img_bytes

@app.route('/')
def index():
    return render_template('index.html')

def generate_plot():
    while True:
        img_bytes = run_trading_logic()

        yield (b'--frame\r\n'
               b'Content-Type: image/png\r\n\r\n' + img_bytes.read() + b'\r\n')

        time.sleep(300)  # Sleep for 5 minutes

@app.route('/plot')
def plot():
    return Response(generate_plot(), content_type='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
