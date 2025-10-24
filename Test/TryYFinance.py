# -*- coding: utf-8 -*-
"""
Created on Fri May  9 10:55:33 2025

@author: Henry Cheung
"""

import yfinance as yf
from yfinance.exceptions import YFRateLimitError

from curl_cffi import requests
session = requests.Session(impersonate="chrome")

# ticker = yf.Ticker('AAPL')
ticker = yf.Ticker('AAPL', session=session)
data = ticker.history(period="1d")

print(data)
