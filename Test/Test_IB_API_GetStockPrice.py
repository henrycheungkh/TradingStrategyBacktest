# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 04:06:25 2021

@author: Henry Cheung
"""


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import BarData
# from ibapi.common import WshEventData

import threading
import time
import datetime
import pandas as pd

class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)
		self.data = []
		self.df = pd.DataFrame()
        
	def wshMetaData(self, reqId: int, dataJson: str):
		super().wshMetaData(reqId, dataJson)
		print("WshMetaData.", "ReqId:", reqId, "Data JSON:", dataJson)

        
	def tickPrice(self, reqId, tickType, price, attrib):
		if tickType == 2 and reqId == 1:
			print('The current ask price is: ', price)

	def historicalData(self, reqId:int, bar: BarData):
		self.data.append(vars(bar))
		print("HistoricalData. ReqId:", reqId, "BarData.", bar)
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

	def contractDetails(self, reqId, contractDetails):
		print('contractDetails is')
		print(contractDetails)
# 		for detail in contractDetails:
# 		    print("Contract Details -")
# 		    print(f"Request ID: {reqId}")
# 		    print(f"Symbol: {detail.contract.symbol}")
# 		    print(f"SecType: {detail.contract.secType}")
# 		    print(f"Exchange: {detail.contract.exchange}")
# 		    print(f"Currency: {detail.contract.currency}")
# 		    if detail.dividends:
# 		        for dividend in detail.dividends:
# 		            print(f"Dividend Date: {dividend.date}")
# 		            print(f"Amount: {dividend.amount}")
# 		            print(f"Payment Date: {dividend.paymentDate}")
# 		            print(f"Record Date: {dividend.recordDate}")
# 		            print(f"Declared Date: {dividend.declaredDate}")


def run_loop():
	app.run()

app = IBapi()
app.connect('127.0.0.1', 7496, 123)

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1) #Sleep interval to allow time for connection to server

#Create contract object
contract = Contract()
# contract.symbol = 'AAPL'
# contract.symbol = 'APPS'
# contract.symbol = 'PMCB'
contract.symbol = 'SGOV'
contract.secType = 'STK'
contract.exchange = 'SMART'
contract.currency = 'USD'


queryTime = datetime.datetime.today().strftime("%Y%m%d %H:%M:%S")
# app.reqHistoricalData(4102, contract, queryTime, "3 D", "30 mins", "TRADES", 0, 1, False, [])
app.reqHistoricalData(4102, contract, queryTime, "1 D", "1 day", "TRADES", 0, 1, False, [])

#Request Market Data
app.reqMktData(1, contract, '', False, False, [])

app.reqContractDetails(1100, contract)  # Replace '1' with a unique request ID

# app.reqWshMetaData(1100)
# app.reqWshMetaData(4103)


# wshEventData1 = WshEventData()
# wshEventData1.conId = 8314
# wshEventData1.startDate = "20220511"
# wshEventData1.totalLimit = 5
# app.reqWshEventData(1101, wshEventData1)


# queryTime = (datetime.datetime.today() - datetime.timedelta(days=180)).strftime("%Y%m%d %H:%M:%S")
# app.reqHistoricalData(4102, ContractSamples.EurGbpFx(), queryTime, "1 M", "1 day", "MIDPOINT", 1, 1, False, [])


# queryTime = (datetime.datetime.today() - datetime.timedelta(days=180)).strftime("%Y%m%d %H:%M:%S")
# app.reqHistoricalData(4102, contract, queryTime, "1 M", "1 day", "MIDPOINT", 1, 1, False, [])

while (len(app.df) == 0):
    time.sleep(10) #Sleep interval to allow time for incoming price data

print('data in dataframe after sleep is')
print(app.df)
app.disconnect()