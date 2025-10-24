# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 00:22:12 2021

@author: Henry Cheung
"""

import InvestmentAnalytics.Config as Config
from InvestmentAnalytics.DBUtil import DBExportDirectUpload
import os
import sys
import pymysql
import csv


# from datetime import datetime
from datetime import date, datetime, timedelta
from InvestmentAnalytics.IB.IBApiProcessHub import RunIBApiProcessHub
from InvestmentAnalytics.IB.IBApiProcess import *
import pandas as pd

pd.set_option('display.max_columns', None)
today = date.today()
DataEndDate = today.strftime("%Y%m%d")
# DataEndDate = "20210719"
print(DataEndDate)
BarSize = "30 mins"
# HistoricalPeriod = "2 M"
HistoricalPeriod = "2 D"
# HistoricalPeriod = "7 D"

dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
# dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)


# DatafilePath = Config.CONFIG_BASE_DatafilePath + 'IB_' + DataEndDate

# if os.path.exists(DatafilePath):
#     i = 1
#     while os.path.exists(DatafilePath + " BK" + str(i)):
#         i = i + 1
#     os.rename(DatafilePath, DatafilePath + " BK" + str(i))
# os.mkdir(DatafilePath)

# DatafilePath = DatafilePath + "\\"

market = "XUSA"
StockFilter = ""

if len(sys.argv) > 1:
    InitialScreeningMarketCapThreshold = int(sys.argv[1])
    PriorDateString = sys.argv[2]
    TickerPerBatch = int(sys.argv[3])
    StartingTickerBatchID = int(sys.argv[4])
else:
    PriorDateString = '2021-07-28'
    InitialScreeningMarketCapThreshold = 10000000
    TickerPerBatch = 2000
    # TickerPerBatch = 100
    StartingTickerBatchID = 0
    # StartingTickerBatchID = 21
print("TickerPerBatch = " + str(TickerPerBatch))

print('len(sys.argv) is ' +str(len(sys.argv)))

if len(sys.argv) > 5:
    Data_Items = sys.argv[5].split(",")
else:
    Data_Items = ['TRADES','BID','ASK']
    # Data_Items = ['BID']    
    # Data_Items = ['ASK']    

if len(sys.argv) > 6:
    HistoricalPeriod = sys.argv[6]

if len(sys.argv) > 7:
    DirectUpload = sys.argv[7]
else:
    DirectUpload = "No Upload"
    # DirectUpload = "DirectUpload"
    

# sql = "SELECT AAAAA.*, IFNULL(BBBBB.Property, 'NONE') AS primaryExchange FROM (SELECT AAAA.ticker as symbol, 'STK' as secType, 'USD' as currency, 'SMART' as exchange, AAAA.*, BBBB.Property As Industry FROM (SELECT AAA.*, BBB.Property AS Sector FROM (SELECT AA.ticker FROM (SELECT A.ticker FROM `fdata_price_dayend` A INNER JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime > '" + PriorDateString + "' " + StockFilter + "  GROUP BY A.ticker) AA INNER JOIN (SELECT ZB.Ticker, ZB.Value FROM (SELECT Ticker, Max(CaptureDate) AS MAX_CaptureDate FROM `fdata_yahoo_fundamental` WHERE Name = 'marketCap'  GROUP BY Ticker) ZA INNER JOIN (SELECT * FROM `fdata_yahoo_fundamental` WHERE Name = 'marketCap' and Value > " + str(InitialScreeningMarketCapThreshold) + ") ZB ON ZA.Ticker = ZB.Ticker and ZA.MAX_CaptureDate = ZB.CaptureDate) BB ON AA.ticker = BB.Ticker ) AAA LEFT JOIN (SELECT Ticker, Property FROM `fdata_yahoo_property` WHERE Property_Type = 'sector') BBB ON AAA.ticker = BBB.Ticker) AAAA LEFT JOIN (SELECT Ticker, Property FROM `fdata_yahoo_property` WHERE Property_Type = 'industry') BBBB ON AAAA.ticker = BBBB.Ticker) AAAAA LEFT JOIN (SELECT * FROM `fdata_tickers_property` WHERE Property_Type = 'primaryExchange') BBBBB ON AAAAA.symbol = BBBBB.Ticker"
# sql = "SELECT AAAAA.*, IFNULL(BBBBB.Property, 'NONE') AS primaryExchange FROM (SELECT AAAA.ticker as symbol, 'STK' as secType, 'USD' as currency, 'SMART' as exchange, AAAA.*, BBBB.Property As Industry FROM (SELECT AAA.*, BBB.Property AS Sector FROM (SELECT AA.ticker FROM (SELECT A.ticker FROM `fdata_price_dayend` A INNER JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime > '" + PriorDateString + "' " + StockFilter + " GROUP BY A.ticker UNION select ticker from `fdata_tickers_ipo`) AA INNER JOIN (SELECT ZB.Ticker, ZB.Value FROM (SELECT Ticker, Max(CaptureDate) AS MAX_CaptureDate FROM `fdata_yahoo_fundamental` WHERE Name = 'marketCap'  GROUP BY Ticker) ZA INNER JOIN (SELECT * FROM `fdata_yahoo_fundamental` WHERE Name = 'marketCap' and Value > " + str(InitialScreeningMarketCapThreshold) + ") ZB ON ZA.Ticker = ZB.Ticker and ZA.MAX_CaptureDate = ZB.CaptureDate) BB ON AA.ticker = BB.Ticker ) AAA LEFT JOIN (SELECT Ticker, Property FROM `fdata_yahoo_property` WHERE Property_Type = 'sector') BBB ON AAA.ticker = BBB.Ticker) AAAA LEFT JOIN (SELECT Ticker, Property FROM `fdata_yahoo_property` WHERE Property_Type = 'industry') BBBB ON AAAA.ticker = BBBB.Ticker) AAAAA LEFT JOIN (SELECT * FROM `fdata_tickers_property` WHERE Property_Type = 'primaryExchange') BBBBB ON AAAAA.symbol = BBBBB.Ticker"
sql = "SELECT A.ticker FROM `fdata_price_dayend` A INNER JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime > '" + PriorDateString + "' " + StockFilter + " GROUP BY A.ticker UNION select ticker from `fdata_tickers_ipo`"
sql = "SELECT AA.ticker FROM (SELECT A.ticker FROM `fdata_price_dayend` A INNER JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime > '" + PriorDateString + "' " + StockFilter + " GROUP BY A.ticker UNION select ticker from `fdata_tickers_ipo`) AA LEFT JOIN (SELECT * FROM `fdata_tickers_property` WHERE Property_Type = 'Yahoo_legalType') BB ON AA.ticker = BB.Ticker WHERE BB.Property IS NULL or BB.Property <> 'Exchange Traded Fund'"
sql = "SELECT AAA.ticker, BBB.Property AS Sector FROM (SELECT AA.ticker FROM (SELECT A.ticker FROM `fdata_price_dayend` A INNER JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime > '" + PriorDateString + "' " + StockFilter + " GROUP BY A.ticker UNION select ticker from `fdata_tickers_ipo`) AA LEFT JOIN (SELECT * FROM `fdata_tickers_property` WHERE Property_Type = 'Yahoo_legalType') BB ON AA.ticker = BB.Ticker WHERE BB.Property IS NULL or BB.Property <> 'Exchange Traded Fund' ) AAA LEFT JOIN (SELECT Ticker, Property FROM `fdata_yahoo_property` WHERE Property_Type = 'sector') BBB ON AAA.ticker = BBB.Ticker"
sql = "SELECT AAAA.ticker as symbol, 'STK' as secType, 'USD' as currency, 'SMART' as exchange, AAAA.*, BBBB.Property As Industry FROM (SELECT AAA.ticker, BBB.Property AS Sector FROM (SELECT AA.ticker FROM (SELECT A.ticker FROM `fdata_price_dayend` A INNER JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime > '" + PriorDateString + "' " + StockFilter + " GROUP BY A.ticker UNION select ticker from `fdata_tickers_ipo`) AA LEFT JOIN (SELECT * FROM `fdata_tickers_property` WHERE Property_Type = 'Yahoo_legalType') BB ON AA.ticker = BB.Ticker WHERE BB.Property IS NULL or BB.Property <> 'Exchange Traded Fund' ) AAA LEFT JOIN (SELECT Ticker, Property FROM `fdata_yahoo_property` WHERE Property_Type = 'sector') BBB ON AAA.ticker = BBB.Ticker) AAAA LEFT JOIN (SELECT Ticker, Property FROM `fdata_yahoo_property` WHERE Property_Type = 'industry') BBBB ON AAAA.ticker = BBBB.Ticker"
sql = "SELECT AAAAA.*, IFNULL(BBBBB.Property, 'NONE') AS primaryExchange FROM (SELECT AAAA.ticker as symbol, 'STK' as secType, 'USD' as currency, 'SMART' as exchange, AAAA.*, BBBB.Property As Industry FROM (SELECT AAA.ticker, BBB.Property AS Sector FROM (SELECT AA.ticker FROM (SELECT A.ticker FROM `fdata_price_dayend` A INNER JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime > '" + PriorDateString + "' " + StockFilter + " GROUP BY A.ticker UNION select ticker from `fdata_tickers_ipo`) AA LEFT JOIN (SELECT * FROM `fdata_tickers_property` WHERE Property_Type = 'Yahoo_legalType') BB ON AA.ticker = BB.Ticker WHERE BB.Property IS NULL or BB.Property <> 'Exchange Traded Fund' ) AAA LEFT JOIN (SELECT Ticker, Property FROM `fdata_yahoo_property` WHERE Property_Type = 'sector') BBB ON AAA.ticker = BBB.Ticker) AAAA LEFT JOIN (SELECT Ticker, Property FROM `fdata_yahoo_property` WHERE Property_Type = 'industry') BBBB ON AAAA.ticker = BBBB.Ticker) AAAAA LEFT JOIN (SELECT * FROM `fdata_tickers_property` WHERE Property_Type = 'primaryExchange') BBBBB ON AAAAA.symbol = BBBBB.Ticker"

# sql = "SELECT * FROM fdata_fut_hist"

print(sql)
Tickers = pd.read_sql_query(sql, dbcon)
Tickers['location'] = Tickers.index

print(Tickers)

Hood = Tickers[Tickers['ticker'] == 'HOOD']

print(Hood)





