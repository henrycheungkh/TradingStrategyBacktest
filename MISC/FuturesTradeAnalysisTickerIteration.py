# -*- coding: utf-8 -*-
"""
Created on Wed Jun 23 23:31:21 2021

@author: Henry Cheung
"""

from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import pymysql
import InvestmentAnalytics.Config as Config

# from InvestmentAnalytics.StrategyPerformanceResult import *
# from InvestmentAnalytics.FuturesTradingStrategy import *
# from InvestmentAnalytics.MarketDataReader import FuturesPriceAnalysisContext
from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy import StrategyBacktest, FuturesStrategyBacktest

pd.set_option('display.max_columns', None)

# StartDate = datetime(2021, 3, 1)
# StartDate = datetime(2021, 7, 21)
# EndDate = datetime(2021, 7, 30)

# TimeFrameFilter = ""
# TimeFrameFilter = " AND TimeFrame = '1 min'"
TimeFrameFilter = " AND TimeFrame = '10 secs'"

# TickerList = ['ES']
# TickerList = ['ES', 'NQ']
# TickerList = []
TickerList = ['ES','NQ','RTY','YM','ZN','ZT','GC','SI','CL','HG']
# TickerList = ['YM']
# TickerList = ['ES', 'NQ']
# TickerList = ['ES','NQ','RTY']
# TickerList = ['GC','HG']

ResultOutputFolderPath = r'd:\temp\\'
KeepOnlyWeekdays = True

AnalysisStartTime = datetime.now()
print('Analysis started at ' + str(AnalysisStartTime))

def AppendBacktestResult(backtest_result):
    # global BacktestingSummaryAllPeriodTop, BacktestingSummaryLast5tradesTop, BacktestingSummaryLast10tradesTop, selected_trade_record_all_period, selected_trade_record_last_5_trades, selected_trade_record_last_10_trades
    global BacktestingSummary, BacktestingTradeRecord

    for backtest_period in StrategyBacktest.BACKTEST_PERIOD_LABEL:
        BacktestingSummary[backtest_period] = BacktestingSummary[backtest_period].append(backtest_result.BacktestingSummaryDict[backtest_period])
        BacktestingTradeRecord[backtest_period] = BacktestingTradeRecord[backtest_period].append(backtest_result.BacktestingTradeRecord[backtest_period])

    
def ExportStrategyResultCSV(ResultOutputFolderPath):
    
    global BacktestingSummary, BacktestingTradeRecord

    for backtest_period in StrategyBacktest.BACKTEST_PERIOD_LABEL:
        BacktestingSummary[backtest_period] = BacktestingSummary[backtest_period].sort_values(by=['Sharpe Ratio after commission'], ascending=False)
        BacktestingSummary[backtest_period].to_csv(ResultOutputFolderPath + r'BacktestingSummary ' + StrategyBacktest.BACKTEST_PERIOD_LABEL[backtest_period] + '.csv', index=False)
        BacktestingTradeRecord[backtest_period].to_csv(ResultOutputFolderPath + r'selected_trade_record ' + StrategyBacktest.BACKTEST_PERIOD_LABEL[backtest_period] + '.csv', index=False)
    

dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
sql = "SELECT * FROM `fdata_backtest_batch` WHERE InstrumentType = 'Futures' AND Enabled = 1 " + TimeFrameFilter
BacktestBatchList = pd.read_sql_query(sql, dbcon)
print('Backtest Batches to be run are')
print(BacktestBatchList)

for index, row in BacktestBatchList.iterrows():

    BacktestingSummary = {}
    BacktestingTradeRecord = {}
    
    for backtest_period in StrategyBacktest.BACKTEST_PERIOD_LABEL:
        BacktestingSummary[backtest_period] = pd.DataFrame()
        BacktestingTradeRecord[backtest_period] = pd.DataFrame()

    
    for ticker in TickerList:
        AnalysisContextList = None
        TickerFilter = [ticker]
        backtest_result = FuturesStrategyBacktest.getBacktestItem(row['BatchID'], AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = False, MinimumTradeNumberCountForFullPeriod = 10)
        AnalysisContextList = backtest_result.AnalysisContextList
        # ExportCSV(backtest_result)
        AppendBacktestResult(backtest_result)
    
    ExportStrategyResultCSV(backtest_result.FullResultOutputFolderPath)

AnalysisEndTime = datetime.now()
analysis_minutes_diff = round((AnalysisEndTime - AnalysisStartTime).total_seconds() / 60.0)

print('Analysis ended at ' + str(AnalysisEndTime) + ', and ' + str(analysis_minutes_diff) + ' minutes taken')

