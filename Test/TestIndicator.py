# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 01:20:39 2021

@author: Henry Cheung
"""


from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import pymysql
import InvestmentAnalytics.Config as Config

from InvestmentAnalytics.MarketDataReader import IBFuturesPriceReader, FuturesPriceAnalysisContext

from InvestmentAnalytics.Indicator.IndicatorSMA import IndicatorSMA

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

indicator = IndicatorSMA(AnalysisContext)
indicator_values = indicator.indicator_values

print(indicator_values)



