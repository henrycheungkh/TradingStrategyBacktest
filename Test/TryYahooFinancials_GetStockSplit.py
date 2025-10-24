# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 12:23:29 2023

@author: Henry Cheung
"""


import yfinance as yf

def get_stock_splits(ticker):
    # Fetch stock data
    stock = yf.Ticker(ticker)
    
    # Get stock splits
    splits = stock.splits

    return splits

ticker_symbol = "AAPL"  # for Apple Inc. as an example
splits_data = get_stock_splits(ticker_symbol)
print(splits_data)