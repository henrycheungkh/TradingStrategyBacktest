# -*- coding: utf-8 -*-
"""
Created on Thu Oct 28 00:22:53 2021

@author: Henry Cheung
"""


from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
# import pymysql
# import mysql.connector


import InvestmentAnalytics.Config as Config
import InvestmentAnalytics.DBUtil as DBUtil

pd.set_option('display.max_columns', None)

# mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
# mycursor = mydb.cursor()


# def UpdateLastRunTradeRecordSizePerSubBatch(StrategyName, BatchGroup, BacktestBatchID, BatchSubID, LastRunTradeRecordResultSize, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch'):
#     print('Start of UpdateLastRunTradeRecordSizePerSubBatch')
#     if BatchListDatabaseName is None:
#         FullBatchListTableName = BatchListTableName
#     else:
#         FullBatchListTableName = BatchListDatabaseName + '.' + BatchListTableName
#     sql = "UPDATE " + FullBatchListTableName + " SET LastRunMaxTradeRecordResultSize = " + str(LastRunTradeRecordResultSize) + " WHERE StrategyName = '" + StrategyName + "' AND BatchGroup = '" + BatchGroup + "' AND BatchID = " + str(BacktestBatchID) + " AND BatchSubID = " + str(BatchSubID)
#     print('sql is')
#     print(sql)
#     DBUtil.GetSQLAlchemyEngine().execute(sql)

#     # sql = "UPDATE fdata_backtest_batch SET LastBestAbsSharpeRatio = %s WHERE StrategyName = %s AND BatchGroup = %s AND BatchID = %s AND BatchSubID = %s"
#     # val = (LastRunTradeRecordResultSize, StrategyName, BatchGroup, BacktestBatchID, BatchSubID)
#     # mycursor.execute(sql, val)
#     # mydb.commit()   

def UpdateLastRunMaxTradeRecordSizePerSubBatch(StrategyName, BatchGroup, BacktestBatchID, BatchSubID, MaxLastRunTradeRecordResultSize, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch'):
    # dbcon = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
    # sql = "SELECT * FROM `fdata_backtest_batch` where StrategyName = '" + StrategyName + "' AND BatchID = " + str(BacktestBatchID) + " AND BatchGroup = '" + BatchGroup + "' AND BatchSubID = " + str(BatchSubID)
    # AnalysisContextParameters = pd.read_sql_query(sql, dbcon)
    
    if BatchListDatabaseName is None:
        FullBatchListTableName = BatchListTableName
    else:
        FullBatchListTableName = BatchListDatabaseName + '.' + BatchListTableName

    AnalysisContextParameters = pd.read_sql("SELECT * FROM " + FullBatchListTableName + " where StrategyName = '" + StrategyName + "' AND BatchID = " + str(BacktestBatchID) + " AND BatchGroup = '" + BatchGroup + "' AND BatchSubID = " + str(BatchSubID),con=DBUtil.GetSQLAlchemyEngine())    
    # AnalysisContextParameters = pd.read_sql("SELECT * FROM `fdata_backtest_batch` where StrategyName = '" + StrategyName + "' AND BatchID = " + str(BacktestBatchID) + " AND BatchGroup = '" + BatchGroup + "' AND BatchSubID = " + str(BatchSubID),con=DBUtil.GetSQLAlchemyEngine())    
    
    try:
        PriorLastRunMaxTradeRecordResultSize = AnalysisContextParameters.loc[0, 'LastRunMaxTradeRecordResultSize']
    except:
        PriorLastRunMaxTradeRecordResultSize = 0
    if PriorLastRunMaxTradeRecordResultSize is None:
        PriorLastRunMaxTradeRecordResultSize = 0
    if MaxLastRunTradeRecordResultSize > PriorLastRunMaxTradeRecordResultSize:
        # print('MaxLastRunTradeRecordResultSize = ' + str(MaxLastRunTradeRecordResultSize))
        # print('type of MaxLastRunTradeRecordResultSize is ' + str(type(MaxLastRunTradeRecordResultSize)))
        # print('StrategyName = ' + str(StrategyName))
        # print('type of StrategyName is ' + str(type(StrategyName)))
        # print('BatchGroup = ' + str(BatchGroup))
        # print('type of BatchGroup is ' + str(type(BatchGroup)))
        if str(type(BacktestBatchID)) == "<class 'numpy.int64'>":
            BacktestBatchID = BacktestBatchID.item()
        # print('BacktestBatchID = ' + str(BacktestBatchID))
        # print('type of BacktestBatchID is ' + str(type(BacktestBatchID)))
        if str(type(BatchSubID)) == "<class 'numpy.int64'>":
            BatchSubID = BatchSubID.item()
        # print('BatchSubID = ' + str(BatchSubID))
        # print('type of BatchSubID is ' + str(type(BatchSubID)))
        # if 
        # MaxLastRunTradeRecordResultSize = MaxLastRunTradeRecordResultSize.item()
# mycursor = mydb.cursor()

        sql = "UPDATE " + FullBatchListTableName + " SET LastRunMaxTradeRecordResultSize = " + str(MaxLastRunTradeRecordResultSize) + " WHERE StrategyName = '" + StrategyName + "' AND BatchGroup = '" + BatchGroup + "' AND BatchID = " + str(BacktestBatchID) + " AND BatchSubID = " + str(BatchSubID)
        DBUtil.GetSQLAlchemyEngine().execute(sql)

        # sql = "UPDATE fdata_backtest_batch SET LastRunMaxTradeRecordResultSize = %s WHERE StrategyName = %s AND BatchGroup = %s AND BatchID = %s AND BatchSubID = %s"
        # val = (MaxLastRunTradeRecordResultSize, StrategyName, BatchGroup, BacktestBatchID, BatchSubID)
        # # val = (0, StrategyName, BatchGroup, BacktestBatchID, BatchSubID)
        # mycursor.execute(sql, val)
        # mydb.commit()

# from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy import StrategyBacktest, FuturesStrategyBacktest
# from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy import FuturesStrategyBacktest
from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy import FuturesStrategyBacktest as FuturesStratBacktest



# def ExportCSV(backtest_result):
#     for backtest_period in StrategyBacktest.BACKTEST_PERIOD_LABEL:
#         backtest_result.BacktestingSummaryDict[backtest_period].to_csv(backtest_result.FullResultOutputFolderPath + r'Backtest Summary ' + StrategyBacktest.BACKTEST_PERIOD_LABEL[backtest_period] + '.csv', index=False)
#         backtest_result.BacktestingTradeRecord[backtest_period].to_csv(backtest_result.FullResultOutputFolderPath + r'Trade Record ' + StrategyBacktest.BACKTEST_PERIOD_LABEL[backtest_period] + '.csv', index=False)

def InitBacktestResult(BacktestPeriodLabel):
    global BacktestingSummary, BacktestingTradeRecord
    BacktestingSummary = {}
    BacktestingTradeRecord = {}
    for backtest_period in BacktestPeriodLabel:
        BacktestingSummary[backtest_period] = pd.DataFrame()
        BacktestingTradeRecord[backtest_period] = pd.DataFrame()

def UpdateLastBestAbsSharpeRatio(StrategyName, BatchGroup, BatchID, SharpeRatio, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch'):
    if BatchListDatabaseName is None:
        FullBatchListTableName = BatchListTableName
    else:
        FullBatchListTableName = BatchListDatabaseName + '.' + BatchListTableName

    sql = "UPDATE " + FullBatchListTableName + " SET LastBestAbsSharpeRatio = " + str(abs(SharpeRatio)) + " WHERE BatchGroup = '" + BatchGroup + "' AND BatchID = " + str(BatchID) + " AND StrategyName = '" + StrategyName + "'"
    DBUtil.GetSQLAlchemyEngine().execute(sql)

    # sql = "UPDATE fdata_backtest_batch SET LastBestAbsSharpeRatio = %s WHERE BatchGroup = %s AND BatchID = %s AND StrategyName = %s"
    # val = (abs(SharpeRatio), BatchGroup, BatchID, StrategyName)
    # mycursor.execute(sql, val)
    # mydb.commit()

def UpdateLastBestAbsSharpeRatioPerSubBatch(StrategyName, BatchGroup, BatchID, BatchSubID, LastRunTimeInMinute, SharpeRatio, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch'):
    # print('Start of UpdateLastBestAbsSharpeRatioPerSubBatch')
    if BatchListDatabaseName is None:
        FullBatchListTableName = BatchListTableName
    else:
        FullBatchListTableName = BatchListDatabaseName + '.' + BatchListTableName
        
    sql = "UPDATE " + FullBatchListTableName + " SET LastBestAbsSharpeRatio = " + str(abs(SharpeRatio)) + ", LastRunStartDate = StartDate, LastRunEndDate = EndDate, LastRunTimeInMinute = " + str(LastRunTimeInMinute) + " WHERE BatchGroup = '" + BatchGroup + "' AND BatchID = " + str(BatchID) + " AND BatchSubID = " + str(BatchSubID) + " AND StrategyName = '" + StrategyName + "'"
    DBUtil.GetSQLAlchemyEngine().execute(sql)
    # print('End of UpdateLastBestAbsSharpeRatioPerSubBatch')
    # sql = "UPDATE fdata_backtest_batch SET LastBestAbsSharpeRatio = %s, LastRunStartDate = StartDate, LastRunEndDate = EndDate, LastRunTimeInMinute = %s WHERE BatchGroup = %s AND BatchID = %s AND BatchSubID = %s AND StrategyName = %s"
    # val = (abs(SharpeRatio), LastRunTimeInMinute, BatchGroup, BatchID, BatchSubID, StrategyName)
    # mycursor.execute(sql, val)
    # mydb.commit()

def AppendBacktestResult(backtest_result, BacktestPeriodLabel, StrategyName = None, BatchGroup = None, BatchID = None, BatchSubID = None, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch'):
    global BacktestingSummary, BacktestingTradeRecord, BatchStartTime
    print('In AppendBacktestResult')
    print('BacktestPeriodLabel is ' + str(BacktestPeriodLabel))

    for backtest_period in BacktestPeriodLabel:
        # print('In AppendBacktestResult, backtest_period is ' + str(backtest_period))
        # print('backtest_result.BacktestingSummaryDict is ')
        # print(backtest_result.BacktestingSummaryDict)
        # print('backtest_result.BacktestingSummaryDict[backtest_period] is ')
        # print(backtest_result.BacktestingSummaryDict[backtest_period])
        
        # BacktestingSummary[backtest_period] = BacktestingSummary[backtest_period].append(backtest_result.BacktestingSummaryDict[backtest_period])
        BacktestingSummary[backtest_period] = pd.concat([BacktestingSummary[backtest_period], backtest_result.BacktestingSummaryDict[backtest_period]])
        
        # BacktestingTradeRecord[backtest_period] = BacktestingTradeRecord[backtest_period].append(backtest_result.BacktestingTradeRecord[backtest_period])
        BacktestingTradeRecord[backtest_period] = pd.concat([BacktestingTradeRecord[backtest_period], backtest_result.BacktestingTradeRecord[backtest_period]])
        
        
    
    if BatchSubID is not None:
        summary = backtest_result.BacktestingSummaryDict[0].copy()
        summary['Abs Sharpe Ratio after commission'] = summary['Sharpe Ratio after commission'].abs()
        # summary = summary.sort_values(by=['Abs Sharpe Ratio after commission'], ascending=False)
        # UpdateLastBestAbsSharpeRatioPerSubBatch(BatchGroup, BatchID, BatchSubID, summary['Abs Sharpe Ratio after commission'].iloc[0].astype(float))
        summary = summary.sort_values(by=['Abs Sharpe Ratio after commission'], ascending=False)
        try:
            batch_minutes_diff = round((datetime.now() - BatchStartTime).total_seconds() / 60.0)
            UpdateLastBestAbsSharpeRatioPerSubBatch(StrategyName, BatchGroup, BatchID, BatchSubID, batch_minutes_diff, summary['Abs Sharpe Ratio after commission'].max(), BatchListDatabaseName = BatchListDatabaseName, BatchListTableName = BatchListTableName)
        except Exception as e: print(e)
        
    
def ExportStrategyResultCSV(ResultOutputFolderPath, BacktestPeriodLabel, StrategyName = None, BatchGroup = None, BatchID = None):
    global BacktestingSummary, BacktestingTradeRecord
    for backtest_period in BacktestPeriodLabel:
        BacktestingSummary[backtest_period]['Abs Sharpe Ratio after commission'] = BacktestingSummary[backtest_period]['Sharpe Ratio after commission'].abs()
        BacktestingSummary[backtest_period] = BacktestingSummary[backtest_period].sort_values(by=['Abs Sharpe Ratio after commission'], ascending=False).drop(['Abs Sharpe Ratio after commission'],axis='columns')

        BacktestingSummary[backtest_period].insert(13, 'Maximum Draw Loss Ratio', 0)
        BacktestingSummary[backtest_period]['Maximum Draw Loss Ratio'] = BacktestingSummary[backtest_period]['max drawdown'] / BacktestingSummary[backtest_period]['average return per trade']
        BacktestingSummary[backtest_period].reset_index(level=0, inplace=True)
        # BacktestingSummary[backtest_period].to_csv(r'G:\TradeAnalysisProject\RoutineAnalysis\df_with_duplicate_axis_' + str(backtest_period) + '.csv')
        BacktestingSummary[backtest_period].loc[BacktestingSummary[backtest_period]['Sharpe Ratio after commission'] < 0, 'Maximum Draw Loss Ratio'] = BacktestingSummary[backtest_period]['max drawup'] / BacktestingSummary[backtest_period]['average return per trade']

        BacktestingSummary[backtest_period].to_csv(ResultOutputFolderPath + str(BatchID) + r'_BacktestingSummary ' + BacktestPeriodLabel[backtest_period] + '.csv', index=False)
        BacktestingTradeRecord[backtest_period].to_csv(ResultOutputFolderPath + str(BatchID) + r'_selected_trade_record ' + BacktestPeriodLabel[backtest_period] + '.csv', index=False)

    if BatchGroup is not None:
        try:
            UpdateLastBestAbsSharpeRatio(StrategyName, BatchGroup, BatchID, BacktestingSummary[0]['Sharpe Ratio after commission'].iloc[0].astype(float))
        except Exception as e: print(e)


def ListToSingleQuotedCSV(lst, value_wrapper):
    for i in range(len(lst)):
        lst[i] = value_wrapper + str(lst[i]) + value_wrapper
    return ",".join(lst)

def getSQLFilter(column_name, lst, value_wrapper = "'"):
    if lst is None:
        return ''
    if len(lst) == 0:
        return ''
    elif len(lst) == 1:
        return " AND " + column_name + " = " + value_wrapper + str(lst[0]) + value_wrapper
    else:
        return " AND " + column_name + " in (" + ListToSingleQuotedCSV(lst, value_wrapper) + ")"

# def RunTradeAnalysisBatch(BatchGroup, BatchType, ResultOutputFolderPath, TimeFrameList = [], InstrumentTypeList = [], StrategyNameList = [], BatchIDList = [], BatchSubIDList = [], KeepOnlyWeekdays = True, FillEveryTimeSlot = False):
def RunTradeAnalysisBatch(BatchGroup, BatchType, ResultOutputFolderPath, TimeFrameList = [], InstrumentTypeList = [], StrategyNameList = [], BatchIDList = [], BatchSubIDList = [], ClearDataAfterEachSubBatch = False, DebugFilepath = None, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch', Override_DBHost = None, Override_DBPort = None, Override_DBUser = None, Override_DBPassword = None):

    global BacktestingSummary, BacktestingTradeRecord, BatchStartTime
    BacktestingSummary = {}
    BacktestingTradeRecord = {}

    RapidCalibrationTopScenarioSelectedCount = 0
    
    ActiveContractPircesTrimmedColumns = ['ticker', 'DataType', 'tDateTime', 'Date', 'TimeInStandardUnit', 'high_adj', 'low_adj', 'open_adj', 'close_adj', 'MarketTimeSectionID', 'date id', 'time id']
    
    InstrumentTypeFilter = getSQLFilter('InstrumentType', InstrumentTypeList)
    StrategyNameFilter = getSQLFilter('StrategyName', StrategyNameList)
    TimeFrameFilter = getSQLFilter('TimeFrame', TimeFrameList)
    BatchIDFilter = getSQLFilter('BatchID', BatchIDList, "")
    BatchSubIDFilter = getSQLFilter('BatchSubID', BatchSubIDList, "")
    
    AnalysisStartTime = datetime.now()
    print('Analysis started at ' + str(AnalysisStartTime))
    
    AnalysisContextList = None
    
    # dbcon = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
    # sql = "SELECT * FROM `fdata_backtest_batch` WHERE Enabled = 1 AND BatchGroup = '" + BatchGroup + "'" + InstrumentTypeFilter + StrategyNameFilter + TimeFrameFilter + BatchIDFilter + BatchSubIDFilter + " AND BatchType = '" + BatchType + "' ORDER BY StrategyName, BatchID, BatchSubID"
    # BacktestBatchList = pd.read_sql_query(sql, dbcon)
    
    if BatchListDatabaseName is None:
        FullBatchListTableName = BatchListTableName
    else:
        FullBatchListTableName = BatchListDatabaseName + '.' + BatchListTableName

    sql = "SELECT * FROM " + FullBatchListTableName + " WHERE Enabled = 1 AND BatchGroup = '" + BatchGroup + "'" + InstrumentTypeFilter + StrategyNameFilter + TimeFrameFilter + BatchIDFilter + BatchSubIDFilter + " AND BatchType = '" + BatchType + "' ORDER BY StrategyName, BatchID, BatchSubID"
    print(sql)

# BacktestBatchList = pd.read_sql("SELECT * FROM " + FullBatchListTableName + " WHERE Enabled = 1 AND BatchGroup = '" + BatchGroup + "'" + InstrumentTypeFilter + StrategyNameFilter + TimeFrameFilter + BatchIDFilter + BatchSubIDFilter + " AND BatchType = '" + BatchType + "' ORDER BY StrategyName, BatchID, BatchSubID",con=DBUtil.GetSQLAlchemyEngine(Override_DBHost = Override_DBHost, Override_DBPort = Override_DBPort, Override_DBUser = Override_DBUser, Override_DBPassword = Override_DBPassword))    
    # BacktestBatchList = pd.read_sql("SELECT * FROM " + FullBatchListTableName + " WHERE Enabled = 1 AND BatchGroup = '" + BatchGroup + "'" + InstrumentTypeFilter + StrategyNameFilter + TimeFrameFilter + BatchIDFilter + BatchSubIDFilter + " AND BatchType = '" + BatchType + "' ORDER BY StrategyName, BatchID, BatchSubID",con=DBUtil.GetSQLAlchemyEngine())    
    BacktestBatchList = pd.read_sql(sql,con=DBUtil.GetSQLAlchemyEngine())    

    print('Backtest Batches to be run are')
    print(BacktestBatchList)
    
    parameter_string = BacktestBatchList.loc[0, 'BacktestSummaryTradeCount']
    BacktestSummaryTradeCount = [int(e) if e.isdigit() else e for e in parameter_string.split(',')]
    BacktestPeriodLabel = {0:'full period'}
    for backtest_trade_count in BacktestSummaryTradeCount:
        if backtest_trade_count != 0:
            BacktestPeriodLabel[backtest_trade_count] = 'last ' + str(backtest_trade_count) + ' trades'
    
    for backtest_period in BacktestPeriodLabel:
        BacktestingSummary[backtest_period] = pd.DataFrame()
        BacktestingTradeRecord[backtest_period] = pd.DataFrame()
    PriorBatchID = -1
    PriorStrategyName = ''
    
    for index, row in BacktestBatchList.iterrows():
        BatchStartTime = datetime.now()
        if BatchType == 'Selected' or ClearDataAfterEachSubBatch:
            AnalysisContextList = None
        if (PriorBatchID != -1) and ((row['BatchID'] != PriorBatchID) or (row['StrategyName'] != PriorStrategyName)):
            # ExportStrategyResultCSV(backtest_result.FullResultOutputFolderPath, BacktestPeriodLabel, BatchGroup, PriorBatchID)
            ExportStrategyResultCSV(backtest_result.FullResultOutputFolderPath, BacktestPeriodLabel, StrategyName = PriorStrategyName, BatchGroup = PriorBatchGroup, BatchID = PriorBatchID)
            InitBacktestResult(BacktestPeriodLabel)
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
        InstrumentType = row['InstrumentType']
        
        KeepOnlyWeekdays = (row['KeepOnlyWeekdays'] == 1)
        FillEveryTimeSlot = (row['FillEveryTimeSlot'] == 1)
        DataTimeLowerBound = row['TimeLowerBound']
        DataTimeUpperBound = row['TimeUpperBound']
        
        MarketTimeSectionString = row['MarketTimeSection']
        if MarketTimeSectionString is not None:
            # MarketTimeSectionTimeList = pd.DataFrame(columns=['SectionID', 'Start', 'End'])
            if MarketTimeSectionString == '':
                # MarketTimeSectionTimeList = pd.DataFrame(columns=['SectionID', 'Start', 'End'])
                MarketTimeSectionTimeList = None
            else:
                MarketTimeSectionTimeList = [int(e) for e in MarketTimeSectionString.split(',')]
                # lst = [int(e) for e in MarketTimeSectionString.split(',')]
                # lst_df = []
                # # lst_sectionid = []
                # # lst_start = []
                # # lst_end = []
                # for i in range(len(lst) - 1):
                #     lst_df.append([i, lst[i], lst[i+1]-1])
                #     # lst_sectionid.append(i)
                #     # lst_start.append(lst[i])
                #     # lst_end.append(lst[i+1]-1)
                
                # MarketTimeSectionTimeList = pd.DataFrame(lst_df, columns=['SectionID', 'Start', 'End'])
                # # MarketTimeSectionTimeList = {'SectionID':lst_sectionid, 'Start':lst_start, 'End':lst_end}
        else:
            MarketTimeSectionTimeList = None
        
        BacktestParameterDF = BacktestBatchList.loc[(BacktestBatchList['StrategyName'] == row['StrategyName']) & (BacktestBatchList['BatchGroup'] == row['BatchGroup']) & (BacktestBatchList['BatchID'] == row['BatchID']) & (BacktestBatchList['BatchSubID'] == row['BatchSubID'])].copy().reset_index()
        
        print('before FuturesStrategyBacktest.getBacktestItem')
        print('BacktestParameterDF is')
        print(BacktestParameterDF)
        
        # backtest_result = FuturesStrategyBacktest.getBacktestItem(row['StrategyName'], row['BatchGroup'], row['BatchID'], row['BatchSubID'], AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType)
        # backtest_result = FuturesStrategyBacktest.getBacktestItem(BacktestParameterDF, AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, DataTimeLowerBound = DataTimeLowerBound, DataTimeUpperBound = DataTimeUpperBound, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList , DebugFilepath = DebugFilepath, BatchListDatabaseName = BatchListDatabaseName, BatchListTableName = BatchListTableName)
        backtest_result = FuturesStratBacktest.getBacktestItem(BacktestParameterDF, AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, DataTimeLowerBound = DataTimeLowerBound, DataTimeUpperBound = DataTimeUpperBound, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList , DebugFilepath = DebugFilepath, BatchListDatabaseName = BatchListDatabaseName, BatchListTableName = BatchListTableName)

        print('after FuturesStrategyBacktest.getBacktestItem')

        AnalysisContextList = backtest_result.AnalysisContextList
        # AppendBacktestResult(backtest_result, BacktestPeriodLabel)
        # AppendBacktestResult(backtest_result, BacktestPeriodLabel,row['BatchGroup'], row['BatchID'], row['BatchSubID'])
        AppendBacktestResult(backtest_result, BacktestPeriodLabel,row['StrategyName'], row['BatchGroup'], row['BatchID'], row['BatchSubID'], BatchListDatabaseName = BatchListDatabaseName, BatchListTableName = BatchListTableName  )
    
        PriorBatchID = row['BatchID']
        PriorStrategyName = row['StrategyName']
        PriorBatchGroup = row['BatchGroup']
    
    # ExportStrategyResultCSV(backtest_result.FullResultOutputFolderPath, BacktestPeriodLabel, BatchGroup, PriorBatchID)
    ExportStrategyResultCSV(backtest_result.FullResultOutputFolderPath, BacktestPeriodLabel, BatchID = PriorBatchID)
        
    AnalysisEndTime = datetime.now()
    analysis_minutes_diff = round((AnalysisEndTime - AnalysisStartTime).total_seconds() / 60.0)
    
    print('Analysis ended at ' + str(AnalysisEndTime) + ', and ' + str(analysis_minutes_diff) + ' minutes taken')
    
    
    
 