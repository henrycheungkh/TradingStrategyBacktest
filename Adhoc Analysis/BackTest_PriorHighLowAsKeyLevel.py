# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 18:29:40 2024

@author: Henry Cheung
"""


import pandas as pd
import numpy as np
import datetime

from AdhocBacktestKeyLevelBaseClass import KeyLevelByHighLowInLookBackPeriodGenerator
from AdhocBacktestKeyLevelClass import AdhocBacktestKeyLevel

pd.set_option('display.max_columns', None)
pd.set_option('display.width',250)
TimeFrameMultiplierToMinute = 6

LookBackPeriod = 1

InputFolder = r'G:\Temp\\'
OutputFolder = r'J:\Temp\\'

Ticker = 'NQ'

KeyLevelName = 'KL-PHL-LB' + str(LookBackPeriod)

Price1MinDataFilepath = InputFolder + r'prices_' + Ticker + '_1 min_20230601_20240630_0700-1600.zip'
# KeyLevelExportFilepath = OutputFolder + Ticker + '_KeyLevel_WithExpiryAdj_' + KeyLevelName + '.csv'

KeyLevelParameters = { 'LookbackTimePeriodStart' : (9*60 + 30), 
                 'LookbackTimePeriodEnd' : (16*60)}

KLGenerator = KeyLevelByHighLowInLookBackPeriodGenerator(KeyLevelName, Price1MinDataFilepath, LookBackPeriod, KeyLevelParameters, Ticker = Ticker)

KLGenerator.generateKeyLevel()

# KLGenerator.df_KL is the generated Key Level, in this case the prior one day high/low
print(KLGenerator.df_KL)

ParameterList = {'StopLoss' : [20], 
                 'RewardRiskRatio' : [1, 1.5], 
                 'MaxLossTradeCountPerDay' : [2], 
                 'MaxWinTradeCountPerDay' : [2], 
                 'TradeEntryTimePeriod' : [[(9*60 + 30)*TimeFrameMultiplierToMinute, (12*60)*TimeFrameMultiplierToMinute]], 
                 'TradeMaxDuration' : [60*6],
                 'PositionMultiplier' : [1]}

PriceDataFilepath = InputFolder + r'prices_' + Ticker + '_10 secs_20230601_20240630_0700-1600.zip'

# EconIndicatorFilepath = InputFolder + 'Econ Calendar - 3 stars 3Y (US Eastern Time).zip'

DebugExportFilepath = OutputFolder + r'DebugOutput_PriorHighLow_' + Ticker + '_10 secs_20230601_20240630_0700-1600.csv'
ResultSummaryExportFilepath = OutputFolder + r'BacktestResultSummary_PriorHighLow_' + Ticker + '_10 secs_20230601_20240630_0700-1600.csv'

LongShortIndicatorsParameterList = {'MACD' : {'Fast Length/Slow Length/Signal Smoothing' : [[12,26,9]], 'Source' : ['close'], 'Oscillator MA Type' : ['SMA'], 'Signal Line MA Type' : ['SMA']},
# LongShortIndicatorsParameterList = {'MACD' : {'Fast Length/Slow Length/Signal Smoothing' : [[12,26,9]], 'Source' : ['close'], 'Oscillator MA Type' : ['EMA'], 'Signal Line MA Type' : ['SMA'], 'EMA Look back Multiple' : [1]},
                                    'RSI' : {}
                                    }

backtest_obj = AdhocBacktestKeyLevel(PriceDataFilepath, Ticker, KeyLevelName = KeyLevelName, KeyLevel = KLGenerator.df_KL, ParameterList = ParameterList, LongShortIndicatorFilepath = Price1MinDataFilepath, LongShortIndicatorParameters = LongShortIndicatorsParameterList, DebugExportFilepath=DebugExportFilepath, ResultSummaryExportFilepath=ResultSummaryExportFilepath)
# backtest_obj = AdhocBacktestKeyLevel(PriceDataFilepath, Ticker, KeyLevelName = KeyLevelName, KeyLevel = KLGenerator.df_KL, ParameterList = ParameterList, DebugExportFilepath=DebugExportFilepath, ResultSummaryExportFilepath=ResultSummaryExportFilepath, EconIndicatorFilepath=EconIndicatorFilepath, EconIndicatorParameters = EconIndicatorParameters)

print(backtest_obj.BacktestResultSummary)



