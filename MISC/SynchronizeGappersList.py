# -*- coding: utf-8 -*-
"""
Created on Sun Jul 18 22:23:39 2021

@author: Henry Cheung
"""


import Config
import os
import sys
import pymysql
import mysql.connector
from datetime import datetime, date
import time
from pytz import timezone
import pandas as pd
import numpy as np
import requests
import math

pd.set_option('display.max_columns', None)

# https://stockfry.000webhostapp.com/gapper_update.php?CaptureDate=20210718&Ticker1=AAPL&Sector1=NA&Industry1=NA&PriorDayClose1=200&CurrentPrice1=0&MA30Vol1=10000&TodayVol1=25000&MarketCap1=1200000000&FreeFloat1=240000&BidAskSpread1=0.05&Ticker2=MSFT&Sector2=NA&Industry2=NA&PriorDayClose2=250&CurrentPrice2=0&MA30Vol2=10000&TodayVol2=25000&MarketCap2=1200000000&FreeFloat2=240000&BidAskSpread2=0.05

dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)







# while True:
    
    
Now_time = datetime.now()
Now_string = Now_time.strftime('%Y-%m-%d')
sql = "SELECT * FROM `fdata_us_gapper_list` WHERE CaptureDate = '" + Now_string + "'"
# print(sql)
GapperList = pd.read_sql_query(sql, dbcon)
# print(GapperList)

URL = "https://stockfry.000webhostapp.com/gapper_update.php"

TotalTickerBatchCount = math.ceil(len(GapperList) / 20)
for i in range(TotalTickerBatchCount):
    TickersBatch = GapperList.loc[i*20:(i+1)*20-1]
    print(TickersBatch)
    
    if i == 0:
        PARAMS = { 'Delete':'Yes', 'CaptureDate':Now_time.strftime('%Y%m%d')}
    else:
        PARAMS = { 'Delete':'No', 'CaptureDate':Now_time.strftime('%Y%m%d')}
    
    for index, row in TickersBatch.iterrows():
        PARAMS['Ticker' + str(index+1)] = row['ticker']
        PARAMS['Sector' + str(index+1)] = row['Sector']
        PARAMS['Industry' + str(index+1)] = row['Industry']
        PARAMS['PriorDayClose' + str(index+1)] = row['PriorDayClose']
        PARAMS['CurrentPrice' + str(index+1)] = row['CurrentPrice']
        PARAMS['MA30Vol' + str(index+1)] = row['30MA_Vol']
        PARAMS['TodayVol' + str(index+1)] = row['Today_Vol']
        PARAMS['MarketCap' + str(index+1)] = row['MarketCap']
        PARAMS['FreeFloat' + str(index+1)] = row['FreeFloat']
        PARAMS['BidAskSpread' + str(index+1)] = row['BidAskSpread']
    
    r = requests.get(url = URL, params = PARAMS)
    print(r.status_code)
print(str(len(GapperList)) + ' gappers synchronised to website, with status code ' + str(r.status_code))
time.sleep(10)   


    
    
    # Now_time = datetime.now()
    # Now_string = Now_time.strftime('%Y-%m-%d')
    
    
    # sql = "SELECT * FROM `fdata_us_gapper_list` WHERE CaptureDate = '" + Now_string + "'"
    # print(sql)
    
    # GapperList = pd.read_sql_query(sql, dbcon)
    # # GapperList = GapperList.head(2)
    # print(GapperList)
    
    # # api-endpoint
    # URL = "https://stockfry.000webhostapp.com/gapper_update.php"
      
    # # defining a params dict for the parameters to be sent to the API
    # PARAMS = {'CaptureDate':Now_time.strftime('%Y%m%d')}
    
    # for index, row in GapperList.iterrows():
    #     # print(str(index+1))
    #     # print('Ticker' + str(index+1) + ":" + str(row['ticker']))
    #     # print('Sector' + str(index+1) + ":" + str(row['Sector']))
    #     # print('Industry' + str(index+1) + ":" + str(row['Industry']))
    #     # print('PriorDayClose' + str(index+1) + ":" + str(row['PriorDayClose']))
    #     # print('CurrentPrice' + str(index+1) + ":" + str(row['CurrentPrice']))
    #     # print('MA30Vol' + str(index+1) + ":" + str(row['30MA_Vol']))
    #     # print('TodayVol' + str(index+1) + ":" + str(row['Today_Vol']))
    #     # print('MarketCap' + str(index+1) + ":" + str(row['MarketCap']))
    #     # print('FreeFloat' + str(index+1) + ":" + str(row['FreeFloat']))
    #     # print('BidAskSpread' + str(index+1) + ":" + str(row['BidAskSpread']))
    #     PARAMS['Ticker' + str(index+1)] = row['ticker']
    #     PARAMS['Sector' + str(index+1)] = row['Sector']
    #     PARAMS['Industry' + str(index+1)] = row['Industry']
    #     PARAMS['PriorDayClose' + str(index+1)] = row['PriorDayClose']
    #     PARAMS['CurrentPrice' + str(index+1)] = row['CurrentPrice']
    #     PARAMS['MA30Vol' + str(index+1)] = row['30MA_Vol']
    #     PARAMS['TodayVol' + str(index+1)] = row['Today_Vol']
    #     PARAMS['MarketCap' + str(index+1)] = row['MarketCap']
    #     PARAMS['FreeFloat' + str(index+1)] = row['FreeFloat']
    #     PARAMS['BidAskSpread' + str(index+1)] = row['BidAskSpread']
    
        
    # # sending get request and saving the response as response object
    # r = requests.get(url = URL, params = PARAMS)
    
    # print()
    # print(r.status_code)
    
    # time.sleep(10)
