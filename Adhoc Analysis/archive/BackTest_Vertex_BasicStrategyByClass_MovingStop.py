# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 19:27:01 2024

@author: Henry Cheung
"""


import pandas as pd
import numpy as np
import datetime

from AdhocBacktestKeyLevelClassMovingStop import AdhocBacktestKeyLevelMovingStop

pd.set_option('display.max_columns', None)
pd.set_option('display.width',250)

InputFolder = r'G:\Temp\\'
OutputFolder = r'G:\Temp\\'

# ticker = 'GC'
# StopLoss = 2

ticker = 'NQ'
StopLoss = 20

ParameterList = {'StopLoss' : [20], 
                 'RewardRiskRatio' : [1, 1.5], 
                 'TradeEntryTimePeriodStart' : [(9*60 + 30)*6], 
                 'TradeEntryTimePeriodEnd' : [(12*60)*6], 
                 'TradeMaxDuration' : [60*6]}

KeyLevelName = 'KL-VT-PD-LB5-MinMove120'

RawDataFilepath = InputFolder + r'prices_' + ticker + '_10 secs_20230601_20240630_0700-1600.csv'

KeyLevelFilepath = InputFolder + ticker + '_KeyLevel_WithExpiryAdj_' + KeyLevelName + '_batch_full.csv'

DebugExportFilepath = OutputFolder + r'DebugOutput_MovingStop_' + ticker + '_10 secs_20230601_20240630_0700-1600.csv'

# DebugExportFilepath = None

backtest_obj = AdhocBacktestKeyLevelMovingStop(RawDataFilepath, KeyLevelName, KeyLevelFilepath, ticker, ParameterList = ParameterList, DebugExportFilepath=DebugExportFilepath)

print(backtest_obj.BacktestResultSummary)

BacktestResultSummaryFilepath = OutputFolder + r'BacktestResultSummary_MovingStop_' + ticker + '_10 secs_20230601_20240630_0700-1600.csv'

backtest_obj.BacktestResultSummary.to_csv(BacktestResultSummaryFilepath)