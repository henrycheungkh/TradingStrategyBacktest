# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 01:23:58 2021

@author: Henry Cheung
"""


# import pymysql
import sys
import InvestmentAnalytics.Config as Config
import InvestmentAnalytics.DBUtil as DBUtil
from sqlalchemy.sql import text
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np

import math

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

today = date.today()
PriorMonthDate = today - timedelta(days=30)

def GetRecentData(sql, DatabaseName = Config.CONFIG_MYSQL_CONNECTION_DATABASE):
    # if DatabaseName is None:
    #     # dbconnect = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD)
    #     # dbconnect = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD)
    #     dbconnect = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, port=Config.CONFIG_MYSQL_CONNECTION_PORT)
    # else:
    #     # dbconnect = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, DatabaseName)
    #     # dbconnect = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=DatabaseName)
    #     dbconnect = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=DatabaseName, port=Config.CONFIG_MYSQL_CONNECTION_PORT)
        
    dbconnect = DBUtil.DBGetDBInstance(DatabaseName)
    # sql = "SELECT COUNT(*) AS RecordCount FROM `" + DBTableName + "`"
    # print(pd.read_sql_query(sql, dbconnect))
    # return pd.read_sql_query(sql, dbconnect)
    return pd.read_sql(sql,con=DBUtil.GetSQLAlchemyEngine(DatabaseName=DatabaseName))

print(today)
print(PriorMonthDate)

if len(sys.argv) > 1:
    HealthCheckSection = sys.argv[1]
else:
    HealthCheckSection = 'All'

if len(sys.argv) > 2:
    UploadFuturesPatchCommand = sys.argv[2]
else:
    UploadFuturesPatchCommand = 'No'
    
print('UploadFuturesPatchCommand is ' + UploadFuturesPatchCommand)

# sql = "SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST + ".fdata_fut_hist where " + TickerFilterString + " tDateTime BETWEEN '" + self.StartDate.strftime("%Y-%m-%d") + " 00:00:00' AND '" + self.EndDate.strftime("%Y-%m-%d") + " 23:59:59' AND timeframe = '" + self.TimeFrame + "'"
# Prices_df = pd.read_sql_query(sql, dbcon)

# sql = "SELECT * FROM fdata_fut_hist where " + TickerFilterString + " tDateTime BETWEEN '" + self.StartDate.strftime("%Y-%m-%d") + " 00:00:00' AND '" + self.EndDate.strftime("%Y-%m-%d") + " 23:59:59' AND timeframe = '" + self.TimeFrame + "'"
# Prices_df = pd.read_sql_query(sql, dbcon)

if (HealthCheckSection == 'All') or (HealthCheckSection == 'YahooStockPrice') or (HealthCheckSection == 'YahooStockPrice1min'):

    # sql = "SELECT DATE(Datetime), count(Close) FROM `fdata_price_1min` WHERE Datetime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(Datetime) ORDER BY DATE(Datetime) DESC LIMIT 14"
    # print('Record summary for Stock Price 1min')
    # print(GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_1MIN))

    # sql = "SELECT A.ValueDate, B.Market, sum(A.record_count) AS RecordCount FROM (SELECT DATE(Datetime) as ValueDate, ticker, count(Close) as record_count FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_1MIN + ".fdata_price_1min WHERE Datetime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(Datetime), ticker) A INNER JOIN " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".fdata_tickers B ON A.ticker = B.Ticker GROUP BY A.ValueDate, B.Market DESC LIMIT 70"
    sql = "SELECT A.ValueDate, B.Market, sum(A.record_count) AS RecordCount FROM (SELECT DATE(Datetime) as ValueDate, ticker, count(Close) as record_count FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_1MIN + ".fdata_price_1min WHERE Datetime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(Datetime), ticker) A INNER JOIN " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".fdata_tickers B ON A.ticker = B.Ticker GROUP BY A.ValueDate, B.Market DESC"
    print(sql)
    print('Record summary for Stock Price 1min')
    df = GetRecentData(sql, None)
    # print(df)
    if len(df) <= 0:
        print('no record for Stock Price 1min')
    else:
        df = pd.pivot_table(df, index=['ValueDate'],columns=['Market'], values='RecordCount', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
        df.set_index('ValueDate', inplace=True)
        print(df)


    sql = "SELECT A.ValueDate, B.Market, sum(A.record_count) AS RecordCount FROM (SELECT DATE(Datetime) as ValueDate, ticker, count(Close) as record_count FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_1MIN_FX + ".fdata_price_1min WHERE ticker like '%=X' AND Datetime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(Datetime), ticker) A INNER JOIN " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".fdata_tickers B ON A.ticker = B.Ticker GROUP BY A.ValueDate, B.Market DESC"
    print(sql)
    print('Record summary for FX Price 1min')
    df = GetRecentData(sql, None)
    if len(df) <= 0:
        print('no record for FX Price 1min')
    else:
        df = pd.pivot_table(df, index=['ValueDate'],columns=['Market'], values='RecordCount', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
        df.set_index('ValueDate', inplace=True)
        print(df)

    
if (HealthCheckSection == 'All') or (HealthCheckSection == 'YahooStockPrice') or (HealthCheckSection == 'YahooStockPriceDayEnd'):
    # sql = "SELECT DATE(Datetime), count(Close) FROM `fdata_price_dayend` WHERE Datetime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(Datetime) ORDER BY DATE(Datetime) DESC LIMIT 14"
    # sql = "SELECT DATE(Datetime), count(Close) FROM `fdata_price_dayend` WHERE Datetime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(Datetime) ORDER BY DATE(Datetime) DESC"
    # print('Record summary for Stock Price dayend')
    # print(GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE))

    sql = "SELECT A.ValueDate, B.Market, sum(A.record_count) AS RecordCount FROM (SELECT DATE(Datetime) As ValueDate, ticker, count(Close) AS record_count FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_DAYEND + ".`fdata_price_dayend` WHERE Datetime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(Datetime), ticker) A INNER JOIN " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".fdata_tickers B ON A.ticker = B.Ticker GROUP BY A.ValueDate, B.Market DESC"
    # sql = "SELECT A.ValueDate, B.Market, sum(A.record_count) AS RecordCount FROM (SELECT DATE(Datetime) as ValueDate, ticker, count(Close) as record_count FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_1MIN + ".fdata_price_1min WHERE Datetime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(Datetime), ticker) A INNER JOIN " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".fdata_tickers B ON A.ticker = B.Ticker GROUP BY A.ValueDate, B.Market DESC"
    print(sql)
    print('Record summary for Stock Price dayend')
    # df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
    df = GetRecentData(sql, None)
    if len(df) <= 0:
        print('no record for Stock Price Day End')
    else:
        df = pd.pivot_table(df, index=['ValueDate'],columns=['Market'], values='RecordCount', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
        df.set_index('ValueDate', inplace=True)
        print(df)
    
if (HealthCheckSection == 'All') or (HealthCheckSection == 'YahooStockPrice') or (HealthCheckSection == 'YahooStockPrice30min'):
    # sql = "SELECT DATE(Datetime), count(Close) FROM `fdata_price_30min` WHERE Datetime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(Datetime) ORDER BY DATE(Datetime) DESC LIMIT 14"
    # sql = "SELECT DATE(Datetime), count(Close) FROM `fdata_price_30min` WHERE Datetime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(Datetime) ORDER BY DATE(Datetime) DESC"
    # print('Record summary for Stock Price 30min')
    # print(GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE))

    sql = "SELECT A.ValueDate, B.Market, sum(A.record_count) AS RecordCount FROM (SELECT DATE(Datetime) As ValueDate, ticker, count(Close) AS record_count FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_30MIN + ".`fdata_price_30min` WHERE Datetime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(Datetime), ticker) A INNER JOIN " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".fdata_tickers B ON A.ticker = B.Ticker GROUP BY A.ValueDate, B.Market DESC"
    # sql = "SELECT A.ValueDate, B.Market, sum(A.record_count) AS RecordCount FROM (SELECT DATE(Datetime) as ValueDate, ticker, count(Close) as record_count FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_1MIN + ".fdata_price_1min WHERE Datetime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(Datetime), ticker) A INNER JOIN " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".fdata_tickers B ON A.ticker = B.Ticker GROUP BY A.ValueDate, B.Market DESC"
    print(sql)
    # df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
    df = GetRecentData(sql, None)
    if len(df) <= 0:
        print('no record for Stock Price 30min')
    else:
        print('Record summary for Stock Price 30min')
        df = pd.pivot_table(df, index=['ValueDate'],columns=['Market'], values='RecordCount', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
        df.set_index('ValueDate', inplace=True)
        print(df)


if (HealthCheckSection == 'All') or (HealthCheckSection == 'IBFuturesPrice'):
    
    # print('Record summary for Futures Price')
    # sql = "SELECT ticker, timeframe, max(tDateTime) FROM `fdata_fut_hist` GROUP BY ticker, timeframe ORDER BY max(tDateTime)"
    # print(GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST))

    # # sql = "SELECT timeframe, DATE(tDateTime) AS ValueDate, DataType, count(close) AS RecordCount FROM `fdata_fut_hist` WHERE tDateTime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY timeframe, DATE(tDateTime), DataType ORDER BY timeframe, DataType, DATE(tDateTime) DESC"
    # df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)
    # sql = "SELECT timeframe, DATE(tDateTime) AS ValueDate, DataType, count(close) AS RecordCount FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST + ".`fdata_fut_hist` WHERE tDateTime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY timeframe, DATE(tDateTime), DataType UNION ALL SELECT timeframe, DATE(tDateTime) AS ValueDate, DataType, count(close) AS RecordCount FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST_10SECS + ".`fdata_fut_hist` WHERE tDateTime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY timeframe, DATE(tDateTime), DataType"
    # df = GetRecentData(sql, None)
    # df = pd.pivot_table(df, index=['ValueDate'],columns=['timeframe', 'DataType'], values='RecordCount', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
    # df.set_index('ValueDate', inplace=True)
    # print(df.head(10))
    
    if UploadFuturesPatchCommand == 'UploadFuturesPatch':
        print('delete done patches')
        statement = text("""DELETE FROM daily_futures_download_patching WHERE Uploaded = 1""")
        engine = DBUtil.GetSQLAlchemyEngine()
        # engine.execute(statement)
        with engine.connect() as conn:
            # result = conn.execute(statement)
            conn.execute(statement)
            conn.commit()
            conn.close()
    

    
    
    sql = "SELECT ticker, timeframe, DATE(tDateTime) as ValueDate, DataType, count(close) as RecordCount FROM fdata_fut_hist WHERE DataType = 'TRADES' AND timeframe = '1 min' and tDateTime > '" + PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY ticker, timeframe, DATE(tDateTime), DataType ORDER BY ticker, DATE(tDateTime) DESC"
    df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)
    df = pd.pivot_table(df, index=['timeframe', 'ValueDate'],columns=['DataType', 'ticker'], values='RecordCount', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
    df.set_index(['timeframe','ValueDate'], inplace=True)
    print(df.head(10))
    
    if UploadFuturesPatchCommand == 'UploadFuturesPatch':
        Barsize = '1 min'
        firstrow_series = df.iloc[0]
        # print(firstrow_series)
        for ticker, v in firstrow_series.items():
            if (math.isnan(v)):
                print('add upload patch for: ', ticker[1], ', for: ', Barsize)
                statement = text("""INSERT IGNORE INTO daily_futures_download_patching (ticker, timeframe, Uploaded) VALUES (:ticker, :timeframe, :Uploaded )""")
                line = { "ticker": ticker[1], "timeframe": Barsize, "Uploaded": 0 }
                engine = DBUtil.GetSQLAlchemyEngine()
                # engine.execute(statement, **line)
                with engine.connect() as conn:
                    # result = conn.execute(statement, line)
                    conn.execute(statement, line)
                    conn.commit()
                    conn.close()
    

                print('add upload done')


           
    sql = "SELECT ticker, timeframe, DATE(tDateTime) as ValueDate, DataType, count(close) as RecordCount FROM fdata_fut_hist WHERE DataType = 'TRADES' AND timeframe = '10 secs' and tDateTime > '" + PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY ticker, timeframe, DATE(tDateTime), DataType ORDER BY ticker, DATE(tDateTime) DESC"
    df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST_10SECS)
    df = pd.pivot_table(df, index=['timeframe', 'ValueDate'],columns=['DataType', 'ticker'], values='RecordCount', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
    df.set_index(['timeframe','ValueDate'], inplace=True)
    print(df.head(10))
    
    if UploadFuturesPatchCommand == 'UploadFuturesPatch':
        Barsize = '10 secs'
        firstrow_series = df.iloc[0]
        # print(firstrow_series)
        for ticker, v in firstrow_series.items():
            if (math.isnan(v)):
                print('add upload patch for: ', ticker[1], ', for: ', Barsize)
                statement = text("""INSERT IGNORE INTO daily_futures_download_patching (ticker, timeframe, Uploaded) VALUES (:ticker, :timeframe, :Uploaded )""")
                line = { "ticker": ticker[1], "timeframe": Barsize, "Uploaded": 0 }
                engine = DBUtil.GetSQLAlchemyEngine()
                # engine.execute(statement, **line)
                with engine.connect() as conn:
                    # result = conn.execute(statement, line)
                    conn.execute(statement, line)
                    conn.commit()
                    conn.close()

                print('add upload done')


    sql = "SELECT ticker, timeframe, DATE(tDateTime) as ValueDate, DataType, count(close) as RecordCount FROM fdata_fut_hist WHERE DataType = 'TRADES' AND timeframe = '5 secs' and tDateTime > '" + PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY ticker, timeframe, DATE(tDateTime), DataType ORDER BY ticker, DATE(tDateTime) DESC"
    df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST_5SECS)
    df = pd.pivot_table(df, index=['timeframe', 'ValueDate'],columns=['DataType', 'ticker'], values='RecordCount', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
    df.set_index(['timeframe','ValueDate'], inplace=True)
    print(df.head(10))

    
    if UploadFuturesPatchCommand == 'UploadFuturesPatch':
        Barsize = '5 secs'
        firstrow_series = df.iloc[0]
        # print(firstrow_series)
        for ticker, v in firstrow_series.items():
            if (math.isnan(v)):
                print('add upload patch for: ', ticker[1], ', for: ', Barsize)
                statement = text("""INSERT IGNORE INTO daily_futures_download_patching (ticker, timeframe, Uploaded) VALUES (:ticker, :timeframe, :Uploaded )""")
                line = { "ticker": ticker[1], "timeframe": Barsize, "Uploaded": 0 }
                engine = DBUtil.GetSQLAlchemyEngine()
                # engine.execute(statement, **line)
                with engine.connect() as conn:
                    # result = conn.execute(statement, line)
                    conn.execute(statement, line)
                    conn.commit()
                    conn.close()

                print('add upload done')


    sql = "SELECT ticker, timeframe, DATE(tDateTime) as ValueDate, DataType, count(close) as RecordCount FROM fdata_fut_hist WHERE DataType = 'TRADES' AND timeframe = '5 mins' and tDateTime > '" + PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY ticker, timeframe, DATE(tDateTime), DataType ORDER BY ticker, DATE(tDateTime) DESC"
    df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)
    df = pd.pivot_table(df, index=['timeframe', 'ValueDate'],columns=['DataType', 'ticker'], values='RecordCount', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
    df.set_index(['timeframe','ValueDate'], inplace=True)
    print(df.head(10))
    
    if UploadFuturesPatchCommand == 'UploadFuturesPatch':
        Barsize = '5 mins'
        firstrow_series = df.iloc[0]
        # print(firstrow_series)
        for ticker, v in firstrow_series.items():
            if (math.isnan(v)):
                print('add upload patch for: ', ticker[1], ', for: ', Barsize)
                statement = text("""INSERT IGNORE INTO daily_futures_download_patching (ticker, timeframe, Uploaded) VALUES (:ticker, :timeframe, :Uploaded )""")
                line = { "ticker": ticker[1], "timeframe": Barsize, "Uploaded": 0 }
                engine = DBUtil.GetSQLAlchemyEngine()
                # engine.execute(statement, **line)
                with engine.connect() as conn:
                    # result = conn.execute(statement, line)
                    conn.execute(statement, line)
                    conn.commit()
                    conn.close()

                print('add upload done')

    
if (HealthCheckSection == 'IBFuturesPriceHighestVolumeTime'):
    
    # print('Record summary for Futures Price')
    # sql = "SELECT ticker, timeframe, max(tDateTime) FROM `fdata_fut_hist` GROUP BY ticker, timeframe ORDER BY max(tDateTime)"
    # print(GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST))

    # sql = "SELECT ticker, timeframe, DATE(tDateTime) as ValueDate, DataType, count(close) as RecordCount FROM fdata_fut_hist WHERE DataType = 'TRADES' AND timeframe = '1 min' and tDateTime > '" + PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY ticker, timeframe, DATE(tDateTime), DataType ORDER BY ticker, DATE(tDateTime) DESC"
    sql = "SELECT B.ticker, B.expiry, B.tDateTime, DATE(B.tDateTime) as ValueDate FROM (SELECT ticker, DATE(tDateTime) as ValueDate, max(vol) as MaxVolume FROM fdata_fut_hist WHERE ticker in ('ES', 'NQ', 'RTY', 'YM') AND DataType = 'TRADES' AND timeframe = '1 min' and tDateTime > '" + PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY ticker, timeframe, DATE(tDateTime), DataType ORDER BY ticker, DATE(tDateTime) DESC) A LEFT JOIN (SELECT * FROM fdata_fut_hist WHERE ticker in ('ES', 'NQ', 'RTY', 'YM') AND DataType = 'TRADES' AND timeframe = '1 min' and tDateTime > '" + PriorMonthDate.strftime("%Y-%m-%d") + "') B ON A.ticker = B.ticker AND A.ValueDate = DATE(B.tDateTime) AND A.MaxVolume = B.vol"
    df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)
    df = pd.pivot_table(df, index=['ValueDate'],columns=['ticker'], values='tDateTime', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
    df.set_index(['ValueDate'], inplace=True)
    print(df.head(10))

if (HealthCheckSection == 'IBFuturesPriceByTicker'):

    # sql = "SELECT ticker, timeframe, DATE(tDateTime) AS ValueDate, DataType, count(close) AS RecordCount FROM `fdata_fut_hist` WHERE tDateTime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY ticker, timeframe, DATE(tDateTime), DataType ORDER BY ticker, timeframe, DataType, DATE(tDateTime) DESC"
    # df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)
    sql = "SELECT ticker, timeframe, DATE(tDateTime) AS ValueDate, DataType, count(close) AS RecordCount FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST + ".`fdata_fut_hist` WHERE tDateTime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY ticker, timeframe, DATE(tDateTime), DataType UNION ALL SELECT ticker, timeframe, DATE(tDateTime) AS ValueDate, DataType, count(close) AS RecordCount FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST_10SECS + ".`fdata_fut_hist` WHERE tDateTime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY ticker, timeframe, DATE(tDateTime), DataType"
    df = GetRecentData(sql, None)
    print('Record summary for Futures Price')
    df = pd.pivot_table(df, index=['ticker', 'ValueDate'],columns=['timeframe', 'DataType'], values='RecordCount', aggfunc=np.mean).reset_index().sort_values(by=['ticker', 'ValueDate'], ascending=False)
    df.set_index(['ticker','ValueDate'], inplace=True)
    print(df)


if (HealthCheckSection == 'All') or (HealthCheckSection == 'IBStockPrice') or (HealthCheckSection == 'IBStockPrice30mins'):
    sql = "SELECT DATE(DateTime) AS ValueDate, DataType, count(close) AS RecordCount FROM `fdata_price_30min_ib` WHERE DateTime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(DateTime), DataType ORDER BY DATE(DateTime), DataType DESC"
    print('Record summary for IB Stock 30min bar Price')
    df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_30MIN_IB)
    if len(df) > 0:
        df = pd.pivot_table(df, index=['ValueDate'],columns=['DataType'], values='RecordCount', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
        df.set_index('ValueDate', inplace=True)
        print(df)
        
if (HealthCheckSection == 'All') or (HealthCheckSection == 'IBStockPrice') or (HealthCheckSection == 'IBStockPriceDayEnd'):

    sql = "SELECT DATE(DateTime) AS ValueDate, DataType, count(close) AS RecordCount FROM `fdata_price_dayend_ib` WHERE DateTime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(DateTime), DataType ORDER BY DATE(DateTime), DataType DESC"
    print('Record summary for IB Stock day end bar Price')
    df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_DAYEND_IB)
    if len(df) > 0:
        df = pd.pivot_table(df, index=['ValueDate'],columns=['DataType'], values='RecordCount', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
        df.set_index('ValueDate', inplace=True)
        print(df)

if (HealthCheckSection == 'All') or (HealthCheckSection == 'IBStockPrice') or (HealthCheckSection == 'IBStockPrice1min'):
    sql = "SELECT DATE(DateTime) AS ValueDate, DataType, count(close) AS RecordCount FROM `fdata_price_1min_ib` WHERE DateTime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(DateTime), DataType ORDER BY DATE(DateTime), DataType DESC"
    print('Record summary for IB Stock 1min bar Price')
    df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_1MIN_IB)
    if len(df) > 0:
        df = pd.pivot_table(df, index=['ValueDate'],columns=['DataType'], values='RecordCount', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
        df.set_index('ValueDate', inplace=True)
        print(df)


# sql = "SELECT DATE(tDateTime), DataType, count(close) FROM `fdata_fut_hist` WHERE timeframe = '1 min' AND tDateTime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(tDateTime), DataType ORDER BY DATE(tDateTime), DataType DESC LIMIT 42"
# print('Record summary for Futures Price 1min')
# ShowRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)

# sql = "SELECT DATE(tDateTime), DataType, count(close) FROM `fdata_fut_hist` WHERE timeframe = '5 mins' AND tDateTime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(tDateTime), DataType ORDER BY DATE(tDateTime), DataType DESC LIMIT 42"
# print('Record summary for Futures Price 5min')
# ShowRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)

# sql = "SELECT DATE(tDateTime), DataType, count(close) FROM `fdata_fut_hist` WHERE timeframe = '10 secs' AND tDateTime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY DATE(tDateTime), DataType ORDER BY DATE(tDateTime), DataType DESC LIMIT 42"
# print('Record summary for Futures Price 10sec')
# ShowRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)