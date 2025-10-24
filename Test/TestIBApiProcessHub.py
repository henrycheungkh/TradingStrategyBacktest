# -*- coding: utf-8 -*-
"""
Created on Sat May 22 23:06:19 2021

@author: Henry Cheung
"""

import numpy as np
import pandas as pd
from datetime import datetime
from InvestmentAnalytics.IB.IBApiProcessHub import RunIBApiProcessHub
from InvestmentAnalytics.IB.IBApiProcess import *


# ContractList = {"NQ":[{"secType":"FUT", "exchange":"GLOBEX", "currency":"USD", "lastTradeDateOrContractMonth":"202106"}, {"LocalTimeZone":'Europe/London', "MarketTimeZone":'US/Central'}]}

# # BarSize = "10 secs"
# BarSize = "1 min"
# HistoricalPeriod = "3 D"
# # DataEndTime = "20210510 24:00:00"
# DataEndDate = datetime.strptime("10/05/2021 23:59:59", "%d/%m/%Y %H:%M:%S")

# process = IBapiFuturesHistoricalDataReader(ContractList, BarSize, HistoricalPeriod, DataEndDate)
# # print(process)
# # process.RunProcess()
# RunIBApiProcessHub([process])



# TickerList = pd.DataFrame({'symbol':['IBKR', 'MSFT'],'secType':['STK','STK'],'currency':['USD','USD'],'exchange':['ISLAND','SMART'],'primaryExchange':['NONE','ISLAND']})
# TickerList = pd.DataFrame({'symbol':['IBKR', 'MSFT'],'secType':['STK','STK'],'currency':['USD','USD'],'exchange':['ISLAND','SMART'],'primaryExchange':['NONE','NONE']})
# TickerList = pd.DataFrame({'symbol':['IBKR', 'MSFT'],'secType':['STK','STK'],'currency':['USD','USD'],'exchange':['SMART','SMART'],'primaryExchange':['NONE','NONE']})
# TickerList = pd.DataFrame({'symbol':['IBKR', 'MSFT', 'AMC'],'secType':['STK','STK','STK'],'currency':['USD','USD','USD'],'exchange':['SMART','SMART','SMART'],'primaryExchange':['NONE','NONE','NONE']})
# TickerList = pd.DataFrame({'symbol':['MSFT'],'secType':['STK'],'currency':['USD'],'exchange':['SMART'],'primaryExchange':['ISLAND']})
# TickerList = pd.DataFrame({'symbol':['AMC'],'secType':['STK'],'currency':['USD'],'exchange':['SMART'],'primaryExchange':['ISLAND']})
TickerList = pd.DataFrame({'symbol':['AMC'],'secType':['STK'],'currency':['USD'],'exchange':['SMART'],'primaryExchange':['NONE']})
# TickerList = pd.DataFrame({'symbol':['AGRO'],'secType':['STK'],'currency':['USD'],'exchange':['SMART'],'primaryExchange':['ISLAND']})
# TickerList = pd.DataFrame({'symbol':['AWH'],'secType':['STK'],'currency':['USD'],'exchange':['SMART'],'primaryExchange':['NONE']})
# TickerList = pd.DataFrame({'symbol':['APLS'],'secType':['STK'],'currency':['USD'],'exchange':['SMART'],'primaryExchange':['ISLAND']})




# TickerList = pd.DataFrame({'symbol':['BF-B'],'secType':['STK'],'currency':['USD'],'exchange':['SMART'],'primaryExchange':['ISLAND']})


# BarSize = "10 secs"
# BarSize = "1 min"
BarSize = "30 mins"
HistoricalPeriod = "2 D"
# DataEndTime = "20210510 24:00:00"
# DataEndDate = datetime.strptime("13/07/2021 23:59:59", "%d/%m/%Y %H:%M:%S")
DataEndDate = "20210728"
# TickerList['ticker id'] = TickerList.index
# TickerList['batch id'] = np.trunc(TickerList['ticker id'] / 3000)
# TickerList['req id'] = np.remainder(TickerList['ticker id'], 3000) + 1000
# print(TickerList)

process = IBapiUSStocksHistoricalDataReader(TickerList, BarSize, HistoricalPeriod, DataEndDate)
# print(process)
# process.RunProcess()
RunIBApiProcessHub([process])




# TickerList = pd.DataFrame({'symbol':['AMC'],'secType':['STK'],'currency':['USD'],'exchange':['SMART'],'primaryExchange':['NONE']})


# # BarSize = "10 secs"
# # BarSize = "1 min"
# BarSize = "30 mins"
# HistoricalPeriod = "2 D"
# # DataEndTime = "20210510 24:00:00"
# DataEndDate = datetime.strptime("13/07/2021 23:59:59", "%d/%m/%Y %H:%M:%S")
# # TickerList['ticker id'] = TickerList.index
# # TickerList['batch id'] = np.trunc(TickerList['ticker id'] / 3000)
# # TickerList['req id'] = np.remainder(TickerList['ticker id'], 3000) + 1000
# # print(TickerList)

# process = IBapiUSStocksHistoricalDataReader(TickerList, BarSize, HistoricalPeriod, DataEndDate)
# # print(process)
# # process.RunProcess()
# RunIBApiProcessHub([process])



