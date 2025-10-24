# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 10:40:24 2021

@author: Henry Cheung
"""


from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import pymysql
import InvestmentAnalytics.Config as Config

from InvestmentAnalytics.MarketDataReader import IBFuturesPriceReader, FuturesPriceAnalysisContext

from InvestmentAnalytics.Strategy.Futures.KeyLevels import KeyLevelContext

pd.set_option('display.max_columns', None)

StartDate = datetime(2021, 3, 1)
EndDate = datetime(2021, 10, 6)
TimeFrame = '1 min'
TickerFilter = None
# TickerFilter = ['CL', 'RTY']
# TickerFilter = ['NQ', 'ES']

AnalysisStartTime = datetime.now()
print('Analysis started at ' + str(AnalysisStartTime))


AnalysisContext = FuturesPriceAnalysisContext(StartDate, EndDate, TimeFrame, TickerFilter = TickerFilter)
MaxTimeID = AnalysisContext.FuturesData.TimeIDMapping['time id'].max()

key_level_context = KeyLevelContext(AnalysisContext)

print('MaxTimeID is ' + str(MaxTimeID))
group_key_levels = key_level_context.GetKeyLevel(MaxTimeID)
group_key_levels = group_key_levels.merge(AnalysisContext.FuturesData.TickerIDMapping, on='ticker id')
print('key levels before MaxTimeID are')
print(group_key_levels)
group_key_levels.to_csv(r'd:\temp\group_key_levels.csv')

AnalysisEndTime = datetime.now()
analysis_minutes_diff = round((AnalysisEndTime - AnalysisStartTime).total_seconds() / 60.0)

print('Analysis ended at ' + str(AnalysisEndTime) + ', and ' + str(analysis_minutes_diff) + ' minutes taken')

