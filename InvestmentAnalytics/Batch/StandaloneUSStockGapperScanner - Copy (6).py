# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 13:06:00 2023

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
from datetime import datetime, date, timedelta
from pytz import timezone
import math

from pandas.tseries.offsets import BDay

from sqlalchemy import create_engine


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import *
from ibapi.common import *


IB_API_hostname = os.getenv('TradeAnalysis_IB_API_hostname')
IB_API_port = int(os.getenv('TradeAnalysis_IB_API_port'))
IB_API_clientId = int(os.getenv('TradeAnalysis_IB_API_clientId'))


# from InvestmentAnalytics.EmailModule import SendEmail
from InvestmentAnalytics.IB.IBApiProcessHub import RunIBApiProcessHub
# from InvestmentAnalytics.IB.IBApiProcessUSStockGapperScanner import *

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

# def StartGappersScanner(ib_api_consolidated_process, Tickers, BeginDateOf30Days):
#     process = IBapiUSStocksGapperScanner(Tickers, BeginDateOf30Days)
#     ProcessReturnList = RunIBApiProcessHub([process])    

def StartWebSynchronisation():
    x = threading.Thread(target=SynchroniseWebsiteThread, args=('0', '0'), daemon=True)
    x.start()

# def StandardStart(ib_api_consolidated_process, isStartWebSynchronisation = True, StockFilter = ""):
#     if isStartWebSynchronisation:
#         StartWebSynchronisation()
#     Tickers, BeginDateOf30Days = GetScanGapperParameter("XUSA", StockFilter)
#     StartGappersScanner(ib_api_consolidated_process, Tickers, BeginDateOf30Days)


    
    
    
class IBapiProcess(EWrapper, EClient):
    def __init__(self):
        pass
        
    def RunProcess(self):
        pass
    
    def InitiateProcess(self):
        pass
    
class IBapiDataReader(IBapiProcess):
    def __init__(self, RequestID_Range):
        super().__init__()
        self.RequestID_Range = RequestID_Range
        
    def InitiateProcess(self):
        pass

    def clearCache(self):
        self.DownloadComplete = False
        self.DownloadError = False
        

class IBapiUSStocksGapperScanner(IBapiDataReader):
    # RequestIDRange = [1000, 1049]
    # RequestIDRange = [1000, 1039]
    # ShortListReqIDCount = 4
    # Tier1ListReqIDCount = 1
    GapThreshold = 0.04
    Tier1Threshold = 0.02
    # GapperDollarVolumeThreshold = 50000
    GapperDollarVolumeThreshold = 500
    PriceTypeToReqModeMapping = {'TRADES':0, 'BID':2, 'ASK':3}

    def __init__(self, TickerList, BeginDateOf30Days, BarSize = "1 day", RequestID_Range = [1000, 1049]):
        print('IBapiUSStocksGapperScanner.init')
        if BarSize is None:
            BarSize = "1 day"
        # if RequestID_Range is None:
        #     RequestID_Range = IBapiUSStocksGapperScanner.RequestIDRange
        super().__init__(RequestID_Range)
        # self.RequestID_Range = RequestID_Range
        # self.RequestID_Range = RequestID_Range
        # print(self.RequestID_Range)
        # print(self.RequestID_Range[1])
        # print(self.RequestID_Range[0])
        self.TickerList = TickerList
        
        # print('In IBapiUSStocksGapperScanner, self.TickerList = ')
        # print(self.TickerList)

        self.TickerListLength = len(self.TickerList)
        # self.HistoricalPrices = HistoricalPrices
        self.BeginDateOf30Days = BeginDateOf30Days
        self.TodayUSDate = datetime.now(timezone('America/New_York')) 

        self.BarSize = BarSize
        self.AllReqIDCount = self.RequestID_Range[1] - self.RequestID_Range[0] + 1
        # self.BaseReqIDCount = self.AllReqIDCount - IBapiUSStocksGapperScanner.Tier1ListReqIDCount - IBapiUSStocksGapperScanner.ShortListReqIDCount
        self.BaseReqIDCount = self.AllReqIDCount
        # self.mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
        # self.dbcon = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
        # self.dbcon_alldb = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD)
        self.ContinuousLargeGapperCount = 0

        self.TickerWithHistorical30MinBarUpdated = []
        
        self.ReqIDIdle = {}
        self.TickerIndexOffset = {}
        self.TickerIndex = {}
        self.ReqIDPrice = {}
        self.ReqIDVol = {}
        self.ReqMode = {}
        self.ReqIDBidPrice = {}
        self.ReqIDAskPrice = {}
        self.data = {}
        self.TickerDict = {}
        for i in range(self.AllReqIDCount):
            self.ReqIDIdle[i] = True
            self.TickerIndexOffset[i] = -1
            self.TickerIndex[i] = 0
            self.ReqIDPrice[i] = 0
            self.ReqIDVol[i] = 0
            self.ReqMode[i] = 0
            self.data[i] = []
            self.TickerDict[i] = ""

        # self.GapperTickerIndexOffset = {}
        # self.GapperTicker = {}
        
        # for i in range(IBapiUSStocksGapperScanner.ShortListReqIDCount):
        #     self.GapperTickerIndexOffset[i] = 0
        #     self.GapperTicker[i] = None
        
        # self.Tier1TickerList = []


    def InitiateProcess(self):
        super().InitiateProcess()
        self.PricesData =  pd.DataFrame()
        self.TickersWithError = []
        self.clearCache()
        pass
    
    def clearCache(self):
        super().clearCache()
        self.TickerDownloadCompleteCount = 0
        # self.data = []
        self.TickersWithErrorInThisIteration = []
        # self.df = pd.DataFrame()
        self.Request_Data_Item = ""
        self.DownloadError = False
        self.ScanDoneCount = 0
        self.PriorScanDoneCount = 0
        self.StaleScanDontCountIncrement = 0
        # self.DownloadComplete = False
        
    def getIBContract(self, symbol, secType, exchange, currency, primaryExchange = 'NONE'):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = secType
        contract.exchange = exchange
        contract.currency = currency
        if not primaryExchange == 'NONE':
            contract.primaryExchange = primaryExchange 
        return contract


    def getHistoricalPricesOfTicker(self, ticker):
        sql = "SELECT *, DATE(DateTime) AS ValueDate FROM `fdata_price_30min_ib` WHERE DateTime >= '" + self.BeginDateOf30Days.strftime("%Y-%m-%d") + "' AND DateTime < '" + self.TodayUSDate.strftime("%Y-%m-%d") + "' AND ticker = '" + ticker + "' AND DataType = 'TRADES'"
        # print('In getHistoricalPricesOfTicker')
        # print(sql)

        HistoricalPrices = pd.read_sql(sql,con=DBUtil.GetSQLAlchemyEngine(DatabaseName=Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_30MIN_IB))

        # dbcon = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_30MIN_IB)
        # # HistoricalPrices = pd.read_sql_query(sql, self.dbcon)
        # HistoricalPrices = pd.read_sql_query(sql, dbcon)
        # print('HistoricalPrices is')
        # print(HistoricalPrices)
        HistoricalPrices['Hour'] = pd.to_datetime(HistoricalPrices['DateTime']).dt.hour
        HistoricalPrices['Minute'] = pd.to_datetime(HistoricalPrices['DateTime']).dt.minute
        HistoricalPrices['TimeInStandardUnit'] = HistoricalPrices['Hour'] * 60 + HistoricalPrices['Minute']
        # print(HistoricalPrices)
        return HistoricalPrices



    def get30MAVol(self, ticker):
        # print('In get30MAVol')
        US_time = datetime.now(timezone('America/New_York')) 
        US_time_in_minutes = US_time.hour * 60 + US_time.minute
        US_time_end_of_next_30mins_bucket = math.ceil(US_time_in_minutes/30)*30
        # print('In get30MAVol, US_time_end_of_next_30mins_bucket is ' + str(US_time_end_of_next_30mins_bucket))
        HistoricalPricesOfTicker = self.getHistoricalPricesOfTicker(ticker)
        try:
            # ticker = self.TickerList.loc[TickerIndex, 'ticker']
            # HistoricalPricesOfTicker = self.getHistoricalPricesOfTicker(ticker)
            # print('HistoricalPricesOfTicker is')
            # print(HistoricalPricesOfTicker)
            if len(HistoricalPricesOfTicker) <= 0:
                return 0
            # ticker_historical_prices = self.HistoricalPrices[(self.HistoricalPrices['ticker'] == ticker) & (self.HistoricalPrices['DataType'] == 'TRADES') & ( self.HistoricalPrices['TimeInStandardUnit'] <= US_time_end_of_next_30mins_bucket)]
            ticker_historical_prices = HistoricalPricesOfTicker[ HistoricalPricesOfTicker['TimeInStandardUnit'] <= US_time_end_of_next_30mins_bucket]
            # ticker_historical_prices['Date']
            # print('ticker_historical_prices is')
            # print(ticker_historical_prices)
            # ticker_historical_prices = pd.pivot_table(ticker_historical_prices, values='vol', index=['ticker', 'ValueDate'], aggfunc=np.sum).reset_index()
            # print('ticker_historical_prices after first pivot is')
            # print(ticker_historical_prices)
            # ticker_historical_prices = pd.pivot_table(ticker_historical_prices, values='vol', index=['ticker'], aggfunc=np.mean).reset_index()
            ticker_historical_prices = pd.pivot_table(ticker_historical_prices, values='vol', index=['ticker'], aggfunc=np.sum).reset_index()
            # print('ticker_historical_prices after pivot is')
            # print(ticker_historical_prices)
            MA30Vol = ticker_historical_prices['vol'].iloc[0] / 30
            # print('30MAVol is ' + str(MA30Vol))
            return MA30Vol
        except Exception:
            print("Error in getting 30MA Volume for ticker " + ticker )
            return 0

    def AddToGapperList(self, TickerIndex, thread_id):
        print('Ticker ' + self.TickerList.loc[TickerIndex, 'ticker'] + ' is a gapper with Current Price ' + str(self.TickerList.loc[TickerIndex, 'CurrentPrice']) + ' and Prior Day Closing Price ' + str(self.TickerList.loc[TickerIndex, 'PriorDayClose']) + ' and vol ' + str(self.ReqIDVol[thread_id]) + ' at ' + str(datetime.now()))
        US_time = datetime.now(timezone('America/New_York'))
        MA30Vol = self.get30MAVol(self.TickerList.loc[TickerIndex, 'ticker'])
        
        # MarketCap = IBapiUSStocksGapperScanner.GetMarketCap(self.TickerList.loc[TickerIndex, 'ticker'])
        # FreeFloat = IBapiUSStocksGapperScanner.GetFreeFloat(self.TickerList.loc[TickerIndex, 'ticker'])
        
        MarketCap = 0
        FreeFloat = 0
        
        CaptureDateString = US_time.strftime("%Y-%m-%d")
        FirstCaptureDatetimeString = US_time.strftime("%Y-%m-%d %H:%M:%S")
        
        sql = "INSERT INTO fdata_us_gapper_list (CaptureDate, ticker, Sector, Industry, PriorDayClose, CurrentPrice, 30MA_Vol, Today_Vol, MarketCap, FreeFloat, BidAskSpread, FirstCaptureDatetime, FirstCapturePrice) VALUES ('" + CaptureDateString + "', '" + str(self.TickerList.loc[TickerIndex, 'ticker']) + "', '" + str(self.TickerList.loc[TickerIndex, 'Sector']) + "', '" + str(self.TickerList.loc[TickerIndex, 'Industry']) + "', " + str(self.TickerList.loc[TickerIndex, 'PriorDayClose']) + ", " + str(self.TickerList.loc[TickerIndex, 'CurrentPrice']) + ", " + str(MA30Vol) + ", " + str(self.ReqIDVol[thread_id]) + ", " + str(MarketCap) + ", " + str(FreeFloat) + ", 0.1, '" + FirstCaptureDatetimeString + "', " + str(self.TickerList.loc[TickerIndex, 'CurrentPrice']) + ") ON DUPLICATE KEY UPDATE CurrentPrice = " + str(self.TickerList.loc[TickerIndex, 'CurrentPrice']) + ", 30MA_Vol = " + str(MA30Vol) + ", Today_Vol = " + str(self.ReqIDVol[thread_id])
        # print(sql)
        DBUtil.GetSQLAlchemyEngine().execute(sql)
        # self.DB_engine.execute(sql)
        
        # sql = "INSERT INTO fdata_us_gapper_list (CaptureDate, ticker, Sector, Industry, PriorDayClose, CurrentPrice, 30MA_Vol, Today_Vol, MarketCap, FreeFloat, BidAskSpread, FirstCaptureDatetime, FirstCapturePrice) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE CurrentPrice = %s, 30MA_Vol = %s, Today_Vol = %s"
        # val = (US_time, self.TickerList.loc[TickerIndex, 'ticker'], self.TickerList.loc[TickerIndex, 'Sector'], self.TickerList.loc[TickerIndex, 'Industry'], self.TickerList.loc[TickerIndex, 'PriorDayClose'], self.TickerList.loc[TickerIndex, 'CurrentPrice'], MA30Vol, self.ReqIDVol[batch_id], MarketCap, FreeFloat, 0.1, US_time, self.TickerList.loc[TickerIndex, 'CurrentPrice'], self.TickerList.loc[TickerIndex, 'CurrentPrice'], MA30Vol, self.ReqIDVol[batch_id])
        # mycursor = self.mydb.cursor()
        # mycursor.execute(sql, val)
        # self.mydb.commit()
        # self.RemoveTier1Ticker(self.TickerList.loc[TickerIndex, 'ticker'])
        print('Ticker ' + self.TickerList.loc[TickerIndex, 'ticker'] + ' added to gapper list')
        # self.UpdateGoogleNews(self.TickerList.loc[TickerIndex, 'ticker'], US_time)

  
    def TriggerScanning(self, thread_id, PriceType = 'TRADES'):
        if thread_id < self.AllReqIDCount:
            self.ReqIDIdle[thread_id] = False
            self.TickerIndexOffsetIncrement(thread_id)
            self.TickerIndex[thread_id] = self.TickerIndexOffset[thread_id] * self.AllReqIDCount + thread_id
            # print('TriggerScanning for thread_id = ' + str(thread_id) + ', TickerIndex = ' + str(self.TickerIndex[thread_id]) + ', symbol = ' + str(self.TickerList.loc[self.TickerIndex[thread_id], 'symbol']) + ', self.ReqIDIdle[thread_id] = ' + str(self.ReqIDIdle[thread_id]))
            try:
                contract = self.getIBContract(self.TickerList.loc[self.TickerIndex[thread_id], 'symbol'], self.TickerList.loc[self.TickerIndex[thread_id], 'secType'], self.TickerList.loc[self.TickerIndex[thread_id], 'exchange'], self.TickerList.loc[self.TickerIndex[thread_id], 'currency'], self.TickerList.loc[self.TickerIndex[thread_id], 'primaryExchange'])
                self.IBProcessHub.reqHistoricalData(thread_id + self.RequestID_Range[0], contract, self.DataEndTime, "1 D", "1 day", PriceType, 0, 1, False, [])
            except:
                print('Error in TriggerScanning: TickerIndex is ' + str(self.TickerIndex[thread_id]))
                print('symbol is ' + self.TickerList.loc[self.TickerIndex[thread_id], 'symbol'])
                print('secType is ' + self.TickerList.loc[self.TickerIndex[thread_id], 'secType'])
                print('exchange is ' + self.TickerList.loc[self.TickerIndex[thread_id], 'exchange'])
                print('currency is ' + self.TickerList.loc[self.TickerIndex[thread_id], 'currency'])
                print('primaryExchange is ' + self.TickerList.loc[self.TickerIndex[thread_id], 'primaryExchange'])
                self.ReqIDIdle[thread_id] = True
            
            
    def TickerIndexOffsetIncrement(self, thread_id):
        self.TickerIndexOffset[thread_id] = self.TickerIndexOffset[thread_id] + 1
        if(self.TickerIndexOffset[thread_id] * self.AllReqIDCount + thread_id >= self.TickerListLength):
            self.TickerIndexOffset[thread_id] = 0
        self.ScanDoneCount = self.ScanDoneCount + 1
        

    def RunPreRun(self):
        # contract = self.getIBContract("AAPL", "STK", "SMART", "USD", "NONE")
        contract = self.getIBContract("GIS", "STK", "SMART", "USD", "NONE")
        self.PreRun = True
        self.IBProcessHub.reqHistoricalData(self.RequestID_Range[0], contract, self.DataEndTime, "3 D", "1 day", 'TRADES', 0, 1, False, [])
        print('Start Pre Run')
        # time.sleep(10)
        while self.PreRun:
            print('self.PreRun is still True')
            time.sleep(10)
        
    def historicalData(self, reqId:int, bar: BarData):
        # print('self.PreRun = ' + str(self.PreRun))
        thread_id = reqId - self.RequestID_Range[0]
        d = vars(bar)
        if self.PreRun:
            print('historicalData at PreRun, thread_id = ' + str(thread_id))
            print(d)
        else:
            # print('historicalData, thread_id = ' + str(thread_id) + ', symbol = ' + str(self.TickerList.loc[self.TickerIndex[thread_id], 'symbol']))
            # print(d)
            self.ReqIDPrice[thread_id] =  d['close']
            try:
                self.ReqIDVol[thread_id] =  d['volume']
                # print('In historicalData, for ticker ' + self.TickerDict[batch_id] + ' volume is ' + str(d['volume']) + ' and close is ' + str(d['close']))
            except Exception:
                self.ReqIDVol[thread_id] =  0

        
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        # print('historicalDataEnd, self.PreRun = ' + str(self.PreRun))
        super().historicalDataEnd(reqId, start, end)
        thread_id = reqId - self.RequestID_Range[0]
        if self.PreRun:
            print('historicalDataEnd at PreRun, thread_id = ' + str(thread_id))
            self.PreRun = False
        else:
            self.ScanDoneCountProcessAndDisplay()

            self.TickerList.loc[self.TickerIndex[thread_id], 'CurrentPrice'] = self.ReqIDPrice[thread_id]
            PriceGap = (self.TickerList.loc[self.TickerIndex[thread_id], 'CurrentPrice'] - self.TickerList.loc[self.TickerIndex[thread_id], 'PriorDayClose']) / self.TickerList.loc[self.TickerIndex[thread_id], 'PriorDayClose']
            if ( self.TickerList.loc[self.TickerIndex[thread_id], 'CurrentPrice'] * self.ReqIDVol[thread_id] > IBapiUSStocksGapperScanner.GapperDollarVolumeThreshold) and ((PriceGap > IBapiUSStocksGapperScanner.GapThreshold) or (PriceGap < - IBapiUSStocksGapperScanner.GapThreshold)):
                print('*** historicalDataEnd' + ', symbol = ' + str(self.TickerList.loc[self.TickerIndex[thread_id], 'symbol']) + ', PriceGap = ' + str(PriceGap) + ', CurrentPrice = ' + str(self.TickerList.loc[self.TickerIndex[thread_id], 'CurrentPrice']) + ', PriorDayClose = ' + str(self.TickerList.loc[self.TickerIndex[thread_id], 'PriorDayClose'])  + ', TradingVolume = ' + str(self.ReqIDVol[thread_id]) + ', DollarVolumeThreshold = ' + str(self.TickerList.loc[self.TickerIndex[thread_id], 'CurrentPrice'] * self.ReqIDVol[thread_id])+ ',  thread_id = ' + str(thread_id) )
                self.AddToGapperList(self.TickerIndex[thread_id], thread_id)
            else:
                # print('* historicalDataEnd, thread_id = ' + str(thread_id) + ', symbol = ' + str(self.TickerList.loc[self.TickerIndex[thread_id], 'symbol']) + ', CurrentPrice = ' + str(self.TickerList.loc[self.TickerIndex[thread_id], 'CurrentPrice']) + ', PriorDayClose = ' + str(self.TickerList.loc[self.TickerIndex[thread_id], 'PriorDayClose']) + ', PriceGap = ' + str(PriceGap) + ', TradingVolume = ' + str(self.ReqIDVol[thread_id]) + ', DollarVolumeThreshold = ' + str(self.TickerList.loc[self.TickerIndex[thread_id], 'CurrentPrice'] * self.ReqIDVol[thread_id]))
                pass
            self.ReqIDIdle[thread_id] = True

    def ScanDoneCountProcessAndDisplay(self):
        if ((self.ScanDoneCount < 100) and (self.ScanDoneCount % 10 == 0)) or self.ScanDoneCount % 100 == 0:
            print('Scan Done Count = ' + str(self.ScanDoneCount) + ' at ' + str(datetime.now()))
        if self.ScanDoneCount > self.PriorScanDoneCount:
            self.PriorScanDoneCount = self.ScanDoneCount
            self.StaleScanDontCountIncrement = 0
        else:
            self.StaleScanDontCountIncrement = self.StaleScanDontCountIncrement + 1
            # print('StaleScanDontCountIncrement = ' + str(self.StaleScanDontCountIncrement) + ' at ' + str(datetime.now()))
        

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        thread_id = reqId - self.RequestID_Range[0]
        # print("Error. reqId:", reqId, "Code:", errorCode, "Msg:", errorString)
        
        if errorString == 'Not connected' :
            # print("Error. reqId:", reqId, "Code:", errorCode, "Msg:", errorString, "thread_id:", thread_id)
            pass
        else:
            if 'HMDS query returned no data' in errorString:
                # print('thread_id ' + str(thread_id) + ' and ReqMode ' + str(self.ReqMode[thread_id]) + ' released after no price data')
                # time.sleep(0.5)
                self.ReqIDIdle[thread_id] = True
            else:
                if self.ScanDoneCount < 8000:
                    if not 'API version does not support fractional share size rules' in errorString:
                        # super().error(reqId, errorCode, errorString)
                        print("Error. reqId:", reqId, "Code:", errorCode, "Msg:", errorString, "thread_id:", thread_id)
            # print("thread_id " + str(thread_id) + " for ticker " + str(self.TickerList.loc[self.TickerIndex[thread_id], 'symbol']) + " released due to no price data")
            
            # self.ReqMode[batch_id] = 0
        self.ScanDoneCountProcessAndDisplay()

        
    def RunProcess(self, IBProcessHub):
        # print('RunProcess')
        
        ScannerEndTime = datetime.strptime(Config.CONFIG_IB_USGAPPER_SCAN_END_TIME, '%H:%M')
        self.IBProcessHub = IBProcessHub
        Now_time = datetime.now() 
        print("Time now is " + str(Now_time))
        US_time = datetime.now(timezone('America/New_York')) 
        print("US Time now is " + str(US_time))
        # DataEndTime = self.DataEndDateString.strftime("%Y%m%d") + " 24:00:00"
        # self.DataEndTime = Now_time.strftime("%Y%m%d") + " 24:00:00"
        # self.DataEndTime = US_time.strftime("%Y%m%d") + " 24:00:00"
        self.DataEndTime = US_time.strftime("%Y%m%d") + "-24:00:00"
        self.clearCache()
        self.PreRun = False
        
        thread_id = 0
        # self.BaseReqIDCount = self.AllReqIDCount - IBapiUSStocksGapperScanner.Tier1ListReqIDCount - IBapiUSStocksGapperScanner.ShortListReqIDCount
        
        print('Start scanning price' + ' at ' + str(datetime.now()))
        self.ContinuousLargeGapperTime = datetime.now()

        now = datetime.now()
        
        # self.RunPreRun()

        # while (now.hour < 15):
        while ((US_time.hour < ScannerEndTime.hour) or ((US_time.hour == ScannerEndTime.hour) and (US_time.minute < ScannerEndTime.minute))):
        # while (True):
            # print('while loop, cycle = ' + str(cycle) + 'thread_id = ' + str(thread_id) + ', symbol = ' + str(self.TickerList.loc[self.TickerIndex[thread_id], 'symbol']) + ', self.ReqIDIdle[' + str(thread_id) + '] = ' + str(self.ReqIDIdle[thread_id]))
            # time.sleep(0.5)
            if self.ReqIDIdle[thread_id]:
                self.TriggerScanning(thread_id)
            # print('while loop after TriggerScanning, cycle = ' + str(cycle) + ', thread_id = ' + str(thread_id) + ', symbol = ' + str(self.TickerList.loc[self.TickerIndex[thread_id], 'symbol']) + ', self.ReqIDIdle[' + str(thread_id) + '] = ' + str(self.ReqIDIdle[thread_id])) 
    
            thread_id = thread_id + 1
            if thread_id >= self.AllReqIDCount:
                thread_id = 0

            now = datetime.now()
            US_time = datetime.now(timezone('America/New_York')) 


def InitiateAndGetIBApiProcess(isStartWebSynchronisation = True, StockFilter = "", RequestID_Range = None):
    print('InitiateAndGetIBApiProcess')
    
    if isStartWebSynchronisation:
        StartWebSynchronisation()
    
    Tickers, BeginDateOf30Days = GetScanGapperParameter("XUSA", StockFilter)
    # print(Tickers)
    return IBapiUSStocksGapperScanner(Tickers, BeginDateOf30Days, RequestID_Range = RequestID_Range)
        
app = InitiateAndGetIBApiProcess(RequestID_Range = [1000, 1049])

ProcessReturnList = RunIBApiProcessHub([app])    
    
# print('IB_API_hostname is ' + str(IB_API_hostname) + ' and IB_API_port is ' + str(IB_API_port) + ' and IB_API_clientId is ' + str(IB_API_clientId))
# app.connect(IB_API_hostname, IB_API_port, IB_API_clientId)


print('End')