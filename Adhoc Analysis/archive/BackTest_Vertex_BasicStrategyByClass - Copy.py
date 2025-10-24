# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 19:27:01 2024

@author: Henry Cheung
"""


import pandas as pd
import numpy as np
import datetime

from AdhocBacktestKeyLevelClass import AdhocBacktestKeyLevel

pd.set_option('display.max_columns', None)
pd.set_option('display.width',250)

# ticker = 'GC'
# StopLoss = 2

ticker = 'NQ'
StopLoss = 20

RewardRiskRatio = 1
TakeProfit = StopLoss * RewardRiskRatio

TradeEntryTimePeriodStart = (9*60 + 30)*6
TradeEntryTimePeriodEnd = (12*60)*6
TradeMaxDuration = 60*6

KeyLevelName = 'KL-VT-PD-LB5-MinMove120'

RawDataFilepath = r'G:\Temp\prices_' + ticker + '_10 secs_20230601_20240630_0700-1600.csv'

KeyLevelFilepath = r'G:\Temp\\' + ticker + '_KeyLevel_WithExpiryAdj_' + KeyLevelName + '_batch_full.csv'

# DebugExportFilepath = r'G:\Temp\DebugOutput_' + ticker + '_10 secs_20230601_20240630_0700-1600.csv'

DebugExportFilepath = None

backtest_obj = AdhocBacktestKeyLevel(RawDataFilepath, KeyLevelName, KeyLevelFilepath, ticker, Parameters = {'StopLoss' : StopLoss, 'RewardRiskRatio' : RewardRiskRatio, 'TradeEntryTimePeriodStart' : TradeEntryTimePeriodStart, 'TradeEntryTimePeriodEnd' : TradeEntryTimePeriodEnd, 'TradeMaxDuration' : TradeMaxDuration}, DebugExportFilepath=DebugExportFilepath)

print(backtest_obj.BacktestResultSummary)
