# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 02:01:18 2021

@author: Henry Cheung
"""


import pymysql
import pandas as pd
import yfinance as yf
from yfinance.exceptions import YFRateLimitError
import InvestmentAnalytics.Config as Config
import os
from InvestmentAnalytics.DBUtil import AppendDBExportScript

from datetime import date, datetime, timedelta
import time

from curl_cffi import requests
session = requests.Session(impersonate="chrome")


def WriteDBExportScript(DatafilePath, filepath, StartDate, EndDate, DBTableSuffix):
    AppendDBExportScript(DatafilePath, filepath + StartDate + "_" + EndDate + ".csv", "fdata_price_" + DBTableSuffix)

def DownloadFinanceData(StartDate, EndDate, tickers, time_interval, datastore, filepath, DatafilePath, DBTableSuffix, reformat=True):
    # print('In DownloadFinanceData')
    Success = True
    try:
        # data = yf.download(' '.join(tickers), start=StartDate, end=EndDate, interval = time_interval)
        # data = yf.download(' '.join(tickers), start=StartDate, end=EndDate, interval = time_interval, session=session)
        data = yf.download(' '.join(tickers), start=StartDate, end=EndDate, interval = time_interval, session=session, period="1mo")
        if reformat:
            data[('Datetime', '')] = data.index
            cols = data.columns.tolist()
            cols.remove(('Datetime', ''))
            try:
                data = pd.melt(data, id_vars=[('Datetime', '')], value_vars=cols).rename(columns={'variable_0':'ValueDefinition','variable_1':'ticker',('Datetime', ''):'Datetime'})
                data.dropna(subset = ["value"], inplace=True)
                print('Before pivot table, data is')
                print(data)
            # try:
                # data = pd.pivot_table(data, index=['ticker', 'Datetime'], columns=['ValueDefinition'], values='value', fill_value=0)
                data = pd.pivot_table(data, index=['Ticker', 'Datetime'], columns=['Price'], values='value', fill_value=0)
                data.rename(columns={"Ticker": "ticker"}, inplace=True)
                print('After pivot table, data is')
                print(data)
            except Exception as e:
                print(e)
                # data.to_csv(r'd:\temp\data.csv', index=False)
                return None
        # print(data)
        #print(data.columns.tolist())
            
        if len(data) <= 0:
            print('No Data returned')
            
            try:
                ticker = yf.Ticker('AAPL', session=session)
                data = ticker.history(period="1d")
                print(data)
            except YFRateLimitError:
                print('YFRateLimitError - wait for 10 minutes')
                time.sleep(10*60)
                DownloadFinanceData(StartDate, EndDate, tickers, time_interval, datastore, filepath, DatafilePath, DBTableSuffix, reformat=reformat)
                Success = False
                # return False          
            
            # return False

    except YFRateLimitError as e:
        print('YFRateLimitError')
        # return False

    if Success:
        if (datastore == 'csv'): 
            try:
                data.reset_index(inplace=True)
                # print(data)
                # data['Datetime'] = data['Datetime'].replace(tzinfo=None)
                data['Datetime'] = data.apply(lambda x: x['Datetime'].replace(tzinfo=None), axis = 1)   #
                data.to_csv(filepath + StartDate + '_' + EndDate + '.csv', index = False)
                # WriteDBExportScript(DatafilePath, time_interval, filepath, StartDate, EndDate, DBTableSuffix)
                # WriteDBExportScript(DatafilePath, "all", filepath, StartDate, EndDate, DBTableSuffix)
                WriteDBExportScript(DatafilePath, filepath, StartDate, EndDate, DBTableSuffix)
            except Exception as e:
                print(e)
    
        elif (datastore == 'mysql'): 
            db = mysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
            print(db)
        return True

def DownloadFinanceDataByBatch(Tickers, TickerPerBatch, StartDate, EndDate, download_interval, DatafileFullPath, DatafilePath, DBTableSuffix ):
  # print('In DownloadFinanceDataByBatch')
  # print('Tickers is')
  # print(Tickers)
  i = 0
  TickersBatch = Tickers.loc[i:i+TickerPerBatch-1]
  # print('In DownloadFinanceDataByBatch, i = ' + str(i))
  # print('TickersBatch is ')
  # print(TickersBatch)
  j = 1
  Download_Success = True
  while len(TickersBatch) > 0 and Download_Success:
      # print('In DownloadFinanceDataByBatch, i = ' + str(i))
      TickersBatchList = TickersBatch['Ticker'].tolist()
      Download_Success = DownloadFinanceData(StartDate, EndDate, TickersBatchList, download_interval, 'csv', DatafileFullPath + '_' + str(j)+ '_', DatafilePath, DBTableSuffix )
      i = i + TickerPerBatch
      j = j + 1
      TickersBatch = Tickers.loc[i:i+TickerPerBatch-1]
      # print('Wait for 10 seconds')
      # time.sleep(10)
      # time.sleep(60)

