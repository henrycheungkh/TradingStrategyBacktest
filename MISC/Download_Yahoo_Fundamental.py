# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 13:50:31 2021

@author: Henry Cheung
"""
import InvestmentAnalytics.Config as Config
import os
import sys
import pymysql
import mysql.connector
import pandas as pd

import yfinance as yf
from bs4 import BeautifulSoup
import requests
import logging
import threading
import time
from datetime import datetime, date
from InvestmentAnalytics.Download_Yahoo import *

UnitDict = {'T':1000000000000, 'B':1000000000, 'M': 1000000}

mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
# dt_obj = datetime.strptime(h, '%d/%m/%Y')
today_date = date.today()

def DownloadYahooFundamentalForTickersThread(name, Tickers, Yahoo_Tag, DBTableName, DBCaptureDate):
    logging.info("Thread %s: starting", name)
    DownloadYahooFundamentalForTickers(name, Tickers, Yahoo_Tag, DBTableName, DBCaptureDate)
    logging.info("Thread %s: finishing", name)

def DownloadYahooFundamentalForTickers(name, tickers, Yahoo_Tag, DBTableName, DBCaptureDate):
    global mydb
    # for index, row in tickers.iterrows():
    TickerCount = 0
    for ticker in tickers:
        try:
            DownloadYahooFundamental(mydb, ticker, Yahoo_Tag, DBTableName, DBCaptureDate)
            TickerCount = TickerCount + 1
            if TickerCount % 50 == 0:
                print("Thread " + str(name) + " --- " + str(TickerCount) + " Tickers tried to download at " + str(datetime.now()))
            # t = yf.Ticker(ticker)
            # try:
            #     if t.info['marketCap'] is not None:
            #         sql = "INSERT INTO fdata_yahoo_fundamental (Ticker, CaptureDate, Name, Value) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE Value=%s"
            #         val = (ticker, today_date, 'marketCap', t.info['marketCap'], t.info['marketCap'])
            #         mycursor = mydb.cursor()
            #         mycursor.execute(sql, val)
            #         mydb.commit()
            #         print('In thread ' + str(name) + ': uploaded ' + ticker + ' at ' + str(datetime.now()))
            # except Exception:
            #     pass    
        except Exception:
            pass    

Yahoo_Tag_Name = sys.argv[1]
# TickerCountPerThread = 1000
TickerCountPerThread = int(sys.argv[2])


# MarketList = {"XUSA" : [], "XLON" : [], "XHKG": []}
# MarketList = { "XLON" : []}
MarketList = { "XUSA" : []}
# MarketList = { "XHKG" : []}
PriorDateString = '2021-10-20'
MarketCapPriorDateString = '2021-10-20'

dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)

# Yahoo_Tag_Name = 'marketCap'
DBTableName = 'fdata_yahoo_fundamental'

for market in MarketList:
    print("Start downloading for market " + market)
    # Tickers = pd.read_sql_query("SELECT ticker from (SELECT A.* FROM `fdata_price_dayend` A LEFT JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime = '" + PriorDateString + "') AA GROUP BY ticker", dbcon)
    sql = "SELECT AAA.ticker FROM (SELECT A.ticker FROM `fdata_price_dayend` A INNER JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime = '" + PriorDateString + "' GROUP BY A.ticker) AAA LEFT JOIN (SELECT Ticker FROM `fdata_yahoo_fundamental` WHERE Name = '" + Yahoo_Tag_Name + "' AND CaptureDate > '" + MarketCapPriorDateString + "' GROUP BY Ticker) BBB ON AAA.ticker = BBB.Ticker WHERE BBB.Ticker IS NULL"
    print(sql)
    Tickers = pd.read_sql_query(sql, dbcon)
    # sql = "SELECT ticker from (SELECT A.* FROM `fdata_price_dayend` A LEFT JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime = '" + PriorDateString + "' AND A.ticker IN ('XONE','XOMA')) AA GROUP BY ticker"
    # print(sql)
    # Tickers = pd.read_sql_query(sql, dbcon)

    print(Tickers)

    SplitTickers = Config.SplitDataframe(Tickers, TickerCountPerThread)
    print("Number of Tickers Batch = " + str(len(SplitTickers)))

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    threads = list()

    for index in range(len(SplitTickers)):
        logging.info("Main    : create and start thread %d.", index)
        tickers = SplitTickers[index]['ticker'].tolist()
        x = threading.Thread(target=DownloadYahooFundamentalForTickersThread, args=(index, tickers, Yahoo_Tag_Name, DBTableName, today_date), daemon=True)
        threads.append(x)
        x.start()


    for index, thread in enumerate(threads):
        logging.info("Main    : before joining thread %d.", index)
        thread.join()
        logging.info("Main    : thread %d done", index)

print("done")
    

    
    
