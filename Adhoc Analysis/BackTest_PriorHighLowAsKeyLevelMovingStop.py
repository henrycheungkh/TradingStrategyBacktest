# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 18:29:40 2024

@author: Henry Cheung
"""


import pandas as pd
import numpy as np
import datetime

from AdhocBacktestKeyLevelBaseClass import KeyLevelByHighLowInLookBackPeriodGenerator
from AdhocBacktestKeyLevelClassMovingStop import AdhocBacktestKeyLevelMovingStop


pd.set_option('display.max_columns', None)
pd.set_option('display.width',250)

LookBackPeriod = 1

InputFolder = r'G:\Temp\\'
OutputFolder = r'J:\Temp\\'
TimeFrameMultiplierToMinute = 6

Ticker = 'NQ'

KeyLevelName = 'KL-PHL-LB' + str(LookBackPeriod)

PriceDataFilepath = InputFolder + r'prices_' + Ticker + '_1 min_20230601_20240630_0700-1600.zip'
# KeyLevelExportFilepath = OutputFolder + Ticker + '_KeyLevel_WithExpiryAdj_' + KeyLevelName + '.csv'

KeyLevelParameters = { 'LookbackTimePeriodStart' : (9*60 + 30), 
                 'LookbackTimePeriodEnd' : (16*60)}

KLGenerator = KeyLevelByHighLowInLookBackPeriodGenerator(KeyLevelName, PriceDataFilepath, LookBackPeriod, KeyLevelParameters, Ticker = Ticker)

KLGenerator.generateKeyLevel()

print(KLGenerator.df_KL)

ParameterList = {'StopLoss' : [20], 
                 'RewardRiskRatio' : [3, 6], 
                 'TrailingStopLoss' : [20], 
                 'TrailingTakeProfit' : [20], 
                 'TrailingStartTime' : [5*TimeFrameMultiplierToMinute],
                 'MaxLossTradeCountPerDay' : [2], 
                 'MaxWinTradeCountPerDay' : [2], 
                 'TradeEntryTimePeriod' : [[(9*60 + 30)*TimeFrameMultiplierToMinute, (12*60)*TimeFrameMultiplierToMinute]], 
                 'TradeMaxDuration' : [60*TimeFrameMultiplierToMinute],
                 'PositionMultiplier' : [1]}

PriceDataFilepath = InputFolder + r'prices_' + Ticker + '_10 secs_20230601_20240630_0700-1600.zip'

# EconIndicatorFilepath = InputFolder + 'Econ Calendar - 3 stars 3Y (US Eastern Time).zip'

DebugExportFilepath = OutputFolder + r'DebugOutput_PriorHighLowMovingStop_' + Ticker + '_10 secs_20230601_20240630_0700-1600.csv'
ResultSummaryExportFilepath = OutputFolder + r'BacktestResultSummary_PriorHighLowMovingStop_' + Ticker + '_10 secs_20230601_20240630_0700-1600.csv'

backtest_obj = AdhocBacktestKeyLevelMovingStop(PriceDataFilepath, Ticker, KeyLevelName = KeyLevelName, KeyLevel = KLGenerator.df_KL, ParameterList = ParameterList, DebugExportFilepath=DebugExportFilepath, ResultSummaryExportFilepath=ResultSummaryExportFilepath)
# backtest_obj = AdhocBacktestKeyLevel(PriceDataFilepath, KeyLevelName, KLGenerator.df_KL, ticker, ParameterList = ParameterList, DebugExportFilepath=DebugExportFilepath, EconIndicatorFilepath=EconIndicatorFilepath, EconIndicatorParameters = EconIndicatorParameters, ResultSummaryExportFilepath=ResultSummaryExportFilepath)

print(backtest_obj.BacktestResultSummary)

