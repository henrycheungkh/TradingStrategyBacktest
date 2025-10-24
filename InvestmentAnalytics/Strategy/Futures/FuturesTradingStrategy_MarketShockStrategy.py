# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 00:43:40 2021

@author: Henry Cheung
"""

import pymysql
import pandas as pd
import numpy as np
import math
from datetime import date, datetime, timedelta
import time
import InvestmentAnalytics.Config as Config

from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy import FuturesStrategyBacktest

class MarketShockStrategy:
    SCENARIO_COLUMNS = ['ticker id', 'IR Ticker Volume Stdev Threshold', 'Non IR Ticker Volume Stdev Threshold', 'IR Ticker Shock Stdev Threshold', 'Non IR Ticker Shock Stdev Threshold', 'IR Ticker Shock Count Threshold', 'Non IR Ticker Shock Count Threshold', 'Stop Loss Size to Shock Ratio', 'Floating StopLoss Movement', 'Max Holding Period']
    TRADE_ID_SORTING_COLUMNS = ['exit time id']
    def __init__(self, StrategyLabel, AnalysisContext, StartTimeInStdUnit, EndTimeInStdUnit, MaxHoldingPeriodInStdUnitList, IR_Ticker_Volume_Stdev_Threshold, Non_IR_Ticker_Volume_Stdev_Threshold, IR_Ticker_Shock_Stdev_Threshold, Non_IR_Ticker_Shock_Stdev_Threshold, IR_Ticker_Shock_Count_Threshold, Non_IR_Ticker_Shock_Count_Threshold, IR_Tickers_List, StopLossSizeToShockRatio, FloatingStopLossMovement, TradeIDSortingSegmentKeyColumnsCount = 2, PreFilterDataByTime = False, GPUMode = "CUDA", InitialResultCacheSize = None, GPU_CORE_BLOCK_SIZE = 32*32):
        self.StrategyLabel = StrategyLabel
        self.AnalysisContext = AnalysisContext
        # self.TimeFrame = "1 min"
        self.TimeFrame = AnalysisContext.FuturesData.TimeFrame
        
        self.StartTimeInStdUnit = StartTimeInStdUnit
        self.EndTimeInStdUnit = EndTimeInStdUnit
        self.MaxHoldingPeriodInStdUnitList = MaxHoldingPeriodInStdUnitList
        self.MaxHoldingPeriodInStdUnit = max(MaxHoldingPeriodInStdUnitList)
        # self.MaxHoldingPeriodInStdUnit = MaxHoldingPeriodInStdUnit
        self.InitialResultCacheSize = InitialResultCacheSize
        self.GPU_CORE_BLOCK_SIZE = GPU_CORE_BLOCK_SIZE
        self.TradeIDSortingSegmentKeyColumnsCount = TradeIDSortingSegmentKeyColumnsCount
        
        self.CalculateMeanAndStdev()
        
        self.IR_Ticker_Volume_Stdev_Threshold = IR_Ticker_Volume_Stdev_Threshold
        self.Non_IR_Ticker_Volume_Stdev_Threshold = Non_IR_Ticker_Volume_Stdev_Threshold
        self.IR_Ticker_Shock_Stdev_Threshold = IR_Ticker_Shock_Stdev_Threshold
        self.Non_IR_Ticker_Shock_Stdev_Threshold = Non_IR_Ticker_Shock_Stdev_Threshold
        self.IR_Ticker_Shock_Count_Threshold = IR_Ticker_Shock_Count_Threshold
        self.Non_IR_Ticker_Shock_Count_Threshold = Non_IR_Ticker_Shock_Count_Threshold
        self.StopLossSizeToShockRatio = StopLossSizeToShockRatio
        self.FloatingStopLossMovement = FloatingStopLossMovement
        
        TickerIDMapping_DF = self.AnalysisContext.FuturesData.TickerIDMapping
        print('TickerIDMapping_DF is')
        print(TickerIDMapping_DF)

        self.IR_TickersID_List = []
        for idx, row in TickerIDMapping_DF.iterrows():
            if row['ticker'] in IR_Tickers_List:
                self.IR_TickersID_List.append(row['ticker id'])
            # = IR_Tickers_List
        print('self.IR_TickersID_List for IR tickers is ' + str(self.IR_TickersID_List))
        

        TimeIDMapping_DF = self.AnalysisContext.FuturesData.TimeIDMapping
        
        
        DateList = pd.pivot_table(TimeIDMapping_DF, values='time id', index=['Date'], aggfunc=len, fill_value=0).sort_values(by='Date', ascending=False).reset_index()
        DateList['Date id'] = DateList.index
        DateList['Dummy'] = 1
        # print("DateList is")
        # print(DateList)
        # print("TimeIDMapping_DF is")
        # print(TimeIDMapping_DF)
        # TimeIDMapping_DF.to_csv(r'd:\temp\TimeIDMapping_DF.csv', index=False)

        SortingColumns = MarketShockStrategy.SCENARIO_COLUMNS + MarketShockStrategy.TRADE_ID_SORTING_COLUMNS

        if GPUMode == "CUDA":
            from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib import CUDATradeIDAssignment
            from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib_MarketShockStrategy import CUDAMarketShockStrategy

# def CUDAMarketShockStrategy(close_price_matrix, date_id_matrix, time_std_unit_matrix, StartTimeInStdUnit, EndTimeInStdUnit, MaxHoldingPeriodInStdUnit, IR_TickersID_List, IR_Ticker_Volume_Stdev_Threshold, Non_IR_Ticker_Volume_Stdev_Threshold, IR_Ticker_Shock_Stdev_Threshold, Non_IR_Ticker_Shock_Stdev_Threshold, IR_Ticker_Shock_Count_Threshold, Non_IR_Ticker_Shock_Count_Threshold, StopLossSizeToShockRatio, FloatingStopLossMovement, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = None, TimeFrame = "1 min", GPU_CORE_BLOCK_SIZE = 32*32):
            
            self.trade_record = CUDAMarketShockStrategy(self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_close_adj'], self.AnalysisContext.IntradayPricesData.DataMatrix['vol'], self.AnalysisContext.IntradayPricesData.DataMatrix['date id'], self.AnalysisContext.IntradayPricesData.DataMatrix['TimeInStandardUnit'], self.return_mean_matrix, self.return_stdev_matrix, self.vol_mean_matrix, self.vol_stdev_matrix, self.StartTimeInStdUnit, self.EndTimeInStdUnit, self.MaxHoldingPeriodInStdUnitList, self.IR_TickersID_List, self.IR_Ticker_Volume_Stdev_Threshold, self.Non_IR_Ticker_Volume_Stdev_Threshold, self.IR_Ticker_Shock_Stdev_Threshold, self.Non_IR_Ticker_Shock_Stdev_Threshold, self.IR_Ticker_Shock_Count_Threshold, self.Non_IR_Ticker_Shock_Count_Threshold, self.StopLossSizeToShockRatio, self.FloatingStopLossMovement, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = self.InitialResultCacheSize, TimeFrame = self.TimeFrame, GPU_CORE_BLOCK_SIZE = self.GPU_CORE_BLOCK_SIZE)
            
            # self.trade_record = CUDACorrelationOnSpecificTimeSectionStrategy(self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_close_adj'], self.AnalysisContext.IntradayPricesData.DataMatrix['date id'], self.AnalysisContext.IntradayPricesData.DataMatrix['TimeInStandardUnit'], self.StartTimeInStdUnit, self.EndTimeInStdUnit, self.TimeIntervalInStdUnit, len(DateList), ObsPeriodMovementThreshold = self.OBS_PERIOD_MOVEMENT_THRESHOLD, StopLossPerTrade = self.StopLossPerTrade, TakeProfitPerTrade = self.TakeProfitPerTrade, ObsDateIDOffset = self.ObsDateIDOffset, TradeEntryDateIDOffset = self.TradeEntryDateIDOffset, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = self.InitialResultCacheSize, TimeFrame = self.TimeFrame, GPU_CORE_BLOCK_SIZE = self.GPU_CORE_BLOCK_SIZE)

            self.trade_record = self.trade_record.merge(TickerIDMapping_DF, on='ticker id')
            
            # self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'date id', 'TimeInStandardUnit']], left_on='obs time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'obs TimeInStandardUnit'}, inplace = False)
            # self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'TimeInStandardUnit']], left_on='obs time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'obs TimeInStandardUnit'}, inplace = False)
            self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'TimeInStandardUnit']], left_on='entry time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'entry TimeInStandardUnit'}, inplace = False)
            # self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'TimeInStandardUnit']], left_on='exit time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'exit TimeInStandardUnit'}, inplace = False)
            self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'date id', 'TimeInStandardUnit']], left_on='exit time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'exit TimeInStandardUnit'}, inplace = False)
            self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'TimeInStandardUnit']], left_on='stop time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'stop TimeInStandardUnit'}, inplace = False)

            print('trade_record after merging TimeIDMapping is with length ' + str(len(self.trade_record)) + ', max date id ' + str(self.trade_record['date id'].max()) + ' and min date id ' + str(self.trade_record['date id'].min()))
            # print(self.trade_record)
            
            if (len(self.trade_record) >0 ):
    
                print('before sorting for trade id assignment at ' + str(datetime.now()))
        
                self.trade_record = self.trade_record.sort_values(by=SortingColumns, ascending=False, inplace=False).reset_index().drop('index',axis='columns')
                
                print('before assigning trade id by CUDA at ' + str(datetime.now()))
                
                # trade_id = CUDATradeIDAssignment(df, self.TradeIDSortingSegmentKeyColumnsCount)
                # self.trade_record = pd.concat([self.trade_record, trade_id], axis=1)
                self.trade_record = pd.concat([self.trade_record, CUDATradeIDAssignment(self.trade_record[MarketShockStrategy.SCENARIO_COLUMNS], self.TradeIDSortingSegmentKeyColumnsCount)], axis=1)
                print('after assigning trade id by CUDA at ' + str(datetime.now()))
                # self.trade_record.to_csv(r'd:\temp\trade record with trade id.csv', index=False)


    def CalculateMeanAndStdev(self):
        print('In CalculateMeanAndStdev')
        

        close_matrix = self.AnalysisContext.FuturesData.DataMatrix['TRADES_close_adj'].T
        print('close_matrix is with size ' + str(len(close_matrix)) + ' x ' + str(len(close_matrix[0])))
        print(close_matrix)
        # time_size = len(close_matrix)
        # ticker_size = len(close_matrix[0])
        
        rolled_close_matrix = np.roll(close_matrix, 1, axis=0)
        print('rolled_close_matrix is with size ' + str(len(rolled_close_matrix)) + ' x ' + str(len(rolled_close_matrix[0])))
        print(rolled_close_matrix)
        
        # abs_return_matrix = abs(close_matrix - rolled_close_matrix)
        # print('abs_return_matrix is with size ' + str(len(abs_return_matrix)) + ' x ' + str(len(abs_return_matrix[0])))
        # print(abs_return_matrix)

        rel_return_matrix = abs(close_matrix - rolled_close_matrix) / rolled_close_matrix
        print('rel_return_matrix is with size ' + str(len(rel_return_matrix)) + ' x ' + str(len(rel_return_matrix[0])))
        print(rel_return_matrix)


        # data_sheet_name = 'TimeInStandardUnit'
        # print('DataMatrix of ' + data_sheet_name + ' is with size ' + str(len(self.AnalysisContext.FuturesData.DataMatrix[data_sheet_name])) )
        # print(self.AnalysisContext.FuturesData.DataMatrix[data_sheet_name])
        
        TimeInStandardUnit_matrix = self.AnalysisContext.FuturesData.DataMatrix['TimeInStandardUnit'].T
        print('TimeInStandardUnit_matrix is with size ' + str(len(TimeInStandardUnit_matrix)) )
        print(TimeInStandardUnit_matrix)
        rolled_TimeInStandardUnit_matrix = np.roll(TimeInStandardUnit_matrix, 1)
        print('rolled_TimeInStandardUnit_matrix is with size ' + str(len(rolled_TimeInStandardUnit_matrix)) )
        print(rolled_TimeInStandardUnit_matrix)
        
        filter_arr = (TimeInStandardUnit_matrix >= self.StartTimeInStdUnit) & (TimeInStandardUnit_matrix <= self.EndTimeInStdUnit) & (TimeInStandardUnit_matrix - rolled_TimeInStandardUnit_matrix == 1)
        print('filter_arr is with size ' + str(len(filter_arr)) )
        print(filter_arr)
        
        # abs_return_matrix = abs_return_matrix[filter_arr]
        # print('abs_return_matrix after filter is with size ' + str(len(abs_return_matrix)) + ' x ' + str(len(abs_return_matrix[0])))
        # print(abs_return_matrix)
        
        rel_return_matrix = rel_return_matrix[filter_arr]
        print('rel_return_matrix after filter is with size ' + str(len(rel_return_matrix)) + ' x ' + str(len(rel_return_matrix[0])))
        print(rel_return_matrix)


        # self.return_mean_matrix = np.mean(abs_return_matrix, axis=0)
        # print('return_mean_matrix is with size ' + str(len(self.return_mean_matrix)))
        # print(self.return_mean_matrix)
        
        self.return_mean_matrix = np.mean(rel_return_matrix, axis=0)
        print('return_mean_matrix is with size ' + str(len(self.return_mean_matrix)))
        print(self.return_mean_matrix)


        # self.return_stdev_matrix = np.std(abs_return_matrix, axis=0)
        # print('return_stdev_matrix is with size ' + str(len(self.return_stdev_matrix)))
        # print(self.return_stdev_matrix)

        self.return_stdev_matrix = np.std(rel_return_matrix, axis=0)
        print('return_stdev_matrix is with size ' + str(len(self.return_stdev_matrix)))
        print(self.return_stdev_matrix)

        
        vol_matrix = self.AnalysisContext.FuturesData.DataMatrix['vol'].T
        print('vol_matrix is with size ' + str(len(vol_matrix)) + ' x ' + str(len(vol_matrix[0])))
        print(vol_matrix)

        vol_matrix = vol_matrix[filter_arr]
        print('vol_matrix after filter is with size ' + str(len(vol_matrix)) + ' x ' + str(len(vol_matrix[0])))
        print(vol_matrix)
        
        self.vol_mean_matrix = np.mean(vol_matrix, axis=0)
        print('vol_mean_matrix is with size ' + str(len(self.vol_mean_matrix)))
        print(self.vol_mean_matrix)
        
        self.vol_stdev_matrix = np.std(vol_matrix, axis=0)
        print('vol_stdev_matrix is with size ' + str(len(self.vol_stdev_matrix)))
        print(self.vol_stdev_matrix)

class BacktestMarketShockStrategy(FuturesStrategyBacktest):
    PreFilterOffset = 10
    # threshold_count_per_batch = 2
    def __init__(self, BacktestParameterDF, AnalysisContextList, TickerFilter = [], ResultOutputFolderPath = None, PerformContangoAdjustment = True, MinimumTradeNumberCountForFullPeriod = 20, RandomNoiseTickerStdev = None, FillEveryTimeSlot = False, ActiveContractPircesTrimmedColumns = None, RapidCalibration = False, RapidCalibrationTopScenarioSelectedCount = 0, KeepOnlyWeekdays = False, DataTimeLowerBound = None, DataTimeUpperBound = None, threshold_count_per_batch = 1, InstrumentType = 'Futures', MAX_TRADE_ID = 100000, PreFilterDataByTime = False, MarketTimeSectionTimeList = None, DebugFilepath = None):

        self.StrategyLabel = 'MarketShockStrategy'
        self.BacktestParameterDF = BacktestParameterDF
        self.loadStrategyParameters()
        print('MinimumTradeNumberCountForFullPeriod is ' + str(MinimumTradeNumberCountForFullPeriod))
        super().__init__('MarketShockStrategy', BacktestParameterDF, AnalysisContextList, PreFilterDataByTime = self.PreFilterDataByTime, PreFilterDataStartTimeInStdUnit = self.PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit = self.PreFilterDataEndTimeInStdUnit, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, DataTimeLowerBound = DataTimeLowerBound, DataTimeUpperBound = DataTimeUpperBound, InstrumentType = InstrumentType, MAX_TRADE_ID = MAX_TRADE_ID, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath )

        self.backtest_result = MarketShockStrategy(self.StrategyLabel, self.AnalysisContext, self.StartTimeInStdUnit, self.EndTimeInStdUnit, self.MaxHoldingPeriodInStdUnitList, self.IR_Ticker_Volume_Stdev_Threshold, self.Non_IR_Ticker_Volume_Stdev_Threshold, self.IR_Ticker_Shock_Stdev_Threshold, self.Non_IR_Ticker_Shock_Stdev_Threshold, self.IR_Ticker_Shock_Count_Threshold, self.Non_IR_Ticker_Shock_Count_Threshold, self.IR_Tickers_List, self.StopLossSizeToShockRatio, self.FloatingStopLossMovement, TradeIDSortingSegmentKeyColumnsCount = self.TradeIDSortingSegmentKeyColumnsCount, GPUMode = self.GPUMode, InitialResultCacheSize = self.InitialResultCacheSize, GPU_CORE_BLOCK_SIZE = self.GPUCore )
        
        self.UpdateLastRunMaxTradeRecordSizePerSubBatch(len(self.backtest_result.trade_record))
        self.PrepareSummary(MarketShockStrategy.SCENARIO_COLUMNS)

        self.FullResultOutputFolderPath = self.ResultOutputFolderPath + self.StrategyLabel + '_' + self.StartDate.strftime("%Y%m%d") + '_' + self.EndDate.strftime("%Y%m%d") + '_' + self.TimeFrame + '_' + str(self.StartTimeInStdUnit) + '_'+ str(self.EndTimeInStdUnit) + '_'

        for key in self.BacktestingSummaryDict:
            self.BacktestingSummaryDict[key]['Abs Sharpe Ratio after commission'] = self.BacktestingSummaryDict[key]['Sharpe Ratio after commission'].abs()
            self.BacktestingSummaryDict[key] = self.BacktestingSummaryDict[key].sort_values(by='Abs Sharpe Ratio after commission', ascending=False).drop(['Abs Sharpe Ratio after commission'],axis='columns')

    def loadStrategyParameters(self):
        self.StartTimeInStdUnit = self.BacktestParameterDF.loc[0, 'ParameterValue1']
        self.EndTimeInStdUnit = self.BacktestParameterDF.loc[0, 'ParameterValue2']
        
        # self.MaxHoldingPeriodInStdUnit = self.BacktestParameterDF.loc[0, 'ParameterValue3']
        
        self.PreFilterDataByTime = True
        self.PreFilterDataStartTimeInStdUnit = self.StartTimeInStdUnit
        # self.PreFilterDataEndTimeInStdUnit = self.EndTimeInStdUnit + self.MaxHoldingPeriodInStdUnit
        
        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue1']
        # self.IR_Ticker_Volume_Stdev_Threshold = [float(e) if e.isdigit() else e for e in parameter_string.split(',')]
        self.IR_Ticker_Volume_Stdev_Threshold = [float(e) for e in parameter_string.split(',')]
        print('self.IR_Ticker_Volume_Stdev_Threshold is ' + str(self.IR_Ticker_Volume_Stdev_Threshold))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue2']
        # self.Non_IR_Ticker_Volume_Stdev_Threshold = [float(e) if e.isdigit() else e for e in parameter_string.split(',')]
        self.Non_IR_Ticker_Volume_Stdev_Threshold = [float(e) for e in parameter_string.split(',')]
        print('self.Non_IR_Ticker_Volume_Stdev_Threshold is ' + str(self.Non_IR_Ticker_Volume_Stdev_Threshold))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue3']
        # self.IR_Ticker_Shock_Stdev_Threshold = [float(e) if e.isdigit() else e for e in parameter_string.split(',')]
        self.IR_Ticker_Shock_Stdev_Threshold = [float(e) for e in parameter_string.split(',')]
        print('self.IR_Ticker_Shock_Stdev_Threshold is ' + str(self.IR_Ticker_Shock_Stdev_Threshold))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue4']
        # self.Non_IR_Ticker_Shock_Stdev_Threshold = [float(e) if e.isdigit() else e for e in parameter_string.split(',')]
        self.Non_IR_Ticker_Shock_Stdev_Threshold = [float(e) for e in parameter_string.split(',')]
        print('self.Non_IR_Ticker_Shock_Stdev_Threshold is ' + str(self.Non_IR_Ticker_Shock_Stdev_Threshold))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue5']
        self.IR_Ticker_Shock_Count_Threshold = [int(e) if e.isdigit() else e for e in parameter_string.split(',')]
        print('self.IR_Ticker_Shock_Count_Threshold is ' + str(self.IR_Ticker_Shock_Count_Threshold))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue6']
        self.Non_IR_Ticker_Shock_Count_Threshold = [int(e) if e.isdigit() else e for e in parameter_string.split(',')]
        print('self.Non_IR_Ticker_Shock_Count_Threshold is ' + str(self.Non_IR_Ticker_Shock_Count_Threshold))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue7']
        self.IR_Tickers_List = [e for e in parameter_string.split(',')]
        print('self.IR_Tickers_List is ' + str(self.IR_Tickers_List))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue8']
        # self.StopLossSizeToShockRatio = [float(e) if e.isdigit() else e for e in parameter_string.split(',')]
        self.StopLossSizeToShockRatio = [float(e) for e in parameter_string.split(',')]
        print('self.StopLossSizeToShockRatio is ' + str(self.StopLossSizeToShockRatio))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue9']
        self.FloatingStopLossMovement = [int(e) / 10000 if e.isdigit() else e for e in parameter_string.split(',')]
        print('self.FloatingStopLossMovement is ' + str(self.FloatingStopLossMovement))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue10']
        self.MaxHoldingPeriodInStdUnitList = [int(e) if e.isdigit() else e for e in parameter_string.split(',')]
        print('self.MaxHoldingPeriodInStdUnitList is ' + str(self.MaxHoldingPeriodInStdUnitList))
        self.MaxHoldingPeriodInStdUnit = max(self.MaxHoldingPeriodInStdUnitList)
        self.PreFilterDataEndTimeInStdUnit = self.EndTimeInStdUnit + self.MaxHoldingPeriodInStdUnit

        
    def PrepareSummary(self, ScenarioColumnNames):

        self.BacktestingSummaryDict = {}
        self.BacktestingTradeRecord = {}

        if (len(self.backtest_result.trade_record) > 0):
            self.backtest_result.trade_record = super().getPreparedTradeRecord(self.backtest_result.trade_record, ScenarioColumnNames, 'trade id', ascending=True)
            if self.RapidCalibrationTopScenarioSelectedCount == 0:
                self.FillDataMatrix(self.backtest_result.trade_record, 'trade id', ['scenario id'], {'long short flag': 'long short flag', 'entry price': 'entry price', 'exit price': 'exit price'})
            else:
                self.FillDataMatrix(self.backtest_result.trade_record, 'trade id', ['scenario id'], {'long short flag': 'long short flag', 'entry price': 'entry price', 'exit price': 'exit price', 'date id': 'date id'})
            
            if self.GPUMode == "CUDA":
                BacktestingSummary, RapidCalibrationBacktestingSummary = self.getCUDABacktestingSummary()
            # BacktestingSummary.to_csv(self.ResultOutputFolderPath + self.StrategyLabel + '_' + self.StartDate.strftime("%Y%m%d") + '_' + self.EndDate.strftime("%Y%m%d") + '_' + self.TimeFrame + '_'+ r'BacktestingSummary.csv')
    
            self.BacktestingSummaryDict = self.FinishSummary(BacktestingSummary, ScenarioColumnNames)
            self.BacktestingTradeRecord = {}
            for backtest_period in self.BacktestingSummaryDict:
                self.BacktestingTradeRecord[backtest_period] = self.backtest_result.trade_record.merge(self.BacktestingSummaryDict[backtest_period][ScenarioColumnNames], on=ScenarioColumnNames)
                self.BacktestingTradeRecord[backtest_period] = self.BacktestingTradeRecord[backtest_period].merge(self.AnalysisContext.FuturesData.DateIDMapping, on=['date id'])
