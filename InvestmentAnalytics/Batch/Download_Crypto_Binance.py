# -*- coding: utf-8 -*-
"""
Created on Wed Oct 20 11:57:58 2021

@author: Henry Cheung
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

DirectUpload = sys.argv[1]

interval_list = sys.argv[2].split(",")
print('interval_list is ' + str(interval_list))


ticker_list = sys.argv[3].split(",")
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

UploadCryptoPriceToDB(ticker_list, interval_list, DatafilePath, table_name)

if (DirectUpload == "DirectUpload"):
    database_name = Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_CRYPTO_BINANCE

    # DBExportDirectUpload(DatafilePath + 'UploadScript.sql', table_name, DatabaseName = database_name)
    DBExportDirectUploadByBatch(DatafilePath, DatafilePath + 'UploadScript.sql', table_name, DatabaseName = database_name)
    sql = "SELECT DATE(tDateTime), count(close) FROM " + table_name + "  GROUP BY DATE(tDateTime) ORDER BY DATE(tDateTime) DESC LIMIT 15"
    # print(sql)
    # dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database_name)
    dbcon = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=database_name)
    UploadCountCheck = pd.read_sql_query(sql, dbcon)
    print(UploadCountCheck)


print('Download done')

