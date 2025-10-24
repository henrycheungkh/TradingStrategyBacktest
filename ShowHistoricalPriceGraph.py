# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 22:41:17 2023

@author: henry
"""

import pandas as pd
import mplfinance as mpf
import numpy as np
from datetime import date, datetime, timedelta
import InvestmentAnalytics.DBUtil as DBUtil

import logging
logging.disable(logging.INFO)

pd.set_option('display.max_columns', None)

import pytz

StartDateString = '2021-11-26'
EndDateString = '2021-11-26'

TimeFrame = "10 secs"
# TimeFrame = "1 min"

tickerfilter = "ticker = 'RTY'"

# table_name = "`fdata_fut_hist`"
# db_name = "finance_fdata_fut_hist"


if TimeFrame == "1 min":
    DB_and_table_pair_list = [
       {"database": "finance_fdata_fut_hist", "table": "`fdata_fut_hist`"}
      # {"database": "finance_fdata_fut_hist_temp", "table": "`fdata_fut_hist`"}
    ]  
elif TimeFrame == "10 secs":                  

    DB_and_table_pair_list = [
      # {"database": "finance_fdata_fut_hist", "table": "`fdata_fut_hist`"},
      {"database": "finance_fdata_fut_hist_10secs_2021", "table": "`fdata_fut_hist`"},
      #  {"database": "finance_fdata_fut_hist_10secs_2022_h1", "table": "`fdata_fut_hist`"},
      # {"database": "finance_fdata_fut_hist_10secs_2022_h2", "table": "`fdata_fut_hist`"}
      {"database": "finance_fdata_fut_hist_10secs_2022", "table": "`fdata_fut_hist`"}
    ]                     


df_Price = None

for DB_and_table_pair in DB_and_table_pair_list:

    table_name = DB_and_table_pair['table']
    db_name = DB_and_table_pair['database']
    print('db_name is ' + db_name)
    
    

    # sql_filter_string = tickerfilter + " and timeframe = '" + TimeFrame + "' and `DataType` = 'TRADES' and DATE(tDateTime) in ('2021-01-13','2021-02-10','2021-03-10','2021-04-13','2021-05-12','2021-06-10','2021-07-13','2021-08-11','2021-09-14','2021-10-13','2021-11-10','2021-12-10','2022-01-12','2022-02-10','2022-03-10','2022-04-12','2022-05-11','2022-06-10','2022-07-13','2022-08-10','2022-09-13','2022-10-13','2022-11-10','2022-12-13','2023-01-12','2023-02-14')"
    # sql_filter_string = tickerfilter + " and timeframe = '" + TimeFrame + "' and `DataType` = 'TRADES' and DATE(tDateTime) in (" + DateList + ")"
    sql_filter_string = tickerfilter + " and timeframe = '" + TimeFrame + "' and `DataType` = 'TRADES' and DATE(tDateTime) >= '" + StartDateString + "' and DATE(tDateTime) <= '" + EndDateString + "'"

    # sql = "SELECT * FROM " + table_name + " WHERE " + sql_filter_string 
    # df_Price_full = pd.read_sql(sql,con=DBUtil.GetSQLAlchemyEngine(DatabaseName=db_name))
    # df_Price_full.to_csv(r'E:\temp\price_data_full.csv', index=False)

    
    full_sql = "SELECT BBB.* FROM (SELECT BB.* FROM (SELECT ticker, TradeDate, max(Volume) as MaxVol from (SELECT ticker, DATE(tDateTime) as TradeDate, expiry, sum(vol) as Volume FROM " + table_name + " WHERE " + sql_filter_string + " GROUP BY ticker, DATE(tDateTime), expiry) as A GROUP BY ticker, TradeDate) as AA INNER JOIN (SELECT ticker, DATE(tDateTime) as TradeDate, expiry, sum(vol) as Volume FROM " + table_name + " WHERE " + sql_filter_string + " GROUP BY ticker, DATE(tDateTime), expiry) as BB WHERE AA.ticker = BB.ticker AND AA.TradeDate = BB.TradeDate AND AA.MaxVol = BB.Volume) AAA INNER JOIN (SELECT * FROM " + table_name + " WHERE " + sql_filter_string + ") BBB ON AAA.ticker = BBB.ticker AND AAA.TradeDate = DATE(BBB.tDateTime) AND AAA.expiry = BBB.expiry"
    
    # print('full_sql is')
    # print(full_sql)
    df_Price_temp = pd.read_sql(full_sql,con=DBUtil.GetSQLAlchemyEngine(DatabaseName=db_name))
    if (len(df_Price_temp) > 0):
        print('df_Price_temp is with len ' + str(len(df_Price_temp)))
        print(df_Price_temp.dtypes)
        if df_Price is None:
            df_Price = df_Price_temp
        else:
            df_Price = pd.concat([df_Price, df_Price_temp])

print('df_Price is with len ' + str(len(df_Price)))
# print(df_Price)
# print(df_Price.dtypes)

# Load data
# data = pd.read_csv('stock_data.csv', index_col='Date', parse_dates=True)
data = df_Price[['tDateTime', 'high', 'low', 'open', 'close', 'vol']]

data = data.rename(columns={"tDateTime": "dates", "vol": "volume"})
data.index = pd.DatetimeIndex(data['dates'])

print(data)
print(data.dtypes)

# data.to_csv(r'E:\temp\price_data.csv', index=False)

# # Create a new column for the average price
# data['Avg'] = (data['Open'] + data['High'] + data['Low'] + data['Close']) / 4

# Plot the candlestick chart with volume
mpf.plot(data, type='candle', style='charles', volume=True, ylabel='Price')
