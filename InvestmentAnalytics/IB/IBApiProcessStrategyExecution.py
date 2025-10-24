# -*- coding: utf-8 -*-
"""
Created on Sun May 16 00:46:02 2021

@author: Henry Cheung
"""
import InvestmentAnalytics.Config as Config
import InvestmentAnalytics.DBUtil as DBUtil
from InvestmentAnalytics.EmailModule import SendEmail


# from sqlalchemy.sql import text

from InvestmentAnalytics.IB.IBApiProcess import IBapiDataReader

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

def GetTimeInLocalTimezone(ScanningTime, ScanningTimezone):
    ScanningTime = datetime.strptime(date.today().strftime("%d/%m/%Y") + ' ' + str(ScanningTime)[-8:], '%d/%m/%Y %H:%M:%S')
    return timezone(ScanningTimezone).localize(ScanningTime).astimezone(timezone(Config.CONFIG_LOCAL_TIMEZONE))

def isNowInTimePeriod(startTime, endTime, nowTime = datetime.now().astimezone(timezone(Config.CONFIG_LOCAL_TIMEZONE))): 
    # print('nowTime is')
    # print(nowTime)
    if startTime < endTime: 
        return nowTime >= startTime and nowTime <= endTime 
    else: 
        #Over midnight: 
        return nowTime >= startTime or nowTime <= endTime 

class IBapiStrategyExecution(IBapiDataReader):
    RequestIDRange = [1040, 1040]
    # ShortListReqIDCount = 4
    # Tier1ListReqIDCount = 1
    # GapThreshold = 0.04
    # Tier1Threshold = 0.02
    # GapperDollarVolumeThreshold = 50000
    # GapperDollarVolumeThreshold = 500
    PriceTypeToReqModeMapping = {'TRADES':0, 'BID':2, 'ASK':3}

    # def __init__(self, TickerList, HistoricalPrices, BarSize = "1 day", RequestID_Range = RequestIDRange):
    def __init__(self, BarSize = "1 min", RequestID_Range = RequestIDRange):
        if BarSize is None:
            BarSize = "1 min"
        if RequestID_Range is None:
            RequestID_Range = RequestIDRange
        super().__init__(RequestID_Range)
        self.BarSize = BarSize


    def InitiateProcess(self):
        super().InitiateProcess()

        self.clearCache()
        pass
    
    def clearCache(self):
        super().clearCache()
        
    def SpeedUpScanning(self):
        self.TimeWait = 10

    def SpeedDownScanning(self):
        self.TimeWait = self.DefaultTimeWait
    
    def RunProcess(self, IBProcessHub):
        print('*IBapiStrategyExecution: StartRunProcess at ' + str(datetime.now()))
        print()
        self.IBProcessHub = IBProcessHub
        self.clearCache()
        self.StartScanningTimes = []
        self.TriggerTime = []
        self.Triggered = []
        self.EndScanningTimes = []
        self.ScanningTimezone = []
        self.StrategyName = []
        self.StrategyExecutionRowIndex = []
        self.contracts = []
        self.DefaultTimeWait = 60
        self.TimeWait = self.DefaultTimeWait

        self.StrategyExecutionConfig = pd.read_sql("SELECT * FROM strategy_execution_config",con=DBUtil.GetSQLAlchemyEngine())   
        print(self.StrategyExecutionConfig)
        
        for index, row in self.StrategyExecutionConfig.iterrows():
            StartScanningTime = row['StartScanningTime']
            TriggerTime = row['TriggerTime']
            EndScanningTime = row['EndScanningTime']
            ScanningTimezone = row['ScanningTimezone']
            
            self.StartScanningTimes.append(GetTimeInLocalTimezone(StartScanningTime, ScanningTimezone))
            self.TriggerTime.append(GetTimeInLocalTimezone(TriggerTime, ScanningTimezone))
            self.Triggered.append(False)
            self.EndScanningTimes.append(GetTimeInLocalTimezone(EndScanningTime, ScanningTimezone))
            self.ScanningTimezone.append(ScanningTimezone)
            self.StrategyName.append(row['StrategyName'])
            self.StrategyExecutionRowIndex.append(index)

            contract = Contract()
            contract.symbol = row['Ticker']
            contract.secType = "FUT"
            contract.exchange = "CME"
            contract.currency = "USD"
            contract.lastTradeDateOrContractMonth = row['ContractExpiry']   
            
            self.contracts.append(contract)


        # contract = Contract()
        # contract.symbol = "ES"
        # # contract.symbol = "NQ"
        # contract.secType = "FUT"
        # # contract.exchange = "GLOBEX"
        # contract.exchange = "CME"
        # contract.currency = "USD"
        # contract.lastTradeDateOrContractMonth = "202306"        
        
        # while True:
        while True and self.IBProcessHub.Alive:
            # print('*IBapiStrategyExecution: reqMktData')
            # print()
            
            for i in range(len(self.contracts)):
                if isNowInTimePeriod(self.StartScanningTimes[i], self.EndScanningTimes[i]):
                    self.IBProcessHub.reqMktData(self.RequestID_Range[0]+i, self.contracts[i], "", False, False, [])
                else:
                    print('*IBapiStrategyExecution: Not in scanning time yet')
                
            # self.IBProcessHub.reqMktData(self.RequestID_Range[0], contract, "", False, False, [])
            time.sleep(self.TimeWait)

        print('*IBapiStrategyExecution: End RunProcess at ' + str(datetime.now()))
        print()

    def tickPrice(self, reqId, tickType, price, attrib):
        # https://interactivebrokers.github.io/tws-api/tick_types.html

# Tick Name	Tick Id	Description	Delivery Method	Generic tick required
# Bid Size	0	Number of contracts or lots offered at the bid price.	IBApi.EWrapper.tickSize	-
# Bid Price	1	Highest priced bid for the contract.	IBApi.EWrapper.tickPrice	-
# Ask Price	2	Lowest price offer on the contract.	IBApi.EWrapper.tickPrice	-
# Ask Size	3	Number of contracts or lots offered at the ask price.	IBApi.EWrapper.tickSize	-
# Last Price	4	Last price at which the contract traded (does not include some trades in RTVolume).	IBApi.EWrapper.tickPrice	-
# Last Size	5	Number of contracts or lots traded at the last price.	IBApi.EWrapper.tickSize	-
# High	6	High price for the day.	IBApi.EWrapper.tickPrice	-
# Low	7	Low price for the day.	IBApi.EWrapper.tickPrice	-
# Volume	8	Trading volume for the day for the selected contract (US Stocks: multiplier 100).	IBApi.EWrapper.tickSize	-
# Close Price	9	The last available closing price for the previous day. For US Equities, we use corporate action processing to get the closing price, so the close price is adjusted to reflect forward and reverse splits and cash and stock dividends.	IB
        
        if tickType in [1,2,4]:
            # print(f"*IBapiStrategyExecution: tickPrice. reqId: {reqId}, price: {price}, attribs: {attrib}")
            # print(f"*IBapiStrategyExecution: tickPrice. reqId: {reqId}, price: {price}, attribs: {attrib}, tickType: {tickType}")
            # print(f"*IBapiStrategyExecution: tickPrice. reqId: {reqId}, price: {price}, attribs: {attrib}, tickType: {tickType} at " + str(datetime.now()))

            # if (self.StrategyName[reqId - self.RequestID_Range[0]] == 'CorrelationOnSpecificTimeSectionStrategy'):
                # print('ParameterValue1 = ' + str(self.StrategyExecutionConfig.iloc[self.StrategyExecutionRowIndex[reqId - self.RequestID_Range[0]]]['ParameterValue1']))


            if tickType == 4:
                # time_diff = (datetime.now() - self.TriggerTime[reqId - self.RequestID_Range[0]]).total_seconds()
                time_diff = (datetime.now().astimezone(timezone(Config.CONFIG_LOCAL_TIMEZONE)) - self.TriggerTime[reqId - self.RequestID_Range[0]]).total_seconds()
                
                # time_diff = (GetTimeInLocalTimezone(datetime.now(), self.ScanningTimezone[reqId - self.RequestID_Range[0]]) - self.TriggerTime[reqId - self.RequestID_Range[0]]).total_seconds()

                # print(f"*IBapiStrategyExecution: tickPrice. reqId: {reqId}, price: {price}, attribs: {attrib}, tickType: {tickType} at " + str(datetime.now()))

                if (time_diff < 0):
                    print('*IBapiStrategyExecution: time_diff (minutes) = ' + str(time_diff/60))
                    if (time_diff >= -600):
                        self.SpeedUpScanning()
                        if (self.StrategyName[reqId - self.RequestID_Range[0]] == 'CorrelationOnSpecificTimeSectionStrategy'):
                            LowerPrice = self.StrategyExecutionConfig.iloc[self.StrategyExecutionRowIndex[reqId - self.RequestID_Range[0]]]['ParameterValue1']
                            HigherPrice = self.StrategyExecutionConfig.iloc[self.StrategyExecutionRowIndex[reqId - self.RequestID_Range[0]]]['ParameterValue2']
                            MeanReversion = self.StrategyExecutionConfig.iloc[self.StrategyExecutionRowIndex[reqId - self.RequestID_Range[0]]]['ParameterValue3']
                            MeanReversion = (MeanReversion > 0)
                            RangeOffset = (HigherPrice - LowerPrice) * 0.25
                            print(f"*IBapiStrategyExecution: tickPrice. reqId: {reqId}, price: {price}, attribs: {attrib}, tickType: {tickType} at " + str(datetime.now()))
                            if (price > HigherPrice - RangeOffset):
                                print('*IBapiStrategyExecution;' + self.StrategyName[reqId - self.RequestID_Range[0]] + ': Current Price close to trade triggering higher bound of ' + str(HigherPrice) )
                                SendEmail(['henry.cheungkh@gmail.com'], 'Trading Strategy Alert Summary - CorrelationOnSpecificTimeSectionStrategy', 'Current Price close to trade triggering higher bound of ' + str(HigherPrice))
                            elif (price < LowerPrice + RangeOffset):
                                print('*IBapiStrategyExecution;' + self.StrategyName[reqId - self.RequestID_Range[0]] + ': Current Price close to trade triggering lower bound of ' + str(LowerPrice) )
                                SendEmail(['henry.cheungkh@gmail.com'], 'Trading Strategy Alert Summary - CorrelationOnSpecificTimeSectionStrategy', 'Current Price close to trade triggering lower bound of ' + str(LowerPrice))
                            
                if (time_diff >= 0):
                    self.SpeedDownScanning()
                    if not self.Triggered[reqId - self.RequestID_Range[0]]:
                        self.Triggered[reqId - self.RequestID_Range[0]] = True
                        print('*IBapiStrategyExecution: execute at ' + str(datetime.now()))
                        if (self.StrategyName[reqId - self.RequestID_Range[0]] == 'CorrelationOnSpecificTimeSectionStrategy'):
                            # print('ParameterValue1 = ' + str(self.StrategyExecutionConfig.iloc[self.StrategyExecutionRowIndex[reqId - self.RequestID_Range[0]]]['ParameterValue1']))
                            LowerPrice = self.StrategyExecutionConfig.iloc[self.StrategyExecutionRowIndex[reqId - self.RequestID_Range[0]]]['ParameterValue1']
                            HigherPrice = self.StrategyExecutionConfig.iloc[self.StrategyExecutionRowIndex[reqId - self.RequestID_Range[0]]]['ParameterValue2']
                            MeanReversion = self.StrategyExecutionConfig.iloc[self.StrategyExecutionRowIndex[reqId - self.RequestID_Range[0]]]['ParameterValue3']
                            MeanReversion = (MeanReversion > 0)
                            StopLoss = self.StrategyExecutionConfig.iloc[self.StrategyExecutionRowIndex[reqId - self.RequestID_Range[0]]]['ParameterValue4']/10000
                            TakeProfit = self.StrategyExecutionConfig.iloc[self.StrategyExecutionRowIndex[reqId - self.RequestID_Range[0]]]['ParameterValue5']/10000
                            if (price > HigherPrice):
                                if MeanReversion:
                                    print('*IBapiStrategyExecution;' + self.StrategyName[reqId - self.RequestID_Range[0]] + ': shorted when price at ' + str(price) + ' at ' + str(datetime.now()))
                                else:
                                    print('*IBapiStrategyExecution;' + self.StrategyName[reqId - self.RequestID_Range[0]] + ': longed when price at ' + str(price) + ' at ' + str(datetime.now()))
                            elif (price < LowerPrice):
                                if MeanReversion:
                                    print('*IBapiStrategyExecution;' + self.StrategyName[reqId - self.RequestID_Range[0]] + ': longed when price at ' + str(price) + ' at ' + str(datetime.now()))
                                else:
                                    print('*IBapiStrategyExecution;' + self.StrategyName[reqId - self.RequestID_Range[0]] + ': shorted when price at ' + str(price) + ' at ' + str(datetime.now()))
                            else:
                                print('*IBapiStrategyExecution;' + self.StrategyName[reqId - self.RequestID_Range[0]] + ': no trade today. Current price ' + str(price) + ' in range of ' + str(LowerPrice) + ' and ' + str(HigherPrice) + ' at ' + str(datetime.now()))
                        
                
            # print(' at ' + str(datetime.now()))
            # print()
# 		print("tickPrice: " + str(price))
        
    def error(self, reqId: TickerId, errorCode: int, errorStrin: str):
        print("*IBapiStrategyExecution: Error. reqId:", reqId, "Code:", errorCode)
        # print()


      