# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 17:55:04 2024

@author: Henry Cheung
"""

from datetime import date, datetime, timedelta

import pandas as pd
import numpy as np
import InvestmentAnalytics.Config as Config
import InvestmentAnalytics.DBUtil as DBUtil

from InvestmentAnalytics.MarketDataReader import IBFuturesPriceReader, FuturesPriceAnalysisContext, FXFuturesPriceAnalysisContext, CryptoPriceAnalysisContext, GetResampledData

pd.set_option('display.max_columns', None) 
        

FileNameSuffix = ''

StartDate = datetime(2022,1,1)
# EndDate = datetime(2024,6,30)
EndDate = datetime(2025,4,24)


# TimeFrame = "1 day"
TimeFrame = "5 mins"
# TimeFrame = "1 min"
# TimeFrame = "10 secs"

# TickerFilter = ['NQ']
# TickerFilter = ['RTY']
# TickerFilter = ['GC']
# TickerFilter = ['CL']
# TickerFilter = ['NQ', 'CL']
TickerFilter = ['GC', 'SI', 'ES', 'NQ', 'YM', 'CL', 'NG']

# FileFolder = "e:\\temp\\"
FileFolder = "j:\\temp\\"
TickerInString = '_'.join(TickerFilter)

if TimeFrame == "1 min":
    AnalysisContext = FuturesPriceAnalysisContext(StartDate, EndDate, TimeFrame, TickerFilter = TickerFilter)
else:
# For non 1min bar
    AnalysisContext = FuturesPriceAnalysisContext(StartDate, EndDate, TimeFrame, TickerFilter = TickerFilter, PerformContangoAdjustment = False)

print(AnalysisContext.FuturesData.TickerIDMapping)

# print(AnalysisContext.FuturesData.ActiveContractPrices)
# AnalysisContext.FuturesData.ActiveContractPrices.to_csv(FileFolder + FileName, index=False)



df = AnalysisContext.FuturesData.ActiveContractPrices.copy()

# FileNameSuffix = FileNameSuffix + '_0700-1200'
# df = AnalysisContext.FuturesData.ActiveContractPrices.query('Hour >= 7 and Hour < 12')

# FileNameSuffix = FileNameSuffix + '_0900-1600'
# df = AnalysisContext.FuturesData.ActiveContractPrices.query('Hour >= 9 and Hour < 16')

# FileNameSuffix = FileNameSuffix + '_0700-1600'
# df = AnalysisContext.FuturesData.ActiveContractPrices.query('Hour >= 7 and Hour < 16')

# FileNameSuffix = FileNameSuffix + '_0700-1700'
# df = AnalysisContext.FuturesData.ActiveContractPrices.query('Hour >= 7 and Hour < 17')

# FileNameSuffix = FileNameSuffix + '_0700-1300'
# df = AnalysisContext.FuturesData.ActiveContractPrices.query('Hour >= 7 and Hour < 13')

## Resample to daily

# df = AnalysisContext.FuturesData.ActiveContractPrices.query('TimeInStandardUnit >= 510 and TimeInStandardUnit < 960')

# FileNameSuffix = FileNameSuffix + '_ResampledDaily'

# df = GetResampledData(df)


## ---------------------

## Sort descendingly and export file

df.sort_values(by=['ticker', 'tDateTime'], ascending=False, inplace=True)

print(df)

FileName = 'prices_' + TickerInString + '_' + TimeFrame + '_' + StartDate.strftime("%Y%m%d") + '_' + EndDate.strftime("%Y%m%d") + FileNameSuffix
df.to_csv(FileFolder + FileName + '.csv', index=False)

if TimeFrame == "10 secs":


    df['price step 1'] = df['close']
    df['price step 2'] = df['close']
    df.loc[df['close'] > df['open'], 'price step 1'] = df['low']
    df.loc[df['close'] > df['open'], 'price step 2'] = df['high']
    df.loc[df['close'] <= df['open'], 'price step 1'] = df['high']
    df.loc[df['close'] <= df['open'], 'price step 2'] = df['low']
    
    ColumnsToKeep = ['expiry', 'tDateTime', 'TimeInStandardUnit', 'date id', 'MarketTimeSectionID', 'vol']
    
    df_1 = df[ColumnsToKeep + ['price step 1']]
    df_1['vol'] = 0
    df_1['price'] = df_1['price step 1']
    df_1['price step key'] = 1
    
    df_2 = df[ColumnsToKeep + ['price step 2']]
    df_2['vol'] = 0
    df_2['price'] = df_2['price step 2']
    df_2['price step key'] = 2
    
    df_3 = df[ColumnsToKeep + ['close']]
    df_3['price'] = df_3['close']
    df_3['price step key'] = 3
    
    df_SingleSeries = pd.concat([df_1, df_2, df_3])
    
    df_SingleSeries.sort_values(by=['tDateTime', 'price step key'], ascending=False, inplace=True)
    
    df_SingleSeries = df_SingleSeries[ColumnsToKeep + ['price', 'price step key']].copy()
    
    df_SingleSeries.to_csv(FileFolder + FileName + '_SingleSeries.csv', index=False)


# AnalysisContext = FuturesPriceAnalysisContext(self.StartDate, self.EndDate, self.TimeFrame, PreFilterDataByTime = PreFilterDataByTime,PreFilterDataStartTimeInStdUnit = PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit = PreFilterDataEndTimeInStdUnit,  TickerFilter = TickerFilter, KeepDataframeData = KeepDataframeData, PerformContangoAdjustment = PerformContangoAdjustment, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, KeepOnlyWeekdays = KeepOnlyWeekdays, DataTimeLowerBound = DataTimeLowerBound, DataTimeUpperBound = DataTimeUpperBound, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath)


print('done')