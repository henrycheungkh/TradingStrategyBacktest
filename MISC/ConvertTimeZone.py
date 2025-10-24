# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 19:11:33 2021

@author: Henry Cheung
"""


import pymysql
import mysql.connector

import InvestmentAnalytics.Config as Config
import pandas as pd
pd.set_option('max_columns', None)

dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, 'finance_fdata_fut_hist_kirk')
mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database= 'finance_fdata_fut_hist_kirk')

# sql = "SELECT * FROM fin_fut_1min where ticker = 'NQ' AND tDateTime BETWEEN '" + self.StartDate.strftime("%Y-%m-%d") + " 00:00:00' AND '" + self.EndDate.strftime("%Y-%m-%d") + " 23:59:59' AND timeframe = '" + self.TimeFrame + "'" + DataTypeFilter
# sql = "SELECT * FROM fin_fut_1min where ticker = 'NQ' AND tDateTime BETWEEN '2021-03-01 00:00:00' AND '2021-03-15 23:59:59' AND timeframe = '1 min'"
# sql = "SELECT * FROM fin_fut_1min where ticker = 'NQ'  AND timeframe = '1min' AND tDateTime > '2021-03-01'"
# sql = "SELECT * FROM fin_fut_1min where ticker = 'NQ'  AND timeframe = '1min'"
sql = "SELECT * FROM fin_fut_1min where ticker in ('NQ', 'ES', 'RTY', 'YM', 'ZN', 'ZT', 'CL', 'HG', 'GC', 'SI')  AND timeframe = '1min' AND tDateTime > '2019-01-01'"
# sql = "SELECT * FROM fin_fut_1min where ticker = 'ES'  AND timeframe = '1min'"
df = pd.read_sql_query(sql, dbcon)

# df['LocalDateTime'] = pd.to_datetime(df['tDateTime']).dt.tz_localize('Asia/Singapore')
# df['LocalDateTime'] = pd.to_datetime(df['tDateTime']).dt.tz_localize('Asia/Tokyo')
df['LocalDateTime'] = pd.to_datetime(df['tDateTime']).dt.tz_localize('Etc/GMT-7')

df['USDateTime'] = df.apply(lambda x: x['LocalDateTime'].tz_convert('US/Central'), axis = 1)

# df = df.loc[df['vol'] > 5000]

print(df)

for index, row in df.iterrows():
    sql = "INSERT IGNORE INTO fdata_fut_hist (ticker, instrumenttype, expiry, DataType, timeframe, tDateTime, high, low, open, close, vol, src) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (row['ticker'], 'FUT', row['expiry'], 'TRADES', '1 min', row['USDateTime'], row['high'], row['low'], row['open'], row['close'], row['vol'], 'IB,hist')
    mycursor = mydb.cursor()
    mycursor.execute(sql, val)
    mydb.commit()

print('upload done')

