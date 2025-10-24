# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 18:29:40 2024

@author: Henry Cheung
"""


import pandas as pd
import numpy as np

from AdhocBacktestKeyLevelBaseClass import KeyLevelByHighLowInLookBackPeriodGenerator
from AdhocBacktestKeyLevelClassMovingStopKLBand import AdhocBacktestKeyLevelMovingStopKLBand


pd.set_option('display.max_columns', None)
pd.set_option('display.width',250)
TimeFrameMultiplierToMinute = 6

# Number of days looking back for Key Level
LookBackPeriod = 1

InputFolder = r'G:\Temp\\'
OutputFolder = r'J:\Temp\\'

Ticker = 'NQ'

KeyLevelName = 'KL-PHL-LB' + str(LookBackPeriod)

PriceDataFilepath = InputFolder + r'prices_' + Ticker + '_1 min_20230601_20240630_0700-1600.zip'
# KeyLevelExportFilepath = OutputFolder + Ticker + '_KeyLevel_WithExpiryAdj_' + KeyLevelName + '.csv'

# Liquid Trading hours to look for High and Low as Key Level
KeyLevelParameters = { 'LookbackTimePeriodStart' : (9*60 + 30), 
                 'LookbackTimePeriodEnd' : (16*60)}

# High and Low in prior period as Key Level and to be generated
KLGenerator = KeyLevelByHighLowInLookBackPeriodGenerator(KeyLevelName, PriceDataFilepath, LookBackPeriod, KeyLevelParameters, Ticker = Ticker)

KLGenerator.generateKeyLevel()

print(KLGenerator.df_KL)

ParameterList = {'StopLoss' : [20], 
                 'RewardRiskRatio' : [3, 6], 
                 'TrailingStopLoss' : [20], 
                 'TrailingTakeProfit' : [20], 
                 'TrailingStartTime' : [5*6],
                 'KeyLevelBandwidth' : [20], 
                 'TradeEntryByKeyLevelOffset' : [0], 
                 'KeyLevelBandStayingTime' : [1*TimeFrameMultiplierToMinute], 
                 'MaxLossTradeCountPerDay' : [2], 
                 'MaxWinTradeCountPerDay' : [2], 
                 'TradeEntryTimePeriod' : [[(9*60 + 30)*TimeFrameMultiplierToMinute, (12*60)*TimeFrameMultiplierToMinute]], 
                 'TradeMaxDuration' : [60*TimeFrameMultiplierToMinute],
                 'PositionMultiplier' : [1]}

PriceDataFilepath = InputFolder + r'prices_' + Ticker + '_10 secs_20230601_20240630_0700-1600.zip'

# EconIndicatorFilepath = InputFolder + 'Econ Calendar - 3 stars 3Y (US Eastern Time).zip'

DebugExportFilepath = OutputFolder + r'DebugOutput_PriorHighLowMovingStopKLBand_' + Ticker + '_10 secs_20230601_20240630_0700-1600.csv'
ResultSummaryExportFilepath = OutputFolder + r'BacktestResultSummary_PriorHighLowMovingStopKLBand_' + Ticker + '_10 secs_20230601_20240630_0700-1600.csv'

backtest_obj = AdhocBacktestKeyLevelMovingStopKLBand(PriceDataFilepath, Ticker, KeyLevelName = KeyLevelName, KeyLevel = KLGenerator.df_KL, ParameterList = ParameterList, DebugExportFilepath=DebugExportFilepath, DebugShowBeforeAndAfterTimeStepCount = 50, ResultSummaryExportFilepath=ResultSummaryExportFilepath)
# backtest_obj = AdhocBacktestKeyLevel(PriceDataFilepath, Ticker, KeyLevelName = KeyLevelName, KeyLevel = KLGenerator.df_KL, ParameterList = ParameterList, DebugExportFilepath=DebugExportFilepath, EconIndicatorFilepath=EconIndicatorFilepath, EconIndicatorParameters = EconIndicatorParameters, DebugShowBeforeAndAfterTimeStepCount = 50, ResultSummaryExportFilepath=ResultSummaryExportFilepath)

print(backtest_obj.BacktestResultSummary)


