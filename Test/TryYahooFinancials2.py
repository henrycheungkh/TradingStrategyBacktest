# -*- coding: utf-8 -*-
"""
Created on Sun Jul 11 09:53:18 2021

@author: Henry Cheung
"""


import yfinance as yf


arkk = yf.Ticker("ARKK")
print(arkk.info['legalType'])
