# -*- coding: utf-8 -*-
"""
Created on Sun May 16 00:46:02 2021

@author: Henry Cheung
"""
import InvestmentAnalytics.Config as Config
from InvestmentAnalytics.DBUtil import AppendDBExportScript
from InvestmentAnalytics.IB.IBApiProcess import IBapiDataReader
# from InvestmentAnalytics.IB.IBApiProcessIBapiUSStocksHistoricalDataReader import IBapiUSStocksDayEndHistoricalDataReader

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import *
from ibapi.common import *
import pandas as pd
import numpy as np
import time
from datetime import date, datetime, timedelta
import math
import csv
from pytz import timezone
import pymysql
import mysql.connector
import yfinance as yf

from GoogleNews import GoogleNews
from newspaper import Article

class IBapiUSStocksGapperScanner(IBapiDataReader):
    # RequestIDRange = [1000, 1049]
    RequestIDRange = [1000, 1039]
    ShortListReqIDCount = 4
    Tier1ListReqIDCount = 1
    GapThreshold = 0.04
    Tier1Threshold = 0.02
    # GapperDollarVolumeThreshold = 50000
    GapperDollarVolumeThreshold = 500
    PriceTypeToReqModeMapping = {'TRADES':0, 'BID':2, 'ASK':3}

    # def __init__(self, TickerList, HistoricalPrices, BarSize = "1 day", RequestID_Range = RequestIDRange):
    def __init__(self, TickerList, BeginDateOf30Days, BarSize = "1 day", RequestID_Range = RequestIDRange):
        if BarSize is None:
            BarSize = "1 day"
        if RequestID_Range is None:
            RequestID_Range = RequestIDRange
        super().__init__(RequestID_Range)
        self.TickerList = TickerList
        self.TickerListLength = len(self.TickerList)
        # self.HistoricalPrices = HistoricalPrices
        self.BeginDateOf30Days = BeginDateOf30Days
        self.TodayUSDate = datetime.now(timezone('America/New_York')) 

        self.BarSize = BarSize
        self.AllReqIDCount = IBapiUSStocksGapperScanner.RequestIDRange[1] - IBapiUSStocksGapperScanner.RequestIDRange[0] + 1
        self.BaseReqIDCount = self.AllReqIDCount - IBapiUSStocksGapperScanner.Tier1ListReqIDCount - IBapiUSStocksGapperScanner.ShortListReqIDCount
        self.mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
        self.dbcon = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
        self.dbcon_alldb = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD)
        self.ContinuousLargeGapperCount = 0

        self.TickerWithHistorical30MinBarUpdated = []
        
        self.ReqIDIdle = {}
        self.TickerIndexOffset = {}
        self.ReqIDPrice = {}
        self.ReqIDVol = {}
        self.ReqMode = {}
        self.ReqIDBidPrice = {}
        self.ReqIDAskPrice = {}
        self.data = {}
        self.TickerDict = {}
        for i in range(self.AllReqIDCount):
            self.ReqIDIdle[i] = True
            self.TickerIndexOffset[i] = 0
            self.ReqIDPrice[i] = 0
            self.ReqIDVol[i] = 0
            self.ReqMode[i] = 0
            self.data[i] = []
            self.TickerDict[i] = ""

        self.GapperTickerIndexOffset = {}
        self.GapperTicker = {}
        for i in range(IBapiUSStocksGapperScanner.ShortListReqIDCount):
            self.GapperTickerIndexOffset[i] = 0
            self.GapperTicker[i] = None
        
        self.Tier1TickerList = []

    def AddTier1Ticker(self, ticker):
        if not ticker in self.Tier1TickerList:
            self.Tier1TickerList.append(ticker)
            
    def RemoveTier1Ticker(self, ticker):
        if ticker in self.Tier1TickerList:
            self.Tier1TickerList.remove(ticker)
            
    def AddReqIDAndBatchID(self, df):
        df.reset_index(inplace=True, drop=True)
        df['ticker id'] = df.index
        df['batch id'] = np.trunc(df['ticker id'] / self.AllReqIDCount)
        df['req id'] = np.remainder(df['ticker id'], self.AllReqIDCount) + IBapiUSStocksGapperScanner.RequestIDRange[0]
        self.BatchIDCount = len(df[['batch id']].drop_duplicates())
        return df

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
    
    def RunProcess(self, IBProcessHub):
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
        
        thread_id = 0
        # self.BaseReqIDCount = self.AllReqIDCount - IBapiUSStocksGapperScanner.Tier1ListReqIDCount - IBapiUSStocksGapperScanner.ShortListReqIDCount
        
        print('Start scanning price' + ' at ' + str(datetime.now()))
        self.ContinuousLargeGapperTime = datetime.now()

        # for thread_id in range(ReqIDCount):
        # while True:
        now = datetime.now()
        # while (now.hour < 15):
        while ((US_time.hour < ScannerEndTime.hour) or ((US_time.hour == ScannerEndTime.hour) and (US_time.minute < ScannerEndTime.minute))):
            # print('while loop')
            # print('thread_id is ' + str(thread_id) + ' and self.ContinuousLargeGapperCount is ' + str(self.ContinuousLargeGapperCount))
            if self.StaleScanDontCountIncrement > 3:
                print('Should I restart now?')
            if self.ContinuousLargeGapperCount > 10:
                # Now_time = datetime.now() 
                # difference = (Now_time - self.ContinuousLargeGapperTime).total_seconds()
                difference = (datetime.now() - self.ContinuousLargeGapperTime).total_seconds()
                # print('time difference is ' + str(difference))
                if difference > 60:
                    self.ContinuousLargeGapperCount = 0
                    self.ContinuousLargeGapperTime = datetime.now()
                    if self.ReqIDIdle[thread_id]:
                        self.TriggerScanning(thread_id)
            
                    thread_id = thread_id + 1
                    if thread_id >= self.AllReqIDCount:
                        thread_id = 0
            else:
                # print('self.ReqIDIdle[thread_id] is ' + str(self.ReqIDIdle[thread_id]))
                if self.ReqIDIdle[thread_id]:
                    self.TriggerScanning(thread_id)
        
                thread_id = thread_id + 1
                if thread_id >= self.AllReqIDCount:
                    thread_id = 0

            # time.sleep(20)
            now = datetime.now()
            US_time = datetime.now(timezone('America/New_York')) 

        return None
    def get30MAVolCount(self, ticker):
        try:
            # sql = "SELECT COUNT(*) AS CountOfDayWithData (SELECT DATE(DateTime) FROM `fdata_price_30min_ib` WHERE DateTime >= '" + self.BeginDateOf30Days.strftime("%Y-%m-%d") + "' AND DateTime < '" + self.TodayUSDate.strftime("%Y-%m-%d") + "' AND ticker = '" + ticker + "' AND DataType = 'TRADES' GROUP BY DATE(DateTime))"
            sql = "SELECT COUNT(*) AS CountOfDayWithData (SELECT DATE(DateTime) FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_30MIN_IB + ".fdata_price_30min_ib WHERE DateTime >= '" + self.BeginDateOf30Days.strftime("%Y-%m-%d") + "' AND DateTime < '" + self.TodayUSDate.strftime("%Y-%m-%d") + "' AND ticker = '" + ticker + "' AND DataType = 'TRADES' GROUP BY DATE(DateTime))"
            # print(sql)
            df = pd.read_sql_query(sql, self.dbcon_alldb)
            return df.iloc[0, 'CountOfDayWithData']
        except:
            return 0
    
    def TriggerUpdateHistoricalPricesOfTicker(self, batch_id):
        TickerIndex = self.TickerIndexOffset[batch_id] * self.BaseReqIDCount + batch_id
        # print('In TriggerUpdateHistoricalPricesOfTicker, batch_id is ' + str(batch_id) + ' and TickerIndex is ' + str(TickerIndex) + ' and self.BaseReqIDCount is ' + str(self.BaseReqIDCount) + ' and self.TickerListLength is ' + str(self.TickerListLength))
        # print('self.TickerList.loc[TickerIndex, symbol] is ' + self.TickerList.loc[TickerIndex, 'symbol'])
        ticker = self.TickerList.loc[TickerIndex, 'symbol']
        # print('ticker is ' + ticker)
        if batch_id < self.BaseReqIDCount:
            if batch_id < self.TickerListLength:
                try:
                    # MA30VolCount = self.get30MAVolCount(ticker)
                    if (ticker not in self.TickerWithHistorical30MinBarUpdated) and (self.get30MAVolCount(ticker) < 30):
                        self.TickerWithHistorical30MinBarUpdated.append(ticker)
                        contract = Contract()
                        contract.symbol = self.TickerList.loc[TickerIndex, 'symbol']
                        contract.secType = self.TickerList.loc[TickerIndex, 'secType']
                        contract.exchange = self.TickerList.loc[TickerIndex, 'exchange']
                        contract.currency = self.TickerList.loc[TickerIndex, 'currency'] 
                        if not self.TickerList.loc[TickerIndex, 'primaryExchange'] == 'NONE':
                            contract.primaryExchange = self.TickerList.loc[TickerIndex, 'primaryExchange']
                        self.TickerDict[batch_id] = self.TickerList.loc[TickerIndex, 'symbol']
                        # print('In TriggerUpdateHistoricalPricesOfTicker, batch_id is ' + str(batch_id) + ' and self.TickerDict[batch_id] is ' + str(self.TickerDict[batch_id]))
                        self.data[batch_id] = []
                        self.IBProcessHub.reqHistoricalData(batch_id + IBapiUSStocksGapperScanner.RequestIDRange[0], contract, self.DataEndTime, "2 M", "30 mins", 'TRADES', 0, 1, False, [])
                        self.ReqMode[batch_id] = 1
                        self.ReqIDIdle[batch_id] = False
                    # print('For batch_id is ' + str(batch_id) + ' on ticker ' + self.TickerList.loc[TickerIndex, 'symbol'] + ' reqHistoricalData is done')
                    else:
                        self.ReqIDIdle[batch_id] = True
                        self.TickerIndexOffsetIncrement(batch_id)
                    
                except:
                    print('Exception:')
                    print('TickerIndex is ' + str(TickerIndex))
                    print('symbol is ' + self.TickerList.loc[TickerIndex, 'symbol'])
                    print('secType is ' + self.TickerList.loc[TickerIndex, 'secType'])
                    print('exchange is ' + self.TickerList.loc[TickerIndex, 'exchange'])
                    print('currency is ' + self.TickerList.loc[TickerIndex, 'currency'])
                    print('primaryExchange is ' + self.TickerList.loc[TickerIndex, 'primaryExchange'])
                    self.ReqIDIdle[batch_id] = True
                    self.TickerIndexOffsetIncrement(batch_id)
    
    def TriggerScanning(self, batch_id, PriceType = 'TRADES'):
        # print('In TriggerScanning, batch_id is ' + str(batch_id) + ' and self.BaseReqIDCount is ' + str(self.BaseReqIDCount) + ' and self.TickerListLength is ' + str(self.TickerListLength) + ' and Price Type is ' + PriceType)
        # if PriceType == 'BID':
        #     print('In Trigger Scanning, PriceType is BID')
        # self.TickerIndexOffsetIncrement(batch_id)
        if batch_id < self.BaseReqIDCount:
            if batch_id < self.TickerListLength:
                TickerIndex = self.TickerIndexOffset[batch_id] * self.BaseReqIDCount + batch_id
                # print('In TriggerScanning, for batch_id = ' + str(batch_id) + ', TickerIndex = '+ str(TickerIndex))
                
                try:
                    contract = Contract()
                    contract.symbol = self.TickerList.loc[TickerIndex, 'symbol']
                    contract.secType = self.TickerList.loc[TickerIndex, 'secType']
                    contract.exchange = self.TickerList.loc[TickerIndex, 'exchange']
                    contract.currency = self.TickerList.loc[TickerIndex, 'currency'] 
                    if not self.TickerList.loc[TickerIndex, 'primaryExchange'] == 'NONE':
                        contract.primaryExchange = self.TickerList.loc[TickerIndex, 'primaryExchange']
                    self.ReqIDIdle[batch_id] = False
                    self.IBProcessHub.reqHistoricalData(batch_id + IBapiUSStocksGapperScanner.RequestIDRange[0], contract, self.DataEndTime, "1 D", "1 day", PriceType, 0, 1, False, [])
                    self.ReqMode[batch_id] = IBapiUSStocksGapperScanner.PriceTypeToReqModeMapping[PriceType]
                    # print('For batch_id is ' + str(batch_id) + ' on ticker ' + self.TickerList.loc[TickerIndex, 'symbol'] + ' reqHistoricalData is done')
                except:
                    print('TickerIndex is ' + str(TickerIndex))
                    print('symbol is ' + self.TickerList.loc[TickerIndex, 'symbol'])
                    print('secType is ' + self.TickerList.loc[TickerIndex, 'secType'])
                    print('exchange is ' + self.TickerList.loc[TickerIndex, 'exchange'])
                    print('currency is ' + self.TickerList.loc[TickerIndex, 'currency'])
                    print('primaryExchange is ' + self.TickerList.loc[TickerIndex, 'primaryExchange'])
                    self.ReqIDIdle[batch_id] = True
                    self.ReqMode[batch_id] = 0
                    self.TickerIndexOffsetIncrement(batch_id)
                
        elif batch_id >= self.AllReqIDCount - IBapiUSStocksGapperScanner.ShortListReqIDCount:
            sub_batch_id = batch_id + IBapiUSStocksGapperScanner.ShortListReqIDCount - self.AllReqIDCount
            # if PriceType == 'BID':
            #     print('In Trigger Scanning, PriceType is BID, a')
            if PriceType == 'TRADES':
                GapperList = self.getGapperList()
                if GapperList is not None:
                    GapperList = GapperList.merge(self.TickerList[['ticker','symbol','secType','exchange','currency','primaryExchange']], on=['ticker'])
                    if sub_batch_id < len(GapperList):
                        TickerIndex = self.GapperTickerIndexOffset[sub_batch_id] * IBapiUSStocksGapperScanner.ShortListReqIDCount + sub_batch_id
                        try:
                            contract = Contract()
                            contract.symbol = GapperList.loc[TickerIndex, 'symbol']
                            contract.secType = GapperList.loc[TickerIndex, 'secType']
                            contract.exchange = GapperList.loc[TickerIndex, 'exchange']
                            contract.currency = GapperList.loc[TickerIndex, 'currency'] 
                            if not GapperList.loc[TickerIndex, 'primaryExchange'] == 'NONE':
                                contract.primaryExchange = GapperList.loc[TickerIndex, 'primaryExchange']
                            self.ReqIDIdle[batch_id] = False
                            self.GapperTicker[sub_batch_id] = GapperList.loc[TickerIndex, 'symbol']
                            self.ReqIDBidPrice[batch_id] = 0
                            self.ReqIDAskPrice[batch_id] = 0
                            self.IBProcessHub.reqHistoricalData(batch_id + IBapiUSStocksGapperScanner.RequestIDRange[0], contract, self.DataEndTime, "1 D", "1 day", PriceType, 0, 1, False, [])
                            self.ReqMode[batch_id] = IBapiUSStocksGapperScanner.PriceTypeToReqModeMapping[PriceType]
                        except:
                            print('For Gapper, TickerIndex is ' + str(TickerIndex))
                            print('symbol is ' + self.TickerList.loc[TickerIndex, 'symbol'])
                            print('secType is ' + self.TickerList.loc[TickerIndex, 'secType'])
                            print('exchange is ' + self.TickerList.loc[TickerIndex, 'exchange'])
                            print('currency is ' + self.TickerList.loc[TickerIndex, 'currency'])
                            print('primaryExchange is ' + self.TickerList.loc[TickerIndex, 'primaryExchange'])
                            self.ReqIDIdle[batch_id] = True
                            self.TickerIndexOffsetIncrement(batch_id)

            else:
                # if PriceType == 'BID':
                #     print('In Trigger Scanning, PriceType is BID, b')
                # GapperRowForBIDASK = self.TickerList.loc[self.TickerList['ticker'] == self.GapperTicker[sub_batch_id]][['ticker','symbol','secType','exchange','currency','primaryExchange']]
                GapperRowForBIDASK = self.TickerList.loc[self.TickerList['ticker'] == self.GapperTicker[sub_batch_id], ['ticker','symbol','secType','exchange','currency','primaryExchange']].copy()
                # print('GapperRowForBIDASK is')
                # print(GapperRowForBIDASK)
                # print('GapperRowForBIDASK.loc[0, symbol] is ')
                # print(GapperRowForBIDASK['symbol'].iloc[0])
                
                try:
                    # if PriceType == 'BID':
                    #     print('In Trigger Scanning, PriceType is BID, c')
                    #     print(GapperRowForBIDASK)
                    contract = Contract()
                    contract.symbol = GapperRowForBIDASK['symbol'].iloc[0]
                    contract.secType = GapperRowForBIDASK['secType'].iloc[0]  
                    contract.exchange = GapperRowForBIDASK['exchange'].iloc[0]
                    contract.currency = GapperRowForBIDASK['currency'].iloc[0]
                    if not GapperRowForBIDASK['primaryExchange'].iloc[0]  == 'NONE':
                        contract.primaryExchange = GapperRowForBIDASK['primaryExchange'].iloc[0]
                    self.ReqIDIdle[batch_id] = False
                    self.IBProcessHub.reqHistoricalData(batch_id + IBapiUSStocksGapperScanner.RequestIDRange[0], contract, self.DataEndTime, "1 D", "1 day", PriceType, 0, 1, False, [])
                    self.ReqMode[batch_id] = IBapiUSStocksGapperScanner.PriceTypeToReqModeMapping[PriceType]
                    # if PriceType != 'TRADES':
                    #     print('In Trigger Scanning, reqHistoricalData called, PriceType is ' + PriceType + ', self.ReqMode[batch_id] is ' + str(self.ReqMode[batch_id]))
                    # print('For batch_id is ' + str(batch_id) + ' on ticker ' + self.TickerList.loc[TickerIndex, 'symbol'] + ' reqHistoricalData is done')
                except:
                    # print('TickerIndex is ' + str(TickerIndex))
                    # print('symbol is ' + GapperRowForBIDASK.loc[0, 'symbol'])
                    # print('secType is ' + GapperRowForBIDASK.loc[0, 'secType'])
                    # print('exchange is ' + GapperRowForBIDASK.loc[0, 'exchange'])
                    # print('currency is ' + GapperRowForBIDASK.loc[0, 'currency'])
                    # print('primaryExchange is ' + GapperRowForBIDASK.loc[0, 'primaryExchange'])
                    print('PriceType is ' + PriceType)
                    print('symbol is ' + GapperRowForBIDASK['symbol'].iloc[0])
                    print('secType is ' + GapperRowForBIDASK['secType'].iloc[0])
                    print('exchange is ' + GapperRowForBIDASK['exchange'].iloc[0])
                    print('currency is ' + GapperRowForBIDASK['currency'].iloc[0])
                    print('primaryExchange is ' + GapperRowForBIDASK['primaryExchange'].iloc[0])
                    self.ReqIDIdle[batch_id] = True
                    self.ReqMode[batch_id] = 0
                    self.TickerIndexOffsetIncrement(batch_id)
                

        else:
            # sub_batch_id = batch_id + IBapiUSStocksGapperScanner.ShortListReqIDCount - self.AllReqIDCount
            
            # SingleTier1TickerDF = self.TickerList[self.TickerList['ticker'] == self.Tier1TickerList[0]][['ticker','symbol','secType','exchange','currency','primaryExchange']]
            pass

    def getGapperList(self, ticker_filter=""):
        try:
            return pd.read_sql_query("SELECT * FROM `fdata_us_gapper_list` WHERE Today_Vol * CurrentPrice > " + str(IBapiUSStocksGapperScanner.GapperDollarVolumeThreshold) + " AND CaptureDate = '" + datetime.now(timezone('America/New_York')).strftime('%Y-%m-%d') + "' "  + ticker_filter + " ORDER BY ABS((CurrentPrice - PriorDayClose)/PriorDayClose) DESC", self.dbcon)
        except:
            return None
    def getLastScanIndex(self, ticker_filter=""):
        try:
            df = pd.read_sql_query("SELECT * FROM `fdata_us_gapper_list_last_scan_index` WHERE CaptureDate = '" + datetime.now(timezone('America/New_York')).strftime('%Y-%m-%d') + "'", self.dbcon)
            return df.loc[0, 'LastScannedIndex']
        except:
            return 0                
    def updateLastScanIndex(self, LastScanIndex, ticker_filter=""):
        sql = "INSERT INTO `fdata_us_gapper_list_last_scan_index` (CaptureDate, LastScannedIndex) VALUES('" + datetime.now(timezone('America/New_York')).strftime('%Y-%m-%d') + "', " + str(LastScanIndex) + ") ON DUPLICATE KEY UPDATE LastScannedIndex=" + str(LastScanIndex) 
        pass

    def isTickerInGapperList(self, ticker):
        try:
            return len(self.getGapperList("AND ticker = '" + ticker + "'")) > 0
        except:
            return 0
    
    def historicalData(self, reqId:int, bar: BarData):
        batch_id = reqId - IBapiUSStocksGapperScanner.RequestIDRange[0]
        d = vars(bar)
        # if self.ReqMode[batch_id] > 1:
            # print('In historicalData, for batch_id is ' + str(batch_id) + ' self.TickerDict[batch_id] is ' + str(self.TickerDict[batch_id]) + ' and self.ReqMode[batch_id] is ' + str(self.ReqMode[batch_id] ))
            # print(d)
        if self.ReqMode[batch_id] == 1:
            d['ticker'] = self.TickerDict[batch_id]
            self.data[batch_id].append(d)
            # print('in historicalData, for self.ReqMode[batch_id] = 1, d =')
            # print(d)
            # print('in historicalData, self.data =')
            # print(self.data[batch_id])
        elif self.ReqMode[batch_id] == 0:
            # print('in historicalData, d =')
            # print(d)
            self.ReqIDPrice[batch_id] =  d['close']
            try:
                self.ReqIDVol[batch_id] =  d['volume']
                # print('In historicalData, for ticker ' + self.TickerDict[batch_id] + ' volume is ' + str(d['volume']) + ' and close is ' + str(d['close']))
            except Exception:
                self.ReqIDVol[batch_id] =  0
        elif self.ReqMode[batch_id] == 2:
            self.ReqIDBidPrice[batch_id] = d['close']
            # print('In historicalData, self.ReqIDBidPrice[batch_id] is ' + str(self.ReqIDBidPrice[batch_id]))
        elif self.ReqMode[batch_id] == 3:
            self.ReqIDAskPrice[batch_id] = d['close']
            # print('In historicalData, self.ReqIDAskPrice[batch_id] is ' + str(self.ReqIDAskPrice[batch_id]))
            
        # print("HistoricalData. ReqId:", reqId, "BarData.", bar ,"Ticker.", self.TickerList.loc[TickerIndex, 'symbol'], "Close.", d['close'])
        
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        batch_id = reqId - IBapiUSStocksGapperScanner.RequestIDRange[0]
        if self.ContinuousLargeGapperCount > 10:
            self.ReqIDIdle[batch_id] = True
        else:
            # self.ScanDoneCount = self.ScanDoneCount + 1
            if ((self.ScanDoneCount < 100) and (self.ScanDoneCount % 10 == 0)) or self.ScanDoneCount % 100 == 0:
                print('Scan Done Count = ' + str(self.ScanDoneCount) + ' at ' + str(datetime.now()))
                # print('self.TickerDict is ' + str(self.TickerDict))
                if self.ScanDoneCount > self.PriorScanDoneCount:
                    self.PriorScanDoneCount = self.ScanDoneCount
                    self.StaleScanDontCountIncrement = 0
                else:
                    self.StaleScanDontCountIncrement = self.StaleScanDontCountIncrement + 1
                    print('StaleScanDontCountIncrement = ' + str(self.StaleScanDontCountIncrement) + ' at ' + str(datetime.now()))
                    
                
            if batch_id < self.BaseReqIDCount:
                TickerIndex = self.TickerIndexOffset[batch_id] * self.BaseReqIDCount + batch_id
                # print('In historicalDataEnd, for batch_id is ' + str(batch_id) + ' TickerIndex is ' + str(TickerIndex))
                
                if (self.ReqMode[batch_id] == 0):
                    self.TickerList.loc[TickerIndex, 'CurrentPrice'] = self.ReqIDPrice[reqId- IBapiUSStocksGapperScanner.RequestIDRange[0]]
                    PriceGap = (self.TickerList.loc[TickerIndex, 'CurrentPrice'] - self.TickerList.loc[TickerIndex, 'PriorDayClose']) / self.TickerList.loc[TickerIndex, 'PriorDayClose']
                    # print(self.TickerList)
                    # print('for reqId:' + str(reqId) + ', batch_id:' + str(batch_id)+ ', ' + self.TickerList.loc[TickerIndex, 'ticker'] + ' is with gap ' + str(round(PriceGap*100, 2)) + '%, Current Price is ' + str(self.TickerList.loc[TickerIndex, 'CurrentPrice']) + ' and Prior Day Close is ' + str(self.TickerList.loc[TickerIndex, 'PriorDayClose']) + ' and dollar volume ' + str(self.TickerList.loc[TickerIndex, 'CurrentPrice'] * self.ReqIDVol[batch_id]))
                    if ( self.TickerList.loc[TickerIndex, 'CurrentPrice'] * self.ReqIDVol[batch_id] > IBapiUSStocksGapperScanner.GapperDollarVolumeThreshold) and ((PriceGap > IBapiUSStocksGapperScanner.GapThreshold) or (PriceGap < - IBapiUSStocksGapperScanner.GapThreshold)):
                        # print('for reqId:' + str(reqId) + ', batch_id:' + str(batch_id)+ ', ' + self.TickerList.loc[TickerIndex, 'ticker'] + ' is with gap ' + str(round(PriceGap*100, 2)) + '%, Current Price is ' + str(self.TickerList.loc[TickerIndex, 'CurrentPrice']) + ' and Prior Day Close is ' + str(self.TickerList.loc[TickerIndex, 'PriorDayClose']))
                        # self.UpdateHistoricalPricesOfTicker(batch_id)
                        self.AddToGapperList(TickerIndex, batch_id)
                        self.ReqMode[batch_id] = 1
                        
                        
                        if (PriceGap > 0.3) or (PriceGap < -0.3):
                            self.ContinuousLargeGapperCount = self.ContinuousLargeGapperCount + 1
                        else:
                            self.ContinuousLargeGapperCount = 0
                        if self.ContinuousLargeGapperCount > 10:
                            self.ContinuousLargeGapperTime = datetime.now()
                            print('More than 10 continuous large gappers.  Something seems wrong.  Please check.  self.ContinuousLargeGapperTime is ' + str(self.ContinuousLargeGapperTime))
                    else:
                        if ((PriceGap > IBapiUSStocksGapperScanner.Tier1Threshold) or (PriceGap < - IBapiUSStocksGapperScanner.Tier1Threshold)) and not self.isTickerInGapperList(self.TickerList.loc[TickerIndex, 'ticker']):
                            self.AddTier1Ticker(self.TickerList.loc[TickerIndex, 'ticker'])
                        if batch_id >= self.TickerListLength:
                            self.ReqIDIdle[batch_id] = True
                        else:
                            self.TickerIndexOffsetIncrement(batch_id)
                            self.TriggerScanning(batch_id)
                    
                elif (self.ReqMode[batch_id] == 1):
                    self.UpdateHistoricalPricesOfTicker(batch_id)
                    self.ReqMode[batch_id] = 0
                    if batch_id >= self.TickerListLength:
                        self.ReqIDIdle[batch_id] = True
                    else:
                        self.TickerIndexOffsetIncrement(batch_id)
                        self.TriggerScanning(batch_id)
                    
            elif batch_id >= self.AllReqIDCount - IBapiUSStocksGapperScanner.ShortListReqIDCount:
                sub_batch_id = batch_id + IBapiUSStocksGapperScanner.ShortListReqIDCount - self.AllReqIDCount
                TickerIndex = self.GapperTickerIndexOffset[sub_batch_id] * IBapiUSStocksGapperScanner.ShortListReqIDCount + sub_batch_id
                
                if self.ReqMode[batch_id] == 3:
                
                    self.UpdateGapper(sub_batch_id, self.ReqIDAskPrice[batch_id] - self.ReqIDBidPrice[batch_id])
                    
                    if sub_batch_id >= IBapiUSStocksGapperScanner.ShortListReqIDCount:
                        self.ReqIDIdle[batch_id] = True
                    else:
                        self.ReqMode[batch_id] = 0
                        self.TickerIndexOffsetIncrement(batch_id)
                        self.TriggerScanning(batch_id)
                elif self.ReqMode[batch_id] == 0:
                    self.UpdateGapper(sub_batch_id, 0)
                    # print('Start to trigger Bid Price scanning')
                    self.TriggerScanning(batch_id, 'BID')
                elif self.ReqMode[batch_id] == 2:
                    # print('Start to trigger Ask Price scanning')
                    self.TriggerScanning(batch_id, 'ASK')
                # print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)

        
    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        # print("Error. reqId:", reqId, "Code:", errorCode, "Msg:", errorString)
        if not errorString == 'Not connected' :
            if not 'HMDS query returned no data' in errorString:
                super().error(reqId, errorCode, errorString)
                if self.ScanDoneCount < 8000:
                    print("Error. reqId:", reqId, "Code:", errorCode, "Msg:", errorString)
            batch_id = reqId - IBapiUSStocksGapperScanner.RequestIDRange[0]
            # print('batch_id ' + str(batch_id) + ' and ReqMode ' + str(self.ReqMode[batch_id]) + ' released after error')
            time.sleep(0.5)
            self.ReqIDIdle[batch_id] = True
            self.TickerIndexOffsetIncrement(batch_id)
            self.ReqMode[batch_id] = 0
        else:
            print("Error. reqId:", reqId, "Code:", errorCode, "Msg:", errorString)
        if ((self.ScanDoneCount < 100) and (self.ScanDoneCount % 10 == 0)) or self.ScanDoneCount % 100 == 0:
            print('Scan Done Count = ' + str(self.ScanDoneCount) + ' at ' + str(datetime.now()))
            # print('self.TickerDict is ' + str(self.TickerDict))
            if self.ScanDoneCount > self.PriorScanDoneCount:
                self.PriorScanDoneCount = self.ScanDoneCount
                self.StaleScanDontCountIncrement = 0
            else:
                self.StaleScanDontCountIncrement = self.StaleScanDontCountIncrement + 1
                print('StaleScanDontCountIncrement = ' + str(self.StaleScanDontCountIncrement) + ' at ' + str(datetime.now()))
                # print('self.TickerDict is ' + str(self.TickerDict))
        # print('Wait for 60 secs due to error')
        # time.sleep(60)
            
    def UpdateGapper(self, sub_batch_id, bid_ask_spread = 0):
        # if bid_ask_spread == 0:
        #     print('In UpdateGapper with bid ask spread = 0')
        # else:
        #     print('In UpdateGapper with bid ask spread != 0')
        batch_id = sub_batch_id - IBapiUSStocksGapperScanner.ShortListReqIDCount + self.AllReqIDCount
        MA30Vol = self.get30MAVol(self.GapperTicker[sub_batch_id])
        if bid_ask_spread == 0:
            print('Gapper ' + self.GapperTicker[sub_batch_id] + ' to be updated with Current Price ' + str(self.ReqIDPrice[batch_id]) + ', Recent Vol ' + str(self.ReqIDVol[batch_id]) + ', 30MA Vol ' + str(MA30Vol))
        else:
            print('Gapper ' + self.GapperTicker[sub_batch_id] + ' to be updated with Current Price ' + str(self.ReqIDPrice[batch_id]) + ', Recent Vol ' + str(self.ReqIDVol[batch_id]) + ', 30MA Vol ' + str(MA30Vol) + ', bid ask spread ' + str(bid_ask_spread / self.ReqIDPrice[batch_id]))            
        US_time = datetime.now(timezone('America/New_York'))
        if bid_ask_spread == 0:
            sql = "UPDATE fdata_us_gapper_list SET CurrentPrice = %s, Today_Vol = %s, 30MA_Vol = %s WHERE CaptureDate = %s AND ticker = %s"
            val = (self.ReqIDPrice[batch_id], self.ReqIDVol[batch_id], MA30Vol, US_time.strftime("%Y-%m-%d"), self.GapperTicker[sub_batch_id] )
        else:
            sql = "UPDATE fdata_us_gapper_list SET CurrentPrice = %s, Today_Vol = %s, 30MA_Vol = %s, BidAskSpread = %s WHERE CaptureDate = %s AND ticker = %s"
            val = (self.ReqIDPrice[batch_id], self.ReqIDVol[batch_id], MA30Vol, bid_ask_spread / self.ReqIDPrice[batch_id], US_time.strftime("%Y-%m-%d"), self.GapperTicker[sub_batch_id] )
        mycursor = self.mydb.cursor()
        mycursor.execute(sql, val)
        self.mydb.commit()
        
    def AddToGapperList(self, TickerIndex, batch_id):
        print('Ticker ' + self.TickerList.loc[TickerIndex, 'ticker'] + ' is a gapper with Current Price ' + str(self.TickerList.loc[TickerIndex, 'CurrentPrice']) + ' and Prior Day Closing Price ' + str(self.TickerList.loc[TickerIndex, 'PriorDayClose']) + ' and vol ' + str(self.ReqIDVol[batch_id]) + ' at ' + str(datetime.now()))
        US_time = datetime.now(timezone('America/New_York'))
        MA30Vol = self.get30MAVol(self.TickerList.loc[TickerIndex, 'ticker'])
        MarketCap = IBapiUSStocksGapperScanner.GetMarketCap(self.TickerList.loc[TickerIndex, 'ticker'])
        FreeFloat = IBapiUSStocksGapperScanner.GetFreeFloat(self.TickerList.loc[TickerIndex, 'ticker'])
        # sql = "INSERT IGNORE INTO fdata_us_gapper_list (CaptureDate, ticker, Sector, Industry, PriorDayClose, CurrentPrice, 30MA_Vol, Today_Vol, MarketCap, FreeFloat, BidAskSpread, FirstCaptureDatetime, FirstCapturePrice) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        # val = (US_time, self.TickerList.loc[TickerIndex, 'ticker'], self.TickerList.loc[TickerIndex, 'Sector'], self.TickerList.loc[TickerIndex, 'Industry'], self.TickerList.loc[TickerIndex, 'PriorDayClose'], self.TickerList.loc[TickerIndex, 'CurrentPrice'], MA30Vol, self.ReqIDVol[batch_id], MarketCap, FreeFloat, 0.1, US_time, self.TickerList.loc[TickerIndex, 'CurrentPrice'])
        sql = "INSERT INTO fdata_us_gapper_list (CaptureDate, ticker, Sector, Industry, PriorDayClose, CurrentPrice, 30MA_Vol, Today_Vol, MarketCap, FreeFloat, BidAskSpread, FirstCaptureDatetime, FirstCapturePrice) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE CurrentPrice = %s, 30MA_Vol = %s, Today_Vol = %s"
        val = (US_time, self.TickerList.loc[TickerIndex, 'ticker'], self.TickerList.loc[TickerIndex, 'Sector'], self.TickerList.loc[TickerIndex, 'Industry'], self.TickerList.loc[TickerIndex, 'PriorDayClose'], self.TickerList.loc[TickerIndex, 'CurrentPrice'], MA30Vol, self.ReqIDVol[batch_id], MarketCap, FreeFloat, 0.1, US_time, self.TickerList.loc[TickerIndex, 'CurrentPrice'], self.TickerList.loc[TickerIndex, 'CurrentPrice'], MA30Vol, self.ReqIDVol[batch_id])
        mycursor = self.mydb.cursor()
        mycursor.execute(sql, val)
        self.mydb.commit()
        self.RemoveTier1Ticker(self.TickerList.loc[TickerIndex, 'ticker'])
        print('Ticker ' + self.TickerList.loc[TickerIndex, 'ticker'] + ' added to gapper list')
        self.UpdateGoogleNews(self.TickerList.loc[TickerIndex, 'ticker'], US_time)

    def UpdateGoogleNews(self, ticker, CaptureDate):
        pass
    
    # def UpdateGoogleNews(self, ticker, CaptureDate):
    #     try:
    #         # googlenews=GoogleNews(start='08/10/2021',end='08/11/2021')
    #         prior_day = CaptureDate - timedelta(days=1)
    #         # print('Capture Date is ' + str(CaptureDate.strftime("%m/%d/%Y")))
    #         # print('prior_day is ' + str(prior_day.strftime("%m/%d/%Y")))
    #         googlenews=GoogleNews(start=prior_day.strftime("%m/%d/%Y"),end=CaptureDate.strftime("%m/%d/%Y"))
    #         googlenews.search(ticker)
    #         result=googlenews.result()
    #         df=pd.DataFrame(result)
    #         # print(df)
    #         df['ticker'] = ticker
    #         df['date desc order'] = 0
    #         df.loc[df['date'].str.contains("min"), 'date desc order'] = 3
    #         df.loc[df['date'].str.contains("hour"), 'date desc order'] = 2
    #         df.loc[df['date'].str.contains("day"), 'date desc order'] = 1
    #         df.sort_values(by=['date desc order', 'datetime'],  inplace=True, ascending=False)
            
    #         # print(df)
        
    #         for index, row in df.iterrows():
            
    #             sql = "INSERT INTO fdata_us_gapper_list_news (CaptureDate, ticker, title, media, date, datetime, news_desc, link) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE media = %s, date = %s, datetime = %s, news_desc = %s, link = %s"
    #             val = (CaptureDate, row['ticker'], row['title'], row['media'], row['date'], row['datetime'], row['desc'], row['link'], row['media'], row['date'], row['datetime'], row['desc'], row['link'])
    #             mycursor = self.mydb.cursor()
    #             mycursor.execute(sql, val)
    #             self.mydb.commit()
            
    #         print('News for ticker ' + ticker + ' uploaded')    

    #     except Exception:
    #         print('Error in updating news for ticker ' + ticker)    


    def UpdateHistoricalPricesOfTicker(self, batch_id):
        TickerIndex = self.TickerIndexOffset[batch_id] * self.BaseReqIDCount + batch_id
        df = pd.DataFrame(self.data[batch_id])
        print('In UpdateHistoricalPricesOfTicker, batch_id is ' + str(batch_id) + ' and df is')
        print(df)
        df['date'] = pd.to_datetime(df['date']).dt.tz_localize(IBapiUSStocksDayEndHistoricalDataReader.LocalTimeZone)
        df['DateTime'] = df.apply(lambda x: x['date'].tz_convert(IBapiUSStocksDayEndHistoricalDataReader.MarketTimeZone), axis = 1)
        # df.to_csv(r'd:\temp\HistoricalPrice' + str(batch_id) + '.csv')
        
        
        # print('In UpdateHistoricalPricesOfTicker, df is')
        # print(df)
        # uploadcount = 0
        for index, row in df.iterrows():
            # sql = "INSERT IGNORE INTO fdata_price_30min_ib (ticker, DataType, timeframe, DateTime, high, low, open, close, vol) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            # val = (row['ticker'], 'TRADES', '30 mins', row['DateTime'], row['high'], row['low'], row['open'], row['close'], row['volume'])
            sql = "INSERT INTO finance_fdata_price_30min_ib.fdata_price_30min_ib (ticker, DataType, timeframe, DateTime, high, low, open, close, vol) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE high = %s, low = %s, open = %s, close = %s, vol = %s"
            val = (row['ticker'], 'TRADES', '30 mins', row['DateTime'], row['high'], row['low'], row['open'], row['close'], row['volume'], row['high'], row['low'], row['open'], row['close'], row['volume'])
            ticker = row['ticker']
            mycursor = self.mydb.cursor()
            mycursor.execute(sql, val)
            self.mydb.commit()
            # uploadcount = uploadcount + 1
            # print('For ticker ' + row['ticker'] + ', ' + str(uploadcount) + ' records of 30mins data uploaded')
        print('Historical 30mins bar data uploaded for ticker ' + str(df['ticker'].iloc[0]))
        
        # for d in self.data[batch_id]:
        #     sql = "INSERT IGNORE INTO fdata_price_30min_ib (ticker, DataType, timeframe, DateTime, high, low, open, close, vol) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        #     val = (self.TickerDict[batch_id], 'TRADES', '30 mins', self.TickerList.loc[TickerIndex, 'PriorDayClose'], self.TickerList.loc[TickerIndex, 'CurrentPrice'], MA30Vol, self.ReqIDVol[batch_id], MarketCap, FreeFloat, 0.1, US_time, self.TickerList.loc[TickerIndex, 'CurrentPrice'])
        #     mycursor = self.mydb.cursor()
        #     mycursor.execute(sql, val)
        #     self.mydb.commit()
            
        pass


    def getHistoricalPricesOfTicker(self, ticker):
        sql = "SELECT *, DATE(DateTime) AS ValueDate FROM `fdata_price_30min_ib` WHERE DateTime >= '" + self.BeginDateOf30Days.strftime("%Y-%m-%d") + "' AND DateTime < '" + self.TodayUSDate.strftime("%Y-%m-%d") + "' AND ticker = '" + ticker + "' AND DataType = 'TRADES'"
        # print('In getHistoricalPricesOfTicker')
        # print(sql)
        dbcon = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_30MIN_IB)
        # HistoricalPrices = pd.read_sql_query(sql, self.dbcon)
        HistoricalPrices = pd.read_sql_query(sql, dbcon)
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

    def GetMarketCap(ticker):
        t = yf.Ticker(ticker)
        try:
            MarketCap = float(t.info['marketCap'])

            # sql = "INSERT INTO fdata_us_gapper_list_news (CaptureDate, ticker, title, media, date, datetime, news_desc, link) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE media = %s, date = %s, datetime = %s, news_desc = %s, link = %s"
            # val = (CaptureDate, row['ticker'], row['title'], row['media'], row['date'], row['datetime'], row['desc'], row['link'], row['media'], row['date'], row['datetime'], row['desc'], row['link'])
            # mycursor = self.mydb.cursor()
            # mycursor.execute(sql, val)
            # self.mydb.commit()

            return MarketCap
        except Exception:
            return 0.0
    
    def GetFreeFloatRatio(ticker):
        t = yf.Ticker(ticker)
        try:
            return float(t.info['floatShares'])/float(t.info['sharesOutstanding'])
        except Exception:
            return 0.0
    
    def GetFreeFloat(ticker):
        t = yf.Ticker(ticker)
        try:
            return float(t.info['floatShares'])
        except Exception:
            return 0.0

    def TickerIndexOffsetIncrement(self, batch_id):
        if batch_id < self.BaseReqIDCount:
            self.TickerIndexOffset[batch_id] = self.TickerIndexOffset[batch_id] + 1
            if(self.TickerIndexOffset[batch_id] * self.BaseReqIDCount + batch_id >= self.TickerListLength):
                self.TickerIndexOffset[batch_id] = 0
            self.ScanDoneCount = self.ScanDoneCount + 1

            # print('self.TickerIndexOffset for batch_id ' + str(batch_id) + ' is ' + str(self.TickerIndexOffset[batch_id]))
        elif batch_id >= self.AllReqIDCount - IBapiUSStocksGapperScanner.ShortListReqIDCount:
            sub_batch_id = batch_id + IBapiUSStocksGapperScanner.ShortListReqIDCount - self.AllReqIDCount
            self.GapperTickerIndexOffset[sub_batch_id] = self.GapperTickerIndexOffset[sub_batch_id] + 1
            GapperList = self.getGapperList()
            if GapperList is None:
                GapperListLen = 0
            else:
                GapperListLen = len(GapperList)
            if(self.GapperTickerIndexOffset[sub_batch_id] * IBapiUSStocksGapperScanner.ShortListReqIDCount + sub_batch_id >= GapperListLen):
                self.GapperTickerIndexOffset[sub_batch_id] = 0
            else:
                self.ReqIDIdle[batch_id] = True
                self.ReqMode[batch_id] = 0


class IBapiUSStocksDayEndHistoricalDataReader(IBapiDataReader):
    RequestIDRange = [1000, 1049]
    # DataItems = ['TRADES','BID','ASK']
    # DataItems = ['BID','ASK']
    DataItems = ['TRADES']
    LocalTimeZone = 'Europe/London'
    MarketTimeZone = 'America/New_York'
    
    def __init__(self, TickerList, BarSize, HistoricalPeriod, DataEndDate, RequestID_Range = RequestIDRange, Data_Items = DataItems, TickerPerBatch = 6000, StartingTickerBatchID = 0, DatafilePath = None):
        super().__init__(RequestID_Range)
        self.Data_Items = Data_Items
        self.TickerList = TickerList
        # self.AddReqIDAndBatchID()
        self.BarSize = BarSize
        self.HistoricalPeriod = HistoricalPeriod
        self.DataEndDate = DataEndDate
        self.DataEndDateString = datetime.strptime(DataEndDate + " 23:59:59", "%Y%m%d %H:%M:%S")
        self.TickerPerBatch = TickerPerBatch
        self.StartingTickerBatchID = StartingTickerBatchID
        self.DatafilePath = DatafilePath
        self.InitiateProcess()
            
    def ExportDatafile(price_df, tickererror_df, DatafilePath, DataEndDate, BarSize, HistoricalPeriod, batch_id, Dataitem = ""):
        print("Going to export data file")
        print(price_df)
        FilePath = DatafilePath + "EquityIntraDay1d_XUSA_" + DataEndDate + " " + BarSize+ " " + HistoricalPeriod + " " + Dataitem + " batch " + str(batch_id) + ".csv"
        price_df.to_csv(FilePath, index=False)
        # IBapiUSStocksDayEndHistoricalDataReader.WriteDBExportScript(DatafilePath, FilePath, "fdata_price_30min_IB")
        AppendDBExportScript(DatafilePath, FilePath, "fdata_price_dayend_IB")
        
        if len(tickererror_df) > 0:
            print(tickererror_df)
            FilePath = DatafilePath + "EquityIntraDay1d_XUSA_" + DataEndDate + " " + BarSize+ " " + HistoricalPeriod + " " + Dataitem + " batch " + str(batch_id) + " Tickers with error.csv"
            with open(FilePath, 'a') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                wr.writerow(tickererror_df)    
        
    def AddReqIDAndBatchID(self, df):
        df.reset_index(inplace=True, drop=True)
        req_id_count = IBapiUSStocksDayEndHistoricalDataReader.RequestIDRange[1] - IBapiUSStocksDayEndHistoricalDataReader.RequestIDRange[0] + 1
        df['ticker id'] = df.index
        df['batch id'] = np.trunc(df['ticker id'] / req_id_count)
        df['req id'] = np.remainder(df['ticker id'], req_id_count) + IBapiUSStocksDayEndHistoricalDataReader.RequestIDRange[0]
        self.BatchIDCount = len(df[['batch id']].drop_duplicates())
        return df

    def RunProcess(self, IBProcessHub):

        j = self.StartingTickerBatchID
        i = self.TickerPerBatch * (j)
        TotalTickerBatchCount = math.ceil(len(self.TickerList) / self.TickerPerBatch)
        TickersBatch = self.TickerList.loc[i:i+self.TickerPerBatch-1]
        while len(TickersBatch) > 0:
            
            print('going to run ticker batch id ' + str(j) + ' for tickers')
            print(TickersBatch)
            
            TickersBatch = self.AddReqIDAndBatchID(TickersBatch)

            # self.InitiateProcess()
            # for contract_name in self.TickerList:
            for data_item in self.Data_Items:
                self.InitiateProcess()
                for batch_id in range(self.BatchIDCount):
                    TickerListInCurrentBatch = TickersBatch[TickersBatch['batch id'] == batch_id]
                    # TickerListInCurrentBatch.to_csv(r'd:\temp\TickerListInCurrentBatch.csv')
                    self.CurrentBatchID = batch_id
                    self.TickerDict = {}
                    for index, row in TickerListInCurrentBatch.iterrows():
                        self.TickerDict[row['req id']] = row['symbol']
                # for data_item in self.Data_Items:
                    self.clearCache()
                    self.Request_Data_Item = data_item
                    
                    # DataEndTime = self.DataEndDateString.strftime("%Y%m%d") + " 24:00:00"
                    DataEndTime = self.DataEndDateString.strftime("%Y%m%d") + "-24:00:00"
        
                    for index, row in TickerListInCurrentBatch.iterrows():
                        
                        contract = Contract()
                        contract.symbol = row['symbol']
                        contract.secType = row['secType']
                        contract.exchange = row['exchange']
                        contract.currency = row['currency']
                        if not row['primaryExchange'] == 'NONE':
                            contract.primaryExchange = row['primaryExchange']
                        # if not np.isnull(row['primaryExchange']):
                            # contract.primaryExchange = row['primaryExchange']
            
                        IBProcessHub.reqHistoricalData(row['req id'], contract, DataEndTime, self.HistoricalPeriod, self.BarSize, self.Request_Data_Item, 0, 1, False, [])
                        
                    # time.sleep(20) 
                    WaitTime = 5
                    if self.HistoricalPeriod == "2 D":
                        MaxWaitTime = 30
                    else:
                        MaxWaitTime = 120
                    StaleCount = 0
                    Prior_Batch_ID = 0
                    Prior_TickerDownloadCompleteCount = 0
                    while (self.TickerDownloadCompleteCount < len(TickerListInCurrentBatch)):
                        if (batch_id == Prior_Batch_ID) and (self.TickerDownloadCompleteCount == Prior_TickerDownloadCompleteCount):
                            StaleCount = StaleCount + 1
                        else:
                            StaleCount = 0
                        if StaleCount > 20:
                            print('ticker batch id ' + str(j) + '/' + str(TotalTickerBatchCount) + ', request batch id ' + str(batch_id) + '/' + str(self.BatchIDCount) + ', ticker completed '+ str(self.TickerDownloadCompleteCount) + '/' + str(len(TickerListInCurrentBatch)) + ' to be skipped as stale too long at ' + str(datetime.now()))
                            self.TickerDownloadCompleteCount = len(TickerListInCurrentBatch)
                        else:
                            print('waiting for ' + data_item + ' data, ticker batch id ' + str(j) + '/' + str(TotalTickerBatchCount) + ', request batch id ' + str(batch_id) + '/' + str(self.BatchIDCount) + ', ticker completed '+ str(self.TickerDownloadCompleteCount) + '/' + str(len(TickerListInCurrentBatch)) + ' at ' + str(datetime.now()))
                            # df = pd.DataFrame(self.data)
                            # df.to_csv(r'd:\temp\df.csv')
                            # time.sleep(5) #Sleep interval to allow time for incoming price data
                            time.sleep(WaitTime) #Sleep interval to allow time for incoming price data
                            if (len(TickerListInCurrentBatch) - self.TickerDownloadCompleteCount <= 5):
                                WaitTime = 5
                            else:
                                WaitTime = WaitTime * 2
                                if WaitTime > MaxWaitTime:
                                    WaitTime = MaxWaitTime
                            Prior_Batch_ID = batch_id
                            Prior_TickerDownloadCompleteCount = self.TickerDownloadCompleteCount
                                
                            
                    df = pd.DataFrame(self.data)
                    if len(df) > 0:
                        df = self.StandardiseColumns(df, data_item, self.BarSize)
                        self.PricesData = self.PricesData.append(df)
                    
                    if len(self.TickersWithErrorInThisIteration) > 0:
                        print('TickersWithErrorInThisIteration is')
                        print(self.TickersWithErrorInThisIteration)
                        for t in self.TickersWithErrorInThisIteration:
                            if not t in self.TickersWithError:
                                self.TickersWithError.append(t)
                    
                if self.DatafilePath is not None:
                    IBapiUSStocksDayEndHistoricalDataReader.ExportDatafile(self.PricesData, self.TickersWithError, self.DatafilePath, self.DataEndDate, self.BarSize, self.HistoricalPeriod, j, Dataitem = data_item)
                        
                # print('PricesData is ')
                # print(self.PricesData)
                # self.PricesData.to_csv(r'd:\temp\IB_price_data.csv')
                if len(self.TickersWithError) > 0:
                    print('TickersWithError is')
                    print(self.TickersWithError)
                
            i = i + self.TickerPerBatch
            j = j + 1
            TickersBatch = self.TickerList.loc[i:i+self.TickerPerBatch-1]
                
        return [self.PricesData, self.TickersWithError]
        # return None    

    def StandardiseColumns(self, df,data_item,BarSize):
        df = df.reset_index()
        # df['date'] = pd.to_datetime(df['date']).dt.tz_localize(IBapiUSStocksDayEndHistoricalDataReader.LocalTimeZone)
        # df['DateTime'] = df.apply(lambda x: x['date'].tz_convert(IBapiUSStocksDayEndHistoricalDataReader.MarketTimeZone), axis = 1)
        df['DateTime'] = df['date'] 
        # df['timeframe'] = BarSize
        # df['src'] = "IB,hist"
        df['DataType'] = data_item
        try:
            df = df.rename(columns = {'volume': 'vol'}, inplace = False).drop(columns=['date', 'barCount', 'average'], errors='ignore')
        except Exception:
            print("in StandardiseColumns, before column rename and drop")
            print(df)
            df = pd.DataFrame()
        try:
            # df = df[['ticker', 'DataType', 'timeframe', 'DateTime', 'high', 'low', 'open', 'close', 'vol', 'src']]
            df = df[['ticker', 'DataType', 'DateTime', 'high', 'low', 'open', 'close', 'vol']]
        except Exception:
            print("in StandardiseColumns, before picking column")
            print(df)
            df = pd.DataFrame()
        return df
        
    
    def InitiateProcess(self):
        super().InitiateProcess()
        self.PricesData =  pd.DataFrame()
        self.TickersWithError = []
        self.clearCache()
        pass
    
    def clearCache(self):
        super().clearCache()
        self.TickerDownloadCompleteCount = 0
        self.data = []
        self.TickersWithErrorInThisIteration = []
        # self.df = pd.DataFrame()
        self.Request_Data_Item = ""
        self.DownloadError = False
        # self.DownloadComplete = False
        
    def historicalData(self, reqId:int, bar: BarData):
        d = vars(bar)
        # ticker = self.TickerList.loc[(self.TickerList['batch id'] == self.CurrentBatchID) & (self.TickerList['req id'] == reqId)][0]['symbol']
        d['ticker'] = self.TickerDict[reqId]
        self.data.append(d)
# 		print("HistoricalData. ReqId:", reqId, "BarData.", bar)
        pass
        
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        self.TickerDownloadCompleteCount = self.TickerDownloadCompleteCount + 1

        # print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end, " for ", self.Request_Data_Item)

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)
        print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)
        if not self.TickerDict[reqId] in self.TickersWithErrorInThisIteration:
            self.TickersWithErrorInThisIteration.append(self.TickerDict[reqId])
            self.TickerDownloadCompleteCount = self.TickerDownloadCompleteCount + 1
            
        # self.DownloadError = True        