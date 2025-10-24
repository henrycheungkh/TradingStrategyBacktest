# -*- coding: utf-8 -*-
"""
Created on Sat May 22 23:06:19 2021

@author: Henry Cheung
"""

# import InvestmentAnalytics.Config as Config
# import InvestmentAnalytics.DBUtil as DBUtil
import InvestmentAnalytics.IB.DownloadFuturesFromIBLib as DownloadFuturesFromIBLib

# from InvestmentAnalytics.DBUtil import AppendDBExportScript, DBExportDirectUpload, DBExportDirectUploadByBatch

# import os
import sys

# import logging
# import threading

# from datetime import datetime
from datetime import date, datetime, timedelta
# from InvestmentAnalytics.IB.IBApiProcessHub import RunIBApiProcessHub

# from InvestmentAnalytics.IB.IBApiProcessIBapiFuturesHistoricalDataReader import *
# from InvestmentAnalytics.IB.IBApiProcessIBapiFuturesHistoricalDataReader2 import *

import pandas as pd

pd.set_option('display.max_columns', None)

today = date.today()
# today = today + timedelta(days=6)
DataEndDate = today.strftime("%Y%m%d")
# DataEndDate = "20210430"
if len(sys.argv) > 6:
    DataEndDate = sys.argv[6]

print(DataEndDate)

if len(sys.argv) > 2:
    BarSize = sys.argv[1]
    HistoricalPeriod = sys.argv[2]
else:
    BarSize = "1 min"
    HistoricalPeriod = "1 W"
    
if len(sys.argv) > 3:
    DirectUpload = sys.argv[3]
else:
    DirectUpload = "No Upload"

lastTradeDateOrContractMonths = None

if len(sys.argv) > 4:
    if int(sys.argv[4]) != -1:
        lastTradeDateOrContractMonths = [lastTradeDateOrContractMonths[int(sys.argv[4])]]

if len(sys.argv) > 5:
    if sys.argv[5] == 'ALL':
        SingleTicker = ''
    else:
        SingleTicker = sys.argv[5]
else:
    SingleTicker = ''

DownloadFuturesFromIBLib.DownloadFuturesFromIBByLib(BarSize, HistoricalPeriod, today, SingleTicker, DataEndDate, DirectUpload, lastTradeDateOrContractMonths = lastTradeDateOrContractMonths)


# DownloadFuturesFromIB(BarSize, HistoricalPeriod)

