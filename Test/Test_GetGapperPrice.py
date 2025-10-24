# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 15:39:10 2021

@author: Henry Cheung
"""
import Config
import pymysql
import pandas as pd
import numpy as np



DateString = "2021-04-28"
dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
sql = "SELECT * FROM fdata_us_gapper_premarket_price WHERE CaptureDatetime BETWEEN '" + DateString + " 00:00:00' AND '" + DateString + " 23:59:59'"

GapperPrices = pd.read_sql_query(sql, dbcon)

if (len(GapperPrices) > 0):

    GapperPrices = GapperPrices.set_index(['CaptureDatetime'])
    
    GapperPricesTickers = GapperPrices[['Ticker']].drop_duplicates()
    # print(GapperPricesTickers)
    
    GapperPricesOHLC = pd.DataFrame(columns=['Ticker', 'CaptureDatetime', 'open', 'high', 'low', 'close', 'close_vol_5min'])
    
    for index, row in GapperPricesTickers.iterrows():
        GapperPricesForOneTicker = GapperPrices.loc[GapperPrices['Ticker'] == row['Ticker']]
        GapperPricesForOneTicker = GapperPricesForOneTicker['Price'].resample('1Min').ohlc().reset_index().dropna()
        GapperPricesForOneTicker['Ticker'] = row['Ticker']
        GapperPricesForOneTicker['close_vol_5min'] = GapperPricesForOneTicker['close'].rolling(5).std()
        GapperPricesOHLC = GapperPricesOHLC.append(GapperPricesForOneTicker, ignore_index=True)
            
    GapperPricesOHLC = GapperPricesOHLC.dropna()
    
    print(GapperPricesOHLC)
    
    TickerMaxDatetime = pd.pivot_table(GapperPricesOHLC, values='CaptureDatetime', index='Ticker', aggfunc=np.max, fill_value=0).reset_index()
    
    print(TickerMaxDatetime)
    
    GapperPricesLatestSD = GapperPricesOHLC.merge(TickerMaxDatetime, on=['Ticker','CaptureDatetime'] )
    
    print(GapperPricesLatestSD)
    
    # GapperPricesOHLC.to_csv(r'd:\temp\OHLC.csv')