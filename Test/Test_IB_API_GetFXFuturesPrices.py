# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 04:06:25 2021

@author: Henry Cheung
"""


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import BarData

import threading
import time
import datetime

class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)
	def tickPrice(self, reqId, tickType, price, attrib):
		if tickType == 2 and reqId == 1:
			print('The current ask price is: ', price)

	def historicalData(self, reqId:int, bar: BarData):
		print("HistoricalData. ReqId:", reqId, "BarData.", bar)
		pass

	def historicalDataEnd(self, reqId: int, start: str, end: str):
		super().historicalDataEnd(reqId, start, end)
		print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)

def run_loop():
	app.run()

app = IBapi()
app.connect('127.0.0.1', 7496, 123)

#Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1) #Sleep interval to allow time for connection to server

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
# contract.lastTradeDateOrContractMonth = "202112"


contract = Contract()
contract.symbol = "EUR"
contract.secType = "CASH"
contract.currency = "GBP"
contract.exchange = "IDEALPRO"
    
#Create contract object
# contract = Contract()
# contract.symbol = "YM"
# contract.secType = "FUT"
# contract.exchange = "ECBOT"
# contract.currency = "USD"
# contract.lastTradeDateOrContractMonth = "202106"

queryTime = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y%m%d %H:%M:%S")
app.reqHistoricalData(4102, contract, queryTime, "3 D", "1 min", "TRADES", 1, 1, False, [])
# app.reqHistoricalData(4102, contract, queryTime, "3 D", "10 secs", "TRADES", 1, 1, False, [])
# app.reqHistoricalData(4102, contract, queryTime, "1 D", "5 secs", "TRADES", 1, 1, False, [])
# app.reqHistoricalData(4102, contract, queryTime, "1 D", "1 secs", "TRADES", 1, 1, False, [])

#Request Market Data
# app.reqMktData(1, contract, '', False, False, [])


# queryTime = (datetime.datetime.today() - datetime.timedelta(days=180)).strftime("%Y%m%d %H:%M:%S")
# app.reqHistoricalData(4102, ContractSamples.EurGbpFx(), queryTime, "1 M", "1 day", "MIDPOINT", 1, 1, False, [])


# queryTime = (datetime.datetime.today() - datetime.timedelta(days=180)).strftime("%Y%m%d %H:%M:%S")
# app.reqHistoricalData(4102, apple_contract, queryTime, "1 M", "1 day", "MIDPOINT", 1, 1, False, [])


time.sleep(10) #Sleep interval to allow time for incoming price data
app.disconnect()