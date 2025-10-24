# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 22:40:34 2023

@author: henry
"""

import pymysql
import pandas as pd
import InvestmentAnalytics.Config as Config
import os
import sys

from datetime import date, datetime, timedelta

from InvestmentAnalytics.Download_Crypto_Binance_Lib import *
from InvestmentAnalytics.DBUtil import DBExportDirectUpload, DBExportDirectUploadByBatch

today = date.today()

# DirectUpload = sys.argv[1]
DirectUpload = "DirectUpload"

# interval_list = sys.argv[2].split(",")
interval_list = "1d"
print('interval_list is ' + str(interval_list))


# ticker_list = sys.argv[3].split(",")
ticker_list = "BTCUSDT,ETHUSDT"
print('ticker_list is ' + str(ticker_list))

DatafilePath = Config.CONFIG_BASE_DatafilePath + today.strftime("%Y%m%d") + '_Crypto'


if os.path.exists(DatafilePath):
    i = 1
    while os.path.exists(DatafilePath + " BK" + str(i)):
        i = i + 1
    os.rename(DatafilePath, DatafilePath + " BK" + str(i))
os.mkdir(DatafilePath)
DatafilePath = DatafilePath + "\\"

table_name = 'fdata_crypto_hist'

