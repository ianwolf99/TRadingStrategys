import yfinance as yf
import mplfinance as mpf
import matplotlib.pyplot as plt

# Function to fetch historical data for a given ticker symbol
def fetch_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

# Function to calculate Simple Moving Averages (SMA)
def calculate_sma(data, window):
    return data['Close'].rolling(window=window).mean()

# Function to visualize crosses with bear and bull signals using mplfinance
def visualize_crosses(data, ma_50, ma_200):
    # Add moving averages to the data
    data['MA50'] = ma_50
    data['MA200'] = ma_200

    # Create a new axis for signals
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()

    # Plot the financial chart with candlestick plot
    mpf.plot(data, type='candle', mav=(50, 200), style='yahoo', ax=ax1)

    # Find bear and bull crosses
    bear_crosses = data[data['MA50'] < data['MA200']]
    bull_crosses = data[data['MA50'] > data['MA200']]

    # Annotate bear crosses with red arrows
    for date in bear_crosses.index:
        ax2.annotate('▼', xy=(date, data['Close'][date]), xytext=(date, data['Close'][date] + 500),
                     arrowprops=dict(facecolor='red', edgecolor='red', shrink=0.05), fontsize=12, color='red', ha='center')

    # Annotate bull crosses with green arrows
    for date in bull_crosses.index:
        ax2.annotate('▲', xy=(date, data['Close'][date]), xytext=(date, data['Close'][date] - 500),
                     arrowprops=dict(facecolor='green', edgecolor='green', shrink=0.05), fontsize=12, color='green', ha='center')

    # Set axis labels and legend
    ax1.set_ylabel('Price (USD)')
    ax2.set_ylabel('Signals')
    
    # Display the chart
    plt.title('BTCUSD Price with 50-day and 200-day SMAs')
    plt.show()

# Main function
def main():
    # Set the ticker symbol and date range
    ticker_symbol = 'BTC-USD'
    start_date = '2015-01-01'
    end_date = '2024-01-15'

    # Fetch historical data
    data = fetch_data(ticker_symbol, start_date, end_date)

    # Calculate 50-day and 200-day SMAs
    ma_50 = calculate_sma(data, window=50)
    ma_200 = calculate_sma(data, window=200)

    # Visualize crosses with bear and bull signals using mplfinance
    visualize_crosses(data, ma_50, ma_200)

if __name__ == "__main__":
    main()
