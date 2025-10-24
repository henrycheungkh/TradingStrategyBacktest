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
from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib import CUDATradeIDAssignment
from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib_SharpeRatioStrategy import CUDASharpeRatioStrategy
from InvestmentAnalytics.CUDA.CUDADataFrameUtil import CUDAMapByLookup

class BreakOutStrategy:
    SCENARIO_COLUMNS = ['ticker id', 'obs period', 'sharpe ratio threshold', 'exit sharpe ratio offset', 'stop loss', 'take profit', 'max holding period', 'volume to mean volume ratio', 'min return per time slot','MarketTimeSectionID']
    TRADE_ID_SORTING_COLUMNS = ['exit time id']

    # def __init__(self, StrategyLabel, AnalysisContext, StopLossPerTrade = [0, 0.0025, 0.005], TakeProfitPerTrade = [0, 0.0025, 0.005], MaxHoldingPeriod = [10, 20], ObsPeriod = [5, 10], VolumeToMeanVolumeRatio = [3], MinReturnPerTimeSlotThreshold = [0.0001], SharpeRatioThreshold = [0.5, 1, 2], ExitSharpeRatioOffset = [0, 0.5], TradeIDSortingSegmentKeyColumnsCount = 2, PreFilterDataByTime = False, GPUMode = True):
    def __init__(self, StrategyLabel, AnalysisContext, StopLossPerTrade = [0, 0.0025, 0.005], TakeProfitPerTrade = [0, 0.0025, 0.005], MaxHoldingPeriod = [10, 20], ObsPeriod = [5, 10], VolumeToMeanVolumeRatio = [3], MinReturnPerTimeSlotThreshold = [0.0001], SharpeRatioThreshold = [0.5, 1, 2], ExitSharpeRatioOffset = [0, 0.5], UseMidOfHighLow = False, TradeIDSortingSegmentKeyColumnsCount = 3, PreFilterDataByTime = False, GPUMode = True):

        self.StrategyLabel = StrategyLabel
        self.AnalysisContext = AnalysisContext

        self.TradeIDSortingSegmentKeyColumnsCount = TradeIDSortingSegmentKeyColumnsCount
        self.GPUMode = GPUMode
        self.ObsPeriod = ObsPeriod
        self.VolumeToMeanVolumeRatio = VolumeToMeanVolumeRatio
        self.MinReturnPerTimeSlotThreshold = MinReturnPerTimeSlotThreshold
        self.MaxHoldingPeriod = MaxHoldingPeriod
        self.SharpeRatioThreshold = SharpeRatioThreshold
        self.ExitSharpeRatioOffset = ExitSharpeRatioOffset
        self.StopLossPerTrade = StopLossPerTrade
        self.TakeProfitPerTrade = TakeProfitPerTrade
        self.UseMidOfHighLow = UseMidOfHighLow

        TimeIDMapping_DF = self.AnalysisContext.FuturesData.TimeIDMapping
        TickerIDMapping_DF = self.AnalysisContext.FuturesData.TickerIDMapping

        # DateList = pd.pivot_table(TimeIDMapping_DF, values='time id', index=['Date'], aggfunc=len, fill_value=0).sort_values(by='Date', ascending=False).reset_index()
        # DateList['Date id'] = DateList.index
        # DateList['Dummy'] = 1

        SortingColumns = SharpeRatioStrategy.SCENARIO_COLUMNS + SharpeRatioStrategy.TRADE_ID_SORTING_COLUMNS

        if GPUMode:
            
            mean_vol_by_market_time_section_id_matrix = pd.pivot_table(self.AnalysisContext.IntradayPricesData.getAverageVolPerMarketTimeSection(), values='vol', index='ticker id', columns=['MarketTimeSectionID'], aggfunc=np.mean).reset_index().to_numpy().copy(order="C")
            
            if self.UseMidOfHighLow:
                self.trade_record = CUDASharpeRatioStrategy(np.mean( np.array([ self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_high_adj'], self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_low_adj'] ]), axis=0 ), self.AnalysisContext.IntradayPricesData.DataMatrix['vol'], self.AnalysisContext.IntradayPricesData.DataMatrix['date id'], self.AnalysisContext.IntradayPricesData.DataMatrix['TimeInStandardUnit'], self.AnalysisContext.IntradayPricesData.DataMatrix['TimeInStandardUnitToMarketTimeSectioIDMapping'], mean_vol_by_market_time_section_id_matrix, self.StopLossPerTrade, self.TakeProfitPerTrade, self.MaxHoldingPeriod, self.VolumeToMeanVolumeRatio, self.MinReturnPerTimeSlotThreshold, self.ObsPeriod, self.SharpeRatioThreshold, self.ExitSharpeRatioOffset, block_cutting_dimension = "Time Dimension")
            else:
                self.trade_record = CUDASharpeRatioStrategy(self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_close_adj'], self.AnalysisContext.IntradayPricesData.DataMatrix['vol'], self.AnalysisContext.IntradayPricesData.DataMatrix['date id'], self.AnalysisContext.IntradayPricesData.DataMatrix['TimeInStandardUnit'], self.AnalysisContext.IntradayPricesData.DataMatrix['TimeInStandardUnitToMarketTimeSectioIDMapping'], mean_vol_by_market_time_section_id_matrix, self.StopLossPerTrade, self.TakeProfitPerTrade, self.MaxHoldingPeriod, self.VolumeToMeanVolumeRatio, self.MinReturnPerTimeSlotThreshold, self.ObsPeriod, self.SharpeRatioThreshold, self.ExitSharpeRatioOffset, block_cutting_dimension = "Time Dimension")

            self.trade_record = self.trade_record.merge(TickerIDMapping_DF, on='ticker id')
            self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'TimeInStandardUnit', 'MarketTimeSectionID']], left_on='entry time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'entry TimeInStandardUnit'}, inplace = False)
            self.trade_record = self.trade_record.merge(TimeIDMapping_DF[['time id', 'date id', 'TimeInStandardUnit']], left_on='exit time id', right_on='time id').drop(['time id'],axis='columns').rename(columns = {'TimeInStandardUnit': 'exit TimeInStandardUnit'}, inplace = False)

            average_vol_df= self.AnalysisContext.IntradayPricesData.getAverageVolPerMarketTimeSection()
            # average_vol_df.to_csv(r'd:\temp\average_vol_df.csv')
            self.trade_record = self.trade_record.merge(average_vol_df, on=['MarketTimeSectionID', 'ticker id'])

            print('trade_record after merging TimeIDMapping is with length ' + str(len(self.trade_record)) + ', max date id ' + str(self.trade_record['date id'].max()) + ' and min date id ' + str(self.trade_record['date id'].min()))
            # print(self.trade_record)
            
            if (len(self.trade_record) >0 ):
                print('before sorting for trade id assignment at ' + str(datetime.now()))
                self.trade_record = self.trade_record.sort_values(by=SortingColumns, ascending=False, inplace=False).reset_index().drop('index',axis='columns')
                print('before assigning trade id by CUDA at ' + str(datetime.now()))
                # trade_id = CUDATradeIDAssignment(df, self.TradeIDSortingSegmentKeyColumnsCount)
                # self.trade_record = pd.concat([self.trade_record, trade_id], axis=1)
                self.trade_record = pd.concat([self.trade_record, CUDATradeIDAssignment(self.trade_record[SharpeRatioStrategy.SCENARIO_COLUMNS], self.TradeIDSortingSegmentKeyColumnsCount)], axis=1)
                print('after assigning trade id by CUDA at ' + str(datetime.now()))
                # self.trade_record.to_csv(r'd:\temp\trade record with trade id.csv', index=False)

class BacktestSharpeRatioStrategy(FuturesStrategyBacktest):
    PreFilterOffset = 10
    # threshold_count_per_batch = 2

    def __init__(self, BacktestBatchID, BacktestBatchSubID, AnalysisContextList, TickerFilter = [], ResultOutputFolderPath = None, TradeIDSortingSegmentKeyColumnsCount = 2, PerformContangoAdjustment = True, MinimumTradeNumberCountForFullPeriod = 50, RandomNoiseTickerStdev = None, ActiveContractPircesTrimmedColumns = None, RapidCalibration = False, RapidCalibrationTopScenarioSelectedCount = 0, KeepOnlyWeekdays = False, FillEveryTimeSlot = False, threshold_count_per_batch = 1, InstrumentType = 'Futures'):
        self.BacktestBatchID = BacktestBatchID
        self.BacktestBatchSubID = BacktestBatchSubID
        self.loadStrategyParameters()
        super().__init__('SharpeRatioStrategy', BacktestBatchID, AnalysisContextList,  TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType, MAX_TRADE_ID = 100000)

        self.BacktestingSummaryDictAll = {}
        self.BacktestingTradeRecordAll = {}

        # threshold_remain_list = self.OBS_PERIOD_MOVEMENT_THRESHOLD.copy()

        # TotalBatchCount = math.ceil(len(threshold_remain_list)/threshold_count_per_batch) * len(self.StopLossTakeProfitList) * len(self.StopLossTakeProfitList) * len(self.ObsDateIDOffsetList) * len(self.TradeEntryDateIDOffsetList)
        # TotalBatchIndex = 0

        # for threshold in self.OBS_PERIOD_MOVEMENT_THRESHOLD:
        # print('Before while')
        # while len(threshold_remain_list) > 0:

        #     threshold_list = threshold_remain_list[0:threshold_count_per_batch]
        #     # print('threshold_remain_list before reducing is ' + str(threshold_remain_list))
        #     # print('threshold_count_per_batch is ' + str(threshold_count_per_batch))
        #     if len(threshold_remain_list) <= threshold_count_per_batch:
        #         threshold_remain_list = []
        #     else:
        #         threshold_remain_list = threshold_remain_list[-(len(threshold_remain_list)-threshold_count_per_batch):]

            # print('threshold_remain_list after reducing is ' + str(threshold_remain_list))
            # time.sleep(5)
            # for StopLossPerTrade in self.StopLossTakeProfitList:
            #     for TakeProfitPerTrade in self.StopLossTakeProfitList:
            #         for ObsDateIDOffset in self.ObsDateIDOffsetList:
            #             for TradeEntryDateIDOffset in self.TradeEntryDateIDOffsetList:
                            # TotalBatchIndex = TotalBatchIndex + 1
                            # print('Start running CorrelationOnSpecificTimeSectionStrategy ' + str(TotalBatchIndex) + '/' + str(TotalBatchCount) + ' for threshold ' + str(threshold_list) + ', stop loss ' + str(StopLossPerTrade) + ', take profit ' + str(TakeProfitPerTrade) + ' at ' + str(datetime.now()) + ', ObsDateIDOffset is ' + str(ObsDateIDOffset)  + ', TradeEntryDateIDOffset is ' + str(TradeEntryDateIDOffset) )                       

        self.backtest_result = SharpeRatioStrategy('SharpeRatioStrategy', self.AnalysisContext, self.StopLossTakeProfitList, self.StopLossTakeProfitList, self.MaxHoldingPeriod, self.ObsPeriod, self.VolumeToMeanVolumeRatio, self.MinReturnPerTimeSlotThreshold, self.SharpeRatioThreshold, self.ExitSharpeRatioOffset, self.UseMidOfHighLow)

        # print('In BacktestSharpeRatioStrategy.init, self.backtest_result.trade_record is')
        # print(self.backtest_result.trade_record)
        if self.UseMidOfHighLow:
            s = '_MidOfHighLow'
        else:
            s = ''
        self.FullResultOutputFolderPath = self.ResultOutputFolderPath + self.StrategyLabel + '_' + self.InstrumentType + s + '_' + self.StartDate.strftime("%Y%m%d") + '_' + self.EndDate.strftime("%Y%m%d") + '_' + self.TimeFrame + '_'
        self.PrepareSummary(SharpeRatioStrategy.SCENARIO_COLUMNS)

    # def __init__(self, StrategyLabel, AnalysisContext, ObsPeriod = [5, 10], SharpeRatioThreshold = [0.5, 1, 2], ExitSharpeRatioOffset = [0, 0.5], StopLossPerTrade = [0, 0.0025, 0.005], TakeProfitPerTrade = [0, 0.0025, 0.005], TradeIDSortingSegmentKeyColumnsCount = 2, PreFilterDataByTime = False, GPUMode = True):

        # self.FullResultOutputFolderPath = self.ResultOutputFolderPath + self.StrategyLabel + '_' + self.StartDate.strftime("%Y%m%d") + '_' + self.EndDate.strftime("%Y%m%d") + '_' + self.TimeFrame + '_'
        # self.PrepareSummary(SharpeRatioStrategy.SCENARIO_COLUMNS)

        # for key in self.BacktestingSummaryDict:
        #     if key in self.BacktestingSummaryDictAll:
        #         self.BacktestingSummaryDictAll[key] = self.BacktestingSummaryDictAll[key].append(self.BacktestingSummaryDict[key])
        #     else:
        #         self.BacktestingSummaryDictAll[key] = self.BacktestingSummaryDict[key]
        # for key in self.BacktestingTradeRecord:
        #     if key in self.BacktestingTradeRecordAll:
        #         self.BacktestingTradeRecordAll[key] = self.BacktestingTradeRecordAll[key].append(self.BacktestingTradeRecord[key])
        #     else:
        #         self.BacktestingTradeRecordAll[key] = self.BacktestingTradeRecord[key]

        # self.BacktestingSummaryDict = self.BacktestingSummaryDictAll
        # self.BacktestingTradeRecord = self.BacktestingTradeRecordAll
        # for key in self.BacktestingSummaryDict:
        #     self.BacktestingSummaryDict[key]['Abs Sharpe Ratio after commission'] = self.BacktestingSummaryDict[key]['Sharpe Ratio after commission'].abs()
        #     self.BacktestingSummaryDict[key] = self.BacktestingSummaryDict[key].sort_values(by='Abs Sharpe Ratio after commission', ascending=False).drop(['Abs Sharpe Ratio after commission'],axis='columns')

    def loadStrategyParameters(self):
        dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
        sql = "SELECT * FROM `fdata_backtest_batch` where BatchID = " + str(self.BacktestBatchID) + " AND BatchSubID = " + str(self.BacktestBatchSubID)
        ParameterValues = pd.read_sql_query(sql, dbcon)

        # self.StartTimeInStdUnit = ParameterValues.loc[0, 'ParameterValue1']
        # self.EndTimeInStdUnit = ParameterValues.loc[0, 'ParameterValue2']
        # self.TimeIntervalInStdUnit = ParameterValues.loc[0, 'ParameterValue3']
        # self.PreFilterDataByTime = (ParameterValues.loc[0, 'ParameterValue4'] == 1)

        # if self.PreFilterDataByTime:
        #     self.PreFilterDataStartTimeInStdUnit = max(self.StartTimeInStdUnit - BacktestSharpeRatioStrategy.PreFilterOffset, 0)
        #     self.PreFilterDataEndTimeInStdUnit = self.EndTimeInStdUnit + BacktestSharpeRatioStrategy.PreFilterOffset
        # else:
        #     self.PreFilterDataStartTimeInStdUnit = None
        #     self.PreFilterDataEndTimeInStdUnit = None

        parameter_string = ParameterValues.loc[0, 'TextParameterValue1']
        self.StopLossTakeProfitList = [int(e)/10000 for e in parameter_string.split(',')]
        print('self.StopLossTakeProfitList is ' + str(self.StopLossTakeProfitList))

        parameter_string = ParameterValues.loc[0, 'TextParameterValue2']
        self.MaxHoldingPeriod = [int(e) if e.isdigit() else e for e in parameter_string.split(',')]
        print('self.MaxHoldingPeriod is ' + str(self.MaxHoldingPeriod))

        parameter_string = ParameterValues.loc[0, 'TextParameterValue3']
        self.VolumeToMeanVolumeRatio = [float(e) for e in parameter_string.split(',')]
        print('self.VolumeToMeanVolumeRatio is ' + str(self.VolumeToMeanVolumeRatio))

        parameter_string = ParameterValues.loc[0, 'TextParameterValue4']
        self.MinReturnPerTimeSlotThreshold = [int(e)/10000 for e in parameter_string.split(',')]
        print('self.MinReturnPerTimeSlotThreshold is ' + str(self.MinReturnPerTimeSlotThreshold))

        parameter_string = ParameterValues.loc[0, 'TextParameterValue5']
        self.ObsPeriod = [int(e) if e.isdigit() else e for e in parameter_string.split(',')]
        print('self.ObsPeriod is ' + str(self.ObsPeriod))

        parameter_string = ParameterValues.loc[0, 'TextParameterValue6']
        self.SharpeRatioThreshold = [float(e) for e in parameter_string.split(',')]
        print('self.SharpeRatioThreshold is ' + str(self.SharpeRatioThreshold))

        parameter_string = ParameterValues.loc[0, 'TextParameterValue7']
        self.ExitSharpeRatioOffset = [float(e) for e in parameter_string.split(',')]
        print('self.ExitSharpeRatioOffset is ' + str(self.ExitSharpeRatioOffset))
        
        # self.UseMidOfHighLow = False
        self.UseMidOfHighLow = (ParameterValues.loc[0, 'ParameterValue1'] == 1)
       
        self.InstrumentType = ParameterValues.loc[0, 'InstrumentType']

 
        # date_id_offset_string = ParameterValues.loc[0, 'TextParameterValue3']
        # self.ObsDateIDOffsetList = [int(e) if e.isdigit() else e for e in date_id_offset_string.split(',')]
        # date_id_offset_string = ParameterValues.loc[0, 'TextParameterValue4']
        # print('TextParameterValue4 is ' + date_id_offset_string)
        # self.TradeEntryDateIDOffsetList = [int(e) if e.isdigit() else e for e in date_id_offset_string.split(',')]
        # print('TradeEntryDateIDOffsetList is ' + str(self.TradeEntryDateIDOffsetList))
        # self.ObsDateIDOffsetList = [0]
        # self.TradeEntryDateIDOffsetList = [0]

    def PrepareSummary(self, ScenarioColumnNames):

        self.BacktestingSummaryDict = {}
        self.BacktestingTradeRecord = {}

        if (len(self.backtest_result.trade_record) > 0):
            self.backtest_result.trade_record = super().getPreparedTradeRecord(self.backtest_result.trade_record, ScenarioColumnNames, 'trade id', ascending=True)
            if self.RapidCalibrationTopScenarioSelectedCount == 0:
                self.FillDataMatrix(self.backtest_result.trade_record, 'trade id', ['scenario id'], {'long short flag': 'long short flag', 'entry price': 'entry price', 'exit price': 'exit price'})
            else:
                self.FillDataMatrix(self.backtest_result.trade_record, 'trade id', ['scenario id'], {'long short flag': 'long short flag', 'entry price': 'entry price', 'exit price': 'exit price', 'date id': 'date id'})

            BacktestingSummary, RapidCalibrationBacktestingSummary = self.getCUDABacktestingSummary()
            # BacktestingSummary.to_csv(self.ResultOutputFolderPath + self.StrategyLabel + '_' + self.StartDate.strftime("%Y%m%d") + '_' + self.EndDate.strftime("%Y%m%d") + '_' + self.TimeFrame + '_'+ r'BacktestingSummary.csv')

            self.BacktestingSummaryDict = self.FinishSummary(BacktestingSummary, ScenarioColumnNames)
            self.BacktestingTradeRecord = {}
            for backtest_period in self.BacktestingSummaryDict:
                self.BacktestingTradeRecord[backtest_period] = self.backtest_result.trade_record.merge(self.BacktestingSummaryDict[backtest_period][ScenarioColumnNames], on=ScenarioColumnNames)
                self.BacktestingTradeRecord[backtest_period] = self.BacktestingTradeRecord[backtest_period].merge(self.AnalysisContext.FuturesData.DateIDMapping, on=['date id'])