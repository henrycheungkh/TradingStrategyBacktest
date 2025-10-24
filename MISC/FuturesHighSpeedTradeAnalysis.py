# -*- coding: utf-8 -*-
"""
Created on Tue May 11 10:57:15 2021

@author: Henry Cheung
"""
from datetime import datetime
from InvestmentAnalytics.IB.IBFuturesDataReader import GetFuturesData

ContractList = {"NQ":[{"secType":"FUT", "exchange":"GLOBEX", "currency":"USD", "lastTradeDateOrContractMonth":"202106"}, {"LocalTimeZone":'Europe/London', "MarketTimeZone":'US/Central'}]}

# BarSize = "10 secs"
BarSize = "1 min"
HistoricalPeriod = "3 D"
# DataEndTime = "20210510 24:00:00"
DataEndDate = datetime.strptime("10/05/2021 23:59:59", "%d/%m/%Y %H:%M:%S")

# class FuturesStrategyAnalysis():
    

# def MarketOpenLargeVolumeTrendFollowingAnalysis(FuturesData, BarSize):
#     for contract_name in FuturesData:
#         print('in MarketOpenLargeVolumeTrendFollowingAnalysis for ' + contract_name)
#     date (Market timezone) hour
#     pass

FuturesData = GetFuturesData(ContractList, BarSize, HistoricalPeriod, DataEndDate)

print(FuturesData)

# for contract_name in FuturesData:
#     for Request_Data_Item in ['TRADES', 'BID', 'ASK']:
#         print('FuturesData for ' + contract_name + ' ' + Request_Data_Item)
#         print(FuturesData[contract_name][Request_Data_Item])
        
        # csvfilepath = Config.CONFIG_BASE_DatafilePath + '\Futures Dump\Futures Dump ' + contract_name + ' ' + Request_Data_Item + ' ' + BarSize + ' ' + HistoricalPeriod + '.csv'
        # FuturesData[contract_name][Request_Data_Item].to_csv(csvfilepath)
        
# MarketOpenLargeVolumeTrendFollowingAnalysis(FuturesData)
        
        
        
                
                
