# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 00:43:40 2021

@author: Henry Cheung
"""

# import pymysql
import pandas as pd
import math
from datetime import date, datetime, timedelta
import time
import InvestmentAnalytics.Config as Config
import InvestmentAnalytics.DaskUtil as DaskUtil
import InvestmentAnalytics.DBUtil as DBUtil

from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy import FuturesStrategyBacktest

class CorrelationOnSpecificTimeSectionStrategy:
    # SCENARIO_COLUMNS = ['ticker id', 'obs TimeInStandardUnit', 'entry TimeInStandardUnit', 'exit TimeInStandardUnit', 'obs movement threshold', 'stop loss', 'take profit']
    SCENARIO_COLUMNS = ['ticker id', 'obs TimeInStandardUnit', 'entry TimeInStandardUnit', 'exit TimeInStandardUnit', 'obs movement threshold', 'obs movement range', 'stop loss', 'take profit', 'obs date id offset', 'trade entry date id offset']
    TRADE_ID_SORTING_COLUMNS = ['exit time id']
    def __init__(self, StrategyLabel, AnalysisContext, StartTimeInStdUnit, EndTimeInStdUnit, TimeIntervalInStdUnit, OBS_PERIOD_MOVEMENT_THRESHOLD = [0, 0.001], ObsPeriodMovementRange = 0, StopLossPerTrade = 0, TakeProfitPerTrade = 0, ObsDateIDOffset = 0, TradeEntryDateIDOffset = 0, TradeIDSortingSegmentKeyColumnsCount = 2, PreFilterDataByTime = False, GPUMode = "CUDA", InitialResultCacheSize = None, GPU_CORE_BLOCK_SIZE = 32*32, TotalBatchIndex=0, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch'):
        self.BatchListDatabaseName = BatchListDatabaseName
        self.BatchListTableName = BatchListTableName
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

        SortingColumns = CorrelationOnSpecificTimeSectionStrategy.SCENARIO_COLUMNS + CorrelationOnSpecificTimeSectionStrategy.TRADE_ID_SORTING_COLUMNS
        print('SCENARIO_COLUMNS is ' + str(CorrelationOnSpecificTimeSectionStrategy.SCENARIO_COLUMNS))
        print('TRADE_ID_SORTING_COLUMNS is ' + str(CorrelationOnSpecificTimeSectionStrategy.TRADE_ID_SORTING_COLUMNS))

        if GPUMode == "CUDA":
            self.trade_record = CUDACorrelationOnSpecificTimeSectionStrategy(self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_close_adj'], self.AnalysisContext.IntradayPricesData.DataMatrix['date id'], self.AnalysisContext.IntradayPricesData.DataMatrix['TimeInStandardUnit'], self.StartTimeInStdUnit, self.EndTimeInStdUnit, self.TimeIntervalInStdUnit, len(DateList), ObsPeriodMovementThreshold = self.OBS_PERIOD_MOVEMENT_THRESHOLD, StopLossPerTrade = self.StopLossPerTrade, TakeProfitPerTrade = self.TakeProfitPerTrade, ObsDateIDOffset = self.ObsDateIDOffset, TradeEntryDateIDOffset = self.TradeEntryDateIDOffset, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = self.InitialResultCacheSize, TimeFrame = self.TimeFrame, GPU_CORE_BLOCK_SIZE = self.GPU_CORE_BLOCK_SIZE)

            # import dask.dataframe as dd
            # import dask.array as da
            # import dask.bag as db
            # self.trade_record = dd.from_pandas(self.trade_record, npartitions=10)

            # print('self.trade_record is')
            # print(self.trade_record.head(10))
            
            self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'TimeInStandardUnit']], left_on='obs time id', right_on='time id').drop(['time id'], axis=1).rename(columns = {'TimeInStandardUnit': 'obs TimeInStandardUnit'})
            self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'TimeInStandardUnit']], left_on='entry time id', right_on='time id').drop(['time id'], axis=1).rename(columns = {'TimeInStandardUnit': 'entry TimeInStandardUnit'})
            self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'date id', 'TimeInStandardUnit']], left_on='exit time id', right_on='time id').drop(['time id'], axis=1).rename(columns = {'TimeInStandardUnit': 'exit TimeInStandardUnit'})
            self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'TimeInStandardUnit']], left_on='stop time id', right_on='time id').drop(['time id'], axis=1).rename(columns = {'TimeInStandardUnit': 'stop TimeInStandardUnit'})

            from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy import StrategyBacktest
            StrategyBacktest.OrganiseTradeRecord(self, TickerIDMapping_DF, SortingColumns, CorrelationOnSpecificTimeSectionStrategy.SCENARIO_COLUMNS, self.TradeIDSortingSegmentKeyColumnsCount)
            print('after assigning trade id by CUDA at ' + str(datetime.now()))
            
    def PrepareEmailAlert(MessageID, MessageFirstLine, ticker, ObservationTimeText, ObservationMovement, TakeProfitBps, StopLossBps, TradeEntryTime, TickSize = 0.1, AppendixFirstLine = '', TradeForceExitTime = '', BackTestSharpeRatio = 0, BackTestTradeSampleSize = 0, BackTestPeriod = '', isMeanReversing=True):
        today = date.today()
        PriorDate = today - timedelta(days=1)
        if PriorDate.weekday() > 4:
            PriorDate = PriorDate - timedelta(days=PriorDate.weekday() - 4)
        # print('PriorDate day of week is ' + str(PriorDate.weekday()))
        
        PriorDateTimeText = PriorDate.strftime("%Y-%m-%d") + ' ' + ObservationTimeText
        
        sql = "SELECT * FROM `fdata_fut_hist` WHERE tDateTime = '" + PriorDateTimeText + "' and ticker = '" + ticker + "' and DataType = 'TRADES' and timeframe = '1 min' order by vol desc"
        print(sql)
      
        df = pd.read_sql(sql, con=DBUtil.GetSQLAlchemyEngine(DatabaseName=Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST))    
        
        # print(df)
        PriorDateClose = df.iloc[0]['close']
        PriorDatePlusMovement = PriorDateClose * (1 + ObservationMovement)
        PriorDateMinusMovement = PriorDateClose * (1 - ObservationMovement)
        if isMeanReversing:
            LongPrice = PriorDateMinusMovement
            ShortPrice = PriorDatePlusMovement
        else:
            LongPrice = PriorDatePlusMovement
            ShortPrice = PriorDateMinusMovement
        
        LongTakeProfit = LongPrice * (1 + TakeProfitBps/10000)
        LongStopLoss = LongPrice * (1 - StopLossBps/10000)
        ShortTakeProfit = ShortPrice * (1 - TakeProfitBps/10000)
        ShortStopLoss = ShortPrice * (1 + StopLossBps/10000)
        
        Message = str(MessageID) + '.<BR>' + MessageFirstLine + '<BR><table border =1>'
        Message = Message + '<tr><td>Ticker</td><td>' + ticker + '</td><td>Trade Entry Time</td><td>' + TradeEntryTime + '</td><td>Trade Force Exit Time</td><td>' + TradeForceExitTime + '</td></tr>'

        if isMeanReversing:
            Message = Message + '<tr><td>Long if price lower than</td><td>' + f"{round(round(LongPrice/TickSize, 0) * TickSize, 2):,}" + '</td><td>Take Profit price</td><td>' + str(TakeProfitBps) + 'bps</td><td>Stop Loss price</td><td>' + str(StopLossBps) + 'bps</td></tr>'
            Message = Message + '<tr><td>Short if price higher than</td><td>' + f"{round(round(ShortPrice/TickSize, 0) * TickSize, 2):,}" + '</td><td>Take Profit price</td><td>' + str(TakeProfitBps) + 'bps</td><td>Stop Loss price</td><td>' + str(StopLossBps) + 'bps</td></tr>'
        else:
            Message = Message + '<tr><td>Short if price lower than</td><td>' + f"{round(round(LongPrice/TickSize, 0) * TickSize, 2):,}" + '</td><td>Take Profit price</td><td>' + str(TakeProfitBps) + 'bps</td><td>Stop Loss price</td><td>' + str(StopLossBps) + 'bps</td></tr>'
            Message = Message + '<tr><td>Long if price higher than</td><td>' + f"{round(round(ShortPrice/TickSize, 0) * TickSize, 2):,}" + '</td><td>Take Profit price</td><td>' + str(TakeProfitBps) + 'bps</td><td>Stop Loss price</td><td>' + str(StopLossBps) + 'bps</td></tr>'
        # Message = Message + '<tr><td></td><td></td><td></td><td></td><td></td><td></td></tr>'
        Message = Message + '</table><BR><BR>'
        # Message = Message + '</table>Observation date time ' + PriorDateTimeText + ' close is ' + str(PriorDateClose) + ' and key levels are ' + str(PriorDatePlusMovement) + ' / ' + str(PriorDateMinusMovement) + '<BR><BR>'

        Appendix = str(MessageID) + '.<BR>' + AppendixFirstLine + '<BR><table border=1><tr><td>Backtest Sharpe Ratio</td><td>' + str(BackTestSharpeRatio) + '</td></tr>'
        Appendix = Appendix + '<tr><td>Backtest Trade Sample Size</td><td>' + str(BackTestTradeSampleSize) + '</td></tr>'
        Appendix = Appendix + '<tr><td>Backtest Period</td><td>' + BackTestPeriod + '</td></tr>'
        # Appendix = Appendix + '<tr><td></td><td></td></tr>'
        Appendix = Appendix + '</table><BR><BR>'
        return (Message, Appendix)
        

class BacktestCorrelationOnSpecificTimeSectionStrategy(FuturesStrategyBacktest):
    PreFilterOffset = 10
    def __init__(self, BacktestParameterDF, AnalysisContextList, TickerFilter = [], ResultOutputFolderPath = None, PerformContangoAdjustment = True, MinimumTradeNumberCountForFullPeriod = 50, RandomNoiseTickerStdev = None, FillEveryTimeSlot = False, ActiveContractPircesTrimmedColumns = None, RapidCalibration = False, RapidCalibrationTopScenarioSelectedCount = 0, KeepOnlyWeekdays = False, threshold_count_per_batch = 1, InstrumentType = 'Futures', PreFilterDataByTime = False, MarketTimeSectionTimeList = None, DebugFilepath = None, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch', Override_DBHost = None, Override_DBPort = None, Override_DBUser = None, Override_DBPassword = None):


        self.StrategyLabel = 'CorrelationOnSpecificTimeSectionStrategy'
        self.BacktestParameterDF = BacktestParameterDF
        self.loadStrategyParameters()
        super().__init__('CorrelationOnSpecificTimeSectionStrategy', BacktestParameterDF, AnalysisContextList, PreFilterDataByTime = self.PreFilterDataByTime, PreFilterDataStartTimeInStdUnit = self.PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit = self.PreFilterDataEndTimeInStdUnit, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath, BatchListDatabaseName = BatchListDatabaseName, BatchListTableName = BatchListTableName )
        
        if self.LoopPerTicker:
            TickerFullList = self.AnalysisContext.FuturesData.TickerIDMapping['ticker'].tolist()
            print('TickerFullList is ' + str(TickerFullList))
            BacktestingSummaryDictAll = {}
            BacktestingTradeRecordAll = {}
            ticker_index = 1
            for ticker in TickerFullList:
                print()
                print('Loop per ticker.  Looping for ' + ticker)
                TickerFilter = [ticker]
                self.AnalysisContext = self.getAnalysisContext(PreFilterDataByTime, self.PreFilterDataStartTimeInStdUnit, self.PreFilterDataEndTimeInStdUnit, TickerFilter, False, PerformContangoAdjustment, RandomNoiseTickerStdev, FillEveryTimeSlot, KeepOnlyWeekdays, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList , DebugFilepath = DebugFilepath)
                BacktestingSummaryDict, BacktestingTradeRecord = self.init_per_ticker_list(BacktestParameterDF, AnalysisContextList, TickerFilter = TickerFilter, TickerLoopLabel = str(ticker_index) + '/' + str(len(TickerFullList)), ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, threshold_count_per_batch = threshold_count_per_batch, InstrumentType = InstrumentType, PreFilterDataByTime = PreFilterDataByTime, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath)
                
                # print('In BacktestCorrelationOnSpecificTimeSectionStrategy.init, BacktestingSummaryDict is')
                # print(BacktestingSummaryDict)
                # print('In BacktestCorrelationOnSpecificTimeSectionStrategy.init, BacktestingTradeRecord is')
                # print(BacktestingTradeRecord)
                # print('BacktestingSummaryDict.keys() is')
                # print(BacktestingSummaryDict.keys())

                for key in BacktestingSummaryDict:
                    if key in BacktestingSummaryDictAll:
                        # BacktestingSummaryDictAll[key] = BacktestingSummaryDictAll[key].append(BacktestingSummaryDict[key])
                        BacktestingSummaryDictAll[key] = pd.concat([BacktestingSummaryDictAll[key], BacktestingSummaryDict[key]])
                    else:
                        BacktestingSummaryDictAll[key] = BacktestingSummaryDict[key]
                        
                for key in BacktestingTradeRecord:
                    if key in BacktestingTradeRecordAll:
                        # BacktestingTradeRecordAll[key] = BacktestingTradeRecordAll[key].append(BacktestingTradeRecord[key])
                        BacktestingTradeRecordAll[key] = pd.concat([BacktestingTradeRecordAll[key], BacktestingTradeRecord[key]])
                    else:
                        BacktestingTradeRecordAll[key] = BacktestingTradeRecord[key]
                ticker_index = ticker_index + 1

            self.BacktestingSummaryDict = BacktestingSummaryDictAll
            self.BacktestingTradeRecord = BacktestingTradeRecordAll

        else:

            BacktestingSummaryDictAll, BacktestingTradeRecordAll = self.init_per_ticker_list(BacktestParameterDF, AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, threshold_count_per_batch = threshold_count_per_batch, InstrumentType = InstrumentType, PreFilterDataByTime = PreFilterDataByTime, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath)
    
            self.BacktestingSummaryDict = BacktestingSummaryDictAll
            self.BacktestingTradeRecord = BacktestingTradeRecordAll
            
        for key in self.BacktestingSummaryDict:
            self.BacktestingSummaryDict[key]['Abs Sharpe Ratio after commission'] = self.BacktestingSummaryDict[key]['Sharpe Ratio after commission'].abs()
            self.BacktestingSummaryDict[key] = self.BacktestingSummaryDict[key].sort_values(by='Abs Sharpe Ratio after commission', ascending=False).drop(['Abs Sharpe Ratio after commission'],axis='columns')

        self.FullResultOutputFolderPath = self.ResultOutputFolderPath + self.BatchGroup + '_' + self.StrategyLabel + '_' + self.StartDate.strftime("%Y%m%d") + '_' + self.EndDate.strftime("%Y%m%d") + '_' + self.TimeFrame + '_' + str(self.StartTimeInStdUnit) + '_'+ str(self.EndTimeInStdUnit) + '_'+ str(self.TimeIntervalInStdUnit) + '_'


    def init_per_ticker_list(self, BacktestParameterDF, AnalysisContextList, TickerFilter = [], TickerLoopLabel = '', ResultOutputFolderPath = None, PerformContangoAdjustment = True, MinimumTradeNumberCountForFullPeriod = 50, RandomNoiseTickerStdev = None, FillEveryTimeSlot = False, ActiveContractPircesTrimmedColumns = None, RapidCalibration = False, RapidCalibrationTopScenarioSelectedCount = 0, KeepOnlyWeekdays = False, threshold_count_per_batch = 1, InstrumentType = 'Futures', PreFilterDataByTime = False, MarketTimeSectionTimeList = None, DebugFilepath = None):
        super().__init__('CorrelationOnSpecificTimeSectionStrategy', BacktestParameterDF, AnalysisContextList, PreFilterDataByTime = self.PreFilterDataByTime, PreFilterDataStartTimeInStdUnit = self.PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit = self.PreFilterDataEndTimeInStdUnit, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath, BatchListDatabaseName = self.BatchListDatabaseName, BatchListTableName = self.BatchListTableName  )

        BacktestingSummaryDictAll = {}
        BacktestingTradeRecordAll = {}
        
        threshold_remain_list = self.OBS_PERIOD_MOVEMENT_THRESHOLD.copy()
        
        TotalBatchCount = len(FuturesStrategyBacktest.getListOfList(self.OBS_PERIOD_MOVEMENT_THRESHOLD, self.ParameterTrialCountPerLoop[0])) * len(self.StopLossTakeProfitList) * len(self.StopLossTakeProfitList) * len(self.ObsDateIDOffsetList) * len(self.TradeEntryDateIDOffsetList)
        TotalBatchIndex = 0

        for threshold_list in FuturesStrategyBacktest.getListOfList(self.OBS_PERIOD_MOVEMENT_THRESHOLD, self.ParameterTrialCountPerLoop[0]):
            for ObsPeriodMovementRange in self.ObsPeriodMovementRangeList:
                for StopLossPerTrade in self.StopLossTakeProfitList:
                    for TakeProfitPerTrade in self.StopLossTakeProfitList:
                        for ObsDateIDOffset in self.ObsDateIDOffsetList:
                            for TradeEntryDateIDOffset in self.TradeEntryDateIDOffsetList:
    
                                TotalBatchIndex = TotalBatchIndex + 1
                                print()
                                print('In Batch ' + str(self.BatchID) + '(' + str(self.BatchSubID) + ') Start running ' + self.StrategyLabel + ' TickerFilter ' + str(TickerFilter) + ' ' + TickerLoopLabel + ' batch ' + str(TotalBatchIndex) + '/' + str(TotalBatchCount) + ' for threshold ' + str(threshold_list) + ', stop loss ' + str(StopLossPerTrade) + ', take profit ' + str(TakeProfitPerTrade)  + ', ObsDateIDOffset is ' + str(ObsDateIDOffset)  + ', TradeEntryDateIDOffset is ' + str(TradeEntryDateIDOffset) + ' at ' + str(datetime.now()))
                            
                                backtest_result = CorrelationOnSpecificTimeSectionStrategy(self.StrategyLabel, self.AnalysisContext, self.StartTimeInStdUnit, self.EndTimeInStdUnit, self.TimeIntervalInStdUnit, OBS_PERIOD_MOVEMENT_THRESHOLD = threshold_list, ObsPeriodMovementRange = ObsPeriodMovementRange, StopLossPerTrade = StopLossPerTrade, TakeProfitPerTrade = TakeProfitPerTrade, ObsDateIDOffset = ObsDateIDOffset, TradeEntryDateIDOffset = TradeEntryDateIDOffset, TradeIDSortingSegmentKeyColumnsCount = self.TradeIDSortingSegmentKeyColumnsCount, GPUMode = self.GPUMode, InitialResultCacheSize = self.InitialResultCacheSize, GPU_CORE_BLOCK_SIZE = self.GPUCore, TotalBatchIndex=TotalBatchIndex, BatchListDatabaseName = self.BatchListDatabaseName, BatchListTableName = self.BatchListTableName )
                                # self.backtest_result = CorrelationOnSpecificTimeSectionStrategy('CorrelationOnSpecificTimeSectionStrategy', self.AnalysisContext, self.StartTimeInStdUnit, self.EndTimeInStdUnit, self.TimeIntervalInStdUnit, OBS_PERIOD_MOVEMENT_THRESHOLD = threshold_list, StopLossPerTrade = StopLossPerTrade, TakeProfitPerTrade = TakeProfitPerTrade, ObsDateIDOffset = ObsDateIDOffset, TradeEntryDateIDOffset = TradeEntryDateIDOffset, TradeIDSortingSegmentKeyColumnsCount = self.TradeIDSortingSegmentKeyColumnsCount, GPUMode = self.GPUMode )
                                
                                self.UpdateLastRunMaxTradeRecordSizePerSubBatch(len(backtest_result.trade_record))
                                BacktestingSummaryDict, BacktestingTradeRecord = self.PrepareSummary(backtest_result, CorrelationOnSpecificTimeSectionStrategy.SCENARIO_COLUMNS, TotalBatchIndex=TotalBatchIndex)
                    
                                for key in BacktestingSummaryDict:
                                    if key in BacktestingSummaryDictAll:
                                        BacktestingSummaryDictAll[key] = pd.concat([BacktestingSummaryDictAll[key], BacktestingSummaryDict[key]])
                                    else:
                                        BacktestingSummaryDictAll[key] = BacktestingSummaryDict[key]
                                for key in BacktestingTradeRecord:
                                    if key in BacktestingTradeRecordAll:
                                        BacktestingTradeRecordAll[key] = pd.concat([BacktestingTradeRecordAll[key], BacktestingTradeRecord[key]])
                                    else:
                                        BacktestingTradeRecordAll[key] = BacktestingTradeRecord[key]
                
        return BacktestingSummaryDictAll, BacktestingTradeRecordAll

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

        
    def PrepareSummary(self, backtest_result, ScenarioColumnNames, TotalBatchIndex=0):
        print('Start of PrepareSummary')

        BacktestingSummaryDict = {}
        BacktestingTradeRecord = {}

        if (len(backtest_result.trade_record) > 0):
            print('In PrepareSummary, len(backtest_result.trade_record) > 0')
            backtest_result.trade_record = super().getPreparedTradeRecord(backtest_result.trade_record, ScenarioColumnNames, 'trade id', ascending=True)
            
            # try to comment and see if it is used
            if self.RapidCalibrationTopScenarioSelectedCount == 0:
                self.FillDataMatrix(backtest_result.trade_record, 'trade id', ['scenario id'], {'long short flag': 'long short flag', 'entry price': 'entry price', 'exit price': 'exit price'})
            else:
                self.FillDataMatrix(backtest_result.trade_record, 'trade id', ['scenario id'], {'long short flag': 'long short flag', 'entry price': 'entry price', 'exit price': 'exit price', 'date id': 'date id'})
            
            
            if self.GPUMode == "CUDA":
                BacktestingSummary, RapidCalibrationBacktestingSummary = self.getCUDABacktestingSummary()
                
            BacktestingSummaryDict = self.FinishSummary(BacktestingSummary, ScenarioColumnNames)
                
            BacktestingTradeRecord = {}
            for backtest_period in BacktestingSummaryDict:
                BacktestingTradeRecord[backtest_period] = backtest_result.trade_record.merge(BacktestingSummaryDict[backtest_period][ScenarioColumnNames], on=ScenarioColumnNames)
                BacktestingTradeRecord[backtest_period] = BacktestingTradeRecord[backtest_period].merge(self.AnalysisContext.FuturesData.DateIDMapping, on=['date id'])

            for backtest_period in BacktestingSummaryDict:
                if not isinstance(BacktestingTradeRecord[backtest_period], pd.DataFrame):
                    BacktestingTradeRecord[backtest_period] = BacktestingTradeRecord[backtest_period].compute()
                
        return BacktestingSummaryDict, BacktestingTradeRecord
