# -*- coding: utf-8 -*-
"""
Created on Sat May 22 23:06:19 2021

@author: Henry Cheung
"""

import InvestmentAnalytics.Config as Config
from InvestmentAnalytics.DBUtil import DBExportDirectUpload
import os
import sys
import pymysql
import csv


# from datetime import datetime
from datetime import date, datetime, timedelta
from InvestmentAnalytics.IB.IBApiProcessHub import RunIBApiProcessHub
from InvestmentAnalytics.IB.IBApiProcess import *
import pandas as pd

pd.set_option('display.max_columns', None)
today = date.today()
DataEndDate = today.strftime("%Y%m%d")
# DataEndDate = "20210719"
print(DataEndDate)
BarSize = "1 day"
# HistoricalPeriod = "2 M"
HistoricalPeriod = "2 D"
# HistoricalPeriod = "7 D"

dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)


DatafilePath = Config.CONFIG_BASE_DatafilePath + 'IB_dayend_' + DataEndDate

if os.path.exists(DatafilePath):
    i = 1
    while os.path.exists(DatafilePath + " BK" + str(i)):
        i = i + 1
    os.rename(DatafilePath, DatafilePath + " BK" + str(i))
os.mkdir(DatafilePath)

DatafilePath = DatafilePath + "\\"

market = "XUSA"
StockFilter = ""

if len(sys.argv) > 1:
    InitialScreeningMarketCapThreshold = int(sys.argv[1])
    PriorDateString = sys.argv[2]
    TickerPerBatch = int(sys.argv[3])
    StartingTickerBatchID = int(sys.argv[4])
else:
    PriorDateString = '2021-07-07'
    InitialScreeningMarketCapThreshold = 500000000
    TickerPerBatch = 4000
    # TickerPerBatch = 100
    StartingTickerBatchID = 0
    # StartingTickerBatchID = 21
print("TickerPerBatch = " + str(TickerPerBatch))

print('len(sys.argv) is ' +str(len(sys.argv)))

if len(sys.argv) > 5:
    Data_Items = sys.argv[5].split(",")
else:
    Data_Items = ['TRADES']
    # Data_Items = ['TRADES','BID','ASK']
    # Data_Items = ['BID']    
    # Data_Items = ['ASK']    

if len(sys.argv) > 6:
    HistoricalPeriod = sys.argv[6]

if len(sys.argv) > 7:
    DirectUpload = sys.argv[7]
else:
    DirectUpload = "No Upload"
    # DirectUpload = "DirectUpload"
    

sql = "SELECT AAAAA.*, IFNULL(BBBBB.Property, 'NONE') AS primaryExchange FROM (SELECT AAAA.ticker as symbol, 'STK' as secType, 'USD' as currency, 'SMART' as exchange, AAAA.*, BBBB.Property As Industry FROM (SELECT AAA.*, BBB.Property AS Sector FROM (SELECT AA.ticker FROM (SELECT A.ticker FROM `fdata_price_dayend` A INNER JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime > '" + PriorDateString + "' " + StockFilter + "  GROUP BY A.ticker) AA INNER JOIN (SELECT ZB.Ticker, ZB.Value FROM (SELECT Ticker, Max(CaptureDate) AS MAX_CaptureDate FROM `fdata_yahoo_fundamental` WHERE Name = 'marketCap'  GROUP BY Ticker) ZA INNER JOIN (SELECT * FROM `fdata_yahoo_fundamental` WHERE Name = 'marketCap' and Value > " + str(InitialScreeningMarketCapThreshold) + ") ZB ON ZA.Ticker = ZB.Ticker and ZA.MAX_CaptureDate = ZB.CaptureDate) BB ON AA.ticker = BB.Ticker ) AAA LEFT JOIN (SELECT Ticker, Property FROM `fdata_yahoo_property` WHERE Property_Type = 'sector') BBB ON AAA.ticker = BBB.Ticker) AAAA LEFT JOIN (SELECT Ticker, Property FROM `fdata_yahoo_property` WHERE Property_Type = 'industry') BBBB ON AAAA.ticker = BBBB.Ticker) AAAAA LEFT JOIN (SELECT * FROM `fdata_tickers_property` WHERE Property_Type = 'primaryExchange') BBBBB ON AAAAA.symbol = BBBBB.Ticker"

print(sql)
Tickers = pd.read_sql_query(sql, dbcon)
print("Full Tickers count = " + str(len(Tickers)))
print(Tickers)

# Tickers = Tickers.head(200)
# print("Trimmed Tickers count = " + str(len(Tickers)))
# print(Tickers)
    
# if len(sys.argv) > 8:
#     if sys.argv[8] == "TickerPatching":
#         if len(sys.argv) > 9:
#             DownloadCycle = int(sys.argv[9])
#         else:
#             DownloadCycle = 0
#         # for DownloadCycle in range(3):


#         DatafilePath = Config.CONFIG_BASE_DatafilePath + 'IB_' + DataEndDate
        
#         if os.path.exists(DatafilePath):
#             i = 1
#             while os.path.exists(DatafilePath + " BK" + str(i)):
#                 i = i + 1
#             os.rename(DatafilePath, DatafilePath + " BK" + str(i))
#         os.mkdir(DatafilePath)
        
#         DatafilePath = DatafilePath + "\\"

        
#         d = today - timedelta(days=(DownloadCycle)*14)
#         DataEndDateInCycle = d.strftime("%Y%m%d")

#         # sql = "SELECT AAAAA.*, IFNULL(BBBBB.Property, 'NONE') AS primaryExchange FROM (SELECT AAAA.ticker as symbol, 'STK' as secType, 'USD' as currency, 'SMART' as exchange, AAAA.*, BBBB.Property As Industry FROM (SELECT AAA.*, BBB.Property AS Sector FROM (SELECT AA.ticker FROM (SELECT A.ticker FROM `fdata_price_dayend` A INNER JOIN `fdata_tickers` B ON A.ticker = B.Ticker WHERE B.Market = '" + market + "' AND A.Datetime > '" + PriorDateString + "' " + StockFilter + "  GROUP BY A.ticker) AA INNER JOIN (SELECT ZB.Ticker, ZB.Value FROM (SELECT Ticker, Max(CaptureDate) AS MAX_CaptureDate FROM `fdata_yahoo_fundamental` WHERE Name = 'marketCap'  GROUP BY Ticker) ZA INNER JOIN (SELECT * FROM `fdata_yahoo_fundamental` WHERE Name = 'marketCap' and Value > " + str(InitialScreeningMarketCapThreshold) + ") ZB ON ZA.Ticker = ZB.Ticker and ZA.MAX_CaptureDate = ZB.CaptureDate) BB ON AA.ticker = BB.Ticker ) AAA LEFT JOIN (SELECT Ticker, Property FROM `fdata_yahoo_property` WHERE Property_Type = 'sector') BBB ON AAA.ticker = BBB.Ticker) AAAA LEFT JOIN (SELECT Ticker, Property FROM `fdata_yahoo_property` WHERE Property_Type = 'industry') BBBB ON AAAA.ticker = BBBB.Ticker) AAAAA LEFT JOIN (SELECT * FROM `fdata_tickers_property` WHERE Property_Type = 'primaryExchange') BBBBB ON AAAAA.symbol = BBBBB.Ticker"
#         # sql = "SELECT A.ticker, count(*) FROM (SELECT DATE(DateTime) As ValueDate, ticker, COUNT(*) FROM `fdata_price_30min_ib` WHERE DataType = 'TRADES' GROUP BY DATE(DateTime), ticker ORDER BY DATE(DateTime), ticker) AS A INNER JOIN (SELECT DATE(DateTime) As ValueDate, COUNT(ticker) FROM `fdata_price_30min_ib` WHERE DateTime <= '" + DataEndDate + "' AND DataType = 'TRADES' GROUP BY DATE(DateTime) ORDER BY DATE(DateTime) DESC LIMIT 30) AS B ON A.ValueDate = B.ValueDate GROUP BY A.ticker HAVING count(*) < 30"
#         # sql = "SELECT A.ticker, count(*) FROM (SELECT DATE(DateTime) As ValueDate, ticker, COUNT(*) FROM `fdata_price_30min_ib` WHERE DataType = 'ASK' GROUP BY DATE(DateTime), ticker ORDER BY DATE(DateTime), ticker) AS A INNER JOIN (SELECT DATE(DateTime) As ValueDate, COUNT(ticker) FROM `fdata_price_30min_ib` WHERE DateTime <= '" + DataEndDate + "' AND DataType = 'TRADES' GROUP BY DATE(DateTime) ORDER BY DATE(DateTime) DESC LIMIT 30) AS B ON A.ValueDate = B.ValueDate GROUP BY A.ticker HAVING count(*) < 30"
#         # sql = "SELECT A.ticker, count(*) FROM (SELECT DATE(DateTime) As ValueDate, ticker, COUNT(*) FROM `fdata_price_30min_ib` WHERE DataType = 'ASK' GROUP BY DATE(DateTime), ticker ORDER BY DATE(DateTime), ticker) AS A INNER JOIN (SELECT DATE(DateTime) As ValueDate, COUNT(ticker) FROM `fdata_price_30min_ib` WHERE DateTime < '" + DataEndDate + "' AND DataType = 'TRADES' GROUP BY DATE(DateTime) ORDER BY DATE(DateTime) DESC LIMIT 30) AS B ON A.ValueDate = B.ValueDate GROUP BY A.ticker HAVING count(*) < 30"
#         sql = "SELECT A.ticker, count(*) FROM (SELECT DATE(DateTime) As ValueDate, ticker, COUNT(*) FROM `fdata_price_30min_ib` WHERE DataType = 'ASK' GROUP BY DATE(DateTime), ticker ORDER BY DATE(DateTime), ticker) AS A INNER JOIN (SELECT DATE(DateTime) As ValueDate, COUNT(ticker) FROM `fdata_price_30min_ib` WHERE DateTime < '" + DataEndDate + "' AND DataType = 'TRADES' GROUP BY DATE(DateTime) ORDER BY DATE(DateTime) DESC LIMIT " + str((DownloadCycle+1)*10) +  ") AS B ON A.ValueDate = B.ValueDate GROUP BY A.ticker HAVING count(*) < " + str((DownloadCycle+1)*10)
        
#         print(sql)
#         TickerForPatching = pd.read_sql_query(sql, dbcon)
#         print("TickerForPatching count = " + str(len(TickerForPatching)))
#         print(TickerForPatching)
#         Tickers = Tickers.merge(TickerForPatching[['ticker']], on='ticker')
#         print("Full Tickers count for patching = " + str(len(Tickers)))
#         print(Tickers)
#         # HistoricalPeriod = "2 M"
#         HistoricalPeriod = "2 W"
#         # process = IBapiUSStocksHistoricalDataReader(Tickers, BarSize, HistoricalPeriod, DataEndDate, Data_Items = Data_Items, TickerPerBatch = TickerPerBatch, StartingTickerBatchID = StartingTickerBatchID, DatafilePath = DatafilePath)
#         process = IBapiUSStocksHistoricalDataReader(Tickers, BarSize, HistoricalPeriod, DataEndDateInCycle, Data_Items = Data_Items, TickerPerBatch = TickerPerBatch, StartingTickerBatchID = StartingTickerBatchID, DatafilePath = DatafilePath)
#         # print(process)
#         # process.RunProcess()
#         ProcessReturnList = RunIBApiProcessHub([process])
# else:

# DataEndDateString = datetime.strptime(DataEndDate + " 23:59:59", "%Y%m%d %H:%M:%S")

    # DatafilePath = Config.CONFIG_BASE_DatafilePath + 'IB_' + DataEndDate
    
    # if os.path.exists(DatafilePath):
    #     i = 1
    #     while os.path.exists(DatafilePath + " BK" + str(i)):
    #         i = i + 1
    #     os.rename(DatafilePath, DatafilePath + " BK" + str(i))
    # os.mkdir(DatafilePath)
    
    # DatafilePath = DatafilePath + "\\"    
    
process = IBapiUSStocksDayEndHistoricalDataReader(Tickers, BarSize, HistoricalPeriod, DataEndDate, Data_Items = Data_Items, TickerPerBatch = TickerPerBatch, StartingTickerBatchID = StartingTickerBatchID, DatafilePath = DatafilePath)
# print(process)
# process.RunProcess()
ProcessReturnList = RunIBApiProcessHub([process])


f = open(DatafilePath + "download_finish.txt", "a")
f.write("Download Finished")
f.close()

if (DirectUpload == "DirectUpload"):
    DBExportDirectUpload(DatafilePath + 'UploadScript.sql', 'fdata_price_dayend_ib')
    # command = r'd:\xampp\mysql\bin\mysql -u root finance < ' + DatafilePath + 'UploadScript.sql'
    # os.system(command)

sql = "SELECT DATE(DateTime), DataType, count(close) FROM `fdata_price_dayend_ib` GROUP BY DATE(DateTime), DataType ORDER BY DATE(DateTime) DESC LIMIT 15"
# print(sql)
UploadCountCheck = pd.read_sql_query(sql, dbcon)
print(UploadCountCheck)
print('done')
