# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 04:06:25 2021

@author: Henry Cheung
"""
import Config


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
# from ibapi.contract import Contract
# from ibapi.common import BarData
from ibapi.contract import *
from ibapi.common import *

import threading
import time
import datetime
import pandas as pd

Request_ID = 2000
Request_Data_Item = 'TRADES'
DownloadError = False

class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)
		self.clearCache()     
    
	def clearCache(self):
		self.data = {'TRADES':[],'BID':[],'ASK':[]}
		self.df = {'TRADES':pd.DataFrame(),'BID':pd.DataFrame(),'ASK':pd.DataFrame()}        
        
	def tickPrice(self, reqId, tickType, price, attrib):
		if tickType == 2 and reqId == 1:
			print('The current ask price is: ', price)

	def historicalData(self, reqId:int, bar: BarData):
		global Request_Data_Item
		self.data[Request_Data_Item].append(vars(bar))
# 		print("HistoricalData. ReqId:", reqId, "BarData.", bar)
		pass

	def historicalDataEnd(self, reqId: int, start: str, end: str):
		super().historicalDataEnd(reqId, start, end)
		global Request_Data_Item
		self.df[Request_Data_Item] = pd.DataFrame(self.data[Request_Data_Item])
		self.df[Request_Data_Item]['date'] = pd.to_datetime(self.df[Request_Data_Item]['date'])
		self.df[Request_Data_Item].set_index('date', inplace=True)
		print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end, " for ", Request_Data_Item)

	def error(self, reqId: TickerId, errorCode: int, errorString: str):
		global DownloadError, Request_ID
		super().error(reqId, errorCode, errorString)
		print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)
		if reqId == Request_ID:
		    print('for reqId = ' + str(reqId) + ' setting DownloadError to True')
		    DownloadError = True

def run_loop():
	app.run()

app = IBapi()
app.connect('127.0.0.1', 7496, 123)
# app2 = IBapi()
# app2.connect('127.0.0.1', 7496, 123)
# app.connect('127.0.0.1', 7497, 123)

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1) #Sleep interval to allow time for connection to server


# ------------

# ContractList = {"ES":{"secType":"FUT", "exchange":"GLOBEX", "currency":"USD", "lastTradeDateOrContractMonth":"202106"},
#                 "NQ":{"secType":"FUT", "exchange":"GLOBEX", "currency":"USD", "lastTradeDateOrContractMonth":"202106"},
#                 "YM":{"secType":"FUT", "exchange":"ECBOT", "currency":"USD", "lastTradeDateOrContractMonth":"202106"},
#                 "GC":{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":"202106"},
#                 "CL":{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":"202106"}
#                 }
# ContractList = {"NQ":{"secType":"FUT", "exchange":"GLOBEX", "currency":"USD", "lastTradeDateOrContractMonth":"202106"}


# for contract_symbol in ContractList:
#     app.df = pd.DataFrame()
#     app.data = []
#     DownloadError = False
    
#     contract = Contract()
#     contract.symbol = contract_symbol
#     contract.secType = ContractList[contract_symbol]["secType"]
#     contract.exchange = ContractList[contract_symbol]["secType"]
#     contract.currency = ContractList[contract_symbol]["currency"]
#     contract.lastTradeDateOrContractMonth = ContractList[contract_symbol]["lastTradeDateOrContractMonth"]
#     # app.reqHistoricalData(Request_ID, contract, '', "1 D", "10 secs", "TRADES", 0, 1, False, [])
#     while (len(app.df) == 0) and not DownloadError:
#         print('waiting for data, len(app.df) is '+ str(len(app.df)) + ' and DownloadError is ' + str(DownloadError))
#         time.sleep(5) #Sleep interval to allow time for incoming price data
    
#     if not DownloadError:
#         # print('data in dataframe after sleep is')
#         # print(app.df)
        
#         df = app.df.copy()
#         # print('Dataframe before exporting')
#         # print(df)
#         # csvfilepath = Config.CONFIG_BASE_DatafilePath + '\Pre Market Volume Dump\Pre Market Volume Dump ' + row['Ticker'] + ' ' + today_date.strftime("%Y%m%d") + ' All Hours.csv'
#         # df.to_csv(csvfilepath)
#         df = df.reset_index()
#         # print('After reset index, column types are')
#         # print(df.dtypes)
#         if not is_datetime(df['date']):
#             df['date'] = df['date'].astype('datetime64[ns]')
#             # print('After astype')
#             # print(df)
#         df['date_only'] = df['date'].dt.date
#         # print('After trying spliting out date')
#         # print(df)
#         df['time_only'] = df['date'].dt.hour * 100 + df['date'].dt.minute
    
#     Request_ID = Request_ID + 1
    

# ---------
    

#Create contract object
# contract = Contract()
# contract.symbol = "EUR"
# contract.secType = "CASH"
# contract.currency = "GBP"
# contract.exchange = "IDEALPRO"

#Create contract object
# contract = Contract()
# contract.symbol = "GC"
# contract.secType = "FUT"
# contract.exchange = "NYMEX"
# contract.currency = "USD"
# contract.lastTradeDateOrContractMonth = "202106"

#Create contract object
# contract = Contract()
# contract.symbol = "CL"
# contract.secType = "FUT"
# contract.exchange = "NYMEX"
# contract.currency = "USD"
# contract.lastTradeDateOrContractMonth = "202106"

#Create contract object
# contract = Contract()
# contract.symbol = "ES"
# contract.secType = "FUT"
# contract.exchange = "GLOBEX"
# contract.currency = "USD"
# contract.lastTradeDateOrContractMonth = "202106"


#Create contract object
# contract = Contract()
# contract.symbol = "NQ"
# contract.secType = "FUT"
# contract.exchange = "GLOBEX"
# contract.currency = "USD"
# contract.lastTradeDateOrContractMonth = "202106"

#Create contract object
# contract = Contract()
# contract.symbol = "YM"
# contract.secType = "FUT"
# contract.exchange = "ECBOT"
# contract.currency = "USD"
# contract.lastTradeDateOrContractMonth = "202106"

# app.reqHistoricalData(4102, contract, '', "1 D", "10 secs", "TRADES", 0, 1, False, [])
# app.reqHistoricalData(4102, contract, '', "2 D", "10 secs", "TRADES", 0, 1, False, [])
# app.reqHistoricalData(4102, contract, '', "2 D", "30 mins", "TRADES", 0, 1, False, [])

# app.reqHistoricalData(4102, contract, '', "1 D", "10 secs", "BID", 0, 1, False, [])
# app.reqHistoricalData(4102, contract, '', "1 D", "10 secs", "ASK", 0, 1, False, [])

# queryTime = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y%m%d %H:%M:%S")
# queryTime = "20201231 24:00:00"
# app.reqHistoricalData(Request_ID, contract, queryTime, "1 D", "10 secs", "TRADES", 0, 1, False, [])

# ContractList = {"NQ":[{"secType":"FUT", "exchange":"GLOBEX", "currency":"USD", "lastTradeDateOrContractMonth":"202106"}, {"LocalTimeZone":'Europe/London', "MarketTimeZone":'US/Central'}}

def MergeData(FuturesData, BarSize):
    MergedData = pd.DataFrame()
    for contract_name in FuturesData:
        for data_item in FuturesData[contract_name]:
            df = FuturesData[contract_name][data_item].copy()
            df['Ticker'] = contract_name
            df['Tick Type'] = data_item
            df['Bar Size'] = BarSize
            df = df.drop(columns=['date'])
            MergedData = MergedData.append(df)
    return MergedData
    

def GetFuturesData(ContractList, BarSize, HistoricalPeriod, DataEndDate):
    global Request_Data_Item
    FuturesData =  {}
    
    # Request_Data_Item = 'TRADES'
    # BarSize = "10 secs"
    # BarSize = "1 min"
    # HistoricalPeriod = "3 D"
    
    for contract_name in ContractList:
        FuturesData[contract_name] =  {'TRADES':pd.DataFrame(),'BID':pd.DataFrame(),'ASK':pd.DataFrame()}

        contract = Contract()
        contract.symbol = contract_name
        contract.secType = ContractList[contract_name][0]['secType']
        contract.exchange = ContractList[contract_name][0]['exchange']
        contract.currency = ContractList[contract_name][0]['currency']
        contract.lastTradeDateOrContractMonth = ContractList[contract_name][0]['lastTradeDateOrContractMonth']   

        for data_item in FuturesData[contract_name]:
            Request_Data_Item = data_item
            print('Request_Data_Item = ' + Request_Data_Item)
            
            DownloadError = False
            app.clearCache()
            # DataEndTime = "20210510 24:00:00"
            DataEndTime = DataEndDate.strftime("%Y%m%d") + " 24:00:00"
            app.reqHistoricalData(Request_ID, contract, DataEndTime, HistoricalPeriod, BarSize, Request_Data_Item, 0, 1, False, [])
            
            while (len(app.df[Request_Data_Item]) == 0) and not DownloadError:
                print('waiting for data for ' + contract_name + ', len(app.df) is '+ str(len(app.df[Request_Data_Item])) + ' and DownloadError is ' + str(DownloadError))
                time.sleep(5) #Sleep interval to allow time for incoming price data
            
            if not DownloadError:
                # FuturesData[Request_Data_Item] = FuturesData[Request_Data_Item].append(app.df[Request_Data_Item])
                FuturesData[contract_name][Request_Data_Item] = app.df[Request_Data_Item].copy().reset_index()
                
                FuturesData[contract_name][Request_Data_Item]['date'] = pd.to_datetime(FuturesData[contract_name][Request_Data_Item]['date']).dt.tz_localize(ContractList[contract_name][1]['LocalTimeZone'])
                FuturesData[contract_name][Request_Data_Item]['time_Market_timezone)'] = FuturesData[contract_name][Request_Data_Item].apply(lambda x: x['date'].tz_convert(ContractList[contract_name][1]['MarketTimeZone']), axis = 1)
                # FuturesData[contract_name][Request_Data_Item]['date (Market timezone) hour'] = FuturesData[contract_name][Request_Data_Item]['date (Market timezone)'].dt.hour
                # FuturesData[contract_name][Request_Data_Item]['date (Market timezone) minute'] = FuturesData[contract_name][Request_Data_Item]['date (Market timezone)'].dt.minute
                # FuturesData[contract_name][Request_Data_Item]['date (Market timezone) second'] = FuturesData[contract_name][Request_Data_Item]['date (Market timezone)'].dt.second
                
                # FuturesData[Request_Data_Item]['date (US timezone)'] = FuturesData[Request_Data_Item]['date']\.tz_convert('US/Central')
                
                # print('FuturesData for ')
                # print(FuturesData[contract_name][Request_Data_Item])
                # csvfilepath = Config.CONFIG_BASE_DatafilePath + '\Futures Dump\Futures Dump ' + contract_name + ' ' + Request_Data_Item + ' ' + BarSize + '.csv'
                # FuturesData[contract_name][Request_Data_Item].to_csv(csvfilepath)
            
            # Request_Data_Item = 'TRADES'
            # DownloadError = False
            # app.clearCache()
            # queryTime = "20210506 24:00:00"
            # app.reqHistoricalData(Request_ID, contract, queryTime, "1 D", "10 secs", Request_Data_Item, 0, 1, False, [])
            
            # while (len(app.df[Request_Data_Item]) == 0) and not DownloadError:
            #     print('waiting for data, len(app.df) is '+ str(len(app.df[Request_Data_Item])) + ' and DownloadError is ' + str(DownloadError))
            #     time.sleep(5) #Sleep interval to allow time for incoming price data
            
            # if not DownloadError:
            #     print('FuturesData at b before append')
            #     print(FuturesData[Request_Data_Item])
            #     print('app.df[Request_Data_Item] before append')
            #     print(app.df[Request_Data_Item])
            #     FuturesData[Request_Data_Item] = FuturesData[Request_Data_Item].append(app.df[Request_Data_Item])
            #     print('FuturesData at b')
            #     print(FuturesData[Request_Data_Item])
                
            # FuturesData[Request_Data_Item] = FuturesData[Request_Data_Item].sort_values(by=['date'])
                
            # csvfilepath = Config.CONFIG_BASE_DatafilePath + '\Futures Dump\Futures Dump ' + Request_Data_Item + 'b.csv'
            # FuturesData[Request_Data_Item].to_csv(csvfilepath)
            
            
            #Request Market Data
            # app.reqMktData(1, contract, '', False, False, [])
            
            
            # queryTime = (datetime.datetime.today() - datetime.timedelta(days=180)).strftime("%Y%m%d %H:%M:%S")
            # app.reqHistoricalData(4102, ContractSamples.EurGbpFx(), queryTime, "1 M", "1 day", "MIDPOINT", 1, 1, False, [])
            
            
            # queryTime = (datetime.datetime.today() - datetime.timedelta(days=180)).strftime("%Y%m%d %H:%M:%S")
            # app.reqHistoricalData(4102, apple_contract, queryTime, "1 M", "1 day", "MIDPOINT", 1, 1, False, [])
            
            
    # time.sleep(10) #Sleep interval to allow time for incoming price data
    app.disconnect()
    
    
    # queryTime = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y%m%d %H:%M:%S")
    # app.reqHistoricalData(4102, contract, queryTime, "3 D", "1 min", "TRADES", 1, 1, False, [])
    # app.reqHistoricalData(4102, contract, queryTime, "3 D", "10 secs", "TRADES", 1, 1, False, [])
    # app.reqHistoricalData(4102, contract, '', "3 D", "10 secs", "TRADES", 1, 1, False, [])
    # app.reqHistoricalData(4102, contract, '', "3 D", "10 secs", "TRADES", 0, 1, False, [])
    # app.reqHistoricalData(4102, contract, '', "3 D", "30 mins", "TRADES", 0, 1, False, [])
    # app.reqHistoricalData(4102, contract, '', "3 D", "10 secs", "TRADES", 0, 1, False, [])
    # app.reqHistoricalData(4102, contract, '', "3 D", "1 min", "TRADES", 0, 1, False, [])
    # app.reqHistoricalData(4102, contract, '', "3 D", "10 secs", "TRADES", 1, 1, False, [])
    if DataEndTime is not None:
        print(DataEndTime)
    return MergeData(FuturesData, BarSize)