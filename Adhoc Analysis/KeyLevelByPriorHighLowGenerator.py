# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 18:29:40 2024

@author: Henry Cheung
"""


import pandas as pd
import numpy as np
import datetime

from AdhocBacktestKeyLevelClass import KeyLevelByHighLowInLookBackPeriodGenerator

pd.set_option('display.max_columns', None)
pd.set_option('display.width',250)

LookBackPeriod = 1

InputFolder = r'G:\Temp\\'
OutputFolder = r'J:\Temp\\'

Ticker = 'NQ'

KeyLevelName = 'KL-PHL-LB' + str(LookBackPeriod)

PriceDataFilepath = InputFolder + r'prices_' + Ticker + '_1 min_20230601_20240630_0700-1600.csv'
KeyLevelExportFilepath = OutputFolder + Ticker + '_KeyLevel_WithExpiryAdj_' + KeyLevelName + '.csv'

KeyLevelParameters = { 'LookbackTimePeriodStart' : (9*60 + 30), 
                 'LookbackTimePeriodEnd' : (16*60)}

KLGenerator = KeyLevelByHighLowInLookBackPeriodGenerator(KeyLevelName, PriceDataFilepath, LookBackPeriod, KeyLevelParameters, Ticker = Ticker, KeyLevelExportFilepath = KeyLevelExportFilepath)

KLGenerator.generateKeyLevel()

