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

class IBapiFuturesHistoricalDataReader2(IBapiDataReader):
    RequestIDRange = [10, 12]
    DataItems = ['TRADES','BID','ASK']
    QUARTERLY_CONTRACTS = ['YM', 'ES', 'NQ', 'RTY', 'ZN', 'ZT']
    QUARTER_END_MONTH = ["03", "06", "09", "12"]
    TIME_OUT_MINUTES_THRESHOLD = 5

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
        TimeOutMinutesThreshold = IBapiFuturesHistoricalDataReader2.TIME_OUT_MINUTES_THRESHOLD
        for contract_name in self.ContractList:
            # if (self.ContractList[contract_name][0]['lastTradeDateOrContractMonth'][-2:] in IBapiFuturesHistoricalDataReader.QUARTER_END_MONTH) or (contract_name not in IBapiFuturesHistoricalDataReader.QUARTERLY_CONTRACTS):
            if (contract_name in IBapiFuturesHistoricalDataReader2.QUARTERLY_CONTRACTS) and (self.ContractList[contract_name][0]['lastTradeDateOrContractMonth'][-2:] not in IBapiFuturesHistoricalDataReader2.QUARTER_END_MONTH):
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
        
                # for data_item in self.Data_Items:
                    
                self.clearCache()
                # self.Request_Data_Item = data_item
                
                # DataEndTime = self.DataEndDate.strftime("%Y%m%d") + " 24:00:00"
                DataEndTime = self.DataEndDate.strftime("%Y%m%d") + "-24:00:00"
                # IBProcessHub.reqHistoricalData(self.RequestID_Range[0], contract, DataEndTime, self.HistoricalPeriod, self.BarSize, self.Request_Data_Item, 0, 1, False, [])
                # print('self.RequestID_Range is ' + str(self.RequestID_Range))
                # print('self.Data_Items is ' + str(self.Data_Items))
                for i in range(len(self.Data_Items)):
                    # print('i = ' + str(i))
                    IBProcessHub.reqHistoricalData(self.RequestID_Range[0] + i, contract, DataEndTime, self.HistoricalPeriod, self.BarSize, self.Data_Items[i], 0, 1, False, [])
                
                TimeStartWaiting = datetime.now()
                TimeWaited = 0
                # FirstMsgPrinted = False
                
                
                # while (len(self.df) == 0) and not self.DownloadError and TimeWaited <= IBapiFuturesHistoricalDataReader2.TIME_OUT_MINUTES_THRESHOLD:
                # while not self.AllDFFilled() and self.NoDownloadError() and TimeWaited <= IBapiFuturesHistoricalDataReader2.TIME_OUT_MINUTES_THRESHOLD:
                while not self.AllDFFilled() and self.NoDownloadError() and TimeWaited <= TimeOutMinutesThreshold:
                    # print('waiting for data for ' + contract_name + ', expiry ' + contract.lastTradeDateOrContractMonth + ', data item ' + data_item + ' len(self.data) is '+ str(len(self.data))+ ', len(self.df) is '+ str(len(self.df)) + ' and self.DownloadError is ' + str(self.DownloadError) + ' at ' + str(datetime.now()) + ' waited for ' + str(TimeWaited) + ' minutes', end = "\r")
                    # print('waiting for data for ' + contract_name + ', expiry ' + contract.lastTradeDateOrContractMonth + ', ' + data_item + ', len(self.data) is '+ str(len(self.data))+ ' at ' + str(datetime.now()) + ' waited for ' + str(TimeWaited) + ' minutes', end = "\r")
                    # print('waiting for data for ' + contract_name + ', expiry ' + contract.lastTradeDateOrContractMonth + ', len(self.data) is '+ str(len(self.data))+ ' at ' + str(datetime.now()) + ' waited for ' + str(TimeWaited) + ' minutes', end = "\r")
                    # print('waiting for data for ' + contract_name + ', expiry ' + contract.lastTradeDateOrContractMonth + ', len(self.data) is '+ str(len(self.data))+ ' at ' + str(datetime.now()) + ' waited for ' + str(TimeWaited) + ' minutes')
                    print('waiting for data for ' + contract_name + ', expiry ' + contract.lastTradeDateOrContractMonth + ', len(self.data) is '+ str(len(self.data[0])) + ';' + str(len(self.data[1])) + ';' + str(len(self.data[2])) + ' at ' + str(datetime.now()) + ' waited for ' + str(TimeWaited) + ' minutes', end = "\r")
                    time.sleep(20) #Sleep interval to allow time for incoming price data
                    TimeWaited = round((datetime.now() - TimeStartWaiting).total_seconds() / 60.0)
                    
                    
                # print('waiting for data for ' + contract_name + ', expiry ' + contract.lastTradeDateOrContractMonth + ', len(self.data) is '+ str(len(self.data))+ ' at ' + str(datetime.now()) + ' waited for ' + str(TimeWaited) + ' minutes')
                # print('waiting for data for ' + contract_name + ', expiry ' + contract.lastTradeDateOrContractMonth + ', len(self.data) is '+ str(len(self.data))+ ' at ' + str(datetime.now()) + ' waited for ' + str(TimeWaited) + ' minutes')
                print('waiting for data for ' + contract_name + ', expiry ' + contract.lastTradeDateOrContractMonth + ', len(self.data) is '+ str(len(self.data[0])) + ';' + str(len(self.data[1])) + ';' + str(len(self.data[2])) + ' at ' + str(datetime.now()) + ' waited for ' + str(TimeWaited) + ' minutes')
                print('waiting for data for ' + contract_name + ', expiry ' + contract.lastTradeDateOrContractMonth + ', len(self.data) is '+ str(len(self.data[0])) + ';' + str(len(self.data[1])) + ';' + str(len(self.data[2])) + ' at ' + str(datetime.now()) + ' waited for ' + str(TimeWaited) + ' minutes')
                # if TimeWaited > IBapiFuturesHistoricalDataReader2.TIME_OUT_MINUTES_THRESHOLD:
                if TimeWaited > TimeOutMinutesThreshold:
                    print('Time out waiting')
                
                # if self.DownloadComplete and not self.DownloadError:
                #     if (len(self.df) > 0):
                #         # self.StandardiseColumns(data_item, contract_name, self.ContractList[contract_name][0]['lastTradeDateOrContractMonth'], self.BarSize)
                #         self.StandardiseColumns(contract_name, self.ContractList[contract_name][0]['lastTradeDateOrContractMonth'], self.BarSize)
                #         self.FuturesData = self.FuturesData.append(self.df)

                if self.AllDownloadComplete() and self.NoDownloadError() and self.AllDFFilled():
                    TimeOutMinutesThreshold = 2
                    self.StandardiseColumns(contract_name, self.ContractList[contract_name][0]['lastTradeDateOrContractMonth'], self.BarSize)
                    for i in range(len(self.Data_Items)):
                        # self.FuturesData = self.FuturesData.append(self.df[i])
                        self.FuturesData = pd.concat([self.FuturesData, self.df[i]])

                            
        return self.FuturesData
    
    def AllDFFilled(self):
        for i in range(len(self.Data_Items)):
            if len(self.df[i]) == 0:
                return False
        return True

    def NoDownloadError(self):
        for i in range(len(self.Data_Items)):
            if self.DownloadError[i]:
                return False
        return True

    def AllDownloadComplete(self):
        for i in range(len(self.Data_Items)):
            if not self.DownloadComplete[i]:
                return False
        return True



    # def StandardiseColumns(self,data_item,contract_name,lastTradeDateOrContractMonth,BarSize):
    def StandardiseColumns(self,contract_name,lastTradeDateOrContractMonth,BarSize):
        for i in range(len(self.Data_Items)):
            self.df[i] = self.df[i].reset_index()
            self.df[i]['date'] = pd.to_datetime(self.df[i]['date']).dt.tz_localize(self.ContractList[contract_name][1]['LocalTimeZone'])
            
            # self.df['tDateTime'] = self.df.apply(lambda x: x['date'].tz_convert(self.ContractList[contract_name][1]['MarketTimeZone']), axis = 1)
            
            # self.df['tDateTime'] = self.df.apply(lambda x: x['date'].astimezone(self.ContractList[contract_name][1]['MarketTimeZone']), axis = 1)   # 09:30:00-05:00
            # self.df['tDateTime'] = self.df.apply(lambda x: x['date'].astimezone(self.ContractList[contract_name][1]['MarketTimeZone']).tz_convert(None), axis = 1)   # 14:30:00
            self.df[i]['tDateTime'] = self.df[i].apply(lambda x: x['date'].astimezone(self.ContractList[contract_name][1]['MarketTimeZone']).replace(tzinfo=None), axis = 1)   #
            # self.df['tDateTime'] = self.df.apply(lambda x: x['date'].tz_convert(self.ContractList[contract_name][1]['MarketTimeZone']).tz_convert(None), axis = 1)
            # self.df['tDateTime'] = self.df.apply(lambda x: x['date'].dt.tz_locallize(self.ContractList[contract_name][1]['MarketTimeZone']), axis = 1)
            
            
            
            self.df[i]['ticker'] = contract_name
            self.df[i]['instrumenttype'] = "FUT"
            self.df[i]['expiry'] = lastTradeDateOrContractMonth
            self.df[i]['timeframe'] = BarSize
            self.df[i]['src'] = "IB,hist"
            # self.df[i]['DataType'] = data_item
            self.df[i]['DataType'] = self.Data_Items[i]
            try:
                self.df[i] = self.df[i].rename(columns = {'volume': 'vol'}, inplace = False).drop(columns=['date', 'barCount', 'average'], errors='ignore')
            except Exception:
                print("in StandardiseColumns, before column rename and drop")
                print(self.df[i])
                self.df[i] = pd.DataFrame()
            try:
                self.df[i] = self.df[i][['ticker', 'instrumenttype', 'expiry', 'DataType', 'timeframe', 'tDateTime', 'high', 'low', 'open', 'close', 'vol', 'src']]
            except Exception:
                print("in StandardiseColumns, before picking column")
                print(self.df[i])
                self.df[i] = pd.DataFrame()
        
    
    def InitiateProcess(self):
        super().InitiateProcess()
        self.FuturesData =  pd.DataFrame()
        self.clearCache()
        pass
    
    def clearCache(self):
        super().clearCache()
        self.data = []
        # self.df = pd.DataFrame()
        self.df = []
        self.DownloadComplete = []
        self.DownloadError = []
        for i in range(len(self.Data_Items)):
            # self.data[i] = []
            # self.df[i] = pd.DataFrame()
            # self.DownloadComplete[i] = False
            # self.DownloadError[i] = False
            self.data.append([])
            self.df.append(pd.DataFrame())
            self.DownloadComplete.append(False)
            self.DownloadError.append(False)
        # self.Request_Data_Item = ""
        # self.DownloadError = False
        # self.DownloadComplete = False

        
    def historicalData(self, reqId:int, bar: BarData):
        # self.data.append(vars(bar))
        self.data[reqId - self.RequestID_Range[0]].append(vars(bar))
# 		print("HistoricalData. ReqId:", reqId, "BarData.", bar)
        pass
        
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        # self.df = pd.DataFrame(self.data)
        # self.df['date'] = pd.to_datetime(self.df['date'])
        # self.df.set_index('date', inplace=True)

        self.df[reqId - self.RequestID_Range[0]] = pd.DataFrame(self.data[reqId - self.RequestID_Range[0]])
        self.df[reqId - self.RequestID_Range[0]]['date'] = pd.to_datetime(self.df[reqId - self.RequestID_Range[0]]['date'])
        self.df[reqId - self.RequestID_Range[0]].set_index('date', inplace=True)


        # self.DownloadComplete = True
        self.DownloadComplete[reqId - self.RequestID_Range[0]] = True
        # print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end, " for ", self.Request_Data_Item)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end, " for ", self.Data_Items[reqId - self.RequestID_Range[0]])

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)
        print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)
        # self.DownloadError = True        
        self.DownloadError[reqId - self.RequestID_Range[0]] = True        


        
