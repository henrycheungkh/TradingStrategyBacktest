# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 13:50:31 2021

@author: Henry Cheung
"""
import os
import sys

DebugMode = False
# DebugMode = True

if DebugMode:
    WebSynchronisation = 'WebSynOff'
else:
    WebSynchronisation = sys.argv[1]
    
if len(sys.argv) > 2:
    StockFilter = " AND ticker in ("
    StockFilterList = sys.argv[2].split(",")
    FirstItem = True
    for ticker in StockFilterList:
        if not FirstItem:
            StockFilter = StockFilter + ", "
        else:
            FirstItem = False
        StockFilter = StockFilter + "'" + ticker + "'"
    StockFilter = StockFilter + ")"
    print('Stock Filter is ' + StockFilter)
else:
    StockFilter = ""
        
import InvestmentAnalytics.IB.ScreenGapperByIBLib as ScreenGapperByIBLib
ScreenGapperByIBLib.StandardStart(None, isStartWebSynchronisation = (WebSynchronisation == 'WebSynOn'), StockFilter = StockFilter)


