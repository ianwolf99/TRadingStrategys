from flask import Flask, render_template, Response, jsonify
from binance.client import Client
import pandas as pd
import mplfinance as mpf
from io import BytesIO
import time
import matplotlib.pyplot as plt

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
    
    # Convert columns to appropriate types
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

    df.set_index('timestamp', inplace=True)
    return df

def run_trading_logic(position):
    df = fetch_data()

    # Calculate moving averages and signals
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
            print(f"Buy order executed")
            # Execute Buy Order
            '''
            order = client.create_order(
                symbol=symbol,
                side='BUY',
                type='MARKET',
                quantity=quantity
            )
            '''
            # print(f"Buy Order Executed:")
            # position = 1

        elif row['short_signal'] and position != -1:
            # Execute Sell Order
            '''
            order = client.create_order(
                symbol=symbol,
                side='SELL',
                type='MARKET',
                quantity=quantity
            )
            '''

            print(f"Sell Order Executed:")
            position = -1

    # Print final position
    if position == 1:
        print("Final Position: Long")
    elif position == -1:
        print("Final Position: Short")
    else:
        print("Final Position: No position")

    # Plotting with mplfinance
    apds = [mpf.make_addplot(df['fast_ma'], color='orange'),  # Add fast MA
            mpf.make_addplot(df['slow_ma'], color='blue')]    # Add slow MA

    # Convert plot to bytes for display in Flask
    img_bytes = BytesIO()
    mpf.plot(df, type='candle', addplot=apds, style='yahoo', volume=True, show_nontrading=True, savefig=img_bytes)

    return img_bytes

@app.route('/')
def index():
    return render_template('index.html')
import base64
def generate_plot_data():
    position = 0  # Initialize position variable

    while True:
        img_bytes = run_trading_logic(position)

        # Convert binary image data to base64
        img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')

        # Prepare JSON response
        json_response = {
            'image': img_base64,
            'position': position,
        }

        # Return JSON response
        yield jsonify(json_response)
        time.sleep(300)  # Sleep for 5 minutes

@app.route('/plot')
def plot():
    return Response(generate_plot_data(), content_type='application/json')

if __name__ == '__main__':
    app.run(debug=True, threaded=False)
