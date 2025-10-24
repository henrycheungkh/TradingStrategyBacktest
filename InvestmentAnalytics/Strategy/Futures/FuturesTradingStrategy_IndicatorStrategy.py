# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 16:13:08 2021

@author: Henry Cheung
"""

# import pymysql
import pandas as pd
import math
from datetime import date, datetime, timedelta
import time
import InvestmentAnalytics.Config as Config
import numpy as np

from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy import FuturesStrategyBacktest
from InvestmentAnalytics.Indicator.Indicator import IndicatorLocator


class IndicatorStrategy:
    # SCENARIO_COLUMNS = ['ticker id', 'obs period', 'sharpe ratio threshold', 'exit sharpe ratio offset', 'stop loss', 'take profit', 'max holding period', 'volume to mean volume ratio', 'min return per time slot','MarketTimeSectionID']

    # scenario_column = {'indicator type':IndicatorType, 'indicator threshold':IndicatorThreshold, 'exit indicator offset':ExitIndicatorOffsetOffset, 'stop loss':StopLossPerTrade, 'take profit':TakeProfitPerTrade, 'max holding period':MaxHoldingPeriod}

    # SCENARIO_COLUMNS = ['ticker id', 'indicator type', 'indicator threshold', 'exit indicator offset', 'stop loss', 'take profit', 'max holding period', 'MarketTimeSectionID', 'indicator parameter 0', 'indicator parameter 1']
    SCENARIO_COLUMNS = ['ticker id', 'indicator type', 'indicator threshold', 'exit indicator offset', 'stop loss', 'take profit', 'max holding period', 'MarketTimeSectionID']
    TRADE_ID_SORTING_COLUMNS = ['exit time id']

# def CUDAIndicatorStrategy(close_price_matrix, indicator_matrix, IndicatorType, IndicatorThreshold = [0.5, 1, 2], ExitIndicatorOffsetOffset = [0, 0.5], date_id_matrix, time_std_unit_matrix, time_std_unit_to_market_time_section_id_matrix, StopLossPerTrade = [0, 0.0025, 0.005], TakeProfitPerTrade = [0, 0.0025, 0.005], MaxHoldingPeriod = [10], MinReturnPerTimeSlotThreshold = [0.0001], TradeFilterIndicatorName = None, TradeFilterIndicatorDataLabel = None, TradeFilterIndicatorParameterList = None, TradeFilterIndicatorThreshold = None, TradeFilterIndicator_matrix_list = None, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = 50000000, volume_matrix=None, mean_vol_by_market_time_section_id_matrix=None, VolumeToMeanVolumeRatio = None):

    def GetFullScenarioColumns(self):
    	indicator_parameter_label_list = self.Indicator.GetParameterLabelList()
    	for i in range(len(indicator_parameter_label_list)):
    		indicator_parameter_label_list[i] = 'indicator param ' + indicator_parameter_label_list[i]
    	return IndicatorStrategy.SCENARIO_COLUMNS + indicator_parameter_label_list
    	

    def __init__(self, StrategyLabel, AnalysisContext, Indicator, IndicatorType = 0, IndicatorThreshold = [0.5, 1, 2], ExitIndicatorOffset = [0, 0.5], StopLossPerTrade = [0, 0.0025, 0.005], TakeProfitPerTrade = [0, 0.0025, 0.005], MaxHoldingPeriod = [10, 20],  VolumeToMeanVolumeRatio = None, MinReturnPerTimeSlotThreshold = None, TradeFilterIndicatorName = None, TradeFilterIndicatorDataLabel = None, TradeFilterIndicatorParameter = None, TradeFilterIndicatorThreshold = None, TradeIDSortingSegmentKeyColumnsCount = 4, PreFilterDataByTime = False, GPUMode = 'CUDA', InitialResultCacheSize = 50000000):

        self.StrategyLabel = StrategyLabel
        self.AnalysisContext = AnalysisContext

        self.TradeIDSortingSegmentKeyColumnsCount = TradeIDSortingSegmentKeyColumnsCount
        self.GPUMode = GPUMode
        self.InitialResultCacheSize = InitialResultCacheSize
        
        self.Indicator = Indicator
        self.FullScenarioColumns = self.GetFullScenarioColumns()
        
        for i in range(len(Indicator.IndicatorParameterList)):
            s = Indicator.GetFullMatrixLabel(Indicator.IndicatorParameterList[i])
            df = pd.DataFrame(AnalysisContext.IntradayPricesData.DataMatrix[s].T.copy(order="C"), columns=AnalysisContext.FuturesData.TickerIDMapping['ticker'].tolist())
            print(Indicator.IndicatorLabel + '(' + str(Indicator.IndicatorParameterList[i]) + ') is')
            print(df)
            # df.to_csv(r'G:\TradeAnalysisProject\temp\\' + Indicator.IndicatorLabel.replace('|','_') + '_' + str(Indicator.IndicatorParameterList[i]) + '.csv', index=False)        
        
        self.IndicatorType = IndicatorType
        self.VolumeToMeanVolumeRatio = VolumeToMeanVolumeRatio
        self.MinReturnPerTimeSlotThreshold = MinReturnPerTimeSlotThreshold
        self.MaxHoldingPeriod = MaxHoldingPeriod
        self.IndicatorThreshold = IndicatorThreshold
        self.ExitIndicatorOffset = ExitIndicatorOffset
        self.StopLossPerTrade = StopLossPerTrade
        self.TakeProfitPerTrade = TakeProfitPerTrade
        self.TradeFilterIndicatorName = TradeFilterIndicatorName
        self.TradeFilterIndicatorDataLabel = TradeFilterIndicatorDataLabel
        self.TradeFilterIndicatorParameter = TradeFilterIndicatorParameter
        self.TradeFilterIndicatorThreshold = TradeFilterIndicatorThreshold

        TimeIDMapping_DF = self.AnalysisContext.FuturesData.TimeIDMapping
        TickerIDMapping_DF = self.AnalysisContext.FuturesData.TickerIDMapping

        # DateList = pd.pivot_table(TimeIDMapping_DF, values='time id', index=['Date'], aggfunc=len, fill_value=0).sort_values(by='Date', ascending=False).reset_index()
        # DateList['Date id'] = DateList.index
        # DateList['Dummy'] = 1

        # SortingColumns = IndicatorStrategy.SCENARIO_COLUMNS + IndicatorStrategy.TRADE_ID_SORTING_COLUMNS
        SortingColumns = self.FullScenarioColumns + IndicatorStrategy.TRADE_ID_SORTING_COLUMNS

        if GPUMode == 'CUDA':
            
            from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib import CUDATradeIDAssignment
            from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib_IndicatorStrategy import CUDAIndicatorStrategy

            # mean_vol_by_market_time_section_id_matrix = pd.pivot_table(self.AnalysisContext.IntradayPricesData.getAverageVolPerMarketTimeSection(), values='vol', index='ticker id', columns=['MarketTimeSectionID'], aggfunc=np.mean).reset_index().to_numpy().copy(order="C")
            mean_vol_by_market_time_section_id_matrix = None
            
            # TradeFilterIndicatorLevel = None
            if self.TradeFilterIndicatorName is not None:
                TradeFilterIndicator_matrix_list = []
                for parameter in self.TradeFilterIndicatorParameter:
                    IndicatorDataLabel = IndicatorLocator.GetFullMatrixLabel(self.TradeFilterIndicatorName, self.TradeFilterIndicatorDataLabel, parameter)
                    TradeFilterIndicator_matrix_list.append(self.AnalysisContext.IntradayPricesData.DataMatrix[IndicatorDataLabel])
            else:
                TradeFilterIndicator_matrix_list = None
            
# def CUDAIndicatorStrategy(close_price_matrix, indicator_matrix, indicator, IndicatorType, IndicatorThreshold = [0.5, 1, 2], ExitIndicatorOffsetOffset = [0, 0.5], date_id_matrix = np.array([0]).astype(np.float32), time_std_unit_matrix = np.array([0]).astype(np.float32), time_std_unit_to_market_time_section_id_matrix = np.array([0]).astype(np.float32), StopLossPerTrade = [0, 0.0025, 0.005], TakeProfitPerTrade = [0, 0.0025, 0.005], MaxHoldingPeriod = [10], MinReturnPerTimeSlotThreshold = [0.0001], TradeFilterIndicatorName = None, TradeFilterIndicatorDataLabel = None, TradeFilterIndicatorParameterList = None, TradeFilterIndicatorThreshold = None, TradeFilterIndicator_matrix_list = None, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = 50000000, volume_matrix=None, mean_vol_by_market_time_section_id_matrix=None, VolumeToMeanVolumeRatio = None):
            self.trade_record = CUDAIndicatorStrategy(self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_close_adj'], self.Indicator, self.IndicatorType, self.IndicatorThreshold, self.ExitIndicatorOffset, self.AnalysisContext.IntradayPricesData.DataMatrix['date id'], self.AnalysisContext.IntradayPricesData.DataMatrix['TimeInStandardUnit'], self.AnalysisContext.IntradayPricesData.DataMatrix['TimeInStandardUnitToMarketTimeSectioIDMapping'], self.StopLossPerTrade, self.TakeProfitPerTrade, MaxHoldingPeriod = self.MaxHoldingPeriod, TradeFilterIndicatorName = self.TradeFilterIndicatorName, TradeFilterIndicatorDataLabel = self.TradeFilterIndicatorDataLabel, TradeFilterIndicatorParameterList = self.TradeFilterIndicatorParameter, TradeFilterIndicatorThreshold = self.TradeFilterIndicatorThreshold, TradeFilterIndicator_matrix_list = TradeFilterIndicator_matrix_list, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = self.InitialResultCacheSize)

            # print('after CUDAIndicatorStrategy, self.trade_record is')
            # print(self.trade_record)

            self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'TimeInStandardUnit', 'MarketTimeSectionID']], left_on='entry time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'entry TimeInStandardUnit'}, inplace = False)
            # print('after merging with MarketTimeSectionID, self.trade_record is')
            # print(self.trade_record)
            self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'date id', 'TimeInStandardUnit']], left_on='exit time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'exit TimeInStandardUnit'}, inplace = False)

            from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy import StrategyBacktest
            StrategyBacktest.OrganiseTradeRecord(self, TickerIDMapping_DF, SortingColumns, IndicatorStrategy.SCENARIO_COLUMNS, self.TradeIDSortingSegmentKeyColumnsCount)
            print('after assigning trade id by CUDA at ' + str(datetime.now()))


            # self.trade_record = self.trade_record.merge(TickerIDMapping_DF, on='ticker id')

            # # average_vol_df= self.AnalysisContext.IntradayPricesData.getAverageVolPerMarketTimeSection()
            # # average_vol_df.to_csv(r'd:\temp\average_vol_df.csv')
            # # self.trade_record = self.trade_record.merge(average_vol_df, on=['MarketTimeSectionID', 'ticker id'])

            # print('trade_record after merging TimeIDMapping is with length ' + str(len(self.trade_record)) + ', max date id ' + str(self.trade_record['date id'].max()) + ' and min date id ' + str(self.trade_record['date id'].min()))
            # # print(self.trade_record)
            
            # if (len(self.trade_record) >0 ):
            #     print('before sorting, self.trade_record is')
            #     print(self.trade_record)
            #     print('before sorting for trade id assignment at ' + str(datetime.now()))
            #     self.trade_record = self.trade_record.sort_values(by=SortingColumns, ascending=False, inplace=False).reset_index().drop('index',axis='columns')
            #     print('before assigning trade id by CUDA at ' + str(datetime.now()))
            #     # trade_id = CUDATradeIDAssignment(df, self.TradeIDSortingSegmentKeyColumnsCount)
            #     # self.trade_record = pd.concat([self.trade_record, trade_id], axis=1)
                
            #     # self.trade_record = pd.concat([self.trade_record, CUDATradeIDAssignment(self.trade_record[IndicatorStrategy.SCENARIO_COLUMNS], self.TradeIDSortingSegmentKeyColumnsCount)], axis=1)
            #     self.trade_record = pd.concat([self.trade_record, CUDATradeIDAssignment(self.trade_record[self.FullScenarioColumns], self.TradeIDSortingSegmentKeyColumnsCount)], axis=1)
            #     print('after assigning trade id by CUDA at ' + str(datetime.now()))
            #     # self.trade_record.to_csv(r'd:\temp\trade record with trade id.csv', index=False)

class BacktestIndicatorStrategy(FuturesStrategyBacktest):
    PreFilterOffset = 10
    # threshold_count_per_batch = 2

    # def __init__(self, BatchGroup, BacktestBatchID, BacktestBatchSubID, AnalysisContextList, TickerFilter = [], ResultOutputFolderPath = None, PerformContangoAdjustment = True, MinimumTradeNumberCountForFullPeriod = 50, RandomNoiseTickerStdev = None, ActiveContractPircesTrimmedColumns = None, RapidCalibration = False, RapidCalibrationTopScenarioSelectedCount = 0, KeepOnlyWeekdays = False, FillEveryTimeSlot = False, threshold_count_per_batch = 1, InstrumentType = 'Futures', DebugFilepath = None):
    def __init__(self, BacktestParameterDF, AnalysisContextList, TickerFilter = [], ResultOutputFolderPath = None, PerformContangoAdjustment = True, MinimumTradeNumberCountForFullPeriod = 50, RandomNoiseTickerStdev = None, ActiveContractPircesTrimmedColumns = None, RapidCalibration = False, RapidCalibrationTopScenarioSelectedCount = 0, KeepOnlyWeekdays = False, FillEveryTimeSlot = False, threshold_count_per_batch = 1, InstrumentType = 'Futures', MarketTimeSectionTimeList = None, DebugFilepath = None, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch'):
        # self.BatchGroup = BatchGroup
        # self.BacktestBatchID = BacktestBatchID
        # self.BacktestBatchSubID = BacktestBatchSubID
        # self.loadStrategyParameters()
        # self.DebugFilepath = DebugFilepath
        # super().__init__('IndicatorStrategy', BatchGroup, BacktestBatchID, BacktestBatchSubID, AnalysisContextList,  TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType, MAX_TRADE_ID = 100000)
        super().__init__('IndicatorStrategy', BacktestParameterDF, AnalysisContextList,  TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType, MAX_TRADE_ID = 100000, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath, BatchListDatabaseName = BatchListDatabaseName, BatchListTableName = BatchListTableName)
        self.loadStrategyParameters()
        IndicatorLocator.UploadIndicatorToAnalysisContext(self.AnalysisContext, self.TradeFilterIndicatorName, self.TradeFilterIndicatorDataLabel, self.TradeFilterIndicatorParameter, self.IndicatorTimeFrame)
        

        # self.PrepareFilterIndicatorParameters(self.AnalysisContext, self.ParameterValues)
        self.BacktestingSummaryDictAll = {}
        self.BacktestingTradeRecordAll = {}

        # self.backtest_result = SharpeRatioStrategy('SharpeRatioStrategy', self.AnalysisContext, self.StopLossTakeProfitList, self.StopLossTakeProfitList, self.MaxHoldingPeriod, self.ObsPeriod, self.VolumeToMeanVolumeRatio, self.MinReturnPerTimeSlotThreshold, self.SharpeRatioThreshold, self.ExitSharpeRatioOffset, self.UseMidOfHighLow, TradeIDSortingSegmentKeyColumnsCount = self.TradeIDSortingSegmentKeyColumnsCount, GPUMode = self.GPUMode)

        # for StopLossPerTrade in FuturesStrategyBacktest.getListOfList(self.StopLossTakeProfitList, 1):
        #     for TakeProfitPerTrade in FuturesStrategyBacktest.getListOfList(self.StopLossTakeProfitList, 1):
                
        StopLossPerTrade = self.StopLossTakeProfitList
        TakeProfitPerTrade = self.StopLossTakeProfitList
                
        for Indicator_Parameter in FuturesStrategyBacktest.getListOfList(self.IndicatorParameter, self.ParameterTrialCountPerLoop[0]):
            for Indicator_Threshold in FuturesStrategyBacktest.getListOfList(self.IndicatorThreshold, self.ParameterTrialCountPerLoop[1]):
                for exit_indicator_offset in FuturesStrategyBacktest.getListOfList(self.ExitIndicatorOffset, self.ParameterTrialCountPerLoop[2]):
                
                    for max_holding_period in FuturesStrategyBacktest.getListOfList(self.MaxHoldingPeriod, self.ParameterTrialCountPerLoop[3]):
                                        
                        # print('StopLossPerTrade is ' + str(StopLossPerTrade) + ' and self.ParameterTrialCountPerLoop[0] is ' + str(self.ParameterTrialCountPerLoop[0]))

                        # self.backtest_result = SharpeRatioStrategy('SharpeRatioStrategy', self.AnalysisContext, StopLossPerTrade, TakeProfitPerTrade, max_holding_period, obs_period, volume_to_mean_volume_ratio, min_return_per_time_slot_threshold, sharpe_ratio_threshold, exit_sharpe_ratio_offset, self.UseMidOfHighLow, TradeFilterIndicatorName = self.TradeFilterIndicatorName, TradeFilterIndicatorDataLabel = self.TradeFilterIndicatorDataLabel, TradeFilterIndicatorParameter = self.TradeFilterIndicatorParameter, TradeFilterIndicatorThreshold = self.TradeFilterIndicatorThreshold, TradeIDSortingSegmentKeyColumnsCount = self.TradeIDSortingSegmentKeyColumnsCount, GPUMode = self.GPUMode)
                        # self.PrepareSummary(SharpeRatioStrategy.SCENARIO_COLUMNS)

    # def __init__(self, StrategyLabel, AnalysisContext, Indicator, IndicatorType = 0, IndicatorThreshold = [0.5, 1, 2], ExitIndicatorOffset = [0, 0.5], StopLossPerTrade = [0, 0.0025, 0.005], TakeProfitPerTrade = [0, 0.0025, 0.005], MaxHoldingPeriod = [10, 20],  VolumeToMeanVolumeRatio = None, MinReturnPerTimeSlotThreshold = None, TradeFilterIndicatorName = None, TradeFilterIndicatorDataLabel = None, TradeFilterIndicatorParameter = None, TradeFilterIndicatorThreshold = None, TradeIDSortingSegmentKeyColumnsCount = 4, PreFilterDataByTime = False, GPUMode = 'CUDA', InitialResultCacheSize = 50000000):

                        
                        self.backtest_result = IndicatorStrategy('IndicatorStrategy', self.AnalysisContext, self.Indicator, self.IndicatorType, self.IndicatorThreshold, self.ExitIndicatorOffset, StopLossPerTrade, TakeProfitPerTrade, max_holding_period, TradeFilterIndicatorName = self.TradeFilterIndicatorName, TradeFilterIndicatorDataLabel = self.TradeFilterIndicatorDataLabel, TradeFilterIndicatorParameter = self.TradeFilterIndicatorParameter, TradeFilterIndicatorThreshold = self.TradeFilterIndicatorThreshold, TradeIDSortingSegmentKeyColumnsCount = self.TradeIDSortingSegmentKeyColumnsCount, GPUMode = self.GPUMode)

                        # self.PrepareSummary(IndicatorStrategy.SCENARIO_COLUMNS)
                        self.PrepareSummary(self.backtest_result.FullScenarioColumns)

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
            
        # print('self.BacktestingSummaryDict is')
        # print(self.BacktestingSummaryDict)

        # print('In BacktestSharpeRatioStrategy.init, self.backtest_result.trade_record is')
        # print(self.backtest_result.trade_record)
        # if self.UseMidOfHighLow:
        #     s = '_MidOfHighLow'
        # else:
        #     s = ''
        # self.FullResultOutputFolderPath = self.ResultOutputFolderPath + self.StrategyLabel + '_' + self.InstrumentType + s + '_' + self.StartDate.strftime("%Y%m%d") + '_' + self.EndDate.strftime("%Y%m%d") + '_' + self.TimeFrame + '_' + str(self.BacktestBatchID) + '_'
        self.FullResultOutputFolderPath = self.ResultOutputFolderPath + self.StrategyLabel + '_' + self.Indicator.IndicatorLabel.replace("|", "_") + '_' + self.InstrumentType + '_' + self.StartDate.strftime("%Y%m%d") + '_' + self.EndDate.strftime("%Y%m%d") + '_' + self.TimeFrame + '_'
        # print('self.FullResultOutputFolderPath is ' + self.FullResultOutputFolderPath)
        # self.PrepareSummary(SharpeRatioStrategy.SCENARIO_COLUMNS)

    def loadStrategyParameters(self):

        parameter_string = self.BacktestParameterDF.loc[0, 'StopLossTakeProfitBps']
        self.StopLossTakeProfitList = [int(e)/10000 for e in parameter_string.split(',')]
        print('self.StopLossTakeProfitList is ' + str(self.StopLossTakeProfitList))

        self.IndicatorType = self.BacktestParameterDF.loc[0, 'ParameterValue1']

        self.IndicatorName = self.BacktestParameterDF.loc[0, 'TextParameterValue1']

        self.IndicatorDataLabel = self.BacktestParameterDF.loc[0, 'TextParameterValue2']
        print('self.IndicatorDataLabel is ' + str(self.IndicatorDataLabel))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue3']
        self.IndicatorParameter = IndicatorLocator.ParameterStringToListOfList(parameter_string)
        print('self.IndicatorParameter is ' + str(self.IndicatorParameter))

        self.IndicatorTimeFrame = self.BacktestParameterDF.loc[0, 'TextParameterValue7']
        # self.PriceTimeFrame = self.AnalysisContext.TimeFrame

        self.Indicator = IndicatorLocator.GetIndicator(self.AnalysisContext, self.IndicatorName, self.IndicatorDataLabel, self.IndicatorParameter, self.IndicatorTimeFrame, self.AnalysisContext.TimeFrame)
        self.Indicator.UploadIndicatorToAnalysisContext(self.AnalysisContext)
        # self.Indicator = IndicatorLocator.GetFilterIndicator(self.AnalysisContext, self.StrategyLabel, self.BatchGroup, self.BacktestBatchID, self.BacktestBatchSubID)
        DebugFilepath = self.DebugFilepath
        # self.DebugFilepath = r'D:\\temp\\'
        if self.DebugFilepath is not None:
            for i in range(len(self.Indicator.IndicatorParameterList)):
                s = self.Indicator.GetFullMatrixLabel(self.Indicator.IndicatorParameterList[i])
                print('before error, i = ' + str(i) + ' and s = ' + s)
                m  = self.AnalysisContext.IntradayPricesData.DataMatrix[s].T.copy(order="C")
                print('dimension of self.AnalysisContext.IntradayPricesData.DataMatrix[s].T.copy is ' + str(len(m)) + ' x ' + str(len(m[0])))
                
                df = pd.DataFrame(m, columns=self.AnalysisContext.FuturesData.TickerIDMapping['ticker'].tolist())
            
                # print(indicator.IndicatorLabel + '(' + str(MA_Day_List[i]) + ') is')
                print(self.Indicator.IndicatorLabel + '(' + str(self.Indicator.IndicatorParameterList[i]) + ') is')
            
                print(df)
                df.to_csv(self.DebugFilepath + self.Indicator.IndicatorLabel.replace('|','_') + '_' + str(self.Indicator.IndicatorParameterList[i]) + '.csv', index=False)
            
        # self.DebugFilepath = DebugFilepath

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue4']
        if (self.IndicatorType == 0):
            self.IndicatorThreshold = [float(e) for e in parameter_string.split(',')]
        elif (self.IndicatorType == 1):
            self.IndicatorThreshold = [int(e)/10000 for e in parameter_string.split(',')]
        print('self.IndicatorThreshold is ' + str(self.IndicatorThreshold))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue5']
        if (self.IndicatorType == 0):
            self.ExitIndicatorOffset = [float(e) for e in parameter_string.split(',')]
        elif (self.IndicatorType == 1):
            self.ExitIndicatorOffset = [int(e)/10000 for e in parameter_string.split(',')]
        print('self.ExitIndicatorOffset is ' + str(self.ExitIndicatorOffset))

        parameter_string = self.BacktestParameterDF.loc[0, 'TextParameterValue6']
        self.MaxHoldingPeriod = [int(e) if e.isdigit() else e for e in parameter_string.split(',')]
        print('self.MaxHoldingPeriod is ' + str(self.MaxHoldingPeriod))



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
                
                