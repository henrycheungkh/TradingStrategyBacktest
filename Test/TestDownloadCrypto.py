# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 22:22:37 2023

@author: henry
"""

import os
import pandas as pd
from datetime import date, datetime, timedelta

pd.set_option('display.max_columns', None)

from binance.client import Client
from InvestmentAnalytics.DBUtil import AppendDBExportScript

api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')
client = Client(api_key, api_secret)


ticker = 'BTCUSDT'
interval = '1d'

timestamp = client._get_earliest_valid_timestamp(ticker, interval)
bars = client.get_historical_klines(ticker, interval, timestamp, limit=1000)
# print(bars)

for line in bars:
    del line[6:]
crypto_df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close', 'vol'])
crypto_df['tDateTime'] = pd.to_datetime(crypto_df['date'], unit='ms')
crypto_df['timeframe'] = interval
crypto_df['ticker'] = ticker
crypto_df.drop(['date'],axis='columns', inplace=True)
crypto_df = crypto_df[['ticker', 'timeframe', 'tDateTime', 'high', 'low', 'open', 'close', 'vol']]

print(crypto_df)
