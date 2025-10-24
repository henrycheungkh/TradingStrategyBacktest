# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 16:13:08 2021

@author: Henry Cheung
"""

import pymysql
import pandas as pd
import math
from datetime import date, datetime, timedelta
import time
import InvestmentAnalytics.Config as Config
import numpy as np

from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy import FuturesStrategyBacktest

class SharpeRatioStrategy:
    SCENARIO_COLUMNS = ['ticker id', 'obs period', 'sharpe ratio threshold', 'exit sharpe ratio offset', 'stop loss', 'take profit', 'max holding period', 'volume to mean volume ratio', 'min return per time slot','MarketTimeSectionID']
    TRADE_ID_SORTING_COLUMNS = ['exit time id']

    def __init__(self, StrategyLabel, AnalysisContext, StopLossPerTrade = [0, 0.0025, 0.005], TakeProfitPerTrade = [0, 0.0025, 0.005], MaxHoldingPeriod = [10, 20], ObsPeriod = [5, 10], VolumeToMeanVolumeRatio = [3], MinReturnPerTimeSlotThreshold = [0.0001], SharpeRatioThreshold = [0.5, 1, 2], ExitSharpeRatioOffset = [0, 0.5], time_in_std_unit_per_day = 24*60, UseMidOfHighLow = False, TradeFilterIndicatorName = None, TradeFilterIndicatorDataLabel = None, TradeFilterIndicatorParameter = None, TradeFilterIndicatorThreshold = None, TradeIDSortingSegmentKeyColumnsCount = 4, PreFilterDataByTime = False, GPUMode = 'CUDA', InitialResultCacheSize = 50000000):

        self.StrategyLabel = StrategyLabel
        self.AnalysisContext = AnalysisContext

        self.TradeIDSortingSegmentKeyColumnsCount = TradeIDSortingSegmentKeyColumnsCount
        self.GPUMode = GPUMode
        self.InitialResultCacheSize = InitialResultCacheSize
        
        self.ObsPeriod = ObsPeriod
        self.VolumeToMeanVolumeRatio = VolumeToMeanVolumeRatio
        self.MinReturnPerTimeSlotThreshold = MinReturnPerTimeSlotThreshold
        self.MaxHoldingPeriod = MaxHoldingPeriod
        self.SharpeRatioThreshold = SharpeRatioThreshold
        self.ExitSharpeRatioOffset = ExitSharpeRatioOffset
        self.time_in_std_unit_per_day = time_in_std_unit_per_day
        self.StopLossPerTrade = StopLossPerTrade
        self.TakeProfitPerTrade = TakeProfitPerTrade
        self.UseMidOfHighLow = UseMidOfHighLow
        self.TradeFilterIndicatorName = TradeFilterIndicatorName
        self.TradeFilterIndicatorDataLabel = TradeFilterIndicatorDataLabel
        self.TradeFilterIndicatorParameter = TradeFilterIndicatorParameter
        self.TradeFilterIndicatorThreshold = TradeFilterIndicatorThreshold

        TimeIDMapping_DF = self.AnalysisContext.FuturesData.TimeIDMapping
        TickerIDMapping_DF = self.AnalysisContext.FuturesData.TickerIDMapping

        # DateList = pd.pivot_table(TimeIDMapping_DF, values='time id', index=['Date'], aggfunc=len, fill_value=0).sort_values(by='Date', ascending=False).reset_index()
        # DateList['Date id'] = DateList.index
        # DateList['Dummy'] = 1

        SortingColumns = SharpeRatioStrategy.SCENARIO_COLUMNS + SharpeRatioStrategy.TRADE_ID_SORTING_COLUMNS

        if GPUMode == 'CUDA':
            
            from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib import CUDATradeIDAssignment
            from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib_SharpeRatioStrategy import CUDASharpeRatioStrategy

            mean_vol_by_market_time_section_id_matrix = pd.pivot_table(self.AnalysisContext.IntradayPricesData.getAverageVolPerMarketTimeSection(), values='vol', index='ticker id', columns=['MarketTimeSectionID'], aggfunc=np.mean).reset_index().to_numpy().copy(order="C")
            # mean_vol_by_market_time_section_id_df = pd.pivot_table(self.AnalysisContext.IntradayPricesData.getAverageVolPerMarketTimeSection(), values='vol', index='ticker id', columns=['MarketTimeSectionID'], aggfunc=np.mean).reset_index()
            # mean_vol_by_market_time_section_id_matrix = mean_vol_by_market_time_section_id_df.to_numpy().copy(order="C")
            # mean_vol_by_market_time_section_id_df.to_csv(r'E:\TradeAnalysisProject\RoutineAnalysis\SharpeRatioStrategy\Debug\mean_vol_by_market_time_section_id_matrix_df.csv', index=False)
            
            # TradeFilterIndicatorLevel = None
            if self.TradeFilterIndicatorName is not None:
                TradeFilterIndicator_matrix_list = []
                for parameter in self.TradeFilterIndicatorParameter:
                    IndicatorDataLabel = IndicatorLocator.GetFullMatrixLabel(self.TradeFilterIndicatorName, self.TradeFilterIndicatorDataLabel, parameter)
                    TradeFilterIndicator_matrix_list.append(self.AnalysisContext.IntradayPricesData.DataMatrix[IndicatorDataLabel])
            else:
                TradeFilterIndicator_matrix_list = None
                
            # time_in_std_unit_per_day = 24*60
            
            if self.UseMidOfHighLow:
                self.trade_record = CUDASharpeRatioStrategy(np.mean( np.array([ self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_high_adj'], self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_low_adj'] ]), axis=0 ), self.AnalysisContext.IntradayPricesData.DataMatrix['vol'], self.AnalysisContext.IntradayPricesData.DataMatrix['date id'], self.AnalysisContext.IntradayPricesData.DataMatrix['TimeInStandardUnit'], self.AnalysisContext.IntradayPricesData.DataMatrix['TimeInStandardUnitToMarketTimeSectioIDMapping'], mean_vol_by_market_time_section_id_matrix, self.StopLossPerTrade, self.TakeProfitPerTrade, self.MaxHoldingPeriod, self.VolumeToMeanVolumeRatio, self.MinReturnPerTimeSlotThreshold, self.ObsPeriod, self.SharpeRatioThreshold, self.ExitSharpeRatioOffset, time_in_std_unit_per_day = self.time_in_std_unit_per_day, TradeFilterIndicatorName = self.TradeFilterIndicatorName, TradeFilterIndicatorDataLabel = self.TradeFilterIndicatorDataLabel, TradeFilterIndicatorParameterList = self.TradeFilterIndicatorParameter, TradeFilterIndicatorThreshold = self.TradeFilterIndicatorThreshold, TradeFilterIndicator_matrix_list = TradeFilterIndicator_matrix_list, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = self.InitialResultCacheSize )
            else:
                # close_price_matrix = self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_close_adj'].T.copy(order="C")
                # df = pd.DataFrame(data=close_price_matrix, columns=['ticker 0', 'ticker 1'])
                # df.to_csv(r'E:\TradeAnalysisProject\RoutineAnalysis\SharpeRatioStrategy\Debug\close_price_matrix_in_SharpeRatioStrategy.csv', index=False)
                
                self.trade_record = CUDASharpeRatioStrategy(self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_close_adj'], self.AnalysisContext.IntradayPricesData.DataMatrix['vol'], self.AnalysisContext.IntradayPricesData.DataMatrix['date id'], self.AnalysisContext.IntradayPricesData.DataMatrix['TimeInStandardUnit'], self.AnalysisContext.IntradayPricesData.DataMatrix['TimeInStandardUnitToMarketTimeSectioIDMapping'], mean_vol_by_market_time_section_id_matrix, self.StopLossPerTrade, self.TakeProfitPerTrade, self.MaxHoldingPeriod, self.VolumeToMeanVolumeRatio, self.MinReturnPerTimeSlotThreshold, self.ObsPeriod, self.SharpeRatioThreshold, self.ExitSharpeRatioOffset, time_in_std_unit_per_day = self.time_in_std_unit_per_day, TradeFilterIndicatorName = self.TradeFilterIndicatorName, TradeFilterIndicatorDataLabel = self.TradeFilterIndicatorDataLabel, TradeFilterIndicatorParameterList = self.TradeFilterIndicatorParameter, TradeFilterIndicatorThreshold = self.TradeFilterIndicatorThreshold, TradeFilterIndicator_matrix_list = TradeFilterIndicator_matrix_list, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = self.InitialResultCacheSize)

            # self.trade_record = self.trade_record.merge(TickerIDMapping_DF, on='ticker id')
            self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'TimeInStandardUnit', 'MarketTimeSectionID']], left_on='entry time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'entry TimeInStandardUnit'}, inplace = False)
            self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'date id', 'TimeInStandardUnit']], left_on='exit time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'exit TimeInStandardUnit'}, inplace = False)

            average_vol_df= self.AnalysisContext.IntradayPricesData.getAverageVolPerMarketTimeSection()
            # average_vol_df.to_csv(r'd:\temp\average_vol_df.csv')
            self.trade_record = self.trade_record.merge(average_vol_df, on=['MarketTimeSectionID', 'ticker id'])

            print('trade_record after merging TimeIDMapping is with length ' + str(len(self.trade_record)) + ', max date id ' + str(self.trade_record['date id'].max()) + ' and min date id ' + str(self.trade_record['date id'].min()))
            # print(self.trade_record)

            from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy import StrategyBacktest

            StrategyBacktest.OrganiseTradeRecord(self, TickerIDMapping_DF, SortingColumns, SharpeRatioStrategy.SCENARIO_COLUMNS, self.TradeIDSortingSegmentKeyColumnsCount)
            print('after assigning trade id by CUDA at ' + str(datetime.now()))

            
            # if (len(self.trade_record) >0 ):
            #     print('before sorting for trade id assignment at ' + str(datetime.now()))
            #     self.trade_record = self.trade_record.sort_values(by=SortingColumns, ascending=False, inplace=False).reset_index().drop('index',axis='columns')
            #     print('before assigning trade id by CUDA at ' + str(datetime.now()))
            #     # trade_id = CUDATradeIDAssignment(df, self.TradeIDSortingSegmentKeyColumnsCount)
            #     # self.trade_record = pd.concat([self.trade_record, trade_id], axis=1)
            #     self.trade_record = pd.concat([self.trade_record, CUDATradeIDAssignment(self.trade_record[SharpeRatioStrategy.SCENARIO_COLUMNS], self.TradeIDSortingSegmentKeyColumnsCount)], axis=1)
            #     print('after assigning trade id by CUDA at ' + str(datetime.now()))
            #     # self.trade_record.to_csv(r'd:\temp\trade record with trade id.csv', index=False)

class BacktestSharpeRatioStrategy(FuturesStrategyBacktest):
    PreFilterOffset = 10
    # threshold_count_per_batch = 2

    # def __init__(self, BatchGroup, BacktestBatchID, BacktestBatchSubID, AnalysisContextList, TickerFilter = [], ResultOutputFolderPath = None, PerformContangoAdjustment = True, MinimumTradeNumberCountForFullPeriod = 50, RandomNoiseTickerStdev = None, ActiveContractPircesTrimmedColumns = None, RapidCalibration = False, RapidCalibrationTopScenarioSelectedCount = 0, KeepOnlyWeekdays = False, FillEveryTimeSlot = False, threshold_count_per_batch = 1, InstrumentType = 'Futures', MarketTimeSectionTimeList = None, DebugFilepath = None, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch'):
    def __init__(self, BacktestParameterDF, AnalysisContextList, TickerFilter = [], ResultOutputFolderPath = None, PerformContangoAdjustment = True, MinimumTradeNumberCountForFullPeriod = 50, RandomNoiseTickerStdev = None, ActiveContractPircesTrimmedColumns = None, RapidCalibration = False, RapidCalibrationTopScenarioSelectedCount = 0, KeepOnlyWeekdays = False, FillEveryTimeSlot = False, threshold_count_per_batch = 1, InstrumentType = 'Futures', MarketTimeSectionTimeList = None, DebugFilepath = None, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch'):
        # self.BatchGroup = BatchGroup
        # self.BacktestBatchID = BacktestBatchID
        # self.BacktestBatchSubID = BacktestBatchSubID
        # self.loadStrategyParameters()
        # super().__init__('SharpeRatioStrategy', BatchGroup, BacktestBatchID, BacktestBatchSubID, AnalysisContextList,  TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType, MAX_TRADE_ID = 100000, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath, BatchListDatabaseName = BatchListDatabaseName, BatchListTableName = BatchListTableName)
        super().__init__('SharpeRatioStrategy', BacktestParameterDF, AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType, MAX_TRADE_ID = 100000, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath, BatchListDatabaseName = BatchListDatabaseName, BatchListTableName = BatchListTableName)
        self.loadStrategyParameters()
        if self.TimeFrame == '10 secs':
            self.time_in_std_unit_per_day = 24*60*6
        else:
            self.time_in_std_unit_per_day = 24*60
            

        # self.PrepareFilterIndicatorParameters(self.AnalysisContext, self.ParameterValues)
        self.BacktestingSummaryDictAll = {}
        self.BacktestingTradeRecordAll = {}

        # self.backtest_result = SharpeRatioStrategy('SharpeRatioStrategy', self.AnalysisContext, self.StopLossTakeProfitList, self.StopLossTakeProfitList, self.MaxHoldingPeriod, self.ObsPeriod, self.VolumeToMeanVolumeRatio, self.MinReturnPerTimeSlotThreshold, self.SharpeRatioThreshold, self.ExitSharpeRatioOffset, self.UseMidOfHighLow, TradeIDSortingSegmentKeyColumnsCount = self.TradeIDSortingSegmentKeyColumnsCount, GPUMode = self.GPUMode)

        for StopLossPerTrade in FuturesStrategyBacktest.getListOfList(self.StopLossTakeProfitList, self.ParameterTrialCountPerLoop[0]):
            for TakeProfitPerTrade in FuturesStrategyBacktest.getListOfList(self.StopLossTakeProfitList, self.ParameterTrialCountPerLoop[1]):
                for max_holding_period in FuturesStrategyBacktest.getListOfList(self.MaxHoldingPeriod, self.ParameterTrialCountPerLoop[2]):
                    for obs_period in FuturesStrategyBacktest.getListOfList(self.ObsPeriod, self.ParameterTrialCountPerLoop[3]):
                        for volume_to_mean_volume_ratio in FuturesStrategyBacktest.getListOfList(self.VolumeToMeanVolumeRatio, self.ParameterTrialCountPerLoop[4]):
                            for min_return_per_time_slot_threshold in FuturesStrategyBacktest.getListOfList(self.MinReturnPerTimeSlotThreshold, self.ParameterTrialCountPerLoop[5]):
                                for sharpe_ratio_threshold in FuturesStrategyBacktest.getListOfList(self.SharpeRatioThreshold, self.ParameterTrialCountPerLoop[6]):
                                    for exit_sharpe_ratio_offset in FuturesStrategyBacktest.getListOfList(self.ExitSharpeRatioOffset, self.ParameterTrialCountPerLoop[6]):
                                        
                                        print('StopLossPerTrade is ' + str(StopLossPerTrade) + ' and self.ParameterTrialCountPerLoop[0] is ' + str(self.ParameterTrialCountPerLoop[0]))
            
                                        # close_price_matrix = self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_close_adj'].T.copy(order="C")
                                        # df = pd.DataFrame(data=close_price_matrix, columns=['ticker 0', 'ticker 1'])
                                        # df.to_csv(r'E:\TradeAnalysisProject\RoutineAnalysis\SharpeRatioStrategy\Debug\close_price_matrix_in_BacktestSharpeRatioStrategy.csv', index=False)

                                        self.backtest_result = SharpeRatioStrategy('SharpeRatioStrategy', self.AnalysisContext, StopLossPerTrade, TakeProfitPerTrade, max_holding_period, obs_period, volume_to_mean_volume_ratio, min_return_per_time_slot_threshold, sharpe_ratio_threshold, exit_sharpe_ratio_offset, self.time_in_std_unit_per_day, self.UseMidOfHighLow, TradeFilterIndicatorName = self.TradeFilterIndicatorName, TradeFilterIndicatorDataLabel = self.TradeFilterIndicatorDataLabel, TradeFilterIndicatorParameter = self.TradeFilterIndicatorParameter, TradeFilterIndicatorThreshold = self.TradeFilterIndicatorThreshold, TradeIDSortingSegmentKeyColumnsCount = self.TradeIDSortingSegmentKeyColumnsCount, GPUMode = self.GPUMode, InitialResultCacheSize = self.InitialResultCacheSize)
                                        self.UpdateLastRunMaxTradeRecordSizePerSubBatch(len(self.backtest_result.trade_record))
                                        self.PrepareSummary(SharpeRatioStrategy.SCENARIO_COLUMNS)

                                        for key in self.BacktestingSummaryDict:
                                            if key in self.BacktestingSummaryDictAll:
                                                self.BacktestingSummaryDictAll[key] = self.BacktestingSummaryDictAll[key].append(self.BacktestingSummaryDict[key])
                                            else:
                                                self.BacktestingSummaryDictAll[key] = self.BacktestingSummaryDict[key]
                                        for key in self.BacktestingTradeRecord:
                                            if key in self.BacktestingTradeRecordAll:
                                                self.BacktestingTradeRecordAll[key] = self.BacktestingTradeRecordAll[key].append(self.BacktestingTradeRecord[key])
                                            else:
                                                self.BacktestingTradeRecordAll[key] = self.BacktestingTradeRecord[key]
                
        self.BacktestingSummaryDict = self.BacktestingSummaryDictAll
        self.BacktestingTradeRecord = self.BacktestingTradeRecordAll
        for key in self.BacktestingSummaryDict:
            self.BacktestingSummaryDict[key]['Abs Sharpe Ratio after commission'] = self.BacktestingSummaryDict[key]['Sharpe Ratio after commission'].abs()
            self.BacktestingSummaryDict[key] = self.BacktestingSummaryDict[key].sort_values(by='Abs Sharpe Ratio after commission', ascending=False).drop(['Abs Sharpe Ratio after commission'],axis='columns')

        # print('In BacktestSharpeRatioStrategy.init, self.backtest_result.trade_record is')
        # print(self.backtest_result.trade_record)
        if self.UseMidOfHighLow:
            s = '_MidOfHighLow'
        else:
            s = ''
        # self.FullResultOutputFolderPath = self.ResultOutputFolderPath + self.StrategyLabel + '_' + self.InstrumentType + s + '_' + self.StartDate.strftime("%Y%m%d") + '_' + self.EndDate.strftime("%Y%m%d") + '_' + self.TimeFrame + '_' + str(self.BacktestBatchID) + '_'
        # self.FullResultOutputFolderPath = self.ResultOutputFolderPath + self.StrategyLabel + '_' + self.InstrumentType + s + '_' + self.StartDate.strftime("%Y%m%d") + '_' + self.EndDate.strftime("%Y%m%d") + '_' + self.TimeFrame + '_'
        self.FullResultOutputFolderPath = self.ResultOutputFolderPath + self.BatchGroup + '_'  + self.StrategyLabel + '_' + self.InstrumentType + s + '_' + self.StartDate.strftime("%Y%m%d") + '_' + self.EndDate.strftime("%Y%m%d") + '_' + self.TimeFrame + '_'
        # print('self.FullResultOutputFolderPath is ' + self.FullResultOutputFolderPath)
        # self.PrepareSummary(SharpeRatioStrategy.SCENARIO_COLUMNS)

    def loadStrategyParameters(self):

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue1']
        self.StopLossTakeProfitList = [int(e)/10000 for e in parameter_string.split(',')]
        print('self.StopLossTakeProfitList is ' + str(self.StopLossTakeProfitList))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue2']
        self.MaxHoldingPeriod = [int(e) if e.isdigit() else e for e in parameter_string.split(',')]
        print('self.MaxHoldingPeriod is ' + str(self.MaxHoldingPeriod))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue3']
        self.VolumeToMeanVolumeRatio = [float(e) for e in parameter_string.split(',')]
        print('self.VolumeToMeanVolumeRatio is ' + str(self.VolumeToMeanVolumeRatio))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue4']
        self.MinReturnPerTimeSlotThreshold = [int(e)/10000 for e in parameter_string.split(',')]
        print('self.MinReturnPerTimeSlotThreshold is ' + str(self.MinReturnPerTimeSlotThreshold))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue5']
        self.ObsPeriod = [int(e) if e.isdigit() else e for e in parameter_string.split(',')]
        print('self.ObsPeriod is ' + str(self.ObsPeriod))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue6']
        self.SharpeRatioThreshold = [float(e) for e in parameter_string.split(',')]
        print('self.SharpeRatioThreshold is ' + str(self.SharpeRatioThreshold))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue7']
        self.ExitSharpeRatioOffset = [float(e) for e in parameter_string.split(',')]
        print('self.ExitSharpeRatioOffset is ' + str(self.ExitSharpeRatioOffset))
        
        self.UseMidOfHighLow = (self.BacktestParameterDF.loc[0, 'ParameterValue1'] == 1)

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