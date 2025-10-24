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
import pytz
# from datetime import datetime

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

	def tickPrice(self, reqId, tickType, price, attrib):
        # https://interactivebrokers.github.io/tws-api/tick_types.html
		if tickType in [1,2,4]:
		    print(f"tickPrice. reqId: {reqId}, price: {price}, attribs: {attrib}")
		    print(tickType)
# 		print("tickPrice: " + str(price))

	def tickSize(self, reqId, tickType, size):
# 		print(f"tickSize. reqId: {reqId}, size: {size}")
# 		print("tickSize: " + str(size))
		pass

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
# contract.symbol = "ES"
contract.symbol = "NQ"
contract.secType = "FUT"
# contract.exchange = "GLOBEX"
contract.exchange = "CME"
contract.currency = "USD"
contract.lastTradeDateOrContractMonth = "202306"


#Create contract object
# contract = Contract()
# contract.symbol = "NQ"
# contract.secType = "FUT"
# contract.exchange = "GLOBEX"
# contract.currency = "USD"
# contract.lastTradeDateOrContractMonth = "202112"

#Create contract object
# contract = Contract()
# contract.symbol = "YM"
# contract.secType = "FUT"
# contract.exchange = "ECBOT"
# contract.currency = "USD"
# contract.lastTradeDateOrContractMonth = "202106"

#Create contract object
# contract = Contract()
# contract.symbol = "2YY"
# contract.symbol = "10Y"
# contract.symbol = "30Y"
# contract.secType = "FUT"
# contract.exchange = "ECBOT"
# contract.currency = "USD"
# contract.lastTradeDateOrContractMonth = "202201"


#Create contract object
# contract = Contract()
# contract.symbol = "VIX"
# # # contract.symbol = "VIX IND"
# # # contract.symbol = "VX"
# contract.secType = "FUT"
# contract.exchange = "CFE"
# # # contract.exchange = "ECBOT"
# contract.currency = "USD"
# contract.lastTradeDateOrContractMonth = "202203"


# queryTime = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y%m%d %H:%M:%S")
# TimeLondon = datetime.datetime.today() - datetime.timedelta(days=1)
TimeLondon = datetime.datetime.today()

TimeLondon = datetime.datetime.now()

london_tz = pytz.timezone('Europe/London')
tz_time = london_tz.localize(TimeLondon)

utc_tz = pytz.timezone('UTC')
utc_time = tz_time.astimezone(utc_tz)

queryTimeUTC = utc_time.strftime("%Y%m%d-%H:%M:%S")

# queryTimeLondon = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y%m%d %H:%M:%S")
# queryTimeLondon = datetime.datetime.today().strftime("%Y%m%d %H:%M:%S")
# queryTime = queryTimeLondon

queryTime = queryTimeUTC

print("queryTime is " + queryTime)

ny_tz = pytz.timezone('America/New_York')
# targetTime = datetime.datetime.strptime("20230328-06:21:00", "%Y%m%d-%H:%M:%S")
# targetTime = datetime.datetime.strptime("20230328-06:21:00 America/New_York", "%Y%m%d-%H:%M:%S %Z")
targetTime = datetime.datetime(2023,3,28,6,21,00,tzinfo=ny_tz)
print("targetTime is " + targetTime.strftime("%Y%m%d-%H:%M:%S"))
targetTime = targetTime.astimezone(london_tz)
print("targetTime in London time is " + targetTime.strftime("%Y%m%d-%H:%M:%S"))

# app.reqHistoricalData(4102, contract, queryTime, "3 D", "1 min", "TRADES", 1, 1, False, [])
# app.reqHistoricalData(4102, contract, queryTime, "3 D", "10 secs", "TRADES", 1, 1, False, [])
# app.reqHistoricalData(4102, contract, queryTime, "1 D", "5 secs", "TRADES", 1, 1, False, [])
# app.reqHistoricalData(4102, contract, queryTime, "1 D", "1 secs", "TRADES", 1, 1, False, [])
# app.reqHistoricalData(4102, contract, queryTime, "60 S", "10 secs", "TRADES", 1, 1, False, [])
# app.reqHistoricalData(4102, contract, "", "60 S", "10 secs", "TRADES", 1, 1, False, [])

app.reqMktData(1001, contract, "", False, False, []);

#Request Market Data
# app.reqMktData(1, contract, '', False, False, [])


# queryTime = (datetime.datetime.today() - datetime.timedelta(days=180)).strftime("%Y%m%d %H:%M:%S")
# app.reqHistoricalData(4102, ContractSamples.EurGbpFx(), queryTime, "1 M", "1 day", "MIDPOINT", 1, 1, False, [])


# queryTime = (datetime.datetime.today() - datetime.timedelta(days=180)).strftime("%Y%m%d %H:%M:%S")
# app.reqHistoricalData(4102, apple_contract, queryTime, "1 M", "1 day", "MIDPOINT", 1, 1, False, [])


time.sleep(10) #Sleep interval to allow time for incoming price data
app.disconnect()
print("queryTime is " + queryTime)
# print('queryTimeLondon is ' + queryTimeLondon)
