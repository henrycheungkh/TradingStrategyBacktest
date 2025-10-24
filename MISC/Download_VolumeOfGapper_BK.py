# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 04:06:25 2021

@author: Henry Cheung
"""

import Config

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import BarData

import threading
import time
from datetime import datetime, date
import pandas as pd
import pymysql

class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)
		self.data = []
		self.df = pd.DataFrame()

	def historicalData(self, reqId:int, bar: BarData):
		self.data.append(vars(bar))
# 		print("HistoricalData. ReqId:", reqId, "BarData.", bar)
		pass

	def historicalDataUpdate(self, reqId, bar):
		line = vars(bar)
        # pop date and make it the index, add rest to df
        # will overwrite last bar at that same time
		self.df.loc[pd.to_datetime(line.pop('date'))] = line

	def historicalDataEnd(self, reqId: int, start: str, end: str):
		super().historicalDataEnd(reqId, start, end)
		self.df = pd.DataFrame(self.data)
		self.df['date'] = pd.to_datetime(self.df['date'])
		self.df.set_index('date', inplace=True)
# 		print('data in dataframe is')
# 		print(self.df)
		print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)

def run_loop():
	app.run()

dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
today_date = date.today()
today_date = datetime.strptime('30042021', '%d%m%Y').date()

StockFilter = ""

# now = datetime.now()

print("Start uploading US gappers premarket volume for "+ today_date.strftime("%Y-%m-%d"))
StockFilter = " AND Ticker in ('APPS') "
sql = "SELECT Ticker FROM `fdata_us_gapper_tickers` WHERE CaptureDate = '" + today_date.strftime("%Y-%m-%d") +"' " + StockFilter
# print(sql)
Tickers = pd.read_sql_query(sql, dbcon)
print("Tickers count = " + str(len(Tickers)))
print(Tickers)

app = IBapi()
app.connect('127.0.0.1', 7496, 123)

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1) #Sleep interval to allow time for connection to server

i = 1000

for index, row in Tickers.iterrows():
    try:
        print('Start trying ' + row['Ticker'])
            
        app.df = pd.DataFrame()
        
        #Create contract object
        stock_contract = Contract()
        stock_contract.symbol = row['Ticker']
        stock_contract.secType = 'STK'
        stock_contract.exchange = 'SMART'
        stock_contract.currency = 'USD'
        
        queryTime = datetime.datetime.today().strftime("%Y%m%d %H:%M:%S")
        app.reqHistoricalData(i, stock_contract, queryTime, "40 D", "30 mins", "TRADES", 0, 1, False, [])
        
        while (len(app.df) == 0):
            time.sleep(10) #Sleep interval to allow time for incoming price data
        
        print('data in dataframe after sleep is')
        print(app.df)
        
        
        
    except Exception:
        pass  
    i = i + 1
        
app.disconnect()