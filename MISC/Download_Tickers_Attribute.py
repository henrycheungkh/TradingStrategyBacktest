# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 13:00:15 2021

@author: Henry Cheung
"""
import pymysql
import pandas as pd
import yfinance as yf
import Config
import os
import mysql.connector

import logging
import threading
import time

dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)


def ImportTickerAttributeToDB(ticker, Property_Type, Property):
    print("ImportTickerAttributeToDB "+ ticker + ' with Property Type ' + Property_Type + ' and Property ' + Property)
    mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
    mycursor = mydb.cursor()
    sql = "INSERT INTO `fdata_tickers_property` (Ticker, Property_Type, Property) VALUES (%s, %s, %s)"
    val = (ticker, Property_Type, Property)
    mycursor.execute(sql, val)
    mydb.commit()

    print(ticker + ' with Property Type ' + Property_Type + ' and Property ' + Property + ' added')

def ImportYahooLegalTypeToDB(Tickers):
    for i, ticker_row in Tickers.iterrows():
        print(ticker_row['Ticker'])
        try:
            t = yf.Ticker(ticker_row['Ticker'])
            if ('legalType' in t.info):
                if (t.info['legalType'] is not None):
                    print(ticker_row['Ticker'] + ":" + str(t.info['legalType']))
                    ImportTickerAttributeToDB(ticker_row['Ticker'], 'Yahoo_legalType', str(t.info['legalType']))
        except Exception as e:
            print(e)

def ImportYahooLegalTypeToDBThread(name, Tickers):
    logging.info("Thread %s: starting", name)
    ImportYahooLegalTypeToDB(Tickers)
    logging.info("Thread %s: finishing", name)

TickersPerBatch = 6000

if __name__ == "__main__":

    Tickers = pd.read_sql_query("select * from fdata_tickers where Market = 'XUSA'", dbcon)
    
    # print(Tickers)
    
    SplitTickers = Config.SplitDataframe(Tickers, TickersPerBatch)
    
    print("Number of Tickers Batch = " + str(len(SplitTickers)))
    
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    threads = list()
    for index in range(len(SplitTickers)):
        logging.info("Main    : create and start thread %d.", index)
        x = threading.Thread(target=ImportYahooLegalTypeToDBThread, args=(index, SplitTickers[index]), daemon=True)
        threads.append(x)
        x.start()

    for index, thread in enumerate(threads):
        logging.info("Main    : before joining thread %d.", index)
        thread.join()
        logging.info("Main    : thread %d done", index)



# ImportYahooLegalTypeToDB(Tickers)

