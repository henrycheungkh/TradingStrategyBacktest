# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 16:47:38 2023

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

NYTargetTime = pytz.timezone('America/New_York').localize(datetime.datetime(2023,3,28,17,25,0))

contract = Contract()
contract.symbol = "ES"
contract.secType = "FUT"
contract.exchange = "CME"
contract.currency = "USD"
contract.lastTradeDateOrContractMonth = "202306"

price_dict = None

class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)
	def tickPrice(self, reqId, tickType, price, attrib):
		if tickType == 2 and reqId == 1:
			print('The current ask price is: ', price)

	def historicalData(self, reqId:int, bar: BarData):
		print("HistoricalData. ReqId:", reqId, "BarData.", bar)
		price_dict = vars(bar)
		print(price_dict)

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

print("NYTargetTime is " + NYTargetTime.strftime("%Y%m%d-%H:%M:%S %z"))

LondonTargetTime = NYTargetTime.astimezone(pytz.timezone('Europe/London'))
print("LondonTargetTime is " + LondonTargetTime.strftime("%Y%m%d-%H:%M:%S %z"))



timediff = 10

while (timediff > 0):
    if timediff > 120:
        time.sleep(60)
    elif timediff > 60:
        time.sleep(30)
    elif timediff > 2:
        time.sleep(1)
    now = datetime.datetime.now()
    LondonNow = pytz.timezone('Europe/London').localize(now)
    NYNow = LondonNow.astimezone(pytz.timezone('America/New_York'))
    timediff = (LondonTargetTime - LondonNow).total_seconds()
    print('London Time:' + LondonNow.strftime("%Y%m%d-%H:%M:%S %z") + ', NY TIme: ' + NYNow.strftime("%Y%m%d-%H:%M:%S %z") + ', time diff to target time is ' + str(timediff))
    # app.reqHistoricalData(4102, contract, LondonNow, "10 S", "10 secs", "TRADES", 1, 1, False, [])
    # app.reqHistoricalData(4102, contract, LondonNow.strftime("%Y%m%d-%H:%M:%S"), "10 S", "10 secs", "TRADES", 1, 1, False, [])
    app.reqHistoricalData(4102, contract, "", "10 S", "10 secs", "TRADES", 1, 1, False, [])




