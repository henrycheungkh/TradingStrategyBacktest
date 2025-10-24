# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 13:11:08 2021

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

DailyGapThreshold = 0.1

market = "XUSA"
# market = "XLON"


today = date.today()
StartDay = (today).strftime("%Y-%m-%d")
EndDay = (today + timedelta(days=1)).strftime("%Y-%m-%d")
TodayMinus70 = (today - timedelta(days=70)).strftime("%Y-%m-%d")
print(StartDay)
print(EndDay)

dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
Tickers_df = pd.read_sql_query("select * from fdata_tickers where Market = '" + market + "'", dbcon)
tickers = Tickers_df['Ticker'].tolist()

tickers = ['AAPL', 'MSFT']

data = yf.download(' '.join(tickers), start=StartDay, end=EndDay, interval = "1m")
if (len(data) <= 0):
    print("Intraday data not yet available")
else:
    data[('Datetime', '')] = data.index
    cols = data.columns.tolist()
    cols.remove(('Datetime', ''))
    data = pd.melt(data, id_vars=[('Datetime', '')], value_vars=cols).rename(columns={'variable_0':'ValueDefinition','variable_1':'ticker',('Datetime', ''):'Datetime'})
    data.dropna(subset = ["value"], inplace=True)
    data = pd.pivot_table(data, index=['ticker', 'Datetime'], columns=['ValueDefinition'], values='value').reset_index()
    accumulatedvolume_data = pd.pivot_table(data, index=['ticker'], values='Volume', aggfunc=np.sum).reset_index().rename(columns = {'Volume':'Volume_Accumulated'})
    print('accumulatedvolume_data')
    print(accumulatedvolume_data)
    latest_time = pd.pivot_table(data, index=['ticker'], values='Datetime', aggfunc=np.max).reset_index()
    latest_price = data.merge(latest_time, on=['ticker', 'Datetime'])
    print('latest_price at point A')
    print(latest_price)
    latest_price = latest_price.merge(accumulatedvolume_data, on=['ticker'])
    print('latest_price at point B')
    print(latest_price)