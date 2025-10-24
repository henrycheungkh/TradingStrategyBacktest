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

from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy import StrategyBacktest, FuturesStrategyBacktest
# from InvestmentAnalytics.MarketDataReader import FuturesPriceAnalysisContext

pd.set_option('display.max_columns', None)

# StartDate = datetime(2021, 3, 1)
# StartDate = datetime(2021, 7, 21)
# EndDate = datetime(2021, 7, 30)

# RandomNoiseTickerStdev = [0.4/250/10, 0.8/250/10]
RandomNoiseTickerStdev = [0.4/250/10]
InsertRandomNoiseTicker = True
RapidCalibrationTopScenarioSelectedCount = 1

TickerFilter = []

# TickerFilter = ['YM']
# TickerFilter = ['ES']
# TickerFilter = ['NQ']
# TickerFilter = ['CL']

TickerFilter = ['CL', 'RTY']
# TickerFilter = ['ES', 'YM']

# TickerFilter = ['ES', 'YM', 'NQ']

# TickerFilter = ['RTY']
# TickerFilter = ['CL', 'ES', 'GC', 'HG', 'NQ', 'RTY', 'SI', 'YM', 'ZN', 'ZT']
# TickerFilter = ['YM', 'ZT']
# TickerFilter = ['YM', 'NQ']
# TimeFrameFilter = ""
TimeFrameFilter = " AND TimeFrame = '1 min'"
# TimeFrameFilter = " AND TimeFrame = '10 secs'"

ActiveContractPircesTrimmedColumns = ['ticker', 'DataType', 'tDateTime', 'Date', 'TimeInStandardUnit', 'high_adj', 'low_adj', 'open_adj', 'close_adj', 'MarketTimeSectionID', 'date id', 'time id']

ResultOutputFolderPath = r'd:\temp\\'

AnalysisStartTime = datetime.now()
print('Analysis started at ' + str(AnalysisStartTime))

def ExportCSV(backtest_result):
    for backtest_period in StrategyBacktest.BACKTEST_PERIOD_LABEL:
        backtest_result.BacktestingSummaryDict[backtest_period].to_csv(backtest_result.FullResultOutputFolderPath + r'Backtesting Summary ' + StrategyBacktest.BACKTEST_PERIOD_LABEL[backtest_period] + '.csv', index=False)
        backtest_result.BacktestingTradeRecord[backtest_period].to_csv(backtest_result.FullResultOutputFolderPath + r'Selected Trade Record ' + StrategyBacktest.BACKTEST_PERIOD_LABEL[backtest_period] + '.csv', index=False)

AnalysisContextList = None

dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
sql = "SELECT * FROM `fdata_backtest_batch` WHERE InstrumentType = 'Futures' AND Enabled = 1 " + TimeFrameFilter
BacktestBatchList = pd.read_sql_query(sql, dbcon)

for index, row in BacktestBatchList.iterrows():
    backtest_result = FuturesStrategyBacktest.getBacktestItem(row['BatchID'], AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, RandomNoiseTickerStdev = RandomNoiseTickerStdev, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount)
    AnalysisContextList = backtest_result.AnalysisContextList
    ExportCSV(backtest_result)
    
AnalysisEndTime = datetime.now()
analysis_minutes_diff = round((AnalysisEndTime - AnalysisStartTime).total_seconds() / 60.0)

print('Analysis ended at ' + str(AnalysisEndTime) + ', and ' + str(analysis_minutes_diff) + ' minutes taken')
# AnalysisContextList[0].FuturesData.ActiveContract.to_csv(r'd:\temp\ActiveContract.csv')
# AnalysisContextList[0].FuturesData.RolloverDate.to_csv(r'd:\temp\RolloverDate.csv')
# AnalysisContextList[0].FuturesData.ActiveContractPrices.loc[AnalysisContextList[0].FuturesData.ActiveContractPrices['DataType'] == 'TRADES'].to_csv(r'd:\temp\ActiveContractPrices_TRADES.csv')
# AnalysisContextList[0].FuturesData.ActiveContractPrices.loc[AnalysisContextList[0].FuturesData.ActiveContractPrices['ticker'] == 'RANDOM_NOISE'].to_csv(r'd:\temp\ActiveContractPrices_RANDOM_NOISE.csv')
