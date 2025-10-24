# -*- coding: utf-8 -*-
"""
Created on Fri May 12 07:56:29 2023

@author: Henry Cheung
"""


import InvestmentAnalytics.Config as Config
import InvestmentAnalytics.DBUtil as DBUtil
# from sqlalchemy import create_engine
from sqlalchemy.sql import text

from InvestmentAnalytics.DBUtil import DBExportDirectUpload
import os
import sys
import csv
import pandas as pd

import logging

from datetime import date, datetime, timedelta

pd.set_option('display.max_columns', None)
today = date.today()
DataEndDate = today.strftime("%Y%m%d")
# DataEndDate = "20210719"
print(DataEndDate)
BarSize = "1 min"
# BarSize = "30 mins"
# BarSize = "1 day"
# BarSize = sys.argv[1]
print("BarSize is " + BarSize)

market = "XUSA"
StockFilter = ""

if len(sys.argv) > 2:
    PriorDateString = sys.argv[2]
else:
    # PriorDateString = '2023-01-01'
    current_date = datetime.now()
    three_months_ago = current_date - timedelta(days=3*30)
    PriorDateString = three_months_ago.strftime('%Y-%m-%d')

print('PriorDateString is ' + PriorDateString)

    

if BarSize == "30 mins":
    sql = "SELECT '30 mins' as timeframe, AAAAA.*, IFNULL(BBBBB.Property, 'NONE') AS primaryExchange FROM (SELECT AAAA.ticker as symbol, 'STK' as secType, 'USD' as currency, 'SMART' as exchange, AAAA.*, BBBB.Property As Industry FROM (SELECT AAA.ticker, BBB.Property AS Sector FROM (SELECT AA.ticker FROM (SELECT A.ticker FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_DAYEND_IB + ".`fdata_price_dayend_ib` A INNER JOIN " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime > '" + PriorDateString + "' " + StockFilter + " GROUP BY A.ticker UNION select ticker from " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_ipo`) AA LEFT JOIN (SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_property` WHERE Property_Type = 'Yahoo_legalType') BB ON AA.ticker = BB.Ticker WHERE BB.Property IS NULL or BB.Property <> 'Exchange Traded Fund' ) AAA LEFT JOIN (SELECT Ticker, Property FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_yahoo_property` WHERE Property_Type = 'sector') BBB ON AAA.ticker = BBB.Ticker) AAAA LEFT JOIN (SELECT Ticker, Property FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_yahoo_property` WHERE Property_Type = 'industry') BBBB ON AAAA.ticker = BBBB.Ticker) AAAAA LEFT JOIN (SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_property` WHERE Property_Type = 'primaryExchange') BBBBB ON AAAAA.symbol = BBBBB.Ticker"
elif BarSize == "1 min":
    sql = "SELECT '1 min' as timeframe, AAAAA.*, IFNULL(BBBBB.Property, 'NONE') AS primaryExchange FROM (SELECT AAAA.ticker as symbol, 'STK' as secType, 'USD' as currency, 'SMART' as exchange, AAAA.*, BBBB.Property As Industry FROM (SELECT AAA.ticker, BBB.Property AS Sector FROM (SELECT AA.ticker FROM (SELECT A.ticker FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_30MIN_IB + ".`fdata_price_30min_ib` A INNER JOIN " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime > '" + PriorDateString + "' " + StockFilter + " GROUP BY A.ticker) AA LEFT JOIN (SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_property` WHERE Property_Type = 'Yahoo_legalType') BB ON AA.ticker = BB.Ticker WHERE BB.Property IS NULL or BB.Property <> 'Exchange Traded Fund' ) AAA LEFT JOIN (SELECT Ticker, Property FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_yahoo_property` WHERE Property_Type = 'sector') BBB ON AAA.ticker = BBB.Ticker) AAAA LEFT JOIN (SELECT Ticker, Property FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_yahoo_property` WHERE Property_Type = 'industry') BBBB ON AAAA.ticker = BBBB.Ticker) AAAAA LEFT JOIN (SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_property` WHERE Property_Type = 'primaryExchange') BBBBB ON AAAAA.symbol = BBBBB.Ticker"
else:
    sql = "SELECT '1 day' as timeframe, AAAAA.*, IFNULL(BBBBB.Property, 'NONE') AS primaryExchange FROM (SELECT AAAA.ticker as symbol, 'STK' as secType, 'USD' as currency, 'SMART' as exchange, AAAA.*, BBBB.Property As Industry FROM (SELECT AAA.ticker, BBB.Property AS Sector FROM (SELECT AA.ticker FROM (SELECT Ticker as ticker FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers` B WHERE Market = '" + market + "'  " + StockFilter + " ) AA LEFT JOIN (SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_property` WHERE Property_Type = 'Yahoo_legalType') BB ON AA.ticker = BB.Ticker WHERE BB.Property IS NULL or BB.Property <> 'Exchange Traded Fund' ) AAA LEFT JOIN (SELECT Ticker, Property FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_yahoo_property` WHERE Property_Type = 'sector') BBB ON AAA.ticker = BBB.Ticker) AAAA LEFT JOIN (SELECT Ticker, Property FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_yahoo_property` WHERE Property_Type = 'industry') BBBB ON AAAA.ticker = BBBB.Ticker) AAAAA LEFT JOIN (SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".`fdata_tickers_property` WHERE Property_Type = 'primaryExchange') BBBBB ON AAAAA.symbol = BBBBB.Ticker"

print(sql)
Tickers = pd.read_sql(sql,con=DBUtil.GetSQLAlchemyEngine())    

print(Tickers)

statement = text("""DELETE FROM fdata_ib_download_stock_tickers WHERE timeframe = :timeframe""")
line = { "timeframe": BarSize}
engine = DBUtil.GetSQLAlchemyEngine()
# engine.execute(statement, **line)
with engine.connect() as conn:
    # result = conn.execute(statement, line)
    conn.execute(statement, line)
    conn.commit()
    conn.close()

Tickers.to_sql(name='fdata_ib_download_stock_tickers', con=engine, if_exists = 'append', index=False)

# statement = text("""INSERT IGNORE INTO pending_db_upload_command (command, DBName, TableName, Uploaded) VALUES (:command, :DBName, :TableName, False)""")
# line = { "command": command, "DBName": DatabaseName, "TableName": DBTableName }
# engine = GetSQLAlchemyEngine()
# engine.execute(statement, **line)



