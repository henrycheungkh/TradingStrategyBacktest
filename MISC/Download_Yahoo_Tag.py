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
# from bs4 import BeautifulSoup
import requests
import logging
import threading
import time
from datetime import datetime, date
from InvestmentAnalytics.Download_Yahoo import *

# UnitDict = {'B':1000000000, 'M': 1000000}

if sys.argv[1] == 'All':
    MarketList = {"XUSA" : [], "XLON" : [], "XHKG": []}
else:
    MarketList = { sys.argv[1] : []}

Yahoo_Tag = sys.argv[2]
TickerCountPerThread = int(sys.argv[3])
# PriorDateString = '2021-04-23'
PriorDateString = sys.argv[4]


# MarketCapPriorDateString = '2020-03-25'



mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
# dt_obj = datetime.strptime(h, '%d/%m/%Y')
today_date = date.today()

def DownloadYahooPropertyThread(name, Tickers, Yahoo_Tag):
    logging.info("Thread %s: starting", name)
    DownloadYahooProperty(name, Tickers, Yahoo_Tag)
    logging.info("Thread %s: finishing", name)

def DownloadYahooProperty(name, tickers, Yahoo_Tag):
    # for index, row in tickers.iterrows():
    TickerCount = 0
    for ticker in tickers:
        try:
            TickerCount = TickerCount + 1
            if TickerCount % 50 == 0:
                print("Thread " + str(name) + " --- " + str(TickerCount) + " Tickers tried to download at " + str(datetime.now()))
            
            DownloadYahooFundamental(mydb, ticker, Yahoo_Tag, 'fdata_yahoo_property', None)
        except Exception:
            pass    


dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)

for market in MarketList:
    print("Start downloading for market " + market)
    # Tickers = pd.read_sql_query("SELECT ticker from (SELECT A.* FROM `fdata_price_dayend` A LEFT JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime = '" + PriorDateString + "') AA GROUP BY ticker", dbcon)
    Tickers = pd.read_sql_query("SELECT AAA.ticker FROM (SELECT ticker from (SELECT A.* FROM `fdata_price_dayend` A LEFT JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime = '" + PriorDateString + "') AA GROUP BY ticker) AAA LEFT JOIN (SELECT Ticker FROM `fdata_yahoo_property` WHERE Property_Type = '" + Yahoo_Tag + "' GROUP BY Ticker) BBB ON AAA.ticker = BBB.Ticker WHERE BBB.Ticker IS NULL", dbcon)
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
        x = threading.Thread(target=DownloadYahooPropertyThread, args=(index, tickers, Yahoo_Tag), daemon=True)
        threads.append(x)
        x.start()


    for index, thread in enumerate(threads):
        logging.info("Main    : before joining thread %d.", index)
        thread.join()
        logging.info("Main    : thread %d done", index)

print("done")
    

    
    
