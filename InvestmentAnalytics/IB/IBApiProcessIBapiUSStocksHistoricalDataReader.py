# -*- coding: utf-8 -*-
"""
Created on Sun May 16 00:46:02 2021

@author: Henry Cheung
"""
import InvestmentAnalytics.Config as Config
from InvestmentAnalytics.DBUtil import AppendDBExportScript
from InvestmentAnalytics.IB.IBApiProcess import IBapiDataReader

# from ibapi.client import EClient
# from ibapi.wrapper import EWrapper
from ibapi.contract import *
from ibapi.common import *
import pandas as pd
import numpy as np
import time
from datetime import date, datetime, timedelta
import math
import csv
# import os
from pytz import timezone
# import pymysql
# import mysql.connector
# import yfinance as yf

class IBapiUSStocksHistoricalDataReader(IBapiDataReader):
    RequestIDRange = [1000, 1049]
    DataItems = ['TRADES','BID','ASK']
    # DataItems = ['BID','ASK']
    # DataItems = ['TRADES']
    # LocalTimeZone = 'Europe/London'
    # LocalTimeZone = os.getenv('TradeAnalysis_LocalTimezone')
    LocalTimeZone = Config.CONFIG_LOCAL_TIMEZONE
    MarketTimeZone = 'America/New_York'
    BarSizeShortLabel = {"30 mins":"30min", "1 min":"1min", "1 day":"dayend"}
    
    def __init__(self, TickerList, BarSize, HistoricalPeriod, DataEndDate, RequestID_Range = RequestIDRange, Data_Items = DataItems, TickerPerBatch = 6000, StartingTickerBatchID = 0, DatafilePath = None):
        super().__init__(RequestID_Range)
        self.Data_Items = Data_Items
        self.TickerList = TickerList
        # self.AddReqIDAndBatchID()
        self.BarSize = BarSize
        # if BarSize == "1 day":
        #     # self.Data_Items.append('ADJUSTED_LAST')
        #     self.Data_Items = ['ADJUSTED_LAST']
        #     print('self.Data_Items is ' + str(self.Data_Items))
        self.HistoricalPeriod = HistoricalPeriod
        self.DataEndDate = DataEndDate
        self.DataEndDateString = datetime.strptime(DataEndDate + "-23:59:59", "%Y%m%d-%H:%M:%S")
        self.TickerPerBatch = TickerPerBatch
        self.StartingTickerBatchID = StartingTickerBatchID
        self.DatafilePath = DatafilePath
        self.DataEndTime = self.DataEndDateString.strftime("%Y%m%d") + "-24:00:00"
        self.TickersTryingOtherExchange = []
        self.InitiateProcess()
            
    def ExportDatafile(price_df, tickererror_df, DatafilePath, DataEndDate, BarSize, HistoricalPeriod, batch_id, Dataitem = ""):
        print("Going to export data file")
        print(price_df)
        FilePath = DatafilePath + "EquityIntraDay" + IBapiUSStocksHistoricalDataReader.BarSizeShortLabel[BarSize] + "_XUSA_" + DataEndDate + " " + BarSize+ " " + HistoricalPeriod + " " + Dataitem + " batch " + str(batch_id) + ".csv"
        price_df.to_csv(FilePath, index=False)
        # IBapiUSStocksHistoricalDataReader.WriteDBExportScript(DatafilePath, FilePath, "fdata_price_30min_IB")
        AppendDBExportScript(DatafilePath, FilePath, "fdata_price_" + IBapiUSStocksHistoricalDataReader.BarSizeShortLabel[BarSize] + "_IB")
        
        if len(tickererror_df) > 0:
            print(tickererror_df)
            FilePath = DatafilePath + "EquityIntraDay" + IBapiUSStocksHistoricalDataReader.BarSizeShortLabel[BarSize] + "_XUSA_" + DataEndDate + " " + BarSize+ " " + HistoricalPeriod + " " + Dataitem + " batch " + str(batch_id) + " Tickers with error.csv"
            with open(FilePath, 'a') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                wr.writerow(tickererror_df)    
        
    def AddReqIDAndBatchID(self, df):
        df.reset_index(inplace=True, drop=True)
        req_id_count = IBapiUSStocksHistoricalDataReader.RequestIDRange[1] - IBapiUSStocksHistoricalDataReader.RequestIDRange[0] + 1
        df['ticker id'] = df.index
        df['batch id'] = np.trunc(df['ticker id'] / req_id_count)
        df['req id'] = np.remainder(df['ticker id'], req_id_count) + IBapiUSStocksHistoricalDataReader.RequestIDRange[0]
        self.BatchIDCount = len(df[['batch id']].drop_duplicates())
        return df

    def RunProcess(self, IBProcessHub):
        self.IBProcessHub = IBProcessHub

        j = self.StartingTickerBatchID
        i = self.TickerPerBatch * (j)
        TotalTickerBatchCount = math.ceil(len(self.TickerList) / self.TickerPerBatch)
        TickersBatch = self.TickerList.loc[i:i+self.TickerPerBatch-1]
        
        print('self.DataEndTime is ' + self.DataEndTime)
        
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
                    
                    # DataEndTime = self.DataEndDateString.strftime("%Y%m%d") + "-24:00:00"
        
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
            
                        # IBProcessHub.reqHistoricalData(row['req id'], contract,  "20230428-24:00:00", self.HistoricalPeriod, "1 min", self.Request_Data_Item, 0, 1, False, [])
                        # if row['symbol'] == 'NVDA':
                        #     print('going to call reqHistoricalData for self.Request_Data_Item = ' + str(self.Request_Data_Item))
                        if self.Request_Data_Item == 'ADJUSTED_LAST':
                            IBProcessHub.reqHistoricalData(row['req id'], contract, '', self.HistoricalPeriod, self.BarSize, self.Request_Data_Item, 0, 1, False, [])
                        else:
                            IBProcessHub.reqHistoricalData(row['req id'], contract, self.DataEndTime, self.HistoricalPeriod, self.BarSize, self.Request_Data_Item, 0, 1, False, [])
                        
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
                            print('waiting for ' + self.BarSize + ' ' + data_item + ' data, ticker batch id ' + str(j) + '/' + str(TotalTickerBatchCount) + ', request batch id ' + str(batch_id) + '/' + str(self.BatchIDCount) + ', ticker completed '+ str(self.TickerDownloadCompleteCount) + '/' + str(len(TickerListInCurrentBatch)) + ' at ' + str(datetime.now()))
                            time.sleep(WaitTime) #Sleep interval to allow time for incoming price data
                            if (len(TickerListInCurrentBatch) - self.TickerDownloadCompleteCount <= 5):
                                WaitTime = 5
                            elif (len(TickerListInCurrentBatch) - self.TickerDownloadCompleteCount <= 10):
                                WaitTime = 10
                            else:
                                WaitTime = WaitTime * 2
                                if WaitTime > MaxWaitTime:
                                    WaitTime = MaxWaitTime
                            Prior_Batch_ID = batch_id
                            Prior_TickerDownloadCompleteCount = self.TickerDownloadCompleteCount
                                
                            
                    df = pd.DataFrame(self.data)
                    if len(df) > 0:
                        df = self.StandardiseColumns(df, data_item, self.BarSize)
                        if data_item ==  'ADJUSTED_LAST':
                            df['UploadDate'] = self.DataEndDate
                        # self.PricesData = self.PricesData.append(df)
                        self.PricesData = pd.concat([self.PricesData, df])
                    
                    if len(self.TickersWithErrorInThisIteration) > 0:
                        print('TickersWithErrorInThisIteration is')
                        print(self.TickersWithErrorInThisIteration)
                        for t in self.TickersWithErrorInThisIteration:
                            if not t in self.TickersWithError:
                                self.TickersWithError.append(t)
                    
                if self.DatafilePath is not None:
                    IBapiUSStocksHistoricalDataReader.ExportDatafile(self.PricesData, self.TickersWithError, self.DatafilePath, self.DataEndDate, self.BarSize, self.HistoricalPeriod, j, Dataitem = data_item)
                        
                if len(self.TickersWithError) > 0:
                    print('TickersWithError is')
                    print(self.TickersWithError)
                
            i = i + self.TickerPerBatch
            j = j + 1
            TickersBatch = self.TickerList.loc[i:i+self.TickerPerBatch-1]
                
        self.IBProcessHub = False
        return [self.PricesData, self.TickersWithError]

    def StandardiseColumns(self, df,data_item,BarSize):
        df = df.reset_index()
        df['date'] = pd.to_datetime(df['date']).dt.tz_localize(IBapiUSStocksHistoricalDataReader.LocalTimeZone)
        
        
        if (BarSize == "1 day"):
            df['DateTime'] = df['date']
        else:
            # df['DateTime'] = df.apply(lambda x: x['date'].tz_convert(IBapiUSStocksHistoricalDataReader.MarketTimeZone), axis = 1)
            df['DateTime'] = df.apply(lambda x: x['date'].astimezone(IBapiUSStocksHistoricalDataReader.MarketTimeZone).replace(tzinfo=None), axis = 1)
        df['timeframe'] = BarSize
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
            df = df[['ticker', 'DataType', 'timeframe', 'DateTime', 'high', 'low', 'open', 'close', 'vol']]
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
        try:
            super().error(reqId, errorCode, errorString)
            print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)
            # if ("The contract description specified for " + self.TickerDict[reqId] + " is ambiguous" in errorString):
            if ("ambiguous" in errorString):
                ErrorTickerDetail = self.TickerList.loc[self.TickerList['symbol'] == self.TickerDict[reqId]]

                if (ErrorTickerDetail['primaryExchange'].iloc[0] == 'NONE') and (ErrorTickerDetail['symbol'].iloc[0] not in self.TickersTryingOtherExchange):
                    
                    contract = Contract()
                    contract.symbol = ErrorTickerDetail['symbol'].iloc[0]
                    contract.secType = ErrorTickerDetail['secType'].iloc[0]
                    contract.exchange = ErrorTickerDetail['exchange'].iloc[0]
                    contract.currency = ErrorTickerDetail['currency'].iloc[0]
                    contract.primaryExchange = "ISLAND"
                    # if not np.isnull(row['primaryExchange']):
                        # contract.primaryExchange = row['primaryExchange']
        
                    self.IBProcessHub.reqHistoricalData(reqId, contract, self.DataEndTime, self.HistoricalPeriod, self.BarSize, self.Request_Data_Item, 0, 1, False, [])
                    print("Trying to download " + ErrorTickerDetail['symbol'].iloc[0] + " again with different exchange setting")
                    self.TickersTryingOtherExchange.append(ErrorTickerDetail['symbol'].iloc[0])
                else:
                    if not self.TickerDict[reqId] in self.TickersWithErrorInThisIteration:
                        self.TickersWithErrorInThisIteration.append(self.TickerDict[reqId])
                        self.TickerDownloadCompleteCount = self.TickerDownloadCompleteCount + 1
            else:
                if not self.TickerDict[reqId] in self.TickersWithErrorInThisIteration:
                    self.TickersWithErrorInThisIteration.append(self.TickerDict[reqId])
                    self.TickerDownloadCompleteCount = self.TickerDownloadCompleteCount + 1
        except Exception:
            print("Exception in error()")
            
        # self.DownloadError = True        


