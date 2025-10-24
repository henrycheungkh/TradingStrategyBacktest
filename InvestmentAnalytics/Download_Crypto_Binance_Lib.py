# -*- coding: utf-8 -*-
"""
Created on Wed Oct 20 10:23:44 2021

@author: Henry Cheung
"""


import os
import pandas as pd
from datetime import date, datetime, timedelta

from binance.client import Client
from InvestmentAnalytics.DBUtil import AppendDBExportScript

api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')
client = Client(api_key, api_secret)

def UploadCryptoPriceToDB(ticker_list, interval_list, DatafilePath, DataTableName):
    for interval in interval_list:
        for ticker in ticker_list:
            df = getPriceSingleTickerDF(ticker, interval)
            filepath = DatafilePath+'Crypto_price_'+ticker+'_'+interval+'.csv'
            df.to_csv(filepath, index=False)
            AppendDBExportScript(DatafilePath, filepath , DataTableName)

def getPriceSingleTickerDF(ticker, interval):

    # valid intervals - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
    # interval = '1m'
    # get timestamp of earliest date data is available
    timestamp = client._get_earliest_valid_timestamp(ticker, interval)
    
    # timestamp = (datetime.now() - timedelta(days=100)).timestamp()
    print('timestamp is')
    print(timestamp)
    
    print('Download for ' + ticker + ' and ' + interval + ' started at ' + str(datetime.now()))
    
    
    # request historical candle (or klines) data
    bars = client.get_historical_klines(ticker, interval, timestamp, limit=1000)
    
    for line in bars:
        del line[6:]
    btc_df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close', 'vol'])
    btc_df['tDateTime'] = pd.to_datetime(btc_df['date'], unit='ms')
    btc_df['timeframe'] = interval
    btc_df['ticker'] = ticker
    btc_df.drop(['date'],axis='columns', inplace=True)
    btc_df = btc_df[['ticker', 'timeframe', 'tDateTime', 'high', 'low', 'open', 'close', 'vol']]
    # btc_df.set_index('date', inplace=True)
    # print(len(btc_df))
    # print(btc_df)
    return btc_df





# print(client.get_account())

# # get latest price from Binance API
# btc_price = client.get_symbol_ticker(symbol="BTCUSDT")
# # print full output (dictionary)
# print(btc_price)
