# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 02:33:37 2020

@author: Henry Cheung
"""
from InvestmentAnalytics.EmailModule import SendEmail
from datetime import date

from InvestmentAnalytics.Download_HL import DownloadNewsBatch 
from InvestmentAnalytics.Download_HL import GetTickersList 

import InvestmentAnalytics.Config as Config
from datetime import datetime

import logging
import threading
import time
import sys

def DownloadNewsBatchThread(name, BaseURL, Tickers, TickerAlias, DaysOfNews, StockHolded, UploadToDBFlag):
    logging.info("Thread %s: starting", name)
    if StockHolded:
        HoldingNewsTextList.extend(DownloadNewsBatch(BaseURL, Tickers, TickerAlias, DaysOfNews, DisplayLoadingStatus = False, ThreadID = name, UploadToDB = UploadToDBFlag)[0])
    else:
        with threading.Lock():
            NewsTextList.extend(DownloadNewsBatch(BaseURL, Tickers, TickerAlias, DaysOfNews, DisplayLoadingStatus = False, ThreadID = name, UploadToDB = UploadToDBFlag)[0])
    logging.info("Thread %s: finishing", name)

NewsTextList = []
HoldingNewsTextList = []
DaysOfNews = 3
TickerCountPerThread = 200
BaseURL = Config.CONFIG_HL_BASE_URL

if __name__ == "__main__":

    UploadToDB = False
    if len(sys.argv) > 1:
        if sys.argv[1] == 'UploadToDB':
            UploadToDB = True

    # Tickers, TickersOfHolding, TickersOfNonHolding, TickerAlias = GetTickersList(" and Ticker = 'AUTO.L'")
    Tickers, TickersOfHolding, TickersOfNonHolding, TickerAlias = GetTickersList()
    
    # print('TickersOfNonHolding is ')
    # print(TickersOfNonHolding)




    SplitTickers = Config.SplitDataframe(TickersOfNonHolding, TickerCountPerThread)
    print("Number of Tickers Batch = " + str(len(SplitTickers)))

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    threads = list()
    x = threading.Thread(target=DownloadNewsBatchThread, args=(len(SplitTickers), BaseURL, TickersOfHolding, TickerAlias, DaysOfNews, True, UploadToDB), daemon=True)
    threads.append(x)
    x.start()
    
    for index in range(len(SplitTickers)):
        # print('SplitTickers is')
        # print(SplitTickers)
        logging.info("Main    : create and start thread %d.", index)
        x = threading.Thread(target=DownloadNewsBatchThread, args=(index, BaseURL, SplitTickers[index], TickerAlias, DaysOfNews, False, UploadToDB), daemon=True)
        threads.append(x)
        x.start()

    # x = threading.Thread(target=DownloadNewsBatchThread, args=(len(SplitTickers), BaseURL, TickersOfHolding, DaysOfNews, True, UploadToDB), daemon=True)
    # threads.append(x)
    # x.start()

    for index, thread in enumerate(threads):
        logging.info("Main    : before joining thread %d.", index)
        thread.join()
        logging.info("Main    : thread %d done", index)

    NewsTextList = sorted(NewsTextList,key=lambda l:l[1], reverse=True)

    
    
    
    
    # print('TickersOfHolding is')
    # print(TickersOfHolding)
    # print('----------News for Holding---------- at ' + str(datetime.now()))
    # HoldingNewsTextList = DownloadNewsBatch(BaseURL, TickersOfHolding, DaysOfNews)[0]
    # # print('----------News for Other Stock---------- at ' + str(datetime.now()))
    # # NewsTextList = DownloadNewsBatch(BaseURL, TickersOfNonHolding, DaysOfNews)[0]
    # NewsTextList = sorted(NewsTextList,key=lambda l:l[1], reverse=True)
    
    
    
    
    
    
    FullNewsTextList = HoldingNewsTextList + NewsTextList
    AccumulatedNewsText = "" 
    for news in FullNewsTextList:
        AccumulatedNewsText = AccumulatedNewsText + news[0] + "<BR>" + "<BR>"
    
    if not UploadToDB:
        SendEmail(['henry.cheungkh@gmail.com'], 'London Stock News ' + date.today().strftime("%B %d, %Y"), AccumulatedNewsText)
        # SendEmail(['henry.cheungkh@gmail.com'], 'London Stock News ' + date.today().strftime("%B %d, %Y"), AccumulatedNewsText)
