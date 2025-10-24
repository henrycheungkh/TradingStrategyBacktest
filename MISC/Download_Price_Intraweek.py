# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 11:24:27 2020

@author: Henry Cheung
"""
import pymysql
import pandas as pd
import yfinance as yf
import Config
import os

from datetime import date, datetime, timedelta

from InvestmentAnalytics.Download_Price_Lib import *

MarketList = {"FXCM" : [], "XLON" : ["ETF", "FTSE100", "FTSE250"], "XHKG": ["HSI"], "XUSA" : []}
MarketListForIntradayDownload = ["FXCM", "XUSA"]
TickerPerBatch = 3200
TickerPerBatchDayEnd = TickerPerBatch/2
# DatafilePath = "\\\\DESKTOP-TBL4G14\Shared\TAHistoricalData\\20201128\\"

today = date.today()
print(today)

DatafilePath = Config.CONFIG_BASE_DatafilePath + today.strftime("%Y%m%d")

DatafilePath = DatafilePath + " Intraweek"

if os.path.exists(DatafilePath):
    i = 1
    while os.path.exists(DatafilePath + " BK" + str(i)):
        i = i + 1
    os.rename(DatafilePath, DatafilePath + " BK" + str(i))
    
os.mkdir(DatafilePath )

DatafilePath = DatafilePath + "\\"

# DownloadInterval = {"1m": [(today - timedelta(days=7)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), 'EquityIntraDay_Yahoo_', '1min'],
#                     "30m": [(today - timedelta(days=30)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), 'EquityIntraDay30m_Yahoo_', '30min']}

# OneDayDownloadInterval = [(today - timedelta(days=3650)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), 'EquityDayEnd_Yahoo_', 'dayend']
OneDayDownloadInterval = [(today - timedelta(days=7)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), 'EquityDayEnd_Yahoo_', 'dayend']


dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)

for market in MarketList:
  print("Start downloading for market " + market)
  Tickers = pd.read_sql_query("select * from fdata_tickers where Market = '" + market + "'", dbcon)
  DownloadFinanceDataByBatch(Tickers, TickerPerBatchDayEnd, OneDayDownloadInterval[0], OneDayDownloadInterval[1], "1d", DatafilePath + OneDayDownloadInterval[2] + market, DatafilePath, OneDayDownloadInterval[3])

  # if market in MarketListForIntradayDownload:
  #   for download_interval in DownloadInterval:
  #       DownloadFinanceDataByBatch(Tickers, TickerPerBatch, DownloadInterval[download_interval][0], DownloadInterval[download_interval][1],download_interval, DatafilePath + DownloadInterval[download_interval][2] + market, DatafilePath, DownloadInterval[download_interval][3] )
      
  # for IndexConstituent in MarketList[market]:
  #   print("Start downloading for market " + market + " and Index " + IndexConstituent)
  #   Tickers = pd.read_sql_query("SELECT A.Ticker FROM (select * from fdata_tickers where Market = '" + market + "') as A INNER JOIN (SELECT Ticker FROM `fdata_tickers_property` WHERE Property_Type = 'Index' AND Property = '" + IndexConstituent + "' GROUP BY Ticker) as B ON A.Ticker = B.Ticker", dbcon)
  #   for download_interval in DownloadInterval:
  #       DownloadFinanceDataByBatch(Tickers, TickerPerBatch, DownloadInterval[download_interval][0], DownloadInterval[download_interval][1],download_interval, DatafilePath + DownloadInterval[download_interval][2] + market + '_' + IndexConstituent, DatafilePath, DownloadInterval[download_interval][3])

print('done')


