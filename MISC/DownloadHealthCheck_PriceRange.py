# -*- coding: utf-8 -*-
"""
Created on Sat Aug 14 01:23:58 2021

@author: Henry Cheung
"""


import pymysql
import sys
import InvestmentAnalytics.Config as Config
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

today = date.today()
PriorMonthDate = today - timedelta(days=30)

def GetRecentData(sql, DatabaseName = Config.CONFIG_MYSQL_CONNECTION_DATABASE):
    if DatabaseName is None:
        dbconnect = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD)
    else:
        dbconnect = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, DatabaseName)
    # sql = "SELECT COUNT(*) AS RecordCount FROM `" + DBTableName + "`"
    # print(pd.read_sql_query(sql, dbconnect))
    return pd.read_sql_query(sql, dbconnect)

print(today)
print(PriorMonthDate)

if len(sys.argv) > 1:
    HealthCheckSection = sys.argv[1]
else:
    HealthCheckSection = 'All'


    

if (HealthCheckSection == 'All') or (HealthCheckSection == 'IBFuturesPrice'):
    
    print('Record summary for Futures Price')
    # sql = "SELECT ticker, timeframe, max(tDateTime) FROM `fdata_fut_hist` GROUP BY ticker, timeframe ORDER BY max(tDateTime)"
    # print(GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST))

    # sql = "SELECT timeframe, DATE(tDateTime) AS ValueDate, DataType, count(close) AS RecordCount FROM `fdata_fut_hist` WHERE tDateTime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY timeframe, DATE(tDateTime), DataType ORDER BY timeframe, DataType, DATE(tDateTime) DESC"
    # df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)
    # df = pd.pivot_table(df, index=['ValueDate'],columns=['timeframe', 'DataType'], values='RecordCount', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
    # df.set_index('ValueDate', inplace=True)
    # print(df)

    sql = "SELECT ticker, timeframe, DATE(tDateTime) as ValueDate, DataType, max(close) as Max_Close FROM fdata_fut_hist WHERE timeframe = '1 min' and tDateTime > '" + PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY ticker, timeframe, DATE(tDateTime), DataType ORDER BY ticker, DATE(tDateTime) DESC"
    df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)
    df = pd.pivot_table(df, index=['timeframe', 'ValueDate'],columns=['DataType', 'ticker'], values='Max_Close', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
    df.set_index(['timeframe','ValueDate'], inplace=True)
    print(df)

    sql = "SELECT ticker, timeframe, DATE(tDateTime) as ValueDate, DataType, min(close) as Min_Close FROM fdata_fut_hist WHERE timeframe = '1 min' and tDateTime > '" + PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY ticker, timeframe, DATE(tDateTime), DataType ORDER BY ticker, DATE(tDateTime) DESC"
    df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)
    df = pd.pivot_table(df, index=['timeframe', 'ValueDate'],columns=['DataType', 'ticker'], values='Min_Close', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
    df.set_index(['timeframe','ValueDate'], inplace=True)
    print(df)


    sql = "SELECT ticker, timeframe, DATE(tDateTime) as ValueDate, DataType, max(close) as Max_Close FROM fdata_fut_hist WHERE timeframe = '10 secs' and tDateTime > '" + PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY ticker, timeframe, DATE(tDateTime), DataType ORDER BY ticker, DATE(tDateTime) DESC"
    df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)
    df = pd.pivot_table(df, index=['timeframe', 'ValueDate'],columns=['DataType', 'ticker'], values='Max_Close', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
    df.set_index(['timeframe','ValueDate'], inplace=True)
    print(df)

    sql = "SELECT ticker, timeframe, DATE(tDateTime) as ValueDate, DataType, min(close) as Min_Close FROM fdata_fut_hist WHERE timeframe = '10 secs' and tDateTime > '" + PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY ticker, timeframe, DATE(tDateTime), DataType ORDER BY ticker, DATE(tDateTime) DESC"
    df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)
    df = pd.pivot_table(df, index=['timeframe', 'ValueDate'],columns=['DataType', 'ticker'], values='Min_Close', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
    df.set_index(['timeframe','ValueDate'], inplace=True)
    print(df)


    sql = "SELECT ticker, timeframe, DATE(tDateTime) as ValueDate, DataType, max(close) as Max_Close FROM fdata_fut_hist WHERE timeframe = '5 mins' and tDateTime > '" + PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY ticker, timeframe, DATE(tDateTime), DataType ORDER BY ticker, DATE(tDateTime) DESC"
    df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)
    df = pd.pivot_table(df, index=['timeframe', 'ValueDate'],columns=['DataType', 'ticker'], values='Max_Close', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
    df.set_index(['timeframe','ValueDate'], inplace=True)
    print(df)
    
    sql = "SELECT ticker, timeframe, DATE(tDateTime) as ValueDate, DataType, min(close) as Min_Close FROM fdata_fut_hist WHERE timeframe = '5 mins' and tDateTime > '" + PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY ticker, timeframe, DATE(tDateTime), DataType ORDER BY ticker, DATE(tDateTime) DESC"
    df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)
    df = pd.pivot_table(df, index=['timeframe', 'ValueDate'],columns=['DataType', 'ticker'], values='Min_Close', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
    df.set_index(['timeframe','ValueDate'], inplace=True)
    print(df)
    

if (HealthCheckSection == 'IBFuturesPriceByTicker'):

    sql = "SELECT ticker, timeframe, DATE(tDateTime) AS ValueDate, DataType, count(close) AS RecordCount FROM `fdata_fut_hist` WHERE tDateTime > '"+ PriorMonthDate.strftime("%Y-%m-%d") + "' GROUP BY ticker, timeframe, DATE(tDateTime), DataType ORDER BY ticker, timeframe, DataType, DATE(tDateTime) DESC"
    print('Record summary for Futures Price')
    df = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)
    df = pd.pivot_table(df, index=['ticker', 'ValueDate'],columns=['timeframe', 'DataType'], values='RecordCount', aggfunc=np.mean).reset_index().sort_values(by=['ticker', 'ValueDate'], ascending=False)
    df.set_index(['ticker','ValueDate'], inplace=True)
    print(df)

