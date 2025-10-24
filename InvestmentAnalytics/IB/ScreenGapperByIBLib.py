# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 13:50:31 2021

@author: Henry Cheung
"""
import InvestmentAnalytics.Config as Config
import InvestmentAnalytics.DBUtil as DBUtil

import logging
logging.disable(logging.INFO)

import os
import sys
import pandas as pd
import yfinance as yf
import numpy as np


from bs4 import BeautifulSoup
import requests
import logging
import threading
import time
from datetime import datetime, date
from pytz import timezone
import math

from pandas.tseries.offsets import BDay

from InvestmentAnalytics.EmailModule import SendEmail
from InvestmentAnalytics.IB.IBApiProcessHub import RunIBApiProcessHub
from InvestmentAnalytics.IB.IBApiProcessUSStockGapperScanner import *

def SynchroniseWebsiteThread(name, name2):
    logging.info("Thread %s: starting", name)
    SynchroniseWebsite(name)
    logging.info("Thread %s: finishing", name)

def SynchroniseWebsite(name):
    WebsiteSynchMessageIterationCounter = 0
    print('Start synchronizing to the website')
    while True:
        Now_time = datetime.now()
        Now_string = Now_time.strftime('%Y-%m-%d')
        Now_string2 = Now_time.strftime('%Y%m%d')
        sql = "SELECT * FROM `fdata_us_gapper_list` WHERE CaptureDate = '" + Now_string + "'"
        # GapperList = pd.read_sql(sql,con=DBUtil.GetSQLAlchemyEngine(DatabaseName=Config.CONFIG_MYSQL_CONNECTION_DATABASE))
        GapperList = pd.read_sql(sql,con=DBUtil.GetSQLAlchemyEngine())
        
        # print(GapperList)
        
        # URL = "https://stockfry.000webhostapp.com/gapper_update_post.php"
        URL = "https://www.vytrix.com/stockfry/gapper_update_post.php"
        
        PARAMS = { 'CaptureDate':Now_string2}
            
        for index, row in GapperList.iterrows():
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
        
        r = requests.post(URL, data=PARAMS)
        # print(r.status_code, r.reason)
        
        # if WebsiteSynchMessageIterationCounter == 0:
        print(str(len(GapperList)) + ' gappers synchronised to website, with status code ' + str(r.status_code) + ' at ' + str(datetime.now()))
        # WebsiteSynchMessageIterationCounter = WebsiteSynchMessageIterationCounter + 1
        # if WebsiteSynchMessageIterationCounter >= 5:
        #     WebsiteSynchMessageIterationCounter = 0
        time.sleep(60*4)    

def GetScanGapperParameter(market, StockFilter = ""):

    US_time = datetime.now(timezone('America/New_York')) 
    print("US Time now is " + str(US_time))
    US_time_in_minutes = US_time.hour * 60 + US_time.minute
    print("US Time in minutes is " + str(US_time_in_minutes))
    US_time_end_of_next_30mins_bucket = math.ceil(US_time_in_minutes/30)*30
    print("US_time_end_of_next_30mins_bucket is " + str(US_time_end_of_next_30mins_bucket))
    US_time_30days_before = US_time -  timedelta(days=60)
    print("US Time 30 days before is " + str(US_time_30days_before))

    sql = "SELECT DATE(DateTime) As ValueDate FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_30MIN_IB + ".fdata_price_30min_ib WHERE DateTime < '" + US_time.strftime("%Y-%m-%d") + "' AND DateTime >= '" + US_time_30days_before.strftime("%Y-%m-%d") + "' AND DataType = 'TRADES' GROUP BY DATE(DateTime) ORDER BY DATE(DateTime) DESC LIMIT 30"
    print(sql)
    
    # DateList = pd.read_sql_query(sql, dbcon_alldb)
    DateList = pd.read_sql(sql,con=DBUtil.GetSQLAlchemyEngine())
    print('Datelist is')
    print(DateList)
    PriorDate = DateList['ValueDate'].iloc[0]
    PriorDateTMinus1 = DateList['ValueDate'].iloc[1]
    BeginDateOf30Days = DateList['ValueDate'].iloc[29]
    print("PriorDate is " + str(PriorDate) + " and BeginDateOf30Days is " + str(BeginDateOf30Days))
    # print(PriorDate)
    # print(BeginDateOf30Days)
    print(DateList)
    PriorDateString = PriorDate.strftime('%Y-%m-%d')

    BeginDateOf30DaysString = BeginDateOf30Days.strftime("%Y-%m-%d")
    print(BeginDateOf30DaysString)

    sql = "SELECT AAAAA.ticker, AAAAA.ticker as symbol, 'STK' as secType, 'USD' as currency, 'SMART' as exchange, IFNULL(BBBBB.Property, 'NONE') AS primaryExchange, Sector, Industry FROM (SELECT AAAA.*, BBBB.Property As Industry FROM (SELECT AAA.*, BBB.Property AS Sector FROM (SELECT AA.ticker FROM (SELECT ticker FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_30MIN_IB + ".fdata_price_30min_ib  WHERE  DateTime > '" + PriorDateTMinus1.strftime('%Y-%m-%d') + "' " + StockFilter + " GROUP BY ticker) AA LEFT JOIN (SELECT ZB.Ticker, ZB.Value FROM (SELECT Ticker, Max(CaptureDate) AS MAX_CaptureDate FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".fdata_yahoo_fundamental WHERE Name = 'marketCap'  GROUP BY Ticker) ZA INNER JOIN (SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".fdata_yahoo_fundamental WHERE Name = 'marketCap' ) ZB ON ZA.Ticker = ZB.Ticker and ZA.MAX_CaptureDate = ZB.CaptureDate) BB ON AA.ticker = BB.Ticker ) AAA LEFT JOIN (SELECT Ticker, Property FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".fdata_yahoo_property WHERE Property_Type = 'sector') BBB ON AAA.ticker = BBB.Ticker) AAAA LEFT JOIN (SELECT Ticker, Property FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".fdata_yahoo_property WHERE Property_Type = 'industry') BBBB ON AAAA.ticker = BBBB.Ticker) AAAAA LEFT JOIN (SELECT Ticker, Property FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE + ".fdata_tickers_property WHERE Property_Type = 'primaryExchange') BBBBB ON AAAAA.ticker = BBBBB.Ticker"

    print(sql)
    
    Tickers = pd.read_sql(sql,con=DBUtil.GetSQLAlchemyEngine())
    print("Tickers count = " + str(len(Tickers)))
    print(Tickers)

    sql = "SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_30MIN_IB + ".fdata_price_30min_ib WHERE DateTime >= '" + PriorDateTMinus1.strftime("%Y-%m-%d") + "' AND DateTime < '" + US_time.strftime("%Y-%m-%d") + "' " + StockFilter
    print(sql)
    
    # HistoricalPrices = pd.read_sql_query(sql, dbcon_alldb)
    HistoricalPrices = pd.read_sql(sql,con=DBUtil.GetSQLAlchemyEngine())
    HistoricalPrices['Hour'] = pd.to_datetime(HistoricalPrices['DateTime']).dt.hour
    HistoricalPrices['Minute'] = pd.to_datetime(HistoricalPrices['DateTime']).dt.minute
    HistoricalPrices['TimeInStandardUnit'] = HistoricalPrices['Hour'] * 60 + HistoricalPrices['Minute']
    HistoricalPrices['Date'] = pd.to_datetime(HistoricalPrices['DateTime']).dt.date
    print("HistoricalPrices count = " + str(len(HistoricalPrices)))
    print(HistoricalPrices)
    
    HistoricalDates = HistoricalPrices[['Date']].drop_duplicates()
    print('HistoricalDates is')
    print(HistoricalDates)
    PriorDate = HistoricalDates['Date'].max()
    print('PriorDate is')
    print(PriorDate)
    PriorDateTMinus1 = HistoricalDates[HistoricalDates['Date'] != PriorDate]['Date'].max()
    print('PriorDateTMinus1 is')
    print(PriorDateTMinus1)
    
    HistoricalPricesPriorDate = HistoricalPrices.loc[HistoricalPrices['Date'] == PriorDate]
    PriorDateHighLowPrices = pd.pivot_table(HistoricalPricesPriorDate, values='close', index=['ticker'], aggfunc=[min, max]).reset_index().rename(columns = {'min': 'prior_day_low', 'max': 'prior_day_high'}, inplace = False).stack()
    # print('PriorDateHighLowPrices after pivot is')
    # print(PriorDateHighLowPrices)
    PriorDateHighLowPrices['priordaygap'] = PriorDateHighLowPrices['prior_day_high'] - PriorDateHighLowPrices['prior_day_low']
    # print('PriorDateHighLowPrices is')
    # print(PriorDateHighLowPrices)
    
    df = PriorDateHighLowPrices[['ticker', 'priordaygap']]
    
    # print('df is')
    # print(df)

    Tickers = Tickers.merge(df, on=['ticker'], how='left')
    # print('Tickers with prior day gap before sorting is')
    # print(Tickers)
    Tickers.sort_values(by=['priordaygap'], inplace=True, ascending=False)
    print('Tickers with prior day gap is')
    print(Tickers)

    
    ClosingPrice = HistoricalPrices[(HistoricalPrices['TimeInStandardUnit'] == 930) & (HistoricalPrices['DataType'] == 'TRADES') ]
    print('Price at Closing Time')
    print(ClosingPrice)
    ClosingPrice = ClosingPrice[ClosingPrice['Date'] == PriorDate][['ticker', 'close']].rename(columns = {'close': 'PriorDayClose'}, inplace = False)
    print('Closing Prices at Prior Date')
    print(ClosingPrice)

    ClosingPrice = HistoricalPrices[(HistoricalPrices['TimeInStandardUnit'] == 930) & (HistoricalPrices['DataType'] == 'TRADES') & (HistoricalPrices['Date'] == PriorDate)][['ticker', 'close']].rename(columns = {'close': 'PriorDayClose'}, inplace = False)
    print('Closing Prices at Prior Date')
    print(ClosingPrice)

    # sql = "SELECT ticker, close AS PriorDayClose FROM `fdata_price_dayend_ib` WHERE DateTime = '" + PriorDate.strftime("%Y-%m-%d") + "' AND DataType = 'TRADES'"
    # print(sql)
    # ClosingPrice = pd.read_sql_query(sql, dbcon)

    Tickers = Tickers.merge(ClosingPrice, on='ticker', how='left')
    Tickers['CurrentPrice'] = Tickers['PriorDayClose']

    ClosingPriceTMinus1 = HistoricalPrices[(HistoricalPrices['TimeInStandardUnit'] == 930) & (HistoricalPrices['DataType'] == 'TRADES') & (HistoricalPrices['Date'] == PriorDateTMinus1)][['ticker', 'close']].rename(columns = {'close': 'PriorTMinus1DayClose'}, inplace = False)
    print('Closing T-1 Prices at Prior Date')
    print(ClosingPriceTMinus1)
    
    # sql = "SELECT ticker, close AS PriorTMinus1DayClose FROM `fdata_price_dayend_ib` WHERE DateTime = '" + PriorDateTMinus1.strftime("%Y-%m-%d") + "' AND DataType = 'TRADES'"
    # print(sql)
    # ClosingPriceTMinus1 = pd.read_sql_query(sql, dbcon)
    

    Tickers = Tickers.merge(ClosingPriceTMinus1, on='ticker', how='left')
    Tickers['AbsPriorGap'] = abs((Tickers['PriorDayClose'] - Tickers['PriorTMinus1DayClose']) / Tickers['PriorTMinus1DayClose'])
    # Tickers.sort_values(by=['AbsPriorGap'], inplace=True, ascending=False)
    Tickers.reset_index(drop=True, inplace=True)
    
    # Tickers = Tickers.head(5)
    
    print('Tickers with prices is')
    print(Tickers)
    
    Tickers = Tickers.sample(frac=1).reset_index(drop=True)
    print('Tickers with prices after shuffle is')
    print(Tickers)

    # TRADE_Prices = HistoricalPrices[HistoricalPrices['DataType'] == 'TRADES']
    
    # print("Minimal DateTime of TRADE_Prices is")
    # print(TRADE_Prices['DateTime'].min())
    
    # process = IBapiUSStocksGapperScanner(Tickers, HistoricalPrices)
    print("Start scanning gappers for market " + market)

    # process = IBapiUSStocksGapperScanner(Tickers, BeginDateOf30Days)
    # ProcessReturnList = RunIBApiProcessHub([process])
    return Tickers, BeginDateOf30Days

def StartGappersScanner(ib_api_consolidated_process, Tickers, BeginDateOf30Days):
    process = IBapiUSStocksGapperScanner(Tickers, BeginDateOf30Days)
    ProcessReturnList = RunIBApiProcessHub([process])    

def StartWebSynchronisation():
    x = threading.Thread(target=SynchroniseWebsiteThread, args=('0', '0'), daemon=True)
    x.start()

def StandardStart(ib_api_consolidated_process, isStartWebSynchronisation = True, StockFilter = ""):
    if isStartWebSynchronisation:
        StartWebSynchronisation()
    Tickers, BeginDateOf30Days = GetScanGapperParameter("XUSA", StockFilter)
    StartGappersScanner(ib_api_consolidated_process, Tickers, BeginDateOf30Days)

def InitiateAndGetIBApiProcess(isStartWebSynchronisation = True, StockFilter = "", RequestID_Range = None):
    if isStartWebSynchronisation:
        StartWebSynchronisation()
    Tickers, BeginDateOf30Days = GetScanGapperParameter("XUSA", StockFilter)
    return IBapiUSStocksGapperScanner(Tickers, BeginDateOf30Days, RequestID_Range = RequestID_Range)

