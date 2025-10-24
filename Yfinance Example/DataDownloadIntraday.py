# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 23:01:41 2020

@author: Henry Cheung
"""


import yfinance as yf

data = yf.download("SPY AAPL", start="2020-06-22", end="2020-06-26", interval = "1m")
print(data)

data = yf.download("EURUSD=X GC=F GBPUSD=X", start="2020-06-22", end="2020-06-26", interval = "1m")
print(data)

data = yf.download("VUKE.L CCL.L", start="2020-06-22", end="2020-06-26", interval = "1m")
print(data)