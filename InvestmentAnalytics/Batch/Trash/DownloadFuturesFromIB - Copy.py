# -*- coding: utf-8 -*-
"""
Created on Sat May 22 23:06:19 2021

@author: Henry Cheung
"""

import InvestmentAnalytics.Config as Config
from InvestmentAnalytics.DBUtil import AppendDBExportScript, DBExportDirectUpload, DBExportDirectUploadByBatch

import os
import sys

import logging
import threading

# from datetime import datetime
from datetime import date, datetime, timedelta
from InvestmentAnalytics.IB.IBApiProcessHub import RunIBApiProcessHub
from InvestmentAnalytics.IB.IBApiProcessIBapiFuturesHistoricalDataReader import *
import pandas as pd

def WriteDBExportScript(DatafilePath, filepath, DBTableName):
    AppendDBExportScript(DatafilePath, filepath, DBTableName)

pd.set_option('display.max_columns', None)
today = date.today()
# today = today + timedelta(days=6)
DataEndDate = today.strftime("%Y%m%d")
# DataEndDate = "20210430"
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

def DownloadFuturesFromIB(BarSize, HistoricalPeriod):
    if BarSize == '10 secs':
        DBTableName = Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST_10SECS + '.' + 'fdata_fut_hist'
    else:
        DBTableName = Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST + '.' + 'fdata_fut_hist'
        
    print('BarSize = ' + BarSize + ' and DBTableName = ' + str(DBTableName))

    # ContractDate1 = today

    ContractDate1 = today + timedelta(days=10)
    print(ContractDate1.strftime("%Y%m"))
    
    ContractDate2 = (ContractDate1.replace(day=1) + timedelta(days=32)).replace(day=1)
    print(ContractDate2.strftime("%Y%m"))
    
    ContractDate3 = (ContractDate2.replace(day=1) + timedelta(days=32)).replace(day=1)
    print(ContractDate3.strftime("%Y%m"))
    
    ContractDate4 = (ContractDate3.replace(day=1) + timedelta(days=32)).replace(day=1)
    print(ContractDate4.strftime("%Y%m"))
    
    ContractDate5 = (ContractDate4.replace(day=1) + timedelta(days=32)).replace(day=1)
    print(ContractDate5.strftime("%Y%m"))
    
    # lastTradeDateOrContractMonths = [ContractDate1.strftime("%Y%m"), ContractDate2.strftime("%Y%m"), ContractDate3.strftime("%Y%m"), ContractDate4.strftime("%Y%m"), ContractDate5.strftime("%Y%m")]
    lastTradeDateOrContractMonths = [ContractDate1.strftime("%Y%m"), ContractDate2.strftime("%Y%m"), ContractDate3.strftime("%Y%m"), ContractDate4.strftime("%Y%m")]
    # lastTradeDateOrContractMonths = [ ContractDate2.strftime("%Y%m"), ContractDate3.strftime("%Y%m"), ContractDate4.strftime("%Y%m"), ContractDate5.strftime("%Y%m")]
    # lastTradeDateOrContractMonths = [ContractDate5.strftime("%Y%m")]
    # lastTradeDateOrContractMonths = ["202109", "202112"]
    # lastTradeDateOrContractMonths = ["202106", "202107", "202109", "202108"]
    
    if len(sys.argv) > 4:
        if int(sys.argv[4]) != -1:
            lastTradeDateOrContractMonths = [lastTradeDateOrContractMonths[int(sys.argv[4])]]

    if len(sys.argv) > 5:
        SingleTicker = sys.argv[5]
    else:
        SingleTicker = ''
        
    # DatafilePath = Config.CONFIG_BASE_FuturesDatafilePath + today.strftime("%Y%m%d") + '_' + BarSize.replace(" ", "") + '_' + SingleTicker + '_' + HistoricalPeriod.replace(" ", "")
    DatafilePath = Config.CONFIG_BASE_FuturesDatafilePath + today.strftime("%Y%m%d") + '_' + BarSize.replace(" ", "") + '_' + SingleTicker + '_' + HistoricalPeriod.replace(" ", "") + '_' + BarSize.strip()
    
    if os.path.exists(DatafilePath):
        i = 1
        while os.path.exists(DatafilePath + " BK" + str(i)):
            i = i + 1
        os.rename(DatafilePath, DatafilePath + " BK" + str(i))
    os.mkdir(DatafilePath)
    
    DatafilePath = DatafilePath + "\\"
    
    print('DatafilePath is ' + DatafilePath)
    
    for lastTradeDateOrContractMonth in lastTradeDateOrContractMonths:
        
        print("lastTradeDateOrContractMonth is " + lastTradeDateOrContractMonth)
    
        # ContractList = {
        #                 "ES":[{"secType":"FUT", "exchange":"GLOBEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":'Europe/London', "MarketTimeZone":'America/New_York'}],
        #                 "NQ":[{"secType":"FUT", "exchange":"GLOBEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":'Europe/London', "MarketTimeZone":'America/New_York'}],
        #                 "RTY":[{"secType":"FUT", "exchange":"GLOBEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":'Europe/London', "MarketTimeZone":'America/New_York'}],
        #                 "YM":[{"secType":"FUT", "exchange":"ECBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":'Europe/London', "MarketTimeZone":'America/New_York'}],
        #                 "ZN":[{"secType":"FUT", "exchange":"ECBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":'Europe/London', "MarketTimeZone":'America/New_York'}],
        #                 "ZT":[{"secType":"FUT", "exchange":"ECBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":'Europe/London', "MarketTimeZone":'America/New_York'}],
        #                 "GC":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":'Europe/London', "MarketTimeZone":'America/New_York'}],
        #                 "SI":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth, "Multiplier":"5000"}, {"LocalTimeZone":'Europe/London', "MarketTimeZone":'America/New_York'}],
        #                 "CL":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":'Europe/London', "MarketTimeZone":'America/New_York'}],
        #                 "HG":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":'Europe/London', "MarketTimeZone":'America/New_York'}]
        #                 }

        # ContractList = {
        #                 "ES":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
        #                 "NQ":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
        #                 "RTY":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
        #                 "YM":[{"secType":"FUT", "exchange":"ECBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
        #                 "ZN":[{"secType":"FUT", "exchange":"ECBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
        #                 "ZT":[{"secType":"FUT", "exchange":"ECBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
        #                 "GC":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
        #                 "SI":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth, "Multiplier":"5000"}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
        #                 "CL":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
        #                 "HG":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
        #                 "2YY":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
        #                 "10Y":[{"secType":"FUT", "exchange":"ECBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
        #                 "30Y":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}]
        #                 }

        ContractList = {
                        "ES":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "NQ":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "RTY":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "YM":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "ZN":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "ZT":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "GC":[{"secType":"FUT", "exchange":"COMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "SI":[{"secType":"FUT", "exchange":"COMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth, "Multiplier":"5000"}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "CL":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "NG":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "RB":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "HO":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "ZW":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "ZS":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "ZC":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "HG":[{"secType":"FUT", "exchange":"COMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "MBT":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        # "MET":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "ETHUSDRR":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "2YY":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "10Y":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "30Y":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}]
                        }


        # ContractList = {
                        # "ES":[{"secType":"FUT", "exchange":"GLOBEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}]
                        # "NQ":[{"secType":"FUT", "exchange":"GLOBEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}]
                        # "RTY":[{"secType":"FUT", "exchange":"GLOBEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}]
        #                 "ZN":[{"secType":"FUT", "exchange":"ECBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}]
                        # "YM":[{"secType":"FUT", "exchange":"ECBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}]
                        # "ZT":[{"secType":"FUT", "exchange":"ECBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}]
                        # "SI":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth, "Multiplier":"5000"}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}]
                        # "CL":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}]
                        # }
        if len(SingleTicker) > 0:
            ContractList2 = ContractList.copy()
            ContractList = {}
            ContractList[SingleTicker] = ContractList2[SingleTicker]
         
        # DataEndDateString = datetime.strptime(DataEndDate + " 23:59:59", "%Y%m%d %H:%M:%S")
        DataEndDateString = datetime.strptime(DataEndDate + "-23:59:59", "%Y%m%d-%H:%M:%S")
        
        process = IBapiFuturesHistoricalDataReader(ContractList, BarSize, HistoricalPeriod, DataEndDateString)
        ProcessReturnList = RunIBApiProcessHub([process])
        
        print(ProcessReturnList[0])
        if (len(ContractList) == 1):
            FilePath = DatafilePath + "FuturesDump " + DataEndDate + " " + BarSize.replace(" ", "")+ " " + HistoricalPeriod.replace(" ", "") + " " + list(ContractList.keys())[0] + " " + lastTradeDateOrContractMonth + ".csv"
        else:
            FilePath = DatafilePath + "FuturesDump " + DataEndDate + " " + BarSize.replace(" ", "")+ " " + HistoricalPeriod.replace(" ", "") + " " + str(len(ContractList))  + " contracts " + lastTradeDateOrContractMonth + ".csv"
        ProcessReturnList[0].to_csv(FilePath, index=False)
        WriteDBExportScript(DatafilePath, FilePath, DBTableName)
    
    f = open(DatafilePath + "download_finish.txt", "a")
    f.write("Download Finished")
    f.close()

    if (DirectUpload == "DirectUpload"):
        TableName = 'fdata_fut_hist'
        if BarSize == '10 secs':
            DBName = Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST_10SECS
        else:
            DBName = Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST
        DBExportDirectUploadByBatch(DatafilePath, DatafilePath + 'UploadScript.sql', TableName, DatabaseName = DBName, UploadToDB = False)
        # DBExportDirectUpload(DatafilePath + 'UploadScript.sql', 'fdata_fut_hist', DatabaseName = Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)
        # print('After DBExportDirectUpload')
        
        if (SingleTicker == ''):
            dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, DBName)
            check_date_from = today - timedelta(days=14)
            sql = "SELECT ticker, DATE(tDateTime) as ValueDate, DataType, count(close) as RecordCount FROM " + TableName + " WHERE timeframe = '" + BarSize + "' and tDateTime > '" + check_date_from.strftime("%Y-%m-%d") + "' GROUP BY ticker, DATE(tDateTime), DataType ORDER BY ticker, DATE(tDateTime) DESC"
            print(sql)
            UploadCountCheck = pd.read_sql_query(sql, dbcon)
            pd.set_option('display.max_rows', 300)
            UploadCountCheck = pd.pivot_table(UploadCountCheck, index=['ValueDate'],columns=['DataType', 'ticker'], values='RecordCount', aggfunc=np.mean).reset_index().sort_values(by=['ValueDate'], ascending=False)
            
            print(UploadCountCheck)
        
    print('done')

DownloadFuturesFromIB(BarSize, HistoricalPeriod)
