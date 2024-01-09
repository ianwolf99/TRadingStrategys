import pandas as pd
import backtrader as bt
import talib
from binance.client import Client

# Replace 'your_api_key' and 'your_api_secret' with your actual Binance API key and secret
api_key = 'ADD YOURS'
api_secret = 'ADD YOURS'

class MyStrategy(bt.Strategy):
    params = (
        ("short_ma", 7),
        ("medium_ma", 25),
    )

    def __init__(self):
        self.short_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_ma)
        self.medium_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.medium_ma)

    def next(self):
        if self.short_ma[0] > self.medium_ma[0]:
            # Buy signal: Short MA above Medium MA
            self.buy()
        elif self.short_ma[0] < self.medium_ma[0]:
            # Sell signal: Short MA below Medium MA
            self.sell()

def fetch_historical_data():
    # Create a Binance API client
    client = Client(api_key, api_secret)

    klines = client.get_historical_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1HOUR, limit=200)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Ensure 'close' column is numeric and replace any non-convertible values with NaN
    df['close'] = pd.to_numeric(df['close'], errors='coerce')

    # Drop rows with missing or NaN values in any column
    df = df.dropna()

    # Set timestamp as index
    df.set_index('timestamp', inplace=True)
    return df

if __name__ == '__main__':
    # Create a Cerebro engine
    cerebro = bt.Cerebro()

    # Add the data to the engine
    cerebro.adddata(bt.feeds.PandasData(dataname=fetch_historical_data()))

    # Add the strategy to the engine
    cerebro.addstrategy(MyStrategy)

    # Set starting cash
    cerebro.broker.set_cash(10000.0)

    # Print starting cash
    print(f"Starting Portfolio Value: {cerebro.broker.getvalue()} USD")

    # Execute backtest
    cerebro.run()

    # Get final metrics
    final_balance = cerebro.broker.getvalue()
    print(f"Final Balance: {final_balance:.2f} USD")
