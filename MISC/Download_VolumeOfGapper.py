# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 04:06:25 2021

@author: Henry Cheung
"""
import Config

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import *
from ibapi.common import *

import threading
import time
from datetime import datetime, date
import pandas as pd
import pymysql
import numpy as np
import mysql.connector
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import sys

class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)
		self.data = []
		self.df = pd.DataFrame()
        
        
	def tickPrice(self, reqId, tickType, price, attrib):
		if tickType == 2 and reqId == 1:
			print('The current ask price is: ', price)

	def historicalData(self, reqId:int, bar: BarData):
# 		global Request_ID
# 		if reqId == Request_ID:
		self.data.append(vars(bar))
# 		print("HistoricalData. ReqId:", reqId, "BarData.", bar)
		pass

# 	def historicalDataUpdate(self, reqId, bar):
# 		line = vars(bar)
#         # pop date and make it the index, add rest to df
#         # will overwrite last bar at that same time
# 		self.df.loc[pd.to_datetime(line.pop('date'))] = line

	def historicalDataEnd(self, reqId: int, start: str, end: str):
		super().historicalDataEnd(reqId, start, end)
		self.df = pd.DataFrame(self.data)
		self.df['date'] = pd.to_datetime(self.df['date'])
		self.df.set_index('date', inplace=True)
# 		print('data in dataframe is')
# 		print(self.df)
		print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)

	def error(self, reqId: TickerId, errorCode: int, errorString: str):
		global DownloadError, Request_ID
		super().error(reqId, errorCode, errorString)
		print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)
		if reqId == Request_ID:
		    print('for reqId = ' + str(reqId) + ' setting DownloadError to True')
		    DownloadError = True

def run_loop():
	app.run()

dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
today_date = date.today()
# today_date = datetime.strptime('30042021', '%d%m%Y').date()

if len(sys.argv) > 1:
    Running_Mode = sys.argv[1]
else:
    Running_Mode = 'Recurring'

StockFilter = ""

# now = datetime.now()

print("Start uploading US gappers premarket volume for "+ today_date.strftime("%Y-%m-%d"))

mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
Request_ID = 1000


app = IBapi()
app.connect('127.0.0.1', 7496, 123)

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

now = datetime.now()

# j = 1
# while j <= 1:
#     j = j + 1

while (now.hour < 15):

    # StockFilter = " AND Ticker in ('ACH', 'BHC') "
    # StockFilter = " AND Ticker in ('AUPH') "
    # sql = "SELECT Ticker FROM `fdata_us_gapper_tickers` WHERE CaptureDate = '" + today_date.strftime("%Y-%m-%d") +"' " + StockFilter
    sql = "SELECT Ticker FROM `fdata_us_gapper_tickers` WHERE CaptureDate = '" + today_date.strftime("%Y-%m-%d") +"' " + StockFilter + " GROUP BY Ticker"
    print(sql)
    Tickers = pd.read_sql_query(sql, dbcon)

    
    if len(Tickers) == 0:
        print("Sleep 2 mins to wait for gappers available")
        time.sleep(120)
    else:
        TickersCount = len(Tickers)
        print("Tickers count = " + str(TickersCount))
        print(Tickers)        # global Request_ID
        Request_ID = 1000
        
        for index, row in Tickers.iterrows():
            # try:
            print('Start downloading premarket volume for ' + row['Ticker'] + ', ' + str(index) + ' out of ' + str(TickersCount))
            df = pd.DataFrame()
            # print('df is')
            # print(df)
            DownloadError = False
            app.df = pd.DataFrame()
            app.data = []
            # print('app.df is')
            # print(app.df)
    
            #Create contract object
            stock_contract = Contract()
            # apple_contract.symbol = 'AAPL'
            stock_contract.symbol = row['Ticker']
            stock_contract.secType = 'STK'
            stock_contract.exchange = 'SMART'
            stock_contract.currency = 'USD'
            
            queryTime = datetime.today().strftime("%Y%m%d %H:%M:%S")
            print('going to request historical data for ' + row['Ticker'] + ' with Request ID ' + str(Request_ID))
            # app.reqHistoricalData(Request_ID, stock_contract, queryTime, "42 D", "5 mins", "TRADES", 0, 1, False, [])
            # app.reqHistoricalData(Request_ID, stock_contract, queryTime, "42 D", "30 mins", "TRADES", 0, 1, False, [])
            if (now.hour >= 14):
                # app.reqHistoricalData(Request_ID, stock_contract, queryTime, "42 D", "5 mins", "TRADES", 0, 1, False, [])
                app.reqHistoricalData(Request_ID, stock_contract, queryTime, "3 D", "5 mins", "TRADES", 0, 1, False, [])
            else:
                app.reqHistoricalData(Request_ID, stock_contract, queryTime, "42 D", "30 mins", "TRADES", 0, 1, False, [])
            
            while (len(app.df) == 0) and not DownloadError:
                print('waiting for data, len(app.df) is '+ str(len(app.df)) + ' and DownloadError is ' + str(DownloadError))
                time.sleep(5) #Sleep interval to allow time for incoming price data
            
            if not DownloadError:
                # print('data in dataframe after sleep is')
                # print(app.df)
                
                df = app.df.copy()
                # print('Dataframe before exporting')
                # print(df)
                # csvfilepath = Config.CONFIG_BASE_DatafilePath + '\Pre Market Volume Dump\Pre Market Volume Dump ' + row['Ticker'] + ' ' + today_date.strftime("%Y%m%d") + ' All Hours.csv'
                # df.to_csv(csvfilepath)
                df = df.reset_index()
                # print('After reset index, column types are')
                # print(df.dtypes)
                if not is_datetime(df['date']):
                    df['date'] = df['date'].astype('datetime64[ns]')
                    # print('After astype')
                    # print(df)
                df['date_only'] = df['date'].dt.date
                # print('After trying spliting out date')
                # print(df)
                df['time_only'] = df['date'].dt.hour * 100 + df['date'].dt.minute
                # df['hour_only'] = df['date'].dt.hour
                # df['minute_only'] = df['date'].dt.minute
        
                # print('data after processing in dataframe after sleep is')
                # print(df)
                df = df.loc[(df['time_only'] > 200) & (df['time_only'] <= 1430) ].copy()
                # csvfilepath = Config.CONFIG_BASE_DatafilePath + '\Pre Market Volume Dump\Pre Market Volume Dump ' + row['Ticker'] + ' ' + today_date.strftime("%Y%m%d") + ' Pre Market Hours.csv'
                # df.to_csv(csvfilepath)
                
                # print('data before pivoting is')
                # print(df)
                # csvfilepath = Config.CONFIG_BASE_DatafilePath + '\Pre Market Volume Dump\Pre Market Volume Dump ' + row['Ticker'] + ' ' + today_date.strftime("%Y%m%d") + ' Before Pivot.csv'
                # df.to_csv(csvfilepath)
                
                df = pd.pivot_table(df, values='volume', index='date_only', aggfunc=np.sum).reset_index()
                
                # print('data after pivoting in dataframe after sleep is')
                # print(df)
                # csvfilepath = Config.CONFIG_BASE_DatafilePath + '\Pre Market Volume Dump\Pre Market Volume Dump ' + row['Ticker'] + ' ' + today_date.strftime("%Y%m%d") + ' After Pivot.csv'
                # df.to_csv(csvfilepath)
                
                for index, row2 in df.iterrows():
                    sql = "INSERT INTO fdata_us_gapper_premarket_volume (CaptureDate, Ticker, Volume) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE Volume=%s"
                    val = (row2['date_only'], row['Ticker'],row2['volume'],row2['volume'])
                    mycursor = mydb.cursor()
                    mycursor.execute(sql, val)
                    mydb.commit()
                    # print('After insert for '+ str(row2['date_only']) + ':' + str(row['Ticker']) + ':' + str(row2['volume']))
                
                # print('Data after uploading to DB, to be exported to ' + Config.CONFIG_BASE_DatafilePath + 'Pre Market Volume Dump ' + row['Ticker'] + ' ' + today_date.strftime("%Y%m%d") + '.csv')
                # df.to_csv(Config.CONFIG_BASE_DatafilePath + 'Pre Market Volume Dump ' + row['Ticker'] + ' ' + today_date.strftime("%Y%m%d") + '.csv')
                # print(df)
                # df.to_csv(r'd:\temp\output3.csv')
        
            # except Exception:
            #     print('Fail to process ' + row['Ticker'])
            #     pass  
            Request_ID = Request_ID + 1
        now = datetime.now()
        if (now.hour >= 14):
            print('Sleeping for 2 secs')
            time.sleep(2)
        else:
            print('Sleeping for 30 secs')
            time.sleep(30)
    if Running_Mode == 'OneOff':
        break
        
    

time.sleep(1) #Sleep interval to allow time for connection to server

# #Create contract object
# stock_contract = Contract()
# # apple_contract.symbol = 'AAPL'
# stock_contract.symbol = 'APPS'
# stock_contract.secType = 'STK'
# stock_contract.exchange = 'SMART'
# stock_contract.currency = 'USD'


# queryTime = datetime.today().strftime("%Y%m%d %H:%M:%S")
# app.reqHistoricalData(i, stock_contract, queryTime, "40 D", "30 mins", "TRADES", 0, 1, False, [])

# while (len(app.df) == 0):
#     time.sleep(10) #Sleep interval to allow time for incoming price data

# print('data in dataframe after sleep is')
# print(app.df)



app.disconnect()