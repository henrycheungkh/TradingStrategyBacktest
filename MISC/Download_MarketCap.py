# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 13:50:31 2021

@author: Henry Cheung
"""
import Config
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

UnitDict = {'T':1000000000000, 'B':1000000000, 'M': 1000000}

mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
# dt_obj = datetime.strptime(h, '%d/%m/%Y')
today_date = date.today()

def DownloadYahooFundamentalAndRecentDatePriceThread(name, Tickers):
    logging.info("Thread %s: starting", name)
    DownloadYahooFundamentalAndRecentDatePrice(name, Tickers)
    logging.info("Thread %s: finishing", name)

def DownloadYahooFundamentalAndRecentDatePrice(name, tickers):
    # for index, row in tickers.iterrows():
    TickerCount = 0
    for ticker in tickers:
        try:
            TickerCount = TickerCount + 1
            if TickerCount % 50 == 0:
                print("Thread " + str(name) + " --- " + str(TickerCount) + " Tickers tried to download at " + str(datetime.now()))
            t = yf.Ticker(ticker)
            try:
                if t.info['marketCap'] is not None:
                    sql = "INSERT INTO fdata_yahoo_fundamental (Ticker, CaptureDate, Name, Value) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE Value=%s"
                    val = (ticker, today_date, 'marketCap', t.info['marketCap'], t.info['marketCap'])
                    mycursor = mydb.cursor()
                    mycursor.execute(sql, val)
                    mydb.commit()
                    print('In thread ' + str(name) + ': uploaded ' + ticker + ' at ' + str(datetime.now()))
            except Exception:
                pass    
        except Exception:
            pass    

# MarketList = {"XUSA" : [], "XLON" : [], "XHKG": []}
# MarketList = { "XLON" : []}
MarketList = { "XUSA" : []}
# MarketList = { "XHKG" : []}
TickerCountPerThread = 1000
PriorDateString = '2021-04-30'
MarketCapPriorDateString = '2020-03-25'

dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)

for market in MarketList:
    print("Start downloading for market " + market)
    # Tickers = pd.read_sql_query("SELECT ticker from (SELECT A.* FROM `fdata_price_dayend` A LEFT JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime = '" + PriorDateString + "') AA GROUP BY ticker", dbcon)
    Tickers = pd.read_sql_query("SELECT AAA.ticker FROM (SELECT ticker from (SELECT A.* FROM `fdata_price_dayend` A LEFT JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime = '" + PriorDateString + "') AA GROUP BY ticker) AAA LEFT JOIN (SELECT Ticker FROM `fdata_yahoo_fundamental` WHERE CaptureDate > '" + MarketCapPriorDateString + "' GROUP BY Ticker) BBB ON AAA.ticker = BBB.Ticker WHERE BBB.Ticker IS NULL", dbcon)
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
        x = threading.Thread(target=DownloadYahooFundamentalAndRecentDatePriceThread, args=(index, tickers), daemon=True)
        threads.append(x)
        x.start()


    for index, thread in enumerate(threads):
        logging.info("Main    : before joining thread %d.", index)
        thread.join()
        logging.info("Main    : thread %d done", index)

print("done")
    

    
    
