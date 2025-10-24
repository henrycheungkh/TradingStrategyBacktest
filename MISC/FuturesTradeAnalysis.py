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

pd.set_option('display.max_columns', None)

# StartDate = datetime(2021, 3, 1)
# StartDate = datetime(2021, 7, 21)
# EndDate = datetime(2021, 7, 30)

BatchType = "Full"
# BatchType = "Selected"

TickerFilter = []
# RandomNoiseTickerStdev = [0.4/250/10, 0.8/250/10]
# RandomNoiseTickerStdev = [0.4/250/10]
# InsertRandomNoiseTicker = True
RapidCalibrationTopScenarioSelectedCount = 0

# TickerFilter = ['CL', 'RTY']
# RapidCalibrationTopScenarioSelectedCount = 1
# RandomNoiseTickerStdev = None
# # InsertRandomNoiseTicker = False


# TickerFilter = ['YM']
# TickerFilter = ['ES']
# TickerFilter = ['NQ']
# TickerFilter = ['CL']


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

KeepOnlyWeekdays = False
KeepOnlyWeekdays = True

FillEveryTimeSlot = False
# FillEveryTimeSlot = True

InstrumentType = 'Futures'
# InstrumentType = 'FXFutures'
InstrumentType = 'Crypto'
# TickerFilter = ['EURUSD=X']

BatchGroup = 'Henry'

AnalysisStartTime = datetime.now()
print('Analysis started at ' + str(AnalysisStartTime))


def ExportCSV(backtest_result):
    for backtest_period in StrategyBacktest.BACKTEST_PERIOD_LABEL:
        backtest_result.BacktestingSummaryDict[backtest_period].to_csv(backtest_result.FullResultOutputFolderPath + r'Backtest Summary ' + StrategyBacktest.BACKTEST_PERIOD_LABEL[backtest_period] + '.csv', index=False)
        backtest_result.BacktestingTradeRecord[backtest_period].to_csv(backtest_result.FullResultOutputFolderPath + r'Trade Record ' + StrategyBacktest.BACKTEST_PERIOD_LABEL[backtest_period] + '.csv', index=False)

def InitBacktestResult():
    global BacktestingSummary, BacktestingTradeRecord
    for backtest_period in StrategyBacktest.BACKTEST_PERIOD_LABEL:
        BacktestingSummary[backtest_period] = pd.DataFrame()
        BacktestingTradeRecord[backtest_period] = pd.DataFrame()


def AppendBacktestResult(backtest_result, BacktestPeriodLabel):
    # global BacktestingSummaryAllPeriodTop, BacktestingSummaryLast5tradesTop, BacktestingSummaryLast10tradesTop, selected_trade_record_all_period, selected_trade_record_last_5_trades, selected_trade_record_last_10_trades
    global BacktestingSummary, BacktestingTradeRecord
    print('In AppendBacktestResult')
    print('BacktestPeriodLabel is ' + str(BacktestPeriodLabel))

    for backtest_period in BacktestPeriodLabel:
        # print('In AppendBacktestResult, backtest_result is')
        # print(backtest_result)
        BacktestingSummary[backtest_period] = BacktestingSummary[backtest_period].append(backtest_result.BacktestingSummaryDict[backtest_period])
        BacktestingTradeRecord[backtest_period] = BacktestingTradeRecord[backtest_period].append(backtest_result.BacktestingTradeRecord[backtest_period])
        # print('In AppendBacktestResult, BacktestingSummary is')
        # print(BacktestingSummary[backtest_period])

    
def ExportStrategyResultCSV(ResultOutputFolderPath, BatchID, BacktestPeriodLabel):
    
    global BacktestingSummary, BacktestingTradeRecord

    for backtest_period in BacktestPeriodLabel:
        # print('In ExportStrategyResultCSV')
        # print(BacktestingSummary[backtest_period])
        # BacktestingSummary[backtest_period].to_csv(r'd:\temp\Summary before adding abs.csv')
        BacktestingSummary[backtest_period]['Abs Sharpe Ratio after commission'] = BacktestingSummary[backtest_period]['Sharpe Ratio after commission'].abs()
        BacktestingSummary[backtest_period] = BacktestingSummary[backtest_period].sort_values(by=['Abs Sharpe Ratio after commission'], ascending=False).drop(['Abs Sharpe Ratio after commission'],axis='columns')
        BacktestingSummary[backtest_period].to_csv(ResultOutputFolderPath + str(BatchID) + r'_BacktestingSummary ' + BacktestPeriodLabel[backtest_period] + '.csv', index=False)
        BacktestingTradeRecord[backtest_period].to_csv(ResultOutputFolderPath + str(BatchID) + r'_selected_trade_record ' + BacktestPeriodLabel[backtest_period] + '.csv', index=False)

AnalysisContextList = None

dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
sql = "SELECT * FROM `fdata_backtest_batch` WHERE StrategyName = 'SharpeRatioStrategy' AND BatchGroup = '" + BatchGroup + "' AND InstrumentType = '" + InstrumentType + "' AND BatchType = '" + BatchType + "' AND Enabled = 1 " + TimeFrameFilter + " ORDER BY BatchID, BatchSubID"
# sql = "SELECT * FROM `fdata_backtest_batch` WHERE InstrumentType = '" + InstrumentType + "' AND BatchGroup = '" + BatchGroup + "' AND BatchType = '" + BatchType + "' AND Enabled = 1 " + TimeFrameFilter + " ORDER BY BatchID, BatchSubID"
# sql = "SELECT * FROM `fdata_backtest_batch` WHERE InstrumentType = '" + InstrumentType + "' AND BatchGroup = '" + BatchGroup + "' AND BatchID = 0 " + TimeFrameFilter
BacktestBatchList = pd.read_sql_query(sql, dbcon)
print('Backtest Batches to be run are')
print(BacktestBatchList)


BacktestingSummary = {}
BacktestingTradeRecord = {}

parameter_string = BacktestBatchList.loc[0, 'BacktestSummaryTradeCount']
BacktestSummaryTradeCount = [int(e) if e.isdigit() else e for e in parameter_string.split(',')]
BacktestPeriodLabel = {0:'full period'}
for backtest_trade_count in BacktestSummaryTradeCount:
    if backtest_trade_count != 0:
        BacktestPeriodLabel[backtest_trade_count] = 'last ' + str(backtest_trade_count) + ' trades'

# for backtest_period in StrategyBacktest.BACKTEST_PERIOD_LABEL:
for backtest_period in BacktestPeriodLabel:
    BacktestingSummary[backtest_period] = pd.DataFrame()
    BacktestingTradeRecord[backtest_period] = pd.DataFrame()
PriorBatchID = -1


for index, row in BacktestBatchList.iterrows():
    if BatchType == 'Selected':
        AnalysisContextList = None
    if (PriorBatchID != -1) and (row['BatchID'] != PriorBatchID):
        ExportStrategyResultCSV(backtest_result.FullResultOutputFolderPath, PriorBatchID, BacktestPeriodLabel)
        InitBacktestResult()
    # TickerFilter = row['TickerFilter']
    if row['TickerFilter'] is None:
        TickerFilter = []
    else:
        TickerFilter = [float(e) if e.isdigit() else e for e in row['TickerFilter'].split(',')]
    print('TickerFilter is ' + str(TickerFilter))
    if row['NoiseTickerStdev'] is None:
        RandomNoiseTickerStdev = []
    else:
        if row['NoiseTickerStdev'] == '':
            RandomNoiseTickerStdev = []
        else:
            RandomNoiseTickerStdev = [float(e) for e in row['NoiseTickerStdev'].split(',')]
    print('RandomNoiseTickerStdev is ' + str(RandomNoiseTickerStdev))
    backtest_result = FuturesStrategyBacktest.getBacktestItem(row['BatchGroup'], row['BatchID'], row['BatchSubID'], AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType)
    AnalysisContextList = backtest_result.AnalysisContextList
    AppendBacktestResult(backtest_result, BacktestPeriodLabel)

    # print('After exiting AppendBacktestResult')
    # print(BacktestingSummary[0])

    # if (PriorBatchID != -1) and (row['BatchID'] != PriorBatchID):
        # ExportStrategyResultCSV(backtest_result.FullResultOutputFolderPath, PriorBatchID)
        # InitBacktestResult()
    PriorBatchID = row['BatchID']
    # ExportCSV(backtest_result)

# print('Before entering ExportStrategyResultCSV')
# print(BacktestingSummary[0])

ExportStrategyResultCSV(backtest_result.FullResultOutputFolderPath, PriorBatchID, BacktestPeriodLabel)
    
AnalysisEndTime = datetime.now()
analysis_minutes_diff = round((AnalysisEndTime - AnalysisStartTime).total_seconds() / 60.0)

print('Analysis ended at ' + str(AnalysisEndTime) + ', and ' + str(analysis_minutes_diff) + ' minutes taken')

# AnalysisContextList[0].FuturesData.ActiveContract.to_csv(r'd:\temp\ActiveContract.csv')
# AnalysisContextList[0].FuturesData.RolloverDate.to_csv(r'd:\temp\RolloverDate.csv')
# AnalysisContextList[0].FuturesData.ActiveContractPrices.loc[AnalysisContextList[0].FuturesData.ActiveContractPrices['DataType'] == 'TRADES'].to_csv(r'd:\temp\ActiveContractPrices_TRADES.csv')
# AnalysisContextList[0].FuturesData.ActiveContractPrices.loc[AnalysisContextList[0].FuturesData.ActiveContractPrices['ticker'] == 'RANDOM_NOISE'].to_csv(r'd:\temp\ActiveContractPrices_RANDOM_NOISE.csv')
