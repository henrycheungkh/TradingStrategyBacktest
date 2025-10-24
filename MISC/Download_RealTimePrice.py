# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 11:13:13 2021

@author: Henry Cheung
"""


import pymysql
import pandas as pd
import yfinance as yf
import Config
import os
import numpy as np

from datetime import date, datetime, timedelta

pd.set_option('display.max_columns', None)
TickerPerBatch = 800

DailyGapThreshold = 0.1
PriceRange = [1, 10]
# MaximumVolumeInShare = {"XUSA": 10000000, "XLON": 10000000, "XHKG": 10000000}
MaximumVolumeInShare = {"XUSA": 10000000}

market = "XUSA"
# market = "XLON"
# market = "XHKG"
StartTime = datetime.now()
print("now =", StartTime)

# today = date.today()- timedelta(days=3)
today = date.today()
StartDay = today.strftime("%Y-%m-%d")
EndDay = (today + timedelta(days=1)).strftime("%Y-%m-%d")
TodayMinus70 = (today - timedelta(days=70)).strftime("%Y-%m-%d")
print(StartDay)
print(EndDay)

dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
Tickers_df = pd.read_sql_query("select * from fdata_tickers where Market = '" + market + "'", dbcon)
tickers = Tickers_df['Ticker'].tolist()

tickers = ['CRHM', 'AEZS', 'BSQR']
Tickers_df = pd.DataFrame (tickers,columns=['Ticker'])

i = 0
TickersBatch = Tickers_df.loc[i:i+TickerPerBatch-1]
full_hot_stock_list = None
while len(TickersBatch) > 0:
    TickersBatchList = TickersBatch['Ticker'].tolist()

    data = yf.download(' '.join(TickersBatchList), start=StartDay, end=EndDay, interval = "1m")
    if (len(data) <= 0):
        print("Intraday data not yet available")
    else:
        data[('Datetime', '')] = data.index
        cols = data.columns.tolist()
        cols.remove(('Datetime', ''))
        data = pd.melt(data, id_vars=[('Datetime', '')], value_vars=cols).rename(columns={'variable_0':'ValueDefinition','variable_1':'ticker',('Datetime', ''):'Datetime'})
        data.dropna(subset = ["value"], inplace=True)
        data = pd.pivot_table(data, index=['ticker', 'Datetime'], columns=['ValueDefinition'], values='value').reset_index()
        accumulatedvolume_data = pd.pivot_table(data, index=['ticker'], values='Volume', aggfunc=np.sum).reset_index()
        accumulatedvolume_data = accumulatedvolume_data.rename(columns = {'Volume':'Volume_Accumulated'})
        # accumulatedvolume_data.to_csv(r'd:\temp\accumulatedvolume_data.csv')
        latest_time = pd.pivot_table(data, index=['ticker'], values='Datetime', aggfunc=np.max).reset_index()
        latest_price = data.merge(latest_time, on=['ticker', 'Datetime'])
        latest_price = latest_price.merge(accumulatedvolume_data, on=['ticker'])
                
        recentclose_data = yf.download(' '.join(TickersBatchList), start=TodayMinus70, end=StartDay, interval = "1d")
        recentclose_data[('Datetime', '')] = recentclose_data.index
        cols = recentclose_data.columns.tolist()
        cols.remove(('Datetime', ''))
        recentclose_data = pd.melt(recentclose_data, id_vars=[('Datetime', '')], value_vars=cols).rename(columns={'variable_0':'ValueDefinition','variable_1':'ticker',('Datetime', ''):'Datetime'})
        recentclose_data.dropna(subset = ["value"], inplace=True)
        recentclose_data = pd.pivot_table(recentclose_data, index=['ticker', 'Datetime'], columns=['ValueDefinition'], values='value').reset_index()
        recentvolume_data = pd.pivot_table(recentclose_data, index=['ticker'], values='Volume', aggfunc=np.mean).reset_index().rename(columns = {'Volume':'Volume_50MA'})
        latest_closedate = pd.pivot_table(recentclose_data, index=['ticker'], values='Datetime', aggfunc=np.max).reset_index()
        latestclose_data = recentclose_data.merge(latest_closedate, on=['ticker', 'Datetime'])
        latestclose_data = latestclose_data[['ticker', 'Datetime', 'Adj Close', 'Volume']]
        latestclose_data = latestclose_data.rename(columns = {'Datetime':'Prior_Datetime', 'Adj Close':'Prior_Adj Close', 'Volume':'Prior_Volume'})
        latestclose_data = latestclose_data.merge(recentvolume_data, on=['ticker'])
        
        hot_stock_list = latest_price.merge(latestclose_data, on='ticker')
        hot_stock_list['Gap'] = (hot_stock_list['Adj Close'] - hot_stock_list['Prior_Adj Close']) / hot_stock_list['Prior_Adj Close']
        
        # hot_stock_list.to_csv(r'd:\temp\hot_stock_list_beforescreening.csv')
        hot_stock_list = hot_stock_list.loc[hot_stock_list['Gap'] > DailyGapThreshold]
        # hot_stock_list.to_csv(r'd:\temp\hot_stock_list_afterscreening.csv')
        
        if full_hot_stock_list is None:
            full_hot_stock_list = hot_stock_list.copy()
        else:
            full_hot_stock_list.append(hot_stock_list, ignore_index=True)
        
        # print(hot_stock_list)

    i = i + TickerPerBatch
    TickersBatch = Tickers_df.loc[i:i+TickerPerBatch-1]

print(full_hot_stock_list)
full_hot_stock_list.to_csv(r'd:\temp\full_hot_stock_list.csv')
print("start time =", StartTime)
print("end time =", datetime.now())
