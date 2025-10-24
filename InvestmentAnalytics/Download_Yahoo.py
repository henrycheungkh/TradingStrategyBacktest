# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 00:11:19 2021

@author: Henry Cheung
"""
import yfinance as yf
# from bs4 import BeautifulSoup
from datetime import datetime, date


def DownloadYahooFundamental(DBConnector, ticker, Yahoo_Tag, DBTableName, DBCaptureDate):
    # print('Try ticker ' + ticker)
    t = yf.Ticker(ticker)
    if DBTableName == 'fdata_yahoo_fundamental':
        if t.info[Yahoo_Tag] is not None:
            sql = "INSERT INTO fdata_yahoo_fundamental (Ticker, CaptureDate, Name, Value) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE Value=%s"
            val = (ticker, DBCaptureDate, Yahoo_Tag, t.info[Yahoo_Tag], t.info[Yahoo_Tag])
            mycursor = DBConnector.cursor()
            mycursor.execute(sql, val)
            DBConnector.commit()
            print('Uploaded ' + Yahoo_Tag + ' of ' + ticker + ' at ' + str(datetime.now()))
    if DBTableName == 'fdata_yahoo_property':
        if t.info[Yahoo_Tag] is not None:
            # print('Trying ticker ' + ticker)
            sql = "INSERT INTO fdata_yahoo_property (Ticker, Property_Type, Property) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE Property=%s"
            val = (ticker, Yahoo_Tag, t.info[Yahoo_Tag], t.info[Yahoo_Tag])
            mycursor = DBConnector.cursor()
            mycursor.execute(sql, val)
            DBConnector.commit()
            print('Uploaded ' + Yahoo_Tag + ' of ' + ticker + ' at ' + str(datetime.now()))