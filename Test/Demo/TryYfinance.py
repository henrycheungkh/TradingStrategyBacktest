import yfinance as yf
import pandas as pd
# London-listed stock symbols must end with ".L"
ticker = "HSBA.L"    # HSBC Holdings
# Download last 60 days of daily data
data = yf.download(ticker, period="60d", interval="1d")
# Show the most recent few rows
print(data.tail())
# Access the last closing price
last_close = data["Close"].iloc[-1]
print(f"\nLast close price for {ticker}: £{last_close:.2f}")
