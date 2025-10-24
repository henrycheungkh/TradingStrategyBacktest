# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 22:40:34 2023

@author: henry
"""

import pymysql
import pandas as pd
import InvestmentAnalytics.Config as Config
import os
import sys

from binance.client import Client

from datetime import date, datetime, timedelta

# from InvestmentAnalytics.Download_Crypto_Binance_Lib import *
from InvestmentAnalytics.DBUtil import DBExportDirectUpload, DBExportDirectUploadByBatch
from InvestmentAnalytics.DBUtil import AppendDBExportScript

def getPriceSingleTickerDF(client, ticker, interval):

    print('Download for ' + ticker + ' and ' + interval + ' started at ' + str(datetime.now()))
    # valid intervals - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
    # interval = '1m'
    # get timestamp of earliest date data is available
    timestamp = client._get_earliest_valid_timestamp(ticker, interval)
    print(timestamp)
    
    
    
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

def UploadCryptoPriceToDB(client, ticker_list, interval_list, DatafilePath, DataTableName):
    for interval in interval_list:
        for ticker in ticker_list:
            df = getPriceSingleTickerDF(client, ticker, interval)
            filepath = DatafilePath+'Crypto_price_'+ticker+'_'+interval+'.csv'
            df.to_csv(filepath, index=False)
            AppendDBExportScript(DatafilePath, filepath , DataTableName)

today = date.today()

try:
    DirectUpload = sys.argv[1]
except:    
    DirectUpload = "DirectUpload"

try:
    interval_list = sys.argv[2].split(",")
except:    
    interval_list = "1d".split(",")
print('interval_list is ' + str(interval_list))


try:
    ticker_list = sys.argv[3].split(",")
except:    
    ticker_list = "BTCUSDT,ETHUSDT".split(",")
print('ticker_list is ' + str(ticker_list))

# DatafilePath = Config.CONFIG_BASE_DatafilePath + today.strftime("%Y%m%d") + '_Crypto'
DatafilePath = r'E:\TAHistoricalData\Crypto'
print('DatafilePath is ' + DatafilePath)


if os.path.exists(DatafilePath):
    i = 1
    while os.path.exists(DatafilePath + " BK" + str(i)):
        i = i + 1
    os.rename(DatafilePath, DatafilePath + " BK" + str(i))
os.mkdir(DatafilePath)
DatafilePath = DatafilePath + "\\"

table_name = 'fdata_crypto_hist'

api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')
client = Client(api_key, api_secret)

UploadCryptoPriceToDB(client, ticker_list, interval_list, DatafilePath, table_name)

if (DirectUpload == "DirectUpload"):
    database_name = Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_CRYPTO_BINANCE

    # DBExportDirectUpload(DatafilePath + 'UploadScript.sql', table_name, DatabaseName = database_name)
    DBExportDirectUploadByBatch(DatafilePath, DatafilePath + 'UploadScript.sql', table_name, DatabaseName = database_name)
    sql = "SELECT DATE(tDateTime), count(close) FROM " + table_name + "  GROUP BY DATE(tDateTime) ORDER BY DATE(tDateTime) DESC LIMIT 15"
    # print(sql)
    # dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database_name)
    dbcon = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=database_name)
    UploadCountCheck = pd.read_sql_query(sql, dbcon)
    print(UploadCountCheck)


print('Download done')
