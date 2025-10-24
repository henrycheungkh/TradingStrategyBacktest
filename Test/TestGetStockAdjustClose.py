# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 18:13:40 2024

@author: Henry Cheung
"""


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
    
    def historicalData(self, reqId, bar):
        print(f"Date: {bar.date}, Close: {bar.close}, Volume: {bar.volume}, Count: {bar.barCount}")

def run_loop():
    app.run()

app = IBapi()
app.connect('127.0.0.1', 7496, 123) # Use your own port number here
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()
time.sleep(1) # Allow time for connection to server

# Create contract object
contract = Contract()
# contract.symbol = "AAPL"
contract.symbol = "NVDA"
contract.secType = "STK"
contract.currency = "USD"
contract.exchange = "SMART"

# Request historical data with adjustments
app.reqHistoricalData(reqId=1,
                      contract=contract,
                       endDateTime='',
                      # endDateTime="20240424-24:00:00",
                      # durationStr='2 Y',
                      durationStr='2 D',
                      barSizeSetting='1 day',
                        whatToShow='ADJUSTED_LAST',
                       # whatToShow='TRADES',
                      useRTH=0,
                      formatDate=1,
                      keepUpToDate=False,
                      chartOptions=[])

time.sleep(5) # Sleep to allow time for data to be returned
app.disconnect()


