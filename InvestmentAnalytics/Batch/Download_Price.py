# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 11:24:27 2020

@author: Henry Cheung
"""
# import pymysql
import pandas as pd
import numpy as np
import yfinance as yf
import InvestmentAnalytics.Config as Config
import InvestmentAnalytics.DBUtil as DBUtil
import os
import sys
import time

from datetime import date, datetime, timedelta

from InvestmentAnalytics.Download_Price_Lib import *
from InvestmentAnalytics.DBUtil import DBExportDirectUpload, DBExportDirectUploadByBatch


def CheckMonthLastDate(date_to_check):
    next_week_date = date_to_check + timedelta(days=7)
    return date_to_check.month != next_week_date.month

# MarketList = {"FXCM" : [], "XLON" : ["ETF", "FTSE100", "FTSE250"], "XHKG": ["HSI"], "XUSA" : []}
MarketList = {"FXCM" : [], "XLON" : [], "XHKG": ["HSI"], "XUSA" : [], "Crypto" : []}
# MarketList = {"FXCM" : [], "XLON" : [], "XHKG": ["HSI"], "Crypto" : []}
# MarketList = {"XLON" : [], "XHKG": ["HSI"], "XUSA" : [], "Crypto" : []}
# MarketList = {"XLON" : []}
# MarketList = {"XUSA" : []}

# MarketListForIntradayDownload = ["XLON"]
# MarketListForIntradayDownload = ["FXCM", "XUSA"]
# MarketListForIntradayDownload = ["XUSA"]
MarketListForIntradayDownload = ["FXCM", "XUSA", "XLON", "Crypto"]
# MarketListForIntradayDownload = ["XUSA", "XLON", "Crypto"]

today = date.today()
# today = today - timedelta(days=6)
print(today)


# PriorDateString = '2021-11-02'
PriorDateString = (today - timedelta(days=15)).strftime("%Y-%m-%d")

if sys.argv[1] == "USOnly":
    MarketList = {"XUSA" : []}
    MarketListForIntradayDownload = ["XUSA"]
elif sys.argv[1] == "FXOnly":
    MarketList = {"FXCM" : []}
    MarketListForIntradayDownload = ["FXCM", "XLON", "Crypto"]
elif sys.argv[1] == "ExcludeUS":
    MarketList = {"XLON" : [], "XHKG": ["HSI"], "Crypto" : []}
    # MarketList = {"XLON" : []}
    MarketList = {"XHKG": ["HSI"]}
    MarketListForIntradayDownload = ["FXCM", "XLON", "XHKG", "Crypto"]
elif sys.argv[1] == "HKOnly":
    MarketList = {"XHKG": ["HSI"]}
    MarketListForIntradayDownload = ["FXCM", "XLON", "XHKG", "Crypto"]
elif sys.argv[1] == "UKOnly":
    MarketList = {"XLON" : []}
    MarketListForIntradayDownload = ["FXCM", "XLON", "XHKG", "Crypto"]

if len(sys.argv) > 2:
    TickerPerBatch = int(sys.argv[2])
else:
    TickerPerBatch = 800
print("TickerPerBatch = " + str(TickerPerBatch))
TickerPerBatchDayEnd = TickerPerBatch/2
# DatafilePath = "\\\\DESKTOP-TBL4G14\Shared\TAHistoricalData\\20201128\\"




DownloadInterval = {"1m": [(today - timedelta(days=6)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), 'EquityIntraDay_Yahoo_', '1min'],
                    "30m": [(today - timedelta(days=15)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), 'EquityIntraDay30m_Yahoo_', '30min'],
                    "5m": [(today - timedelta(days=15)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), 'EquityIntraDay5m_Yahoo_', '5min'],
                    "2m": [(today - timedelta(days=15)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), 'EquityIntraDay2m_Yahoo_', '2min']}

# OneDayDownloadInterval = [(today - timedelta(days=365)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), 'EquityDayEnd_Yahoo_', 'dayend']
OneDayDownloadInterval = [(today - timedelta(days=15)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), 'EquityDayEnd_Yahoo_', 'dayend']

DatafilePathSuffix = ""

Timeframe = "1min"

if len(sys.argv) > 3:
    if sys.argv[3] == "dayend":
        Timeframe = "dayend"
        if len(sys.argv) > 4:
            DatafilePathSuffix = "_dayend"
            # if not CheckMonthLastDate(today):
            #     print("No Day End price downloaded as it is not last weekend of a month")
            #     sys.exit()
            if today.month % int(sys.argv[4]) != 0:
                OneDayDownloadInterval = [(today - timedelta(days=15)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), 'EquityDayEnd_Yahoo_', 'dayend']
                DatafilePathSuffix = "_dayend_intermediate"
        DownloadInterval = {}
    if sys.argv[3] == "1min":
        Timeframe = "1min"
        DatafilePathSuffix = "_1min"
        DownloadInterval = {"1m": [(today - timedelta(days=6)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), 'EquityIntraDay_Yahoo_', '1min']}
        OneDayDownloadInterval = []
    if sys.argv[3] == "5min":
        Timeframe = "5min"
        DatafilePathSuffix = "_5min"
        DownloadInterval = {"5m": [(today - timedelta(days=15)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), 'EquityIntraDay_Yahoo_', '5min']}
        OneDayDownloadInterval = []
    if sys.argv[3] == "2min":
        Timeframe = "2min"
        DatafilePathSuffix = "_2min"
        DownloadInterval = {"2m": [(today - timedelta(days=15)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), 'EquityIntraDay_Yahoo_', '2min']}
        OneDayDownloadInterval = []
    if sys.argv[3] == "30min":
        Timeframe = "30min"
        if len(sys.argv) > 4:
            if sys.argv[4] == "biweekly":
                if (today.day > 7) and (today.day < 21):
                    sys.exit()
        DatafilePathSuffix = "_30min"
        DownloadInterval = {"30m": [(today - timedelta(days=15)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), 'EquityIntraDay30m_Yahoo_', '30min']}
        OneDayDownloadInterval = []

if len(sys.argv) > 5:
    DirectUpload = sys.argv[5]
else:
    DirectUpload = "No Upload"

DatafilePath = Config.CONFIG_BASE_DatafilePath + today.strftime("%Y%m%d") + DatafilePathSuffix



if sys.argv[1] == "USOnly":
    DatafilePath = DatafilePath + "USOnly"
elif sys.argv[1] == "FXOnly":
    DatafilePath = DatafilePath + "FXOnly"
elif sys.argv[1] == "ExcludeUS":
    DatafilePath = DatafilePath + "ExcludeUS"
elif sys.argv[1] == "HKOnly":
    DatafilePath = DatafilePath + "HKOnly"
elif sys.argv[1] == "UKOnly":
    DatafilePath = DatafilePath + "UKOnly"

if os.path.exists(DatafilePath):
    i = 1
    while os.path.exists(DatafilePath + " BK" + str(i)):
        i = i + 1
    os.rename(DatafilePath, DatafilePath + " BK" + str(i))
os.mkdir(DatafilePath)


DatafilePath = DatafilePath + "\\"
    


# dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
# dbcon = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
# dbcon_all = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD)

dbconnect = DBUtil.DBGetDBInstance(Config.CONFIG_MYSQL_CONNECTION_DATABASE)
dbconnect_all = DBUtil.DBGetDBInstance()

# DownloadMode = 'Random'
DownloadMode = 'OldTickers'

# StartDateOfLackingDataText = '2025-03-14'
# StartDateOfRecentFullDataText = '2025-03-10'

StartDateOfLackingDataText = (today - timedelta(days=8)).strftime("%Y-%m-%d")
StartDateOfRecentFullDataText = (today - timedelta(days=30)).strftime("%Y-%m-%d")



for market in MarketList:
    print("Start downloading for market " + market)
    # Tickers = pd.read_sql_query("select * from fdata_tickers where Market = '" + market + "'", dbcon)
    if market == 'XUSA':
        # Tickers = pd.read_sql_query("SELECT AAAAA.ticker as Ticker FROM (SELECT AAAA.ticker as symbol, 'STK' as secType, 'USD' as currency, 'SMART' as exchange, AAAA.*, BBBB.Property As Industry FROM (SELECT AAA.ticker, BBB.Property AS Sector FROM (SELECT AA.ticker FROM (SELECT A.ticker FROM finance_fdata_price_dayend.`fdata_price_dayend` A INNER JOIN finance_fdata_master.`fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = 'XUSA' AND A.Datetime > '2021-09-02' GROUP BY A.ticker UNION select ticker from finance_fdata_master.`fdata_tickers_ipo`) AA LEFT JOIN (SELECT * FROM finance_fdata_master.`fdata_tickers_property` WHERE Property_Type = 'Yahoo_legalType') BB ON AA.ticker = BB.Ticker WHERE BB.Property IS NULL or BB.Property <> 'Exchange Traded Fund' ) AAA LEFT JOIN (SELECT Ticker, Property FROM finance_fdata_master.`fdata_yahoo_property` WHERE Property_Type = 'sector') BBB ON AAA.ticker = BBB.Ticker) AAAA LEFT JOIN (SELECT Ticker, Property FROM finance_fdata_master.`fdata_yahoo_property` WHERE Property_Type = 'industry') BBBB ON AAAA.ticker = BBBB.Ticker) AAAAA LEFT JOIN (SELECT * FROM finance_fdata_master.`fdata_tickers_property` WHERE Property_Type = 'primaryExchange') BBBBB ON AAAAA.symbol = BBBBB.Ticker", dbcon_all)
        # Tickers = pd.read_sql_query("SELECT AAAAA.ticker as Ticker FROM (SELECT AAAA.ticker as symbol, 'STK' as secType, 'USD' as currency, 'SMART' as exchange, AAAA.*, BBBB.Property As Industry FROM (SELECT AAA.ticker, BBB.Property AS Sector FROM (SELECT AA.ticker FROM (SELECT A.ticker FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_DAYEND + ".`fdata_price_dayend` A INNER JOIN " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = 'XUSA' AND A.Datetime > '" + PriorDateString + "' GROUP BY A.ticker UNION select ticker from " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_ipo`) AA LEFT JOIN (SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_property` WHERE Property_Type = 'Yahoo_legalType') BB ON AA.ticker = BB.Ticker WHERE BB.Property IS NULL or BB.Property <> 'Exchange Traded Fund' ) AAA LEFT JOIN (SELECT Ticker, Property FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_yahoo_property` WHERE Property_Type = 'sector') BBB ON AAA.ticker = BBB.Ticker) AAAA LEFT JOIN (SELECT Ticker, Property FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_yahoo_property` WHERE Property_Type = 'industry') BBBB ON AAAA.ticker = BBBB.Ticker) AAAAA LEFT JOIN (SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_property` WHERE Property_Type = 'primaryExchange') BBBBB ON AAAAA.symbol = BBBBB.Ticker", dbcon_all)
        # sql = "SELECT AAAAA.ticker as Ticker FROM (SELECT AAAA.ticker as symbol, 'STK' as secType, 'USD' as currency, 'SMART' as exchange, AAAA.*, BBBB.Property As Industry FROM (SELECT AAA.ticker, BBB.Property AS Sector FROM (SELECT AA.ticker FROM (SELECT A.ticker FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_DAYEND + ".`fdata_price_dayend` A INNER JOIN " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = 'XUSA' AND A.Datetime > '" + PriorDateString + "' GROUP BY A.ticker UNION select ticker from " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_ipo`) AA LEFT JOIN (SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_property` WHERE Property_Type = 'Yahoo_legalType') BB ON AA.ticker = BB.Ticker WHERE BB.Property IS NULL or BB.Property <> 'Exchange Traded Fund' ) AAA LEFT JOIN (SELECT Ticker, Property FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_yahoo_property` WHERE Property_Type = 'sector') BBB ON AAA.ticker = BBB.Ticker) AAAA LEFT JOIN (SELECT Ticker, Property FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_yahoo_property` WHERE Property_Type = 'industry') BBBB ON AAAA.ticker = BBBB.Ticker) AAAAA LEFT JOIN (SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_property` WHERE Property_Type = 'primaryExchange') BBBBB ON AAAAA.symbol = BBBBB.Ticker"
        sql = "SELECT AAAAA.ticker as Ticker FROM (SELECT AAAA.ticker as symbol, 'STK' as secType, 'USD' as currency, 'SMART' as exchange, AAAA.*, BBBB.Property As Industry FROM (SELECT AAA.ticker, BBB.Property AS Sector FROM (SELECT AA.ticker FROM (SELECT A.ticker FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_DAYEND + ".`fdata_price_dayend` A INNER JOIN " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = 'XUSA' AND A.Datetime > '" + PriorDateString + "' GROUP BY A.ticker UNION select ticker from " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_ipo`) AA LEFT JOIN (SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_property` WHERE Property_Type = 'Yahoo_legalType') BB ON AA.ticker = BB.Ticker  ) AAA LEFT JOIN (SELECT Ticker, Property FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_yahoo_property` WHERE Property_Type = 'sector') BBB ON AAA.ticker = BBB.Ticker) AAAA LEFT JOIN (SELECT Ticker, Property FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_yahoo_property` WHERE Property_Type = 'industry') BBBB ON AAAA.ticker = BBBB.Ticker) AAAAA LEFT JOIN (SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_property` WHERE Property_Type = 'primaryExchange') BBBBB ON AAAAA.symbol = BBBBB.Ticker"

        # sql = "SELECT AAAAA.ticker as Ticker FROM (SELECT AAAA.ticker as symbol, 'STK' as secType, 'USD' as currency, 'SMART' as exchange, AAAA.*, BBBB.Property As Industry FROM (SELECT AAA.ticker, BBB.Property AS Sector FROM (SELECT AA.ticker FROM (SELECT Ticker as ticker FROM "  + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers` WHERE Market = 'XUSA' UNION select ticker from " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_ipo`) AA LEFT JOIN (SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_property` WHERE Property_Type = 'Yahoo_legalType') BB ON AA.ticker = BB.Ticker WHERE BB.Property IS NULL or BB.Property <> 'Exchange Traded Fund' ) AAA LEFT JOIN (SELECT Ticker, Property FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_yahoo_property` WHERE Property_Type = 'sector') BBB ON AAA.ticker = BBB.Ticker) AAAA LEFT JOIN (SELECT Ticker, Property FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_yahoo_property` WHERE Property_Type = 'industry') BBBB ON AAAA.ticker = BBBB.Ticker) AAAAA LEFT JOIN (SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_property` WHERE Property_Type = 'primaryExchange') BBBBB ON AAAAA.symbol = BBBBB.Ticker"

    else:
        # Tickers = pd.read_sql_query("select * from fdata_tickers where Market = '" + market + "'", dbcon)
        sql = "select * from fdata_tickers where Market = '" + market + "'"
        # sql = "select * from fdata_tickers where Market = '" + market + "' and  Ticker IN ('0002.HK', '0003.HK')"
        
        if Timeframe == "dayend":

            if DownloadMode == 'OldTickers':
                sql = "SELECT A.Ticker, A.Market, B.C FROM (SELECT * FROM fdata_tickers WHERE Market = '" + market + "') A INNER JOIN (SELECT ticker, COUNT(ticker) AS C FROM finance_fdata_price_dayend.fdata_price_dayend WHERE Datetime > '" + StartDateOfRecentFullDataText +"' GROUP BY ticker) B on A.Ticker = B.ticker ORDER BY B.C ASC"
            else:
                sql = "SELECT A.Ticker, A.Market, B.C FROM (SELECT * FROM fdata_tickers WHERE Market = '" + market + "') A LEFT JOIN (SELECT ticker, COUNT(ticker) AS C FROM finance_fdata_price_dayend.fdata_price_dayend WHERE Datetime > '" + StartDateOfRecentFullDataText +"' GROUP BY ticker) B on A.Ticker = B.ticker ORDER BY B.C ASC"

        elif Timeframe == "30min":
            # sql = "SELECT A.Ticker, A.Market, B.C FROM (SELECT * FROM fdata_tickers WHERE Market = '" + market + "') A LEFT JOIN (SELECT ticker, COUNT(ticker) AS C FROM finance_fdata_price_30min.fdata_price_30min WHERE Datetime > '2025-02-13' GROUP BY ticker) B on A.Ticker = B.ticker ORDER BY B.C ASC"
            # sql = "SELECT A.Ticker, A.Market, B.C FROM (SELECT * FROM fdata_tickers WHERE Market = '" + market + "') A LEFT JOIN (SELECT ticker, COUNT(ticker) AS C FROM finance_fdata_price_30min.fdata_price_30min WHERE Datetime > '2025-02-13' GROUP BY ticker) B on A.Ticker = B.ticker WHERE B.C IS NOT NULL ORDER BY B.C ASC"

            sql = "SELECT AA.Ticker, AA.Market, AA.C, BB.C AS CountOfDayEndPrice FROM (SELECT A.Ticker, A.Market, B.C FROM (SELECT * FROM fdata_tickers WHERE Market = '" + market + "') A LEFT JOIN (SELECT ticker, COUNT(ticker) AS C FROM finance_fdata_price_30min.fdata_price_30min WHERE Datetime > '" + StartDateOfRecentFullDataText +"' GROUP BY ticker) B on A.Ticker = B.ticker) AA INNER JOIN (SELECT ticker,  COUNT(ticker) as C FROM finance_fdata_price_dayend.fdata_price_dayend WHERE Datetime > '" + StartDateOfRecentFullDataText +"' GROUP BY ticker) BB ON AA.Ticker = BB.ticker ORDER BY AA.C ASC"

            # sql = "SELECT A.Ticker FROM (SELECT DISTINCT BB.Ticker FROM (SELECT DISTINCT ticker FROM finance_fdata_price_30min.fdata_price_30min WHERE DATE(Datetime) = '2025-03-07') AA INNER JOIN (SELECT * FROM fdata_tickers WHERE Market = '" + market + "') BB ON AA.ticker = BB.Ticker) A LEFT JOIN (SELECT DISTINCT ticker AS Now_ticker FROM finance_fdata_price_30min.fdata_price_30min WHERE DATE(Datetime) = '2025-03-07') B ON A.ticker = B.Now_ticker WHERE B.Now_ticker IS NULL"

        elif Timeframe == "1min":
            # sql = "SELECT A.Ticker, A.Market, B.C FROM (SELECT * FROM fdata_tickers WHERE Market = '" + market + "') A LEFT JOIN (SELECT ticker, COUNT(ticker) AS C FROM finance_fdata_price_1min.fdata_price_1min WHERE Datetime > '2025-02-13' GROUP BY ticker) B on A.Ticker = B.ticker ORDER BY B.C ASC"
            sql = "SELECT AA.Ticker, AA.Market, AA.C FROM (SELECT A.Ticker, A.Market, B.C FROM (SELECT * FROM fdata_tickers WHERE Market = '" + market + "') A LEFT JOIN (SELECT ticker, COUNT(ticker) AS C FROM finance_fdata_price_1min.fdata_price_1min WHERE Datetime > '2025-02-13' GROUP BY ticker) B on A.Ticker = B.ticker) AA INNER JOIN (SELECT ticker FROM finance_fdata_price_dayend.fdata_price_dayend WHERE Datetime > '2025-02-13' GROUP BY ticker) BB ON AA.Ticker = BB.ticker ORDER BY AA.C ASC"

    print(sql)
    # Tickers = pd.read_sql_query(sql, dbcon)
    Tickers = pd.read_sql(sql,con=DBUtil.GetSQLAlchemyEngine(DatabaseName=Config.CONFIG_MYSQL_CONNECTION_DATABASE)).fillna(0)
    
    if market != 'XUSA':
        Tickers['randNumCol'] = np.random.randint(1, 100, Tickers.shape[0])
        if DownloadMode == 'Random':
           Tickers.sort_values(by='randNumCol',  inplace=True)
        elif DownloadMode == 'NewTickers':
            Tickers.sort_values(by=['C', 'randNumCol'],  inplace=True, ascending=False)
        elif DownloadMode == 'OldTickers':
            Tickers.sort_values(by=['C', 'randNumCol'],  inplace=True, ascending=True)
    else:
        Tickers['randNumCol'] = np.random.randint(1, 100, Tickers.shape[0])
        Tickers.sort_values(by='randNumCol',  inplace=True)
    
    
    if market == "XHKG":
        Tickers['trimmed ticker'] = Tickers['Ticker'].str.replace('.HK', '')
        Tickers['ticker is numeric'] = Tickers['trimmed ticker'].str.isnumeric()
        Tickers = Tickers[Tickers['ticker is numeric'] == True].copy()
    print(Tickers)

    # Tickers = Tickers.sample(frac=1).reset_index(drop=True)
    # print('Tickers with prices after shuffle is')
    # print(Tickers)

    # ThreeDaysString = (today - timedelta(days=3)).strftime("%Y-%m-%d")
    ThreeDaysString = (today - timedelta(days=10)).strftime("%Y-%m-%d")
    TableName = {"1min":"fdata_price_1min", "2min":"fdata_price_2min", "5min":"fdata_price_5min", "30min":"fdata_price_30min", "dayend":"fdata_price_dayend"}
    DatabaseName = {"1min":Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_1MIN , "30min":Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_30MIN, "dayend":Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_DAYEND}
    sql = "SELECT ticker as Ticker, count(Close) as ShortTermCloseCount FROM " + DatabaseName[Timeframe] + "." + TableName[Timeframe] + " WHERE DateTime  > '" + ThreeDaysString + "'   GROUP BY ticker ORDER BY count(Close)"
    # TickerCloseCount = pd.read_sql_query(sql, dbcon)
    TickerCloseCount = pd.read_sql(sql,con=DBUtil.GetSQLAlchemyEngine(DatabaseName=Config.CONFIG_MYSQL_CONNECTION_DATABASE))
    
    # Tickers = Tickers.merge(TickerCloseCount, on='Ticker', how='left').fillna(0).sort_values(by='ShortTermCloseCount', ascending=True).reset_index(drop=True)[['Ticker']]
    Tickers = Tickers.merge(TickerCloseCount, on='Ticker', how='left').fillna(0)

    LongTermDaysString = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    sql = "SELECT ticker as Ticker, count(Close) as LongTermCloseCount FROM " + DatabaseName[Timeframe] + "." + TableName[Timeframe] + " WHERE DateTime  > '" + LongTermDaysString + "'   GROUP BY ticker ORDER BY count(Close)"
    # TickerCloseCount = pd.read_sql_query(sql, dbcon)
    TickerCloseCount = pd.read_sql(sql,con=DBUtil.GetSQLAlchemyEngine(DatabaseName=Config.CONFIG_MYSQL_CONNECTION_DATABASE))

    Tickers = Tickers.merge(TickerCloseCount, on='Ticker', how='left').fillna(0)
    Tickers.loc[(Tickers['LongTermCloseCount'] == 0) & (Tickers['ShortTermCloseCount'] == 0), 'ShortTermCloseCount'] == 1000
    Tickers = Tickers.sort_values(by='ShortTermCloseCount', ascending=True).reset_index(drop=True)[['Ticker']]

    print('Tickers sorted by close count is')
    print(Tickers)


    if len(OneDayDownloadInterval) > 0:
       DownloadFinanceDataByBatch(Tickers, TickerPerBatchDayEnd, OneDayDownloadInterval[0], OneDayDownloadInterval[1], "1d", DatafilePath + OneDayDownloadInterval[2] + market, DatafilePath, OneDayDownloadInterval[3])

    if market in MarketListForIntradayDownload:
      if len(DownloadInterval) > 0:
        for download_interval in DownloadInterval:
            DownloadFinanceDataByBatch(Tickers, TickerPerBatch, DownloadInterval[download_interval][0], DownloadInterval[download_interval][1],download_interval, DatafilePath + DownloadInterval[download_interval][2] + market, DatafilePath, DownloadInterval[download_interval][3] )
      
    for IndexConstituent in MarketList[market]:
        print("Start downloading for market " + market + " and Index " + IndexConstituent)
        # Tickers = pd.read_sql_query("SELECT A.Ticker FROM (select * from fdata_tickers where Market = '" + market + "') as A INNER JOIN (SELECT Ticker FROM `fdata_tickers_property` WHERE Property_Type = 'Index' AND Property = '" + IndexConstituent + "' GROUP BY Ticker) as B ON A.Ticker = B.Ticker", dbcon)
        sql = "SELECT A.Ticker FROM (select * from fdata_tickers where Market = '" + market + "') as A INNER JOIN (SELECT Ticker FROM `fdata_tickers_property` WHERE Property_Type = 'Index' AND Property = '" + IndexConstituent + "' GROUP BY Ticker) as B ON A.Ticker = B.Ticker"
        Tickers = pd.read_sql(sql,con=DBUtil.GetSQLAlchemyEngine(DatabaseName=Config.CONFIG_MYSQL_CONNECTION_DATABASE))
        
        for download_interval in DownloadInterval:
            DownloadFinanceDataByBatch(Tickers, TickerPerBatch, DownloadInterval[download_interval][0], DownloadInterval[download_interval][1],download_interval, DatafilePath + DownloadInterval[download_interval][2] + market + '_' + IndexConstituent, DatafilePath, DownloadInterval[download_interval][3])

f = open(DatafilePath + "download_finish.txt", "a")
f.write("Download Finished")
f.close()

# TableName = {"1min":"fdata_price_1min", "30min":"fdata_price_30min", "dayend":"fdata_price_dayend", }
TableName = {"1min":"fdata_price_1min", "2min":"fdata_price_2min", "5min":"fdata_price_5min", "30min":"fdata_price_30min", "dayend":"fdata_price_dayend"}
DatabaseName = {"1min":Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_1MIN , "30min":Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_30MIN, "dayend":Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_DAYEND}
FXDatabaseName = {"1min":Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_1MIN_FX , "2min":Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_2MIN_FX, "5min":Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_5MIN_FX, "dayend":Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_DAYEND}

if (DirectUpload == "DirectUpload"):
    table_name = TableName[Timeframe]
    if (sys.argv[1] == "FXOnly"):
        database_name = FXDatabaseName[Timeframe]
    else:
        database_name = DatabaseName[Timeframe]
    
        
    # if (sys.argv[1] == "FXOnly") and (Timeframe == "1min"):
    #     database_name = Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_1MIN_FX
    # if (sys.argv[1] == "FXOnly") and (Timeframe == "2min"):
    #     database_name = Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_2MIN_FX
    # if (sys.argv[1] == "FXOnly") and (Timeframe == "5min"):
    #     database_name = Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_5MIN_FX
    # else:
    #     database_name = DatabaseName[Timeframe]


    # DBExportDirectUpload(DatafilePath + 'UploadScript.sql', table_name, DatabaseName = database_name)
    print('Going to call DBExportDirectUploadByBatch')
    DBExportDirectUploadByBatch(DatafilePath, DatafilePath + 'UploadScript.sql', table_name, DatabaseName = database_name)
    sql = "SELECT DATE(DateTime), count(Close) FROM " + table_name + "  GROUP BY DATE(DateTime) ORDER BY DATE(DateTime) DESC LIMIT 15"
    # print(sql)
    # dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database_name)
    # dbcon = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=database_name)
    # UploadCountCheck = pd.read_sql_query(sql, dbcon)
    UploadCountCheck = pd.read_sql(sql,con=DBUtil.GetSQLAlchemyEngine(DatabaseName=database_name))
    print(UploadCountCheck)


print('done')



