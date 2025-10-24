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
import math


from bs4 import BeautifulSoup
import requests
import logging
import threading
import time
from datetime import datetime, date

from InvestmentAnalytics.EmailModule import SendEmail

# MarketList = {"FXCM" : [], "XLON" : [], "XHKG": ["HSI"], "XUSA" : [], "Crypto" : []}

MarketList = { "XUSA" : []}
# TickerCountPerThread = 250
# PriorDateString = '2021-04-22'


today_date = date.today()

mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)



def UploadGappersPriceThread(name, Tickers):
    # print('in UploadGappersPrice, trying ' + ticker)
    global mydb
    
    for index, row in Tickers.iterrows():
        try:
            # print('In for loop for ' + row['Ticker'])
            url = 'https://finance.yahoo.com/quote/' + row['Ticker']
            source = requests.get(url).text
            soup = BeautifulSoup(source, 'lxml')
            pre_market = soup.find('span', attrs={'data-reactid':'37'}).text.replace(',','')
            # print(pre_market)
            PreMarketPrice = float(pre_market)
            # UploadGappersPrice(row['Ticker'], PreMarketPrice)
            # print('before sql')
    
            sql = "INSERT IGNORE INTO fdata_us_gapper_premarket_price (CaptureDatetime, Ticker, Price) VALUES (%s, %s, %s)"
            val = (datetime.now(), row['Ticker'],PreMarketPrice)
            mycursor = mydb.cursor()
            mycursor.execute(sql, val)
            mydb.commit()
            print('In Thread ' + str(name) + ': Pre Market price of ' + row['Ticker'] + ' is uploaded')        
            
        except Exception:
            pass   
    
dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)

now = datetime.now()
# print(now.year, now.month, now.day, now.hour, now.minute, now.second)

# i = 1
# while i <= 1:
#     i = i + 1
while (now.hour < 14) or (now.hour == 14 and now.minute < 30 ):
    for market in MarketList:
        print("Start uploading gappers premarket prices for market " + market + ' for '+ today_date.strftime("%Y-%m-%d"))
        StockFilter = ""
        sql = "SELECT Ticker FROM `fdata_us_gapper_tickers` WHERE CaptureDate = '" + today_date.strftime("%Y-%m-%d") +"' " + StockFilter + " GROUP BY Ticker"
        # print(sql)
        Tickers = pd.read_sql_query(sql, dbcon)
        print("Tickers count = " + str(len(Tickers)))
        print(Tickers)
        
        if len(Tickers) > 0:
        
            SplitTickers = Config.SplitDataframe(Tickers, math.ceil(len(Tickers)/3))
            print("Number of Tickers Batch = " + str(len(SplitTickers)))
        
            format = "%(asctime)s: %(message)s"
            logging.basicConfig(format=format, level=logging.INFO,
                                datefmt="%H:%M:%S")
            threads = list()
        
            # print(SplitTickers[0])
        
            for index in range(len(SplitTickers)):
                logging.info("Main    : create and start thread %d.", index)
                x = threading.Thread(target=UploadGappersPriceThread, args=(index, SplitTickers[index]), daemon=True)
                threads.append(x)
                x.start()
        
            for index, thread in enumerate(threads):
                logging.info("Main    : before joining thread %d.", index)
                thread.join()
                logging.info("Main    : thread %d done", index)        
            
    now = datetime.now()
    
print('done')

