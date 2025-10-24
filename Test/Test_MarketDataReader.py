# -*- coding: utf-8 -*-
"""
Created on Sun Apr  4 00:55:53 2021

@author: Henry Cheung
"""


from InvestmentAnalytics.MarketDataReader import DailySpotPriceReader
from datetime import date, datetime, timedelta
import pandas as pd

StartDate = datetime(2020, 1, 1)
# StartDate = datetime(2021, 1, 4)
EndDate = datetime(2021, 1, 15)
# MarketList = ['XUSA']
MarketList = ['XUSA', 'XHKG']
# TickerFilter = {'XUSA':['AAPL', 'MSFT'],'XHKG':['0700.HK', '0005.HK']}

# d = DailySpotPriceReader(StartDate, EndDate, MarketList, TickerFilter=TickerFilter)
print(datetime.now())
d = DailySpotPriceReader(StartDate, EndDate, MarketList, GPUMode=True)
# d = DailySpotPriceReader(StartDate, EndDate, MarketList, GPUMode=True, ExcludeETF = False)
# d = DailySpotPriceReader(StartDate, EndDate, MarketList, GPUMode=False)


print(datetime.now())
print(d.StartDate.strftime("%Y-%m-%d"))
# print(d.SpotPrices)
print(d.DataMatrix)
print("TickerIDMapping is ")
print(d.TickerIDMapping)

print("DateIDMapping is ")
print(d.DateIDMapping)

# df = d.SpotPrices.loc[d.SpotPrices['Market'] == 'XUSA']
# print(df)


