# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 16:00:36 2023

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

# from InvestmentAnalytics.MarketDataReader import IBFuturesPriceReader, FuturesPriceAnalysisContext, FXFuturesPriceAnalysisContext, CryptoPriceAnalysisContext

import pytz


TimeFrame = "10 secs"
# TimeFrame = "1 min"

table_name = "`fdata_fut_hist`"
db_name = "finance_fdata_fut_hist"


if TimeFrame == "1 min":
    DB_and_table_pair_list = [
      {"database": "finance_fdata_fut_hist", "table": "`fdata_fut_hist`"}
    ]  
elif TimeFrame == "10 secs":                  

    DB_and_table_pair_list = [
      {"database": "finance_fdata_fut_hist", "table": "`fdata_fut_hist`"},
      {"database": "finance_fdata_fut_hist_10secs_2021", "table": "`fdata_fut_hist`"},
      {"database": "finance_fdata_fut_hist_10secs_2022_h1", "table": "`fdata_fut_hist`"},
      {"database": "finance_fdata_fut_hist_10secs_2022_h2", "table": "`fdata_fut_hist`"}
    ]                     

tickerfilter = "ticker = 'ES'"

MacroDataFilePath = r'C:\PythonProjects\TradeAnalysis\Macro Data\US Inflation 2021-2023.csv'

df_MacroData = pd.read_csv(MacroDataFilePath, index_col=False, encoding= 'unicode_escape')

# df_MacroData['Local Time'] = pd.to_datetime(df_MacroData['Time']).dt.tz_localize('Europe/London')
df_MacroData['Local Time'] = pd.to_datetime(df_MacroData['Time']).dt.tz_localize('UTC')
df_MacroData['NY Time'] = df_MacroData.apply(lambda x: x['Local Time'].astimezone('America/New_York').replace(tzinfo=None), axis = 1) 

df_MacroData['MONTH'] = df_MacroData['Indicator'].str[-3:]
df_MacroData['Indicator'] = df_MacroData['Indicator'].str[:-4]

df_MacroData['ComparisonBasis'] = df_MacroData['Indicator'].str[-3:]
df_MacroData['Indicator'] = df_MacroData['Indicator'].str[:-4]

df_MacroData_InflationRate_YOY = df_MacroData[(df_MacroData['Indicator'] == 'Inflation Rate') & (df_MacroData['ComparisonBasis'] == 'YoY')]

df_MacroData_InflationRate_YOY['DateString'] = df_MacroData_InflationRate_YOY['NY Time'].dt.strftime('%Y-%m-%d')
df_MacroData_InflationRate_YOY['DateStringInQuote'] = "'" + df_MacroData_InflationRate_YOY['DateString'] + "'"
print(df_MacroData_InflationRate_YOY)


df_MacroData_InflationRate_YOY['Actual'] = pd.to_numeric(df_MacroData_InflationRate_YOY['Actual'].str.rstrip("%").astype(float)/100, errors='coerce')
df_MacroData_InflationRate_YOY['Forecast'] = pd.to_numeric(df_MacroData_InflationRate_YOY['Forecast'].str.rstrip("%").astype(float)/100, errors='coerce')
 
df_MacroData_InflationRate_YOY['Forecast Diff'] = df_MacroData_InflationRate_YOY['Actual'] - df_MacroData_InflationRate_YOY['Forecast']
df_MacroData_InflationRate_YOY['Abs Forecast Diff'] = df_MacroData_InflationRate_YOY['Forecast Diff'].abs()



print(df_MacroData_InflationRate_YOY)

DateList = ','.join(df_MacroData_InflationRate_YOY['DateStringInQuote'])

print(DateList)

# df_MacroData_InflationRate_YOY.to_csv(r'C:\PythonProjects\TradeAnalysis\Macro Data\US Inflation Rate 2021-2023.csv', index=False)

df_Price = None

for DB_and_table_pair in DB_and_table_pair_list:

    table_name = DB_and_table_pair['table']
    db_name = DB_and_table_pair['database']
    print('db_name is ' + db_name)
    

    # sql_filter_string = tickerfilter + " and timeframe = '" + TimeFrame + "' and `DataType` = 'TRADES' and DATE(tDateTime) in ('2021-01-13','2021-02-10','2021-03-10','2021-04-13','2021-05-12','2021-06-10','2021-07-13','2021-08-11','2021-09-14','2021-10-13','2021-11-10','2021-12-10','2022-01-12','2022-02-10','2022-03-10','2022-04-12','2022-05-11','2022-06-10','2022-07-13','2022-08-10','2022-09-13','2022-10-13','2022-11-10','2022-12-13','2023-01-12','2023-02-14')"
    sql_filter_string = tickerfilter + " and timeframe = '" + TimeFrame + "' and `DataType` = 'TRADES' and DATE(tDateTime) in (" + DateList + ")"
    
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
print(df_Price)
print(df_Price.dtypes)

df_Price['TradeTimeMinute'] = df_Price['tDateTime'].dt.minute
df_Price['TradeTimeHour'] = df_Price['tDateTime'].dt.hour
df_Price['DateString'] = df_Price['tDateTime'].dt.strftime('%Y-%m-%d')

print('df_Price is with len ' + str(len(df_Price)))
print(df_Price)

df_Price = df_Price.merge(df_MacroData_InflationRate_YOY, on=['DateString'], how='left')

if TimeFrame == "1 min":
    df_Price['absTimeDiffVsIndicatorTime'] = abs((df_Price['tDateTime'] - df_Price['NY Time']) / pd.Timedelta(minutes=1))
elif TimeFrame == "10 secs":
    df_Price['absTimeDiffVsIndicatorTime'] = abs((df_Price['tDateTime'] - df_Price['NY Time']) / pd.Timedelta(seconds=1))

df_Price = df_Price[df_Price['absTimeDiffVsIndicatorTime'] <= 60]

df_Price.to_csv(r'c:\temp\df_Price' + TimeFrame + '.csv', index=False)

print('df_Price with time diff is with len ' + str(len(df_Price)))
print(df_Price)

df_Price_at_announcement = df_Price[df_Price['absTimeDiffVsIndicatorTime'] <= 2][['tDateTime', 'high', 'low', 'open', 'close', 'vol', 'Actual', 'Forecast', 'Consensus']]

print('df_Price_at_announcement with time diff is with len ' + str(len(df_Price)))
print(df_Price_at_announcement.head(30))


# # Load data
# data = pd.read_csv('stock_data.csv', index_col='Date', parse_dates=True)

# # Create a new column for the average price
# data['Avg'] = (data['Open'] + data['High'] + data['Low'] + data['Close']) / 4

# # Plot the candlestick chart with volume
# mpf.plot(data, type='candle', style='charles', volume=True, ylabel='Price')