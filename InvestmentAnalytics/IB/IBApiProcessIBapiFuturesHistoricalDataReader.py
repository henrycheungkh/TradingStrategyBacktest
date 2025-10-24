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
from pytz import timezone
import pymysql
import mysql.connector

class IBapiFuturesHistoricalDataReader(IBapiDataReader):
    RequestIDRange = [10, 19]
    DataItems = ['TRADES','BID','ASK']
    QUARTERLY_CONTRACTS = ['YM', 'ES', 'NQ', 'RTY', 'ZN', 'ZT']
    QUARTER_END_MONTH = ["03", "06", "09", "12"]
    TIME_OUT_MINUTES_THRESHOLD = 10

    def __init__(self, ContractList, BarSize, HistoricalPeriod, DataEndDate, RequestID_Range = RequestIDRange, Data_Items = DataItems):
        super().__init__(RequestID_Range)
        self.Data_Items = Data_Items
        self.ContractList = ContractList
        self.BarSize = BarSize
        self.HistoricalPeriod = HistoricalPeriod
        self.DataEndDate = DataEndDate
        self.InitiateProcess()

    def RunProcess(self, IBProcessHub):
        self.InitiateProcess()
        for contract_name in self.ContractList:
            # if (self.ContractList[contract_name][0]['lastTradeDateOrContractMonth'][-2:] in IBapiFuturesHistoricalDataReader.QUARTER_END_MONTH) or (contract_name not in IBapiFuturesHistoricalDataReader.QUARTERLY_CONTRACTS):
            if (contract_name in IBapiFuturesHistoricalDataReader.QUARTERLY_CONTRACTS) and (self.ContractList[contract_name][0]['lastTradeDateOrContractMonth'][-2:] not in IBapiFuturesHistoricalDataReader.QUARTER_END_MONTH):
                print('Skip downloading ' + contract_name + ' for expiry ' + self.ContractList[contract_name][0]['lastTradeDateOrContractMonth'])
            else:
                contract = Contract()
                contract.symbol = contract_name
                contract.secType = self.ContractList[contract_name][0]['secType']
                contract.exchange = self.ContractList[contract_name][0]['exchange']
                contract.currency = self.ContractList[contract_name][0]['currency']
                contract.lastTradeDateOrContractMonth = self.ContractList[contract_name][0]['lastTradeDateOrContractMonth']   
                if "Multiplier" in self.ContractList[contract_name][0]:
                    # print("setting up Multiplier")
                    contract.multiplier = self.ContractList[contract_name][0]['Multiplier']   
        
                for data_item in self.Data_Items:
                    self.clearCache()
                    self.Request_Data_Item = data_item
                    
                    # DataEndTime = self.DataEndDate.strftime("%Y%m%d") + " 24:00:00"
                    DataEndTime = self.DataEndDate.strftime("%Y%m%d") + "-24:00:00"
                    IBProcessHub.reqHistoricalData(self.RequestID_Range[0], contract, DataEndTime, self.HistoricalPeriod, self.BarSize, self.Request_Data_Item, 0, 1, False, [])
                    
                    TimeStartWaiting = datetime.now()
                    TimeWaited = 0
                    # FirstMsgPrinted = False
                    while (len(self.df) == 0) and not self.DownloadError and TimeWaited <= IBapiFuturesHistoricalDataReader.TIME_OUT_MINUTES_THRESHOLD:
                        # print('waiting for data for ' + contract_name + ', expiry ' + contract.lastTradeDateOrContractMonth + ', data item ' + data_item + ' len(self.data) is '+ str(len(self.data))+ ', len(self.df) is '+ str(len(self.df)) + ' and self.DownloadError is ' + str(self.DownloadError) + ' at ' + str(datetime.now()) + ' waited for ' + str(TimeWaited) + ' minutes', end = "\r")
                        print('waiting for data for ' + contract_name + ', expiry ' + contract.lastTradeDateOrContractMonth + ', ' + data_item + ', len(self.data) is '+ str(len(self.data))+ ' at ' + str(datetime.now()) + ' waited for ' + str(TimeWaited) + ' minutes', end = "\r")
                        time.sleep(20) #Sleep interval to allow time for incoming price data
                        TimeWaited = round((datetime.now() - TimeStartWaiting).total_seconds() / 60.0)
                    print('waiting for data for ' + contract_name + ', expiry ' + contract.lastTradeDateOrContractMonth + ', ' + data_item + ', len(self.data) is '+ str(len(self.data))+ ' at ' + str(datetime.now()) + ' waited for ' + str(TimeWaited) + ' minutes')
                    print('waiting for data for ' + contract_name + ', expiry ' + contract.lastTradeDateOrContractMonth + ', ' + data_item + ', len(self.data) is '+ str(len(self.data))+ ' at ' + str(datetime.now()) + ' waited for ' + str(TimeWaited) + ' minutes')
                    if TimeWaited > IBapiFuturesHistoricalDataReader.TIME_OUT_MINUTES_THRESHOLD:
                        print('Time out waiting')
                    
                    if self.DownloadComplete and not self.DownloadError:
                        if (len(self.df) > 0):
                            self.StandardiseColumns(data_item, contract_name, self.ContractList[contract_name][0]['lastTradeDateOrContractMonth'], self.BarSize)
                            self.FuturesData = self.FuturesData.append(self.df)
        return self.FuturesData

    def StandardiseColumns(self,data_item,contract_name,lastTradeDateOrContractMonth,BarSize):
        self.df = self.df.reset_index()
        self.df['date'] = pd.to_datetime(self.df['date']).dt.tz_localize(self.ContractList[contract_name][1]['LocalTimeZone'])
        
        # self.df['tDateTime'] = self.df.apply(lambda x: x['date'].tz_convert(self.ContractList[contract_name][1]['MarketTimeZone']), axis = 1)
        
        # self.df['tDateTime'] = self.df.apply(lambda x: x['date'].astimezone(self.ContractList[contract_name][1]['MarketTimeZone']), axis = 1)   # 09:30:00-05:00
        # self.df['tDateTime'] = self.df.apply(lambda x: x['date'].astimezone(self.ContractList[contract_name][1]['MarketTimeZone']).tz_convert(None), axis = 1)   # 14:30:00
        self.df['tDateTime'] = self.df.apply(lambda x: x['date'].astimezone(self.ContractList[contract_name][1]['MarketTimeZone']).replace(tzinfo=None), axis = 1)   #
        # self.df['tDateTime'] = self.df.apply(lambda x: x['date'].tz_convert(self.ContractList[contract_name][1]['MarketTimeZone']).tz_convert(None), axis = 1)
        # self.df['tDateTime'] = self.df.apply(lambda x: x['date'].dt.tz_locallize(self.ContractList[contract_name][1]['MarketTimeZone']), axis = 1)
        
        
        
        self.df['ticker'] = contract_name
        self.df['instrumenttype'] = "FUT"
        self.df['expiry'] = lastTradeDateOrContractMonth
        self.df['timeframe'] = BarSize
        self.df['src'] = "IB,hist"
        self.df['DataType'] = data_item
        try:
            self.df = self.df.rename(columns = {'volume': 'vol'}, inplace = False).drop(columns=['date', 'barCount', 'average'], errors='ignore')
        except Exception:
            print("in StandardiseColumns, before column rename and drop")
            print(self.df)
            self.df = pd.DataFrame()
        try:
            self.df = self.df[['ticker', 'instrumenttype', 'expiry', 'DataType', 'timeframe', 'tDateTime', 'high', 'low', 'open', 'close', 'vol', 'src']]
        except Exception:
            print("in StandardiseColumns, before picking column")
            print(self.df)
            self.df = pd.DataFrame()
        
    
    def InitiateProcess(self):
        super().InitiateProcess()
        self.FuturesData =  pd.DataFrame()
        self.clearCache()
        pass
    
    def clearCache(self):
        super().clearCache()
        self.data = []
        self.df = pd.DataFrame()
        self.Request_Data_Item = ""
        self.DownloadError = False
        self.DownloadComplete = False
        
    def historicalData(self, reqId:int, bar: BarData):
        self.data.append(vars(bar))
# 		print("HistoricalData. ReqId:", reqId, "BarData.", bar)
        pass
        
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        self.df = pd.DataFrame(self.data)
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df.set_index('date', inplace=True)
        self.DownloadComplete = True
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end, " for ", self.Request_Data_Item)

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)
        print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)
        self.DownloadError = True        


        
