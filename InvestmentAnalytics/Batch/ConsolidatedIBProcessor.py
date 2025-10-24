# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 09:29:54 2023

@author: Henry Cheung
"""


# import InvestmentAnalytics.Config as Config
# import InvestmentAnalytics.DBUtil as DBUtil

# import logging
# logging.disable(logging.INFO)

from InvestmentAnalytics.IB.IBApiProcessHub import RunIBApiProcessHub


import InvestmentAnalytics.IB.ScreenGapperByIBLib as ScreenGapperByIBLib
from InvestmentAnalytics.IB.IBApiProcessStrategyExecution import IBapiStrategyExecution

ProcessList = []

ib_api_consolidated_process = None

# ScreenGapperByIBLib.StandardStart(ib_api_consolidated_process)
ib_api_screen_gapper_process = ScreenGapperByIBLib.InitiateAndGetIBApiProcess(RequestID_Range = [1000, 1049])
ProcessList.append(ib_api_screen_gapper_process)

# ib_api_strategy_execution_process = IBapiStrategyExecution(RequestID_Range = [1040, 1040])
# ib_api_strategy_execution_process = IBapiStrategyExecution(RequestID_Range = [2000, 2000])
# ProcessList.append(ib_api_strategy_execution_process)

print('len of ProcessList is ' + str(len(ProcessList)))

ProcessReturnList = RunIBApiProcessHub(ProcessList)    


