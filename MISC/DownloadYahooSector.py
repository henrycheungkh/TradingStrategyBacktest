# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 23:56:29 2020

@author: Henry Cheung
"""


import pymysql
import mysql.connector
import pandas as pd
import yfinance as yf
import Config

from datetime import date, datetime, timedelta

MarketList = {"XLON" : ["ETF", "FTSE100", "FTSE250"], "XHKG": ["HSI"], "XUSA" : []}

def DownloadSectorFromYahoo(Tickers):
    for t in Tickers['Ticker'].tolist():
        try:
            # print(t)
            aa = yf.Ticker(t)
            # print('a ' + t + ' a')
            sql = "INSERT INTO fdata_tickers_sector (Ticker, Sector, Industry) VALUES (%s, %s, %s)"
            val = (t, aa.info['sector'], aa.info['industry'])
            mycursor.execute(sql, val)
            mydb.commit()
            # print('done for ' + t)
        except Exception:
            pass

dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)

mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
mycursor = mydb.cursor()

for market in MarketList:
  print("Start downloading for market " + market)
  Tickers = pd.read_sql_query("select * from fdata_tickers where Market = '" + market + "'", dbcon)
  # print(Tickers)
  DownloadSectorFromYahoo(Tickers)


