# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 10:59:30 2023

@author: Henry Cheung
"""


from ib_insync import IB, Stock
import nest_asyncio
nest_asyncio.apply()


def fetch_dividend_data(ib, ticker):
    contract = Stock(ticker, exchange='SMART', currency='USD')
    details = ib.reqFundamentalData(contract, 'ReportsFinSummary')
    
    # Here, I'm just returning the raw XML data. You might want to parse it for relevant details.
    return details

if __name__ == "__main__":
    # Create an IB instance and connect
    ib = IB()
    # ib.connect('127.0.0.1', 7497, clientId=1)  # 7497 is the default port for TWS paper trading
    ib.connect('127.0.0.1', 7496, clientId=1)  # 7497 is the default port for TWS paper trading

    ticker = 'AAPL'
    data = fetch_dividend_data(ib, ticker)
    print(data)  # This will print XML data. You'll need to parse this to extract dividend information.

    ib.disconnect()
