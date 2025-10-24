# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 13:50:31 2021

@author: Henry Cheung
"""
import Config
import os
import sys
import pymysql
import pandas as pd


from bs4 import BeautifulSoup
import requests
import logging
import threading
import time
from datetime import datetime

def DownloadPreMarketPriceThread(name, Tickers):
    logging.info("Thread %s: starting", name)
    DownloadPreMarketPrice(name, Tickers)
    logging.info("Thread %s: finishing", name)

def DownloadPreMarketPrice(name, tickers):
    for ticker in tickers:
        try:
            # print('aaa'+ ' at ' + str(datetime.now()))
            # print('In thread ' + str(name) + ': Trying ' + ticker + ' at ' + str(datetime.now()))
            # print('bbb')
            url = 'https://finance.yahoo.com/quote/' + ticker
            source = requests.get(url).text
            soup = BeautifulSoup(source, 'lxml')
            d = soup.find('span', attrs={'data-reactid':'37'})
            print('In thread ' + str(name) + ': ' + ticker + ' price at Pre market is ' + d.text + ' at ' + str(datetime.now()))
        except Exception:
            pass    

# MarketList = {"FXCM" : [], "XLON" : [], "XHKG": ["HSI"], "XUSA" : [], "Crypto" : []}
MarketList = { "XUSA" : []}
TickerCountPerThread = 1000
PriorDateString = '2021-03-25'


dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)

for market in MarketList:
    print("Start downloading for market " + market)
    # Tickers = pd.read_sql_query("select * from fdata_tickers where Market = '" + market + "'", dbcon)
    # Tickers = pd.read_sql_query("SELECT ticker from (SELECT A.* FROM `fdata_price_dayend` A LEFT JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime > '" + PriorDateString + "') AA GROUP BY ticker", dbcon)
    Tickers = pd.read_sql_query("SELECT ticker, `Adj Close` from (SELECT A.* FROM `fdata_price_dayend` A LEFT JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime = '" + PriorDateString + "') AA GROUP BY ticker", dbcon)

    SplitTickers = Config.SplitDataframe(Tickers, TickerCountPerThread)
    print("Number of Tickers Batch = " + str(len(SplitTickers)))

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    threads = list()


    # print(SplitTickers[0])

    for index in range(len(SplitTickers)):
        # print('SplitTickers is')
        # print(SplitTickers)
        logging.info("Main    : create and start thread %d.", index)
        tickers = SplitTickers[index]['ticker'].tolist()
        x = threading.Thread(target=DownloadPreMarketPriceThread, args=(index, tickers), daemon=True)
        threads.append(x)
        x.start()


    for index, thread in enumerate(threads):
        logging.info("Main    : before joining thread %d.", index)
        thread.join()
        logging.info("Main    : thread %d done", index)

    # tickers = Tickers['Ticker'].tolist()
    
    # # tickers = ['TSLA', 'AAPL', 'MSFT', 'KALV']

    # DownloadPreMarketPrice('', tickers)
    

    
    
