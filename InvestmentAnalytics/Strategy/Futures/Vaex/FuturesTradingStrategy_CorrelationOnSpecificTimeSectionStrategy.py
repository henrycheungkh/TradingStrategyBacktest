# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 00:43:40 2021

@author: Henry Cheung
"""

import pymysql
import pandas as pd
import math
from datetime import date, datetime, timedelta
import time
import InvestmentAnalytics.Config as Config

from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy import FuturesStrategyBacktest
# from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib import CUDATradeIDAssignment
# from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib_CorrelationOnSpecificTimeSectionStrategy import CUDACorrelationOnSpecificTimeSectionStrategy
# from InvestmentAnalytics.CUDA.CUDADataFrameUtil import CUDAMapByLookup

class CorrelationOnSpecificTimeSectionStrategy:
    # SCENARIO_COLUMNS = ['ticker id', 'obs TimeInStandardUnit', 'entry TimeInStandardUnit', 'exit TimeInStandardUnit', 'obs movement threshold', 'stop loss', 'take profit']
    SCENARIO_COLUMNS = ['ticker id', 'obs TimeInStandardUnit', 'entry TimeInStandardUnit', 'exit TimeInStandardUnit', 'obs movement threshold', 'obs movement range', 'stop loss', 'take profit', 'obs date id offset', 'trade entry date id offset']
    TRADE_ID_SORTING_COLUMNS = ['exit time id']
    def __init__(self, StrategyLabel, AnalysisContext, StartTimeInStdUnit, EndTimeInStdUnit, TimeIntervalInStdUnit, OBS_PERIOD_MOVEMENT_THRESHOLD = [0, 0.001], ObsPeriodMovementRange = 0, StopLossPerTrade = 0, TakeProfitPerTrade = 0, ObsDateIDOffset = 0, TradeEntryDateIDOffset = 0, TradeIDSortingSegmentKeyColumnsCount = 2, PreFilterDataByTime = False, GPUMode = "CUDA", InitialResultCacheSize = None, GPU_CORE_BLOCK_SIZE = 32*32):
        self.StrategyLabel = StrategyLabel
        self.AnalysisContext = AnalysisContext
        # self.TimeFrame = "1 min"
        self.TimeFrame = AnalysisContext.FuturesData.TimeFrame
        
        self.StartTimeInStdUnit = StartTimeInStdUnit
        self.EndTimeInStdUnit = EndTimeInStdUnit
        self.TimeIntervalInStdUnit = TimeIntervalInStdUnit
        self.InitialResultCacheSize = InitialResultCacheSize
        self.GPU_CORE_BLOCK_SIZE = GPU_CORE_BLOCK_SIZE
        self.TradeIDSortingSegmentKeyColumnsCount = TradeIDSortingSegmentKeyColumnsCount
        self.GPUMode = GPUMode
        if GPUMode == "CUDA":
            from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib import CUDATradeIDAssignment
            from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib_CorrelationOnSpecificTimeSectionStrategy import CUDACorrelationOnSpecificTimeSectionStrategy

        self.OBS_PERIOD_MOVEMENT_THRESHOLD = OBS_PERIOD_MOVEMENT_THRESHOLD
        self.StopLossPerTrade = StopLossPerTrade
        self.TakeProfitPerTrade = TakeProfitPerTrade
        self.ObsDateIDOffset = ObsDateIDOffset
        self.TradeEntryDateIDOffset = TradeEntryDateIDOffset
        self.CountOfTimeInterval = math.floor((EndTimeInStdUnit - StartTimeInStdUnit)/TimeIntervalInStdUnit)
        TimeIDMapping_DF = self.AnalysisContext.FuturesData.TimeIDMapping
        
        TickerIDMapping_DF = self.AnalysisContext.FuturesData.TickerIDMapping
        
        DateList = pd.pivot_table(TimeIDMapping_DF, values='time id', index=['Date'], aggfunc=len, fill_value=0).sort_values(by='Date', ascending=False).reset_index()
        DateList['Date id'] = DateList.index
        DateList['Dummy'] = 1
        # print("DateList is")
        # print(DateList)
        # print("TimeIDMapping_DF is")
        # print(TimeIDMapping_DF)
        # TimeIDMapping_DF.to_csv(r'd:\temp\TimeIDMapping_DF.csv', index=False)

        SortingColumns = CorrelationOnSpecificTimeSectionStrategy.SCENARIO_COLUMNS + CorrelationOnSpecificTimeSectionStrategy.TRADE_ID_SORTING_COLUMNS

        if GPUMode == "CUDA":
            
            import vaex
            from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib import CUDATradeIDAssignmentVaex
            
            trade_record_df_vaex = vaex.from_pandas(df=CUDACorrelationOnSpecificTimeSectionStrategy(self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_close_adj'], self.AnalysisContext.IntradayPricesData.DataMatrix['date id'], self.AnalysisContext.IntradayPricesData.DataMatrix['TimeInStandardUnit'], self.StartTimeInStdUnit, self.EndTimeInStdUnit, self.TimeIntervalInStdUnit, len(DateList), ObsPeriodMovementThreshold = self.OBS_PERIOD_MOVEMENT_THRESHOLD, StopLossPerTrade = self.StopLossPerTrade, TakeProfitPerTrade = self.TakeProfitPerTrade, ObsDateIDOffset = self.ObsDateIDOffset, TradeEntryDateIDOffset = self.TradeEntryDateIDOffset, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = self.InitialResultCacheSize, TimeFrame = self.TimeFrame, GPU_CORE_BLOCK_SIZE = self.GPU_CORE_BLOCK_SIZE), copy_index=False)
            TickerIDMapping_DF['ticker id'] = TickerIDMapping_DF['ticker id'].astype(float)
            TickerIDMapping_DF_vaex = vaex.from_pandas(df=TickerIDMapping_DF, copy_index=False)
            TimeIDMapping_DF['time id'] = TimeIDMapping_DF['time id'].astype(float)
            TimeIDMapping_DF_vaex = vaex.from_pandas(df=TimeIDMapping_DF, copy_index=False)
            
            # print('trade_record_df_vaex is')
            # print(trade_record_df_vaex)
            # print('TickerIDMapping_DF_vaex is')
            # print(TickerIDMapping_DF_vaex)
            # print('TimeIDMapping_DF_vaex is')
            # print(TimeIDMapping_DF_vaex)
            
            trade_record_df_vaex = trade_record_df_vaex.join(TickerIDMapping_DF_vaex, on='ticker id')
            # trade_record_df_vaex = trade_record_df_vaex.join(TimeIDMapping_DF_vaex[['time id', 'TimeInStandardUnit']], left_on='obs time id', right_on='time id').drop(['time id']).rename('TimeInStandardUnit', 'obs TimeInStandardUnit')
            trade_record_df_vaex = trade_record_df_vaex.join(TimeIDMapping_DF_vaex[['time id', 'TimeInStandardUnit']], left_on='obs time id', right_on='time id').drop(['time id'])
            # print('trade_record_df_vaex before column rename is')
            # print(trade_record_df_vaex)
            trade_record_df_vaex.rename('TimeInStandardUnit', 'obs TimeInStandardUnit')
           
            
            # print('trade_record_df_vaex after column rename is')
            # print(trade_record_df_vaex)
            # print('TimeIDMapping_DF_vaex is')
            # print(TimeIDMapping_DF_vaex)
            
            trade_record_df_vaex = trade_record_df_vaex.join(TimeIDMapping_DF_vaex[['time id', 'TimeInStandardUnit']], left_on='entry time id', right_on='time id').drop(['time id'])
            trade_record_df_vaex.rename('TimeInStandardUnit', 'entry TimeInStandardUnit')
            trade_record_df_vaex = trade_record_df_vaex.join(TimeIDMapping_DF_vaex[['time id', 'date id', 'TimeInStandardUnit']], left_on='exit time id', right_on='time id').drop(['time id'])
            trade_record_df_vaex.rename('TimeInStandardUnit', 'exit TimeInStandardUnit')
            trade_record_df_vaex = trade_record_df_vaex.join(TimeIDMapping_DF_vaex[['time id', 'TimeInStandardUnit']], left_on='stop time id', right_on='time id').drop(['time id'])
            trade_record_df_vaex.rename('TimeInStandardUnit', 'stop TimeInStandardUnit')

            print('trade_record after merging TimeIDMapping is with length ' + str(len(trade_record_df_vaex)) + ', max date id ' + str(trade_record_df_vaex['date id'].max()) + ' and min date id ' + str(trade_record_df_vaex['date id'].min()))
            # print(self.trade_record)
            
            if (len(trade_record_df_vaex) >0 ):
    
                print('before sorting for trade id assignment at ' + str(datetime.now()))
        
                trade_record_df_vaex = trade_record_df_vaex.sort(by=SortingColumns, ascending=False)
                
                print('before assigning trade id by CUDA at ' + str(datetime.now()))
                
                # trade_id = CUDATradeIDAssignment(df, self.TradeIDSortingSegmentKeyColumnsCount)
                # self.trade_record = pd.concat([self.trade_record, trade_id], axis=1)
                
                temp_df_vaex = CUDATradeIDAssignmentVaex(trade_record_df_vaex[CorrelationOnSpecificTimeSectionStrategy.SCENARIO_COLUMNS], self.TradeIDSortingSegmentKeyColumnsCount)
                
                
                # self.trade_record = trade_record_df_vaex.to_pandas_df()
                # temp_df_vaex = vaex.from_pandas(CUDATradeIDAssignment(self.trade_record[CorrelationOnSpecificTimeSectionStrategy.SCENARIO_COLUMNS], self.TradeIDSortingSegmentKeyColumnsCount))
                trade_record_df_vaex = trade_record_df_vaex.join(temp_df_vaex)
                print('after assigning trade id by CUDA at ' + str(datetime.now()))
                # self.trade_record.to_csv(r'd:\temp\trade record with trade id.csv', index=False)
                
                # self.trade_record = trade_record_df_vaex.to_pandas_df()
                self.trade_record = trade_record_df_vaex
            
            
# Insufficient memory
            # self.trade_record = CUDACorrelationOnSpecificTimeSectionStrategy(self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_close_adj'], self.AnalysisContext.IntradayPricesData.DataMatrix['date id'], self.AnalysisContext.IntradayPricesData.DataMatrix['TimeInStandardUnit'], self.StartTimeInStdUnit, self.EndTimeInStdUnit, self.TimeIntervalInStdUnit, len(DateList), ObsPeriodMovementThreshold = self.OBS_PERIOD_MOVEMENT_THRESHOLD, StopLossPerTrade = self.StopLossPerTrade, TakeProfitPerTrade = self.TakeProfitPerTrade, ObsDateIDOffset = self.ObsDateIDOffset, TradeEntryDateIDOffset = self.TradeEntryDateIDOffset, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = self.InitialResultCacheSize, TimeFrame = self.TimeFrame, GPU_CORE_BLOCK_SIZE = self.GPU_CORE_BLOCK_SIZE)

            # self.trade_record = self.trade_record.merge(TickerIDMapping_DF, on='ticker id')
            
            # self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'TimeInStandardUnit']], left_on='obs time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'obs TimeInStandardUnit'}, inplace = False)
            # self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'TimeInStandardUnit']], left_on='entry time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'entry TimeInStandardUnit'}, inplace = False)
            # self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'date id', 'TimeInStandardUnit']], left_on='exit time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'exit TimeInStandardUnit'}, inplace = False)
            # self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'TimeInStandardUnit']], left_on='stop time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'stop TimeInStandardUnit'}, inplace = False)

            # print('trade_record after merging TimeIDMapping is with length ' + str(len(self.trade_record)) + ', max date id ' + str(self.trade_record['date id'].max()) + ' and min date id ' + str(self.trade_record['date id'].min()))
            # # print(self.trade_record)
            
            # if (len(self.trade_record) >0 ):
    
            #     print('before sorting for trade id assignment at ' + str(datetime.now()))
        
            #     self.trade_record = self.trade_record.sort_values(by=SortingColumns, ascending=False, inplace=False).reset_index().drop('index',axis='columns')
                
            #     print('before assigning trade id by CUDA at ' + str(datetime.now()))
                
            #     # trade_id = CUDATradeIDAssignment(df, self.TradeIDSortingSegmentKeyColumnsCount)
            #     # self.trade_record = pd.concat([self.trade_record, trade_id], axis=1)
            #     self.trade_record = pd.concat([self.trade_record, CUDATradeIDAssignment(self.trade_record[CorrelationOnSpecificTimeSectionStrategy.SCENARIO_COLUMNS], self.TradeIDSortingSegmentKeyColumnsCount)], axis=1)
            #     print('after assigning trade id by CUDA at ' + str(datetime.now()))
            #     # self.trade_record.to_csv(r'd:\temp\trade record with trade id.csv', index=False)
                

class BacktestCorrelationOnSpecificTimeSectionStrategy(FuturesStrategyBacktest):
    PreFilterOffset = 10
    # threshold_count_per_batch = 2
    # def __init__(self, BatchGroup, BacktestBatchID, BacktestBatchSubID, AnalysisContextList, TickerFilter = [], ResultOutputFolderPath = None, PerformContangoAdjustment = True, MinimumTradeNumberCountForFullPeriod = 50, RandomNoiseTickerStdev = None, FillEveryTimeSlot = False, ActiveContractPircesTrimmedColumns = None, RapidCalibration = False, RapidCalibrationTopScenarioSelectedCount = 0, KeepOnlyWeekdays = False, threshold_count_per_batch = 1, InstrumentType = 'Futures', MarketTimeSectionTimeList = None, DebugFilepath = None):
    def __init__(self, BacktestParameterDF, AnalysisContextList, TickerFilter = [], ResultOutputFolderPath = None, PerformContangoAdjustment = True, MinimumTradeNumberCountForFullPeriod = 50, RandomNoiseTickerStdev = None, FillEveryTimeSlot = False, ActiveContractPircesTrimmedColumns = None, RapidCalibration = False, RapidCalibrationTopScenarioSelectedCount = 0, KeepOnlyWeekdays = False, threshold_count_per_batch = 1, InstrumentType = 'Futures', PreFilterDataByTime = False, MarketTimeSectionTimeList = None, DebugFilepath = None):

        # self.BatchGroup = BatchGroup
        # self.BacktestBatchID = BacktestBatchID
        # self.BacktestBatchSubID = BacktestBatchSubID
        # self.StrategyName = 'CorrelationOnSpecificTimeSectionStrategy'
        self.StrategyLabel = 'CorrelationOnSpecificTimeSectionStrategy'
        self.BacktestParameterDF = BacktestParameterDF
        self.loadStrategyParameters()
        # super().__init__('CorrelationOnSpecificTimeSectionStrategy', BatchGroup, BacktestBatchID, BacktestBatchSubID, AnalysisContextList, PreFilterDataByTime = self.PreFilterDataByTime, PreFilterDataStartTimeInStdUnit = self.PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit = self.PreFilterDataEndTimeInStdUnit, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath )
        super().__init__('CorrelationOnSpecificTimeSectionStrategy', BacktestParameterDF, AnalysisContextList, PreFilterDataByTime = self.PreFilterDataByTime, PreFilterDataStartTimeInStdUnit = self.PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit = self.PreFilterDataEndTimeInStdUnit, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath )
        # self.loadStrategyParameters()
        # self.loadStrategyParameters()
        
        if self.LoopPerTicker:
            TickerFullList = self.AnalysisContext.FuturesData.TickerIDMapping['ticker'].tolist()
            print('TickerFullList is ' + str(TickerFullList))
            BacktestingSummaryDictAll = {}
            BacktestingTradeRecordAll = {}
            for ticker in TickerFullList:
                print('Loop per ticker.  Looping for ' + ticker)
                TickerFilter = [ticker]
                self.AnalysisContext = self.getAnalysisContext(PreFilterDataByTime, self.PreFilterDataStartTimeInStdUnit, self.PreFilterDataEndTimeInStdUnit, TickerFilter, False, PerformContangoAdjustment, RandomNoiseTickerStdev, FillEveryTimeSlot, KeepOnlyWeekdays, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList , DebugFilepath = DebugFilepath)
                BacktestingSummaryDict, BacktestingTradeRecord = self.init_per_ticker_list(BacktestParameterDF, AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, threshold_count_per_batch = threshold_count_per_batch, InstrumentType = InstrumentType, PreFilterDataByTime = PreFilterDataByTime, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath)

                for key in BacktestingSummaryDict:
                    if key in BacktestingSummaryDictAll:
                        BacktestingSummaryDictAll[key] = BacktestingSummaryDictAll[key].append(BacktestingSummaryDict[key])
                    else:
                        BacktestingSummaryDictAll[key] = BacktestingSummaryDict[key]
                for key in BacktestingTradeRecord:
                    if key in BacktestingTradeRecordAll:
                        BacktestingTradeRecordAll[key] = BacktestingTradeRecordAll[key].append(BacktestingTradeRecord[key])
                    else:
                        BacktestingTradeRecordAll[key] = BacktestingTradeRecord[key]

            self.BacktestingSummaryDict = BacktestingSummaryDictAll
            self.BacktestingTradeRecord = BacktestingTradeRecordAll

        else:

            BacktestingSummaryDictAll, BacktestingTradeRecordAll = self.init_per_ticker_list(BacktestParameterDF, AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, threshold_count_per_batch = threshold_count_per_batch, InstrumentType = InstrumentType, PreFilterDataByTime = PreFilterDataByTime, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath)
    
            self.BacktestingSummaryDict = BacktestingSummaryDictAll
            self.BacktestingTradeRecord = BacktestingTradeRecordAll
            
        for key in self.BacktestingSummaryDict:
            self.BacktestingSummaryDict[key]['Abs Sharpe Ratio after commission'] = self.BacktestingSummaryDict[key]['Sharpe Ratio after commission'].abs()
            self.BacktestingSummaryDict[key] = self.BacktestingSummaryDict[key].sort_values(by='Abs Sharpe Ratio after commission', ascending=False).drop(['Abs Sharpe Ratio after commission'],axis='columns')

        self.FullResultOutputFolderPath = self.ResultOutputFolderPath + self.StrategyLabel + '_' + self.StartDate.strftime("%Y%m%d") + '_' + self.EndDate.strftime("%Y%m%d") + '_' + self.TimeFrame + '_' + str(self.StartTimeInStdUnit) + '_'+ str(self.EndTimeInStdUnit) + '_'+ str(self.TimeIntervalInStdUnit) + '_'


    def init_per_ticker_list(self, BacktestParameterDF, AnalysisContextList, TickerFilter = [], ResultOutputFolderPath = None, PerformContangoAdjustment = True, MinimumTradeNumberCountForFullPeriod = 50, RandomNoiseTickerStdev = None, FillEveryTimeSlot = False, ActiveContractPircesTrimmedColumns = None, RapidCalibration = False, RapidCalibrationTopScenarioSelectedCount = 0, KeepOnlyWeekdays = False, threshold_count_per_batch = 1, InstrumentType = 'Futures', PreFilterDataByTime = False, MarketTimeSectionTimeList = None, DebugFilepath = None):
        super().__init__('CorrelationOnSpecificTimeSectionStrategy', BacktestParameterDF, AnalysisContextList, PreFilterDataByTime = self.PreFilterDataByTime, PreFilterDataStartTimeInStdUnit = self.PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit = self.PreFilterDataEndTimeInStdUnit, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath )
        # self.loadStrategyParameters()
        # self.loadStrategyParameters()

        BacktestingSummaryDictAll = {}
        BacktestingTradeRecordAll = {}
        
        threshold_remain_list = self.OBS_PERIOD_MOVEMENT_THRESHOLD.copy()
        
        # TotalBatchCount = math.ceil(len(threshold_remain_list)/threshold_count_per_batch) * len(self.StopLossTakeProfitList) * len(self.StopLossTakeProfitList) * len(self.ObsDateIDOffsetList) * len(self.TradeEntryDateIDOffsetList)
        TotalBatchCount = len(FuturesStrategyBacktest.getListOfList(self.OBS_PERIOD_MOVEMENT_THRESHOLD, self.ParameterTrialCountPerLoop[0])) * len(self.StopLossTakeProfitList) * len(self.StopLossTakeProfitList) * len(self.ObsDateIDOffsetList) * len(self.TradeEntryDateIDOffsetList)
        TotalBatchIndex = 0

        # self.FullResultOutputFolderPath = self.ResultOutputFolderPath + self.StrategyLabel + '_' + self.StartDate.strftime("%Y%m%d") + '_' + self.EndDate.strftime("%Y%m%d") + '_' + self.TimeFrame + '_' + str(self.StartTimeInStdUnit) + '_'+ str(self.EndTimeInStdUnit) + '_'+ str(self.TimeIntervalInStdUnit) + '_'

        for threshold_list in FuturesStrategyBacktest.getListOfList(self.OBS_PERIOD_MOVEMENT_THRESHOLD, self.ParameterTrialCountPerLoop[0]):
            for ObsPeriodMovementRange in self.ObsPeriodMovementRangeList:
                for StopLossPerTrade in self.StopLossTakeProfitList:
                    for TakeProfitPerTrade in self.StopLossTakeProfitList:
                        for ObsDateIDOffset in self.ObsDateIDOffsetList:
                            for TradeEntryDateIDOffset in self.TradeEntryDateIDOffsetList:
    
                                TotalBatchIndex = TotalBatchIndex + 1
                                print()
                                print('In Batch ' + str(self.BatchID) + '(' + str(self.BatchSubID) + ') Start running ' + self.StrategyLabel + ' ' + str(TotalBatchIndex) + '/' + str(TotalBatchCount) + ' for threshold ' + str(threshold_list) + ', stop loss ' + str(StopLossPerTrade) + ', take profit ' + str(TakeProfitPerTrade)  + ', ObsDateIDOffset is ' + str(ObsDateIDOffset)  + ', TradeEntryDateIDOffset is ' + str(TradeEntryDateIDOffset) + ' at ' + str(datetime.now()))
                            
                                backtest_result = CorrelationOnSpecificTimeSectionStrategy(self.StrategyLabel, self.AnalysisContext, self.StartTimeInStdUnit, self.EndTimeInStdUnit, self.TimeIntervalInStdUnit, OBS_PERIOD_MOVEMENT_THRESHOLD = threshold_list, ObsPeriodMovementRange = ObsPeriodMovementRange, StopLossPerTrade = StopLossPerTrade, TakeProfitPerTrade = TakeProfitPerTrade, ObsDateIDOffset = ObsDateIDOffset, TradeEntryDateIDOffset = TradeEntryDateIDOffset, TradeIDSortingSegmentKeyColumnsCount = self.TradeIDSortingSegmentKeyColumnsCount, GPUMode = self.GPUMode, InitialResultCacheSize = self.InitialResultCacheSize, GPU_CORE_BLOCK_SIZE = self.GPUCore )
                                # self.backtest_result = CorrelationOnSpecificTimeSectionStrategy('CorrelationOnSpecificTimeSectionStrategy', self.AnalysisContext, self.StartTimeInStdUnit, self.EndTimeInStdUnit, self.TimeIntervalInStdUnit, OBS_PERIOD_MOVEMENT_THRESHOLD = threshold_list, StopLossPerTrade = StopLossPerTrade, TakeProfitPerTrade = TakeProfitPerTrade, ObsDateIDOffset = ObsDateIDOffset, TradeEntryDateIDOffset = TradeEntryDateIDOffset, TradeIDSortingSegmentKeyColumnsCount = self.TradeIDSortingSegmentKeyColumnsCount, GPUMode = self.GPUMode )
                                
                                self.UpdateLastRunMaxTradeRecordSizePerSubBatch(len(backtest_result.trade_record))
                                # self.FullResultOutputFolderPath = self.ResultOutputFolderPath + self.StrategyLabel + '_' + self.StartDate.strftime("%Y%m%d") + '_' + self.EndDate.strftime("%Y%m%d") + '_' + self.TimeFrame + '_' + str(self.StartTimeInStdUnit) + '_'+ str(self.EndTimeInStdUnit) + '_'+ str(self.TimeIntervalInStdUnit) + '_'
                                BacktestingSummaryDict, BacktestingTradeRecord = self.PrepareSummary(backtest_result, CorrelationOnSpecificTimeSectionStrategy.SCENARIO_COLUMNS)
                    
                                for key in BacktestingSummaryDict:
                                    if key in BacktestingSummaryDictAll:
                                        BacktestingSummaryDictAll[key] = BacktestingSummaryDictAll[key].append(BacktestingSummaryDict[key])
                                    else:
                                        BacktestingSummaryDictAll[key] = BacktestingSummaryDict[key]
                                for key in BacktestingTradeRecord:
                                    if key in BacktestingTradeRecordAll:
                                        BacktestingTradeRecordAll[key] = BacktestingTradeRecordAll[key].append(BacktestingTradeRecord[key])
                                    else:
                                        BacktestingTradeRecordAll[key] = BacktestingTradeRecord[key]
                
        return BacktestingSummaryDictAll, BacktestingTradeRecordAll
        # self.BacktestingSummaryDict = self.BacktestingSummaryDictAll
        # self.BacktestingTradeRecord = self.BacktestingTradeRecordAll


    def loadStrategyParameters(self):
        self.LoopPerTicker = (self.BacktestParameterDF.loc[0, 'LoopPerTicker'] == 1)

        self.StartTimeInStdUnit = self.BacktestParameterDF.loc[0, 'ParameterValue1']
        self.EndTimeInStdUnit = self.BacktestParameterDF.loc[0, 'ParameterValue2']
        self.TimeIntervalInStdUnit = self.BacktestParameterDF.loc[0, 'ParameterValue3']
        
        self.PreFilterDataByTime = (self.BacktestParameterDF.loc[0, 'ParameterValue4'] == 1)
        
        if self.PreFilterDataByTime:
            self.PreFilterDataStartTimeInStdUnit = max(self.StartTimeInStdUnit - BacktestCorrelationOnSpecificTimeSectionStrategy.PreFilterOffset, 0)
            self.PreFilterDataEndTimeInStdUnit = self.EndTimeInStdUnit + BacktestCorrelationOnSpecificTimeSectionStrategy.PreFilterOffset
        else:
            self.PreFilterDataStartTimeInStdUnit = None
            self.PreFilterDataEndTimeInStdUnit = None
            
        threshold_string = self.BacktestParameterDF.loc[0, 'TextParameterValue1']
        self.OBS_PERIOD_MOVEMENT_THRESHOLD = [int(e)/10000 if e.isdigit() else e for e in threshold_string.split(',')]
        print('self.OBS_PERIOD_MOVEMENT_THRESHOLD is ' + str(self.OBS_PERIOD_MOVEMENT_THRESHOLD))

        threshold_string = self.BacktestParameterDF.loc[0, 'TextParameterValue2']
        self.ObsPeriodMovementRangeList = [int(e)/10000 if e.isdigit() else e for e in threshold_string.split(',')]
        print('self.ObsPeriodMovementRange is ' + str(self.ObsPeriodMovementRangeList))

        threshold_string = self.BacktestParameterDF.loc[0, 'StopLossTakeProfitBps']
        self.StopLossTakeProfitList = [int(e)/10000 if e.isdigit() else e for e in threshold_string.split(',')]
        print('self.StopLossTakeProfitList is ' + str(self.StopLossTakeProfitList))

        date_id_offset_string = self.BacktestParameterDF.loc[0, 'TextParameterValue3']
        self.ObsDateIDOffsetList = [int(e) if e.isdigit() else e for e in date_id_offset_string.split(',')]
        date_id_offset_string = self.BacktestParameterDF.loc[0, 'TextParameterValue4']
        print('TextParameterValue4 is ' + date_id_offset_string)
        self.TradeEntryDateIDOffsetList = [int(e) if e.isdigit() else e for e in date_id_offset_string.split(',')]
        print('TradeEntryDateIDOffsetList is ' + str(self.TradeEntryDateIDOffsetList))

        
    def PrepareSummary(self, backtest_result, ScenarioColumnNames):

        BacktestingSummaryDict = {}
        BacktestingTradeRecord = {}

        if (len(backtest_result.trade_record) > 0):
            backtest_result.trade_record = super().getPreparedTradeRecord(backtest_result.trade_record, ScenarioColumnNames, 'trade id', ascending=True)
            if self.RapidCalibrationTopScenarioSelectedCount == 0:
                self.FillDataMatrix(backtest_result.trade_record, 'trade id', ['scenario id'], {'long short flag': 'long short flag', 'entry price': 'entry price', 'exit price': 'exit price'})
            else:
                self.FillDataMatrix(backtest_result.trade_record, 'trade id', ['scenario id'], {'long short flag': 'long short flag', 'entry price': 'entry price', 'exit price': 'exit price', 'date id': 'date id'})
            
            if self.GPUMode == "CUDA":
                BacktestingSummary, RapidCalibrationBacktestingSummary = self.getCUDABacktestingSummary()
            # BacktestingSummary.to_csv(self.ResultOutputFolderPath + self.StrategyLabel + '_' + self.StartDate.strftime("%Y%m%d") + '_' + self.EndDate.strftime("%Y%m%d") + '_' + self.TimeFrame + '_'+ r'BacktestingSummary.csv')
    
            BacktestingSummaryDict = self.FinishSummary(BacktestingSummary, ScenarioColumnNames)
            BacktestingTradeRecord = {}
            for backtest_period in BacktestingSummaryDict:
                BacktestingTradeRecord[backtest_period] = backtest_result.trade_record.merge(BacktestingSummaryDict[backtest_period][ScenarioColumnNames], on=ScenarioColumnNames)
                BacktestingTradeRecord[backtest_period] = BacktestingTradeRecord[backtest_period].merge(self.AnalysisContext.FuturesData.DateIDMapping, on=['date id'])
        return BacktestingSummaryDict, BacktestingTradeRecord
