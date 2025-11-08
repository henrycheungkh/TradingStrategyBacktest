# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 04:06:25 2021

@author: Henry Cheung
"""
import InvestmentAnalytics.Config as Config
from InvestmentAnalytics.IB.IBApiProcess import *

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import *
from ibapi.common import *

import logging
import threading
import time
import os
from datetime import datetime
import pandas as pd


# IB_API_hostname = os.getenv('TradeAnalysis_IB_API_hostname')
# IB_API_port = int(os.getenv('TradeAnalysis_IB_API_port'))
# IB_API_clientId = int(os.getenv('TradeAnalysis_IB_API_clientId'))

IB_API_hostname = Config.CONFIG_IB_CONNECTION_HOST
IB_API_port = Config.CONFIG_IB_CONNECTION_PORT
IB_API_clientId = Config.CONFIG_IB_CONNECTION_DEFAULT_CLIENT_ID 

print('IB_API_hostname = ' + IB_API_hostname)
print('IB_API_port = ')
print(IB_API_port)
print('IB_API_clientId = ')
print(IB_API_clientId)
time.sleep(10)

ErrorCodeIgnored = [1100, 1102, 2104, 2106, 2108, 2158]
Request_ID = 2000
Request_Data_Item = 'TRADES'
DownloadError = False

class IBapi(EWrapper, EClient):
    def __init__(self, IBApiProcessList):
        EClient.__init__(self, self)
        self.IBApiProcessList = IBApiProcessList
        self.Initiate()
    
    def Initiate(self):
        self.Alive = True
        for process in self.IBApiProcessList:
            process.InitiateProcess()
        
    def tickPrice(self, reqId, tickType, price, attrib):
        for process in self.IBApiProcessList:
            if reqId >= process.RequestID_Range[0] and reqId <= process.RequestID_Range[1]:
                process.tickPrice(reqId, tickType, price, attrib)

    def historicalData(self, reqId:int, bar: BarData):
        # print(bar)
        for process in self.IBApiProcessList:
            if reqId >= process.RequestID_Range[0] and reqId <= process.RequestID_Range[1]:
                process.historicalData(reqId, bar)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        for process in self.IBApiProcessList:
            if reqId >= process.RequestID_Range[0] and reqId <= process.RequestID_Range[1]:
                process.historicalDataEnd(reqId, start, end)

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        # super().error(reqId, errorCode, errorString)
        # print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)
        if errorCode not in ErrorCodeIgnored:
            for process in self.IBApiProcessList:
                if reqId >= process.RequestID_Range[0] and reqId <= process.RequestID_Range[1]:
                    process.error(reqId, errorCode, errorString)

app = None
IBprocess = None
ProcessReturn = {}

def run_loop():
    app.run()
    
def RunRunProcess(index):
    ProcessReturn[index] = IBprocess.RunProcess(app)

def RunIBApiProcessHub(IBApiProcessList):
    print('Start of RunIBApiProcessHub')
    global app, IBprocess
    app = IBapi(IBApiProcessList)
    # app.connect('127.0.0.1', 7496, 123)
    app.connect(IB_API_hostname, IB_API_port, IB_API_clientId)
    
    #Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    threads = list()
    index = 0
    
    # for process in IBApiProcessList:
    #     ProcessReturn.append(None)
        
    for process in IBApiProcessList:
        logging.info("Main    : create and start thread %d.", index)
        IBprocess = process
        x = threading.Thread(target=RunRunProcess, args=([index]), daemon=True)
        threads.append(x)
        x.start()
        index = index + 1
        
    for index, thread in enumerate(threads):
        logging.info("Main    : before joining thread %d.", index)
        thread.join()
        logging.info("Main    : thread %d done", index)

    time.sleep(1) 
    
    print('To disconnect')
    app.disconnect()
    time.sleep(10) 
    
    return ProcessReturn