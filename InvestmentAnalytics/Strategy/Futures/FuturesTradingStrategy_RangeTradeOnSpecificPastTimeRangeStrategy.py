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

import InvestmentAnalytics.DBUtil as DBUtil

from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy import FuturesStrategyBacktest

class RangeTradeOnSpecificPastTimeRangeStrategy:
    SCENARIO_COLUMNS = ['ticker id', 'obs start TimeInStandardUnit', 'obs end TimeInStandardUnit', 'start trading TimeInStandardUnit', 'trade period length', 'min range width', 'max range width', 'trade entry level offset', 'stop loss', 'take profit', 'stop loss take profit relative to range', 'max profit trade per day', 'max loss trade per day']
    TRADE_ID_SORTING_COLUMNS = ['exit time id']
    def __init__(self, StrategyLabel, AnalysisContext, StartTimeInStdUnit, EndTimeInStdUnit, TimeIntervalInStdUnit, MaxBackdateTimePeriodInStdUnit = 2160, MinBackdateTimePeriodInStdUnit = 240, RangeBoundaryTimeIntervalInStdUnit = 60, MinRangeTimeWidthInStdUnit = 240, MinRangeWidth = [0.01], MaxRangeWidth = [0.05],TradeEntryLevelOffset = [0, 0.0025, -0.0025], TradeStopLoss = [0.0025, 0.0050], TradeTakeProfit = [0.0025, 0.0050], MaxProfitTradePerDay = [1, 2], MaxLossTradePerDay = [1, 2], TradePeriodLength = [90,180,270,360], StopLossTakeProfitRelativeToRange = [1], TradeIDSortingSegmentKeyColumnsCount = 2, PreFilterDataByTime = False, GPUMode = "CUDA", InitialResultCacheSize = None, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch'):
        print("Start of RangeTradeOnSpecificPastTimeRangeStrategy.init, TradeStopLoss = " + str(TradeStopLoss) + " and TradeTakeProfit = " + str(TradeTakeProfit))
        self.BatchListDatabaseName = BatchListDatabaseName
        self.BatchListTableName = BatchListTableName
        self.StrategyLabel = StrategyLabel
        self.AnalysisContext = AnalysisContext
        self.TimeFrame = AnalysisContext.FuturesData.TimeFrame
        
        self.StartTimeInStdUnit = StartTimeInStdUnit
        self.EndTimeInStdUnit = EndTimeInStdUnit
        self.TimeIntervalInStdUnit = TimeIntervalInStdUnit
        self.MaxBackdateTimePeriodInStdUnit = MaxBackdateTimePeriodInStdUnit
        self.MinBackdateTimePeriodInStdUnit = MinBackdateTimePeriodInStdUnit
        self.RangeBoundaryTimeIntervalInStdUnit = RangeBoundaryTimeIntervalInStdUnit
        self.MinRangeTimeWidthInStdUnit = MinRangeTimeWidthInStdUnit
        
        self.InitialResultCacheSize = InitialResultCacheSize
        self.TradeIDSortingSegmentKeyColumnsCount = TradeIDSortingSegmentKeyColumnsCount
        self.GPUMode = GPUMode
        if GPUMode == "CUDA":
            from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib import CUDATradeIDAssignment
            from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib_RangeTradeOnSpecificPastTimeRangeStrategy import CUDARangeTradeOnSpecificPastTimeRangeStrategy

        self.MinRangeWidth = MinRangeWidth
        self.MaxRangeWidth = MaxRangeWidth
        self.TradeEntryLevelOffset = TradeEntryLevelOffset
        self.TradeStopLoss = TradeStopLoss
        self.TradeTakeProfit = TradeTakeProfit
        self.MaxProfitTradePerDay = MaxProfitTradePerDay
        self.MaxLossTradePerDay = MaxLossTradePerDay
        self.TradePeriodLength = TradePeriodLength
        self.StopLossTakeProfitRelativeToRange = StopLossTakeProfitRelativeToRange

        self.CountOfTimeInterval = math.floor((EndTimeInStdUnit - StartTimeInStdUnit)/TimeIntervalInStdUnit)
        TimeIDMapping_DF = self.AnalysisContext.FuturesData.TimeIDMapping
        
        TickerIDMapping_DF = self.AnalysisContext.FuturesData.TickerIDMapping
        
        DateList = pd.pivot_table(TimeIDMapping_DF, values='time id', index=['Date'], aggfunc=len, fill_value=0).sort_values(by='Date', ascending=False).reset_index()
        DateList['Date id'] = DateList.index
        DateList['Dummy'] = 1

        SortingColumns = RangeTradeOnSpecificPastTimeRangeStrategy.SCENARIO_COLUMNS + RangeTradeOnSpecificPastTimeRangeStrategy.TRADE_ID_SORTING_COLUMNS

        if GPUMode == "CUDA":
            
            self.trade_record = CUDARangeTradeOnSpecificPastTimeRangeStrategy(self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_close_adj'], self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_high_adj'], self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_low_adj'], self.AnalysisContext.IntradayPricesData.DataMatrix['date id'], self.AnalysisContext.IntradayPricesData.DataMatrix['TimeInStandardUnit'], self.StartTimeInStdUnit, self.EndTimeInStdUnit, self.TimeIntervalInStdUnit, self.RangeBoundaryTimeIntervalInStdUnit, self.MinRangeTimeWidthInStdUnit, self.MaxBackdateTimePeriodInStdUnit, self.MinBackdateTimePeriodInStdUnit, MinRangeWidth = self.MinRangeWidth, MaxRangeWidth = self.MaxRangeWidth, TradeEntryLevelOffset = self.TradeEntryLevelOffset, TradeStopLoss = self.TradeStopLoss, TradeTakeProfit = self.TradeTakeProfit, MaxProfitTradePerDay = self.MaxProfitTradePerDay, MaxLossTradePerDay = self.MaxLossTradePerDay, TradePeriodLength = self.TradePeriodLength, StopLossTakeProfitRelativeToRange = self.StopLossTakeProfitRelativeToRange, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = self.InitialResultCacheSize, TimeFrame = self.TimeFrame)

            self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'TimeInStandardUnit']], left_on='obs time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'obs TimeInStandardUnit'}, inplace = False)
            self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'TimeInStandardUnit']], left_on='entry time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'entry TimeInStandardUnit'}, inplace = False)
            self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'date id', 'TimeInStandardUnit']], left_on='exit time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'exit TimeInStandardUnit'}, inplace = False)
            self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'TimeInStandardUnit']], left_on='stop time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'stop TimeInStandardUnit'}, inplace = False)

            from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy import StrategyBacktest
            StrategyBacktest.OrganiseTradeRecord(self, TickerIDMapping_DF, SortingColumns, RangeTradeOnSpecificPastTimeRangeStrategy.SCENARIO_COLUMNS, self.TradeIDSortingSegmentKeyColumnsCount)
            print('after assigning trade id by CUDA at ' + str(datetime.now()))

    def PrepareEmailAlert(MessageID, MessageFirstLine, ticker, ObservationStartTimeOffset, ObservationEndTimeOffset, StartTradingTime, TradePeriodLength, MinRangeWidth, MaxRangeWidth, TakeProfitBps, StopLossBps, StopLossTakeProfitRelativeToRange, TradeEntryTime, TickSize = 0.1, AppendixFirstLine = '', TradeForceExitTime = '', BackTestSharpeRatio = 0, BackTestTradeSampleSize = 0, BackTestPeriod = '', isMeanReversing=False):
# mes, app = RangeTradeOnSpecificPastTimeRangeStrategy.PrepareEmailAlert(3, 'RangeTradeOnSpecificPastTimeRangeStrategy, Breakthrough<BR>ticker = ES', 'ES', -1320, -1080, 750, 300, 0.02, 0.05, 100, 150, True, '12:30pm NY time', TickSize = 0.25, AppendixFirstLine = 'For RangeTradeOnSpecificPastTimeRangeStrategy, Batch ID 20805<BR>ticker = ES, Take Profit = 10% of range, Stop Loss = 150% of range', TradeForceExitTime = '5:30pm NY time', BackTestSharpeRatio = 1.1871157, BackTestTradeSampleSize = 56, BackTestPeriod='2019-01-01 to 2022-12-31')
        Message = ''
        Appendix = ''
        today = date.today()
        PriorDate = today - timedelta(days=1)
        if PriorDate.weekday() > 4:
            PriorDate = PriorDate - timedelta(days=PriorDate.weekday() - 4)
        # print('PriorDate day of week is ' + str(PriorDate.weekday()))
            
        if ObservationStartTimeOffset + StartTradingTime < 0:
            ObservationStartTime = StartTradingTime + (24*60) + ObservationStartTimeOffset
        else:
            ObservationStartTime = StartTradingTime + ObservationStartTimeOffset
        # '12:05:00'
        ObservationTimeText = str(ObservationStartTime // 60) + ':' + str(ObservationStartTime % 60) + ':00'
        ObservationStartTimeText = PriorDate.strftime("%Y-%m-%d") + ' ' + ObservationTimeText
        print(ObservationStartTimeText)
            
        if ObservationEndTimeOffset + StartTradingTime < 0:
            ObservationEndTime = StartTradingTime + (24*60) + ObservationEndTimeOffset
        else:
            ObservationEndTime = StartTradingTime + ObservationEndTimeOffset
        # '12:05:00'
        ObservationTimeText = str(ObservationEndTime // 60) + ':' + str(ObservationEndTime % 60) + ':00'
        ObservationEndTimeText = PriorDate.strftime("%Y-%m-%d") + ' ' + ObservationTimeText
        print(ObservationEndTimeText)

        
        # PriorDateTimeText = PriorDate.strftime("%Y-%m-%d") + ' ' + ObservationTimeText
        
        sql = "tDateTime >= '" + ObservationStartTimeText + "' and tDateTime <= '" + ObservationEndTimeText + "' and ticker in ('" + ticker + "') and DataType = 'TRADES' and timeframe = '1 min'"
        sql = "SELECT AAA.* FROM (SELECT * FROM fdata_fut_hist WHERE " + sql + ") AAA INNER JOIN (SELECT AA.ticker, AA.expiry FROM (SELECT ticker,expiry,SUM(vol) AS VolSum FROM fdata_fut_hist WHERE " + sql + " GROUP BY ticker,expiry) AA INNER JOIN (SELECT ticker, MAX(VolSum) as VolSum FROM (SELECT ticker,expiry,SUM(vol) AS VolSum FROM fdata_fut_hist WHERE " + sql + " GROUP BY ticker,expiry) B) BB ON AA.ticker = BB.ticker AND AA.VolSum = BB.VolSum) BBB ON AAA.ticker =  BBB.ticker and AAA.expiry = BBB.expiry"
        print(sql)
      
        df = pd.read_sql(sql, con=DBUtil.GetSQLAlchemyEngine(DatabaseName=Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST))    
        
        while len(df) == 0:
            PriorDate = PriorDate - timedelta(days=1)
            PriorDateTimeText = PriorDate.strftime("%Y-%m-%d") + ' ' + ObservationTimeText

            if ObservationStartTimeOffset + StartTradingTime < 0:
                ObservationStartTime = StartTradingTime + (24*60) + ObservationStartTimeOffset
            else:
                ObservationStartTime = StartTradingTime + ObservationStartTimeOffset
            # '12:05:00'
            ObservationTimeText = str(ObservationStartTime // 60) + ':' + str(ObservationStartTime % 60) + ':00'
            ObservationStartTimeText = PriorDate.strftime("%Y-%m-%d") + ' ' + ObservationTimeText
            print(ObservationStartTimeText)
                
            if ObservationEndTimeOffset + StartTradingTime < 0:
                ObservationEndTime = StartTradingTime + (24*60) + ObservationEndTimeOffset
            else:
                ObservationEndTime = StartTradingTime + ObservationEndTimeOffset
            # '12:05:00'
            ObservationTimeText = str(ObservationEndTime // 60) + ':' + str(ObservationEndTime % 60) + ':00'
            ObservationEndTimeText = PriorDate.strftime("%Y-%m-%d") + ' ' + ObservationTimeText
            print(ObservationEndTimeText)

            sql = "tDateTime >= '" + ObservationStartTimeText + "' and tDateTime <= '" + ObservationEndTimeText + "' and ticker in ('" + ticker + "') and DataType = 'TRADES' and timeframe = '1 min'"
            sql = "SELECT AAA.* FROM (SELECT * FROM fdata_fut_hist WHERE " + sql + ") AAA INNER JOIN (SELECT AA.ticker, AA.expiry FROM (SELECT ticker,expiry,SUM(vol) AS VolSum FROM fdata_fut_hist WHERE " + sql + " GROUP BY ticker,expiry) AA INNER JOIN (SELECT ticker, MAX(VolSum) as VolSum FROM (SELECT ticker,expiry,SUM(vol) AS VolSum FROM fdata_fut_hist WHERE " + sql + " GROUP BY ticker,expiry) B) BB ON AA.ticker = BB.ticker AND AA.VolSum = BB.VolSum) BBB ON AAA.ticker =  BBB.ticker and AAA.expiry = BBB.expiry"
            print(sql)
          
            df = pd.read_sql(sql, con=DBUtil.GetSQLAlchemyEngine(DatabaseName=Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST))    
        
        
        df = df[['ticker', 'tDateTime', 'expiry', 'open', 'high', 'low', 'close', 'vol']]
        print(df)
        
        RangeTop = df['high'].max()
        RangeBottom = df['low'].min()
        RangeWidth = (RangeTop - RangeBottom) / RangeBottom
        
        print('Range is ' + str(RangeBottom) + ' to ' + str(RangeTop))
        
        if (RangeWidth >= MinRangeWidth) and (RangeWidth <= MaxRangeWidth):
            Message = str(MessageID) + '.<BR>' + MessageFirstLine + '<BR><table border =1>'
            Message = Message + '<tr><td>Ticker</td><td>' + ticker + '</td><td>Trade Entry Time</td><td>' + TradeEntryTime + '</td><td>Trade Force Exit Time</td><td>' + TradeForceExitTime + '</td></tr>'
            
            if StopLossTakeProfitRelativeToRange:
                TakeProfit = RangeWidth*TakeProfitBps/10000
                StopLoss = RangeWidth*StopLossBps/10000
            else:
                TakeProfit = RangeTop*TakeProfitBps/10000
                StopLoss = RangeTop*StopLossBps/10000
            if isMeanReversing:
                pass
            else:
                RangeTopTakeProfit = RangeTop + TakeProfit
                RangeTopStopLoww = RangeTop - StopLoss
                Message = Message + '<tr><td>Long at price</td><td>' + f"{round(round(RangeTop/TickSize, 0) * TickSize, 2):,}" + '</td><td>Take Profit price</td><td>' + f"{round(round(RangeTopTakeProfit/TickSize, 0) * TickSize, 2):,}" + '</td><td>Stop Loss price</td><td>' + f"{round(round(RangeTopStopLoss/TickSize, 0) * TickSize, 2):,}" + '</td></tr>'
            
            
            if not StopLossTakeProfitRelativeToRange:
                TakeProfit = RangeBottom*TakeProfitBps/10000
                StopLoss = RangeBottom*StopLossBps/10000
            if isMeanReversing:
                pass
            else:
                RangeBottomTakeProfit = RangeBottom - TakeProfit
                RangeBottomStopLoss = RangeBottom + StopLoss
                Message = Message + '<tr><td>Short at price</td><td>' + f"{round(round(RangeBottom/TickSize, 0) * TickSize, 2):,}" + '</td><td>Take Profit price</td><td>' + f"{round(round(RangeBottomTakeProfit/TickSize, 0) * TickSize, 2):,}" + '</td><td>Stop Loss price</td><td>' + f"{round(round(RangeBottomStopLoss/TickSize, 0) * TickSize, 2):,}" + '</td></tr>'

            # Message = Message + '<tr><td></td><td></td><td></td><td></td><td></td><td></td></tr>'
            Message = Message + '</table><BR><BR>'
        

        else:
            Message = str(MessageID) + '.<BR>' + MessageFirstLine + '<BR>No Trade Today<BR>Price Range of ' + str(RangeBottom) + ' to ' + str(RangeTop) + ' between ' + ObservationStartTimeText + ' and ' + ObservationEndTimeText + '  is not within threshold of ' + str(MinRangeWidth*100) + '% to ' + str(MaxRangeWidth*100) + '%'

        Appendix = str(MessageID) + '.<BR>' + AppendixFirstLine + '<BR><table border=1><tr><td>Backtest Sharpe Ratio</td><td>' + str(BackTestSharpeRatio) + '</td></tr>'
        Appendix = Appendix + '<tr><td>Backtest Trade Sample Size</td><td>' + str(BackTestTradeSampleSize) + '</td></tr>'
        Appendix = Appendix + '<tr><td>Backtest Period</td><td>' + BackTestPeriod + '</td></tr>'
        # Appendix = Appendix + '<tr><td></td><td></td></tr>'
        Appendix = Appendix + '</table><BR><BR>'

            
        return (Message, Appendix)    

class BacktestRangeTradeOnSpecificPastTimeRangeStrategy(FuturesStrategyBacktest):
    PreFilterOffset = 10
    MAX_TRADE_ID = 4000
    # threshold_count_per_batch = 2
    # def __init__(self, BatchGroup, BacktestBatchID, BacktestBatchSubID, AnalysisContextList, TickerFilter = [], ResultOutputFolderPath = None, PerformContangoAdjustment = True, MinimumTradeNumberCountForFullPeriod = 50, RandomNoiseTickerStdev = None, FillEveryTimeSlot = False, ActiveContractPircesTrimmedColumns = None, RapidCalibration = False, RapidCalibrationTopScenarioSelectedCount = 0, KeepOnlyWeekdays = False, threshold_count_per_batch = 1, InstrumentType = 'Futures', MarketTimeSectionTimeList = None, DebugFilepath = None):
    def __init__(self, BacktestParameterDF, AnalysisContextList, TickerFilter = [], ResultOutputFolderPath = None, PerformContangoAdjustment = True, MinimumTradeNumberCountForFullPeriod = 50, RandomNoiseTickerStdev = None, FillEveryTimeSlot = False, ActiveContractPircesTrimmedColumns = None, RapidCalibration = False, RapidCalibrationTopScenarioSelectedCount = 0, KeepOnlyWeekdays = False, threshold_count_per_batch = 1, InstrumentType = 'Futures', PreFilterDataByTime = False, MarketTimeSectionTimeList = None, DebugFilepath = None, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch'):

        self.StrategyLabel = 'RangeTradeOnSpecificPastTimeRangeStrategy'
        self.BacktestParameterDF = BacktestParameterDF
        self.loadStrategyParameters()
        # super().__init__('RangeTradeOnSpecificPastTimeRangeStrategy', BacktestParameterDF, AnalysisContextList, PreFilterDataByTime = self.PreFilterDataByTime, PreFilterDataStartTimeInStdUnit = self.PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit = self.PreFilterDataEndTimeInStdUnit, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath )
        super().__init__('RangeTradeOnSpecificPastTimeRangeStrategy', BacktestParameterDF, AnalysisContextList, MAX_TRADE_ID = BacktestRangeTradeOnSpecificPastTimeRangeStrategy.MAX_TRADE_ID, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath, BatchListDatabaseName = BatchListDatabaseName, BatchListTableName = BatchListTableName )
        
        print('self.BatchListDatabaseName = ' + self.BatchListDatabaseName)
        
        if self.LoopPerTicker:
            TickerFullList = self.AnalysisContext.FuturesData.TickerIDMapping['ticker'].tolist()
            print('TickerFullList is ' + str(TickerFullList))
            BacktestingSummaryDictAll = {}
            BacktestingTradeRecordAll = {}
            
            for ticker in TickerFullList:
                print('Loop per ticker.  Looping for ' + ticker)
                TickerFilter = [ticker]
                self.AnalysisContext = self.getAnalysisContext(False, None, None, TickerFilter, False, PerformContangoAdjustment, RandomNoiseTickerStdev, FillEveryTimeSlot, KeepOnlyWeekdays, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList , DebugFilepath = DebugFilepath)
                BacktestingSummaryDict, BacktestingTradeRecord = self.init_per_ticker_list(BacktestParameterDF, AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, threshold_count_per_batch = threshold_count_per_batch, InstrumentType = InstrumentType, PreFilterDataByTime = PreFilterDataByTime, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath)

                for key in BacktestingSummaryDict:
                    print('key is ' + str(key))
                    if key in BacktestingSummaryDictAll:
                        BacktestingSummaryDictAll[key] = pd.concat([BacktestingSummaryDictAll[key], BacktestingSummaryDict[key]])
                    else:
                        BacktestingSummaryDictAll[key] = BacktestingSummaryDict[key]
                for key in BacktestingTradeRecord:
                    if key in BacktestingTradeRecordAll:
                        BacktestingTradeRecordAll[key] = pd.concat([BacktestingTradeRecordAll[key], BacktestingTradeRecord[key]])
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

        self.FullResultOutputFolderPath = self.ResultOutputFolderPath + self.BatchGroup + '_'  + self.StrategyLabel + '_' + self.StartDate.strftime("%Y%m%d") + '_' + self.EndDate.strftime("%Y%m%d") + '_' + self.TimeFrame + '_' + str(self.StartTimeInStdUnit) + '_'+ str(self.EndTimeInStdUnit) + '_'+ str(self.TimeIntervalInStdUnit) + '_'


    def init_per_ticker_list(self, BacktestParameterDF, AnalysisContextList, TickerFilter = [], ResultOutputFolderPath = None, PerformContangoAdjustment = True, MinimumTradeNumberCountForFullPeriod = 50, RandomNoiseTickerStdev = None, FillEveryTimeSlot = False, ActiveContractPircesTrimmedColumns = None, RapidCalibration = False, RapidCalibrationTopScenarioSelectedCount = 0, KeepOnlyWeekdays = False, threshold_count_per_batch = 1, InstrumentType = 'Futures', PreFilterDataByTime = False, MarketTimeSectionTimeList = None, DebugFilepath = None):
        super().__init__('RangeTradeOnSpecificPastTimeRangeStrategy', BacktestParameterDF, AnalysisContextList, MAX_TRADE_ID = BacktestRangeTradeOnSpecificPastTimeRangeStrategy.MAX_TRADE_ID, PreFilterDataByTime = False, PreFilterDataStartTimeInStdUnit = None, PreFilterDataEndTimeInStdUnit = None, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath, BatchListDatabaseName = self.BatchListDatabaseName, BatchListTableName = self.BatchListTableName )

        BacktestingSummaryDictAll = {}
        BacktestingTradeRecordAll = {}
        
        print('In Batch ' + str(self.BatchID) + '(' + str(self.BatchSubID) + ') Start running ' + self.StrategyLabel + ' at ' + str(datetime.now()))
        print('self.MaxBackdateTimePeriodInStdUnit is ' + str(self.MaxBackdateTimePeriodInStdUnit))
        print('self.MinBackdateTimePeriodInStdUnit is ' + str(self.MinBackdateTimePeriodInStdUnit))
    
        backtest_result = RangeTradeOnSpecificPastTimeRangeStrategy(self.StrategyLabel, self.AnalysisContext, self.StartTimeInStdUnit, self.EndTimeInStdUnit, self.TimeIntervalInStdUnit, MaxBackdateTimePeriodInStdUnit = self.MaxBackdateTimePeriodInStdUnit, MinBackdateTimePeriodInStdUnit = self.MinBackdateTimePeriodInStdUnit, RangeBoundaryTimeIntervalInStdUnit = self.RangeBoundaryTimeIntervalInStdUnit, MinRangeTimeWidthInStdUnit = self.MinRangeTimeWidthInStdUnit, MinRangeWidth = self.MinRangeWidth, MaxRangeWidth = self.MaxRangeWidth, TradeEntryLevelOffset = self.TradeEntryLevelOffset, TradeStopLoss = self.TradeStopLoss, TradeTakeProfit = self.TradeTakeProfit, MaxProfitTradePerDay = self.MaxProfitTradePerDay, MaxLossTradePerDay = self.MaxLossTradePerDay, TradePeriodLength = self.TradePeriodLength, StopLossTakeProfitRelativeToRange = self.StopLossTakeProfitRelativeToRange, TradeIDSortingSegmentKeyColumnsCount = self.TradeIDSortingSegmentKeyColumnsCount, GPUMode = self.GPUMode, InitialResultCacheSize = self.InitialResultCacheSize, BatchListDatabaseName = self.BatchListDatabaseName, BatchListTableName = self.BatchListTableName )
        
        self.UpdateLastRunMaxTradeRecordSizePerSubBatch(len(backtest_result.trade_record))
        BacktestingSummaryDict, BacktestingTradeRecord = self.PrepareSummary(backtest_result, RangeTradeOnSpecificPastTimeRangeStrategy.SCENARIO_COLUMNS)

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
        self.StartTimeInStdUnit = self.BacktestParameterDF.loc[0, 'ParameterValue1']
        self.EndTimeInStdUnit = self.BacktestParameterDF.loc[0, 'ParameterValue2']
        self.TimeIntervalInStdUnit = self.BacktestParameterDF.loc[0, 'ParameterValue3']
        # self.PreFilterDataByTime = (self.BacktestParameterDF.loc[0, 'ParameterValue4'] == 1)
        self.MaxBackdateTimePeriodInStdUnit = self.BacktestParameterDF.loc[0, 'ParameterValue4']
        self.MinBackdateTimePeriodInStdUnit = self.BacktestParameterDF.loc[0, 'ParameterValue5']
        self.RangeBoundaryTimeIntervalInStdUnit = self.BacktestParameterDF.loc[0, 'ParameterValue6']
        self.MinRangeTimeWidthInStdUnit = self.BacktestParameterDF.loc[0, 'ParameterValue7']

        self.LoopPerTicker = (self.BacktestParameterDF.loc[0, 'LoopPerTicker'] == 1)
        
        threshold_string = self.BacktestParameterDF.loc[0, 'TextParameterValue1']
        self.MinRangeWidth = [int(e)/10000 if e.isdigit() else e for e in threshold_string.split(',')]
        print('self.MinRangeWidth is ' + str(self.MinRangeWidth))

        threshold_string = self.BacktestParameterDF.loc[0, 'TextParameterValue2']
        self.MaxRangeWidth = [int(e)/10000 if e.isdigit() else e for e in threshold_string.split(',')]
        print('self.MaxRangeWidth is ' + str(self.MaxRangeWidth))

        threshold_string = self.BacktestParameterDF.loc[0, 'TextParameterValue3']
        self.TradeEntryLevelOffset = [int(e)/10000 if e.lstrip("-").isdigit() else e for e in threshold_string.split(',')]
        print('self.TradeEntryLevelOffset is ' + str(self.TradeEntryLevelOffset))

        threshold_string = self.BacktestParameterDF.loc[0, 'TextParameterValue4']
        self.TradeStopLoss = [int(e)/10000 if e.isdigit() else e for e in threshold_string.split(',')]
        print('self.TradeStopLoss is ' + str(self.TradeStopLoss))

        threshold_string = self.BacktestParameterDF.loc[0, 'TextParameterValue5']
        self.TradeTakeProfit = [int(e)/10000 if e.isdigit() else e for e in threshold_string.split(',')]
        print('self.TradeTakeProfit is ' + str(self.TradeTakeProfit))

        threshold_string = self.BacktestParameterDF.loc[0, 'TextParameterValue6']
        self.MaxProfitTradePerDay = [int(e) if e.isdigit() else e for e in threshold_string.split(',')]
        print('self.MaxProfitTradePerDay is ' + str(self.MaxProfitTradePerDay))

        threshold_string = self.BacktestParameterDF.loc[0, 'TextParameterValue7']
        self.MaxLossTradePerDay = [int(e) if e.isdigit() else e for e in threshold_string.split(',')]
        print('self.MaxLossTradePerDay is ' + str(self.MaxLossTradePerDay))

        threshold_string = self.BacktestParameterDF.loc[0, 'TextParameterValue8']
        self.TradePeriodLength = [int(e) if e.isdigit() else e for e in threshold_string.split(',')]
        print('self.TradePeriodLength is ' + str(self.TradePeriodLength))

        threshold_string = self.BacktestParameterDF.loc[0, 'TextParameterValue9']
        self.StopLossTakeProfitRelativeToRange = [int(e) if e.isdigit() else e for e in threshold_string.split(',')]
        print('self.StopLossTakeProfitRelativeToRange is ' + str(self.StopLossTakeProfitRelativeToRange))
        
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
