# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 00:43:40 2021

@author: Henry Cheung
"""

from datetime import date, datetime, timedelta
import vaex

# import mysql.connector
import pandas as pd
import numpy as np
import InvestmentAnalytics.Config as Config
import InvestmentAnalytics.DBUtil as DBUtil

from InvestmentAnalytics.MarketDataReader import IBFuturesPriceReader, FuturesPriceAnalysisContext, FXFuturesPriceAnalysisContext, CryptoPriceAnalysisContext
from InvestmentAnalytics.Indicator.Indicator import IndicatorLocator

from InvestmentAnalytics.CUDA.BacktestingCUDALib import CUDABacktestingSummary, CUDABacktestingRapidCalibrationSummary
from InvestmentAnalytics.CUDA.MarketDataReaderCUDALib import CUDAFillModifiedFollowing, CUDAFillByOverride

from InvestmentAnalytics.TradeAnalysisOutputLib import UpdateLastRunTradeRecordSizePerSubBatch, UpdateLastRunMaxTradeRecordSizePerSubBatch


# mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
# mycursor = mydb.cursor()


def check_if_list_equal(list_1, list_2):
    if len(list_1) != len(list_2):
        return False
    if len(list_1) == 0:
        return True
    return sorted(list_1) == sorted(list_2)

def drop_duplicates(df, columns=None):
    """Return a :class:`DataFrame` object with no duplicates in the given columns.
    .. warning:: The resulting dataframe will be in memory, use with caution.
    :param columns: Column or list of column to remove duplicates by, default to all columns.
    :return: :class:`DataFrame` object with duplicates filtered away.
    """
    if columns is None:
        columns = df.get_column_names()
    if type(columns) is str:
        columns = [columns]
    return df.groupby(columns, agg={'__hidden_count': vaex.agg.count()}).drop('__hidden_count')

def new_column_by_column_merging(df, columns=None):
    if columns is None:
        columns = df.get_column_names()
    if type(columns) is str:
        df['merged_column_key'] = df[columns]
        return df

    df['merged_column_key'] = np.array(['']*len(df))
    for col in columns:
        if df[col].dtype == 'int64':
            df[col] = df[col].astype('float64')
        df['merged_column_key'] = df['merged_column_key'] + '_' + df[col].astype('string')
    return df
    
    


class StrategyBacktest:
    # BACKTEST_PERIOD_LABEL = {0:'full period', 5:'last 5 trades', 10:'last 10 trades'}
    COLUMNS_FOR_TRADE_RECORD_MERGING_WITHOUT_BACKTEST_PERIOD_HEAD = ['ticker', 'number of trades', 'long ratio']
    COLUMNS_FOR_TRADE_RECORD_MERGING_WITHOUT_BACKTEST_PERIOD_TAIL = ['Sharpe Ratio', 'average return per trade', 'stdev of point return per trade', 'Multiplier', 'Commission', 'TickSize']
    COLUMNS_FOR_TRADE_RECORD_MERGING_WITH_BACKTEST_PERIOD = ['Sharpe Ratio after commission', 'average return per trade after commission', 'max drawdown', 'max drawup', 'win percentage', 'p-value-z-score', 't-score', 'p-value']
    SYMMETRICAL_TRADING_STRATEGY_SORTING_KEY = 'Abs Sharpe Ratio after commission'
    ASYMMETRICAL_TRADING_STRATEGY_SORTING_KEY = 'Sharpe Ratio after commission'
    # 'Abs Sharpe Ratio after commission'
    
    def __init__(self, StrategyLabel, BacktestParameterDF, TickerFilter = [], ResultOutputFolderPath = None, MinimumTradeNumberCountForFullPeriod = 50, DebugFilepath = None, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch'):
        self.StrategyLabel = StrategyLabel
        self.BacktestParameterDF = BacktestParameterDF
        self.loadAnalysisContextParameters()
        self.TickerFilter = TickerFilter
        self.ResultOutputFolderPath = ResultOutputFolderPath
        self.MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod
        self.MaxTradeResultCountPerBatch = 0
        self.DebugFilepath = DebugFilepath
        self.BatchListDatabaseName = BatchListDatabaseName
        self.BatchListTableName = BatchListTableName

    def UpdateLastRunTradeRecordSizePerSubBatch(self, LastRunTradeRecordResultSize):
        UpdateLastRunTradeRecordSizePerSubBatch(self.BacktestParameterDF.loc[0, 'StrategyName'], self.BacktestParameterDF.loc[0, 'BatchGroup'], self.BacktestParameterDF.loc[0, 'BatchID'], self.BacktestParameterDF.loc[0, 'BatchSubID'], LastRunTradeRecordResultSize, BatchListDatabaseName = self.BatchListDatabaseName, BatchListTableName = self.BatchListTableName)

    def UpdateLastRunMaxTradeRecordSizePerSubBatch(self, MaxLastRunTradeRecordResultSize):
        UpdateLastRunMaxTradeRecordSizePerSubBatch(self.BacktestParameterDF.loc[0, 'StrategyName'], self.BacktestParameterDF.loc[0, 'BatchGroup'], self.BacktestParameterDF.loc[0, 'BatchID'], self.BacktestParameterDF.loc[0, 'BatchSubID'], MaxLastRunTradeRecordResultSize, BatchListDatabaseName = self.BatchListDatabaseName, BatchListTableName = self.BatchListTableName)

    def loadAnalysisContextParameters(self):
        self.BatchGroup = self.BacktestParameterDF.loc[0, 'BatchGroup']
        self.BatchID = self.BacktestParameterDF.loc[0, 'BatchID']
        self.BatchSubID = self.BacktestParameterDF.loc[0, 'BatchSubID']
        self.StartDate = self.BacktestParameterDF.loc[0, 'StartDate']
        self.EndDate = self.BacktestParameterDF.loc[0, 'EndDate']
        self.TimeFrame = self.BacktestParameterDF.loc[0, 'TimeFrame']
        parameter_string = self.BacktestParameterDF.loc[0, 'BacktestSummaryTradeCount']
        self.BacktestSummaryTradeCount = [int(e) if e.isdigit() else e for e in parameter_string.split(',')]
        self.BacktestPeriodLabel = self.getBacktestPeriodLabel()
        
    def getBacktestPeriodLabel(self):
        BacktestPeriodLabel = {0:'full period'}
        for backtest_trade_count in self.BacktestSummaryTradeCount:
            if backtest_trade_count != 0:
                BacktestPeriodLabel[backtest_trade_count] = 'last ' + str(backtest_trade_count) + ' trades'
        return BacktestPeriodLabel
        
    def AddAutoincrementalID(df, ColumnsToAddID, IDColumnLabel, ascending=True):
        IDMapping = df[ColumnsToAddID].drop_duplicates().sort_values(by=ColumnsToAddID, ascending=ascending).reset_index().drop(['index'],axis='columns')
        IDMapping[IDColumnLabel] = IDMapping.index
        # df.to_csv(r'C:\temp\AddAutoincrementalID1.csv')
        # IDMapping.to_csv(r'C:\temp\AddAutoincrementalID2.csv')
        # print('df is')
        # print(df)
        # print('ID Mapping is')
        # print(IDMapping)
        # print('ColumnsToAddID is')
        # print(ColumnsToAddID)
        df = df.merge(IDMapping, on=ColumnsToAddID)
        return df, IDMapping
        # if isinstance(df, pd.DataFrame):
        #     IDMapping = df[ColumnsToAddID].drop_duplicates().sort_values(by=ColumnsToAddID, ascending=ascending).reset_index().drop(['index'],axis='columns')
        #     IDMapping[IDColumnLabel] = IDMapping.index
        #     df = df.merge(IDMapping, on=ColumnsToAddID)
        #     return df, IDMapping
        # else:
        #     import vaex
        #     IDMapping = drop_duplicates(df, ColumnsToAddID)
        #     IDMapping = IDMapping.sort(ColumnsToAddID, ascending=ascending)
        #     IDMapping[IDColumnLabel] = vaex.vrange(0, len(IDMapping))
        #     print('df is')
        #     print(df)
        #     print('IDMapping is')
        #     print(IDMapping)
        #     df2 = new_column_by_column_merging(df, ColumnsToAddID)
        #     IDMapping2 = new_column_by_column_merging(IDMapping, ColumnsToAddID)
        #     # df = df.join(IDMapping, on=ColumnsToAddID)
        #     df = df2.join(IDMapping2, on='merged_column_key', rsuffix='_y')
        #     df = df.drop('merged_column_key')
        #     for col in ColumnsToAddID:
        #         df = df.drop(col + '_y')
        #     return df, IDMapping
            
    
    def to_numpy(df, x_matrix_column_name, y_matrix_row_names, value_column, FillNaNWith=0):
        df = df.fillna(FillNaNWith)
        
        if isinstance(df, pd.DataFrame):
            df = pd.pivot_table(df, index=y_matrix_row_names,columns=[x_matrix_column_name], values=value_column, aggfunc=np.mean).reset_index()
        else:
            df = df.compute()
            df = pd.pivot_table(df, index=y_matrix_row_names,columns=[x_matrix_column_name], values=value_column, aggfunc=np.mean).reset_index()
        # to change to CUDA
        df = df.drop(y_matrix_row_names,axis='columns')
        df = df.to_numpy()
        where_are_NaNs = np.isnan(df)
        df[where_are_NaNs] = FillNaNWith
        return df  

    # def OrganiseTradeRecord(trade_record, TickerIDMapping_DF, SortingColumns, SCENARIO_COLUMNS, TradeIDSortingSegmentKeyColumnsCount):
    #     trade_record = trade_record.merge(TickerIDMapping_DF, on='ticker id')
    #     # print('self.trade_record after merge is')
    #     # print(self.trade_record.head(10))

    #     if isinstance(trade_record, pd.DataFrame):
    #         print('trade_record after merging TimeIDMapping is with length ' + str(len(trade_record)) + ', max date id ' + str(trade_record['date id'].max()) + ' and min date id ' + str(trade_record['date id'].min()))
    #     else:
    #         print('trade_record after merging TimeIDMapping is with length ' + str(len(trade_record)) + ', max date id ' + str(trade_record['date id'].max().compute()) + ' and min date id ' + str(trade_record['date id'].min().compute()))

    #     if (len(trade_record) >0 ):
    #         print('before sorting for trade id assignment at ' + str(datetime.now()) + ', SortingColumns is ' + str(SortingColumns))
    #         if isinstance(trade_record, pd.DataFrame):
    #             print('before pandas sorting for ' + str(len(trade_record)) + ' rows at ' + str(datetime.now()))
    #             trade_record = trade_record.sort_values(by=SortingColumns, ascending=False, inplace=False)
    #             print('after pandas sorting for ' + str(len(trade_record)) + ' rows at ' + str(datetime.now()))
    #         else:
    #             import InvestmentAnalytics.DaskUtil as DaskUtil
    #             trade_record = DaskUtil.GroupAndSort(trade_record, by=SortingColumns, ascending=False, ScenarioColumns = SCENARIO_COLUMNS, TradeIDSortingSegmentKeyColumnsCount = TradeIDSortingSegmentKeyColumnsCount)
            
    #         trade_record = trade_record.reset_index(drop=True)
    #         # df = self.trade_record[CorrelationOnSpecificTimeSectionStrategy.SCENARIO_COLUMNS]
            
    #         print('before assigning trade id by CUDA at ' + str(datetime.now()))
            
    #         # self.trade_record = pd.concat([self.trade_record, CUDATradeIDAssignment(self.trade_record[CorrelationOnSpecificTimeSectionStrategy.SCENARIO_COLUMNS], self.TradeIDSortingSegmentKeyColumnsCount)], axis=1)
    #         if "trade id" in trade_record.columns:
    #             print('Trade ID assigned when doing sorting')
    #         else:
    #             if isinstance(trade_record, pd.DataFrame):
    #                 from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib import CUDATradeIDAssignment
    #                 # df = CUDATradeIDAssignment(df, self.TradeIDSortingSegmentKeyColumnsCount)
    #                 trade_record = pd.concat([trade_record, CUDATradeIDAssignment(trade_record[SCENARIO_COLUMNS], TradeIDSortingSegmentKeyColumnsCount)], axis=1)
    #             else:
    #                 print('trade_record is with len ' + f"{len(trade_record):,}" + ' and partition total count of ' + str(len(trade_record.partitions)))
                    
    #                 import dask.dataframe as dd
    #                 # import dask.array as da
    #                 # import dask.bag as db
    #                 # ddf = dd.from_pandas(self.trade_record[CorrelationOnSpecificTimeSectionStrategy.SCENARIO_COLUMNS], npartitions=len(self.trade_record.partitions))
    #                 trade_record = dd.concat([trade_record, dd.from_pandas(trade_record[SCENARIO_COLUMNS], npartitions=len(trade_record.partitions))], axis=1)
    #                 print('trade_record after concat trade id is with len ' + f"{len(trade_record):,}")
    #     return trade_record

    def OrganiseTradeRecord(strategy, TickerIDMapping_DF, SortingColumns, SCENARIO_COLUMNS, TradeIDSortingSegmentKeyColumnsCount):
        
        print('Start of OrganiseTradeRecord')
        
        # if strategy.MaxTradeRecordSizePerSubBatch is None:
        #     strategy.MaxTradeRecordSizePerSubBatch = len(strategy.trade_record)
        # else:
        #     if strategy.MaxTradeRecordSizePerSubBatch < len(strategy.trade_record):
        #         strategy.MaxTradeRecordSizePerSubBatch = len(strategy.trade_record)
        
        # from InvestmentAnalytics.TradeAnalysisLib import UpdateLastRunMaxTradeRecordSizePerSubBatch
        # UpdateLastRunMaxTradeRecordSizePerSubBatch(strategy.StrategyLabel, strategy.BatchGroup, strategy.BatchID, strategy.BatchSubID, len(strategy.trade_record), BatchListDatabaseName = strategy.BatchListDatabaseName, BatchListTableName = strategy.BatchListTableName)
# UpdateLastRunMaxTradeRecordSizePerSubBatch(StrategyName, BatchGroup, BacktestBatchID, BatchSubID, MaxLastRunTradeRecordResultSize, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch'):        

        # if 'ticker' not in strategy.trade_record:
        strategy.trade_record = strategy.trade_record.merge(TickerIDMapping_DF, on='ticker id')
        # print('self.trade_record after merge is')
        # print(self.trade_record.head(10))

        if isinstance(strategy.trade_record, pd.DataFrame):
            print('trade_record after merging TimeIDMapping is with length ' + str(len(strategy.trade_record)) + ', max date id ' + str(strategy.trade_record['date id'].max()) + ' and min date id ' + str(strategy.trade_record['date id'].min()))
        else:
            print('trade_record after merging TimeIDMapping is with length ' + str(len(strategy.trade_record)) + ', max date id ' + str(strategy.trade_record['date id'].max().compute()) + ' and min date id ' + str(strategy.trade_record['date id'].min().compute()))

        if (len(strategy.trade_record) >0 ):
            print('before sorting for trade id assignment at ' + str(datetime.now()) + ', SortingColumns is ' + str(SortingColumns))
            if isinstance(strategy.trade_record, pd.DataFrame):
                # print('before pandas sorting for ' + str(len(strategy.trade_record)) + ' rows at ' + str(datetime.now()))
                print('before pandas sorting for ' + f"{len(strategy.trade_record):,}" + ' rows at ' + str(datetime.now()))
                strategy.trade_record = strategy.trade_record.sort_values(by=SortingColumns, ascending=False, inplace=False)
                # print('after pandas sorting for ' + str(len(strategy.trade_record)) + ' rows at ' + str(datetime.now()))
                print('after pandas sorting for ' + f"{len(strategy.trade_record):,}" + ' rows at ' + str(datetime.now()))
            else:
                import InvestmentAnalytics.DaskUtil as DaskUtil
                strategy.trade_record = DaskUtil.GroupAndSort(strategy.trade_record, by=SortingColumns, ascending=False, ScenarioColumns = SCENARIO_COLUMNS, TradeIDSortingSegmentKeyColumnsCount = TradeIDSortingSegmentKeyColumnsCount)
            
            strategy.trade_record = strategy.trade_record.reset_index(drop=True)
            # df = self.trade_record[CorrelationOnSpecificTimeSectionStrategy.SCENARIO_COLUMNS]
            
            print('before assigning trade id by CUDA at ' + str(datetime.now()))
            
            # self.trade_record = pd.concat([self.trade_record, CUDATradeIDAssignment(self.trade_record[CorrelationOnSpecificTimeSectionStrategy.SCENARIO_COLUMNS], self.TradeIDSortingSegmentKeyColumnsCount)], axis=1)
            if "trade id" in strategy.trade_record.columns:
                print('Trade ID assigned when doing sorting')
            else:
                if isinstance(strategy.trade_record, pd.DataFrame):
                    from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib import CUDATradeIDAssignment
                    strategy.trade_record = pd.concat([strategy.trade_record, CUDATradeIDAssignment(strategy.trade_record[SCENARIO_COLUMNS], TradeIDSortingSegmentKeyColumnsCount)], axis=1)
                else:
                    print('trade_record is with len ' + f"{len(strategy.trade_record):,}" + ' and partition total count of ' + str(len(strategy.trade_record.partitions)))
                    
                    import dask.dataframe as dd
                    strategy.trade_record = dd.concat([strategy.trade_record, dd.from_pandas(strategy.trade_record[SCENARIO_COLUMNS], npartitions=len(strategy.trade_record.partitions))], axis=1)
                    print('trade_record after concat trade id is with len ' + f"{len(strategy.trade_record):,}")



from InvestmentAnalytics.Indicator.Indicator import IndicatorLocator

    
class FuturesStrategyBacktest(StrategyBacktest):
    
    def __init__(self, StrategyLabel, BacktestParameterDF, AnalysisContextList, PreFilterDataByTime = False, PreFilterDataStartTimeInStdUnit = None, PreFilterDataEndTimeInStdUnit = None, TickerFilter = [], KeepDataframeData = False, ResultOutputFolderPath = None, PerformContangoAdjustment = True, MinimumTradeNumberCountForFullPeriod = 50, RandomNoiseTickerStdev = None, FillEveryTimeSlot = False, ActiveContractPircesTrimmedColumns = None, RapidCalibration = False, RapidCalibrationTopScenarioSelectedCount = 0, RapidCalibrationFrequencyTag = 'date id', KeepOnlyWeekdays = False, DataTimeLowerBound = None, DataTimeUpperBound = None, InstrumentType = 'Futures', MAX_TRADE_ID = 2000, MarketTimeSectionTimeList = None, DebugFilepath = None, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch', Override_DBHost = None, Override_DBPort = None, Override_DBUser = None, Override_DBPassword = None):

        super().__init__(StrategyLabel, BacktestParameterDF, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, MinimumTradeNumberCountForFullPeriod = MinimumTradeNumberCountForFullPeriod, DebugFilepath = DebugFilepath, BatchListDatabaseName = BatchListDatabaseName, BatchListTableName = BatchListTableName)
        
        self.MAX_TRADE_ID = MAX_TRADE_ID
        self.AnalysisContext = None
        
        if AnalysisContextList is None:
            print('AnalysisContextList is None')
            print('TickerFilter is ' + str(TickerFilter))
            self.AnalysisContext = self.getAnalysisContext(PreFilterDataByTime, PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit, TickerFilter, KeepDataframeData, PerformContangoAdjustment, RandomNoiseTickerStdev, FillEveryTimeSlot, KeepOnlyWeekdays, DataTimeLowerBound = DataTimeLowerBound, DataTimeUpperBound = DataTimeUpperBound, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList , DebugFilepath = DebugFilepath)
            
            # close_price_matrix = self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_close_adj'].T.copy(order="C")
            # df = pd.DataFrame(data=close_price_matrix, columns=['ticker 0', 'ticker 1'])
            # df.to_csv(r'E:\TradeAnalysisProject\RoutineAnalysis\SharpeRatioStrategy\Debug\close_price_matrix_in_FuturesStrategyBacktest.csv', index=False)
            
            self.AnalysisContextList = [self.AnalysisContext]
        else:
            self.AnalysisContextList = AnalysisContextList
            for AnalysisContext in AnalysisContextList:
                if ((self.StartDate == AnalysisContext.FuturesData.StartDate) and (self.EndDate == AnalysisContext.FuturesData.EndDate) and (self.TimeFrame == AnalysisContext.FuturesData.TimeFrame) and check_if_list_equal(TickerFilter, AnalysisContext.FuturesData.TickerFilter) and (KeepOnlyWeekdays == AnalysisContext.FuturesData.KeepOnlyWeekdays) and (FillEveryTimeSlot == AnalysisContext.FuturesData.FillEveryTimeSlot)):
                    self.AnalysisContext = AnalysisContext
            if self.AnalysisContext is None:
                # self.AnalysisContext = FuturesPriceAnalysisContext(self.StartDate, self.EndDate, self.TimeFrame, TickerFilter = TickerFilter, KeepDataframeData = True, PerformContangoAdjustment = PerformContangoAdjustment)
                self.AnalysisContext = self.getAnalysisContext(PreFilterDataByTime, PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit, TickerFilter, KeepDataframeData, PerformContangoAdjustment, RandomNoiseTickerStdev, FillEveryTimeSlot, KeepOnlyWeekdays, DataTimeLowerBound = DataTimeLowerBound, DataTimeUpperBound = DataTimeUpperBound, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList , DebugFilepath = DebugFilepath)
                self.AnalysisContextList.append(self.AnalysisContext)
                
        self.DataMatrix = {}
        self.RapidCalibration = RapidCalibration
        self.RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount
        self.RapidCalibrationFrequencyTag = RapidCalibrationFrequencyTag

        self.loadCommonStrategyParameters()
        # IndicatorLocator.UploadIndicatorToAnalysisContext(self.AnalysisContext, self.ParameterValues.loc[0, 'TradeFilterIndicatorName'], self.ParameterValues.loc[0, 'TradeFilterIndicatorDataLabel'], self.ParameterValues.loc[0, 'TradeFilterIndicatorParameter'])
        # IndicatorLocator.UploadIndicatorToAnalysisContext(self.AnalysisContext, self.TradeFilterIndicatorName, self.TradeFilterIndicatorDataLabel, self.TradeFilterIndicatorParameter)

        
    def getAnalysisContext(self, PreFilterDataByTime, PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit, TickerFilter, KeepDataframeData, PerformContangoAdjustment, RandomNoiseTickerStdev, FillEveryTimeSlot, KeepOnlyWeekdays, DataTimeLowerBound = None, DataTimeUpperBound = None, InstrumentType = 'Futures', MarketTimeSectionTimeList = None, DebugFilepath = None):
        print('in getAnalysisContext, DebugFilepath = ' + str(DebugFilepath))
        if InstrumentType == 'Futures':
            # print('Going to run FuturesPriceAnalysisContext (' + str(self.StartDate) + ', ' + str(self.EndDate) + ', ' + self.TimeFrame + ', ' + str(PreFilterDataByTime) + ', ' + str(PreFilterDataStartTimeInStdUnit) + ', ' + str(PreFilterDataEndTimeInStdUnit) + ', ' + str(TickerFilter) + ', ' + str(KeepDataframeData) + ', ' + str(PerformContangoAdjustment) + ', ' + str(RandomNoiseTickerStdev) + ', ' + str(FillEveryTimeSlot) + ', ' + str(KeepOnlyWeekdays) + ', ' + str(DataTimeLowerBound) + ', ' + str(DataTimeUpperBound) + ', ' + str(MarketTimeSectionTimeList) + ', ' + str(DebugFilepath) + ')')
            # context = FuturesPriceAnalysisContext(self.StartDate, self.EndDate, self.TimeFrame, PreFilterDataByTime = PreFilterDataByTime,PreFilterDataStartTimeInStdUnit = PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit = PreFilterDataEndTimeInStdUnit,  TickerFilter = TickerFilter, KeepDataframeData = KeepDataframeData, PerformContangoAdjustment = PerformContangoAdjustment, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, KeepOnlyWeekdays = KeepOnlyWeekdays, DataTimeLowerBound = DataTimeLowerBound, DataTimeUpperBound = DataTimeUpperBound, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath)
            # close_price_matrix = context.IntradayPricesData.DataMatrix['TRADES_close_adj'].T.copy(order="C")
            # df = pd.DataFrame(data=close_price_matrix, columns=['ticker 0', 'ticker 1'])
            # df.to_csv(r'E:\TradeAnalysisProject\RoutineAnalysis\SharpeRatioStrategy\Debug\close_price_matrix_in_FuturesStrategyBacktest_getAnalysisContext.csv', index=False)
            # return context
            return FuturesPriceAnalysisContext(self.StartDate, self.EndDate, self.TimeFrame, PreFilterDataByTime = PreFilterDataByTime,PreFilterDataStartTimeInStdUnit = PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit = PreFilterDataEndTimeInStdUnit,  TickerFilter = TickerFilter, KeepDataframeData = KeepDataframeData, PerformContangoAdjustment = PerformContangoAdjustment, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, KeepOnlyWeekdays = KeepOnlyWeekdays, DataTimeLowerBound = DataTimeLowerBound, DataTimeUpperBound = DataTimeUpperBound, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath)
        elif InstrumentType == 'FXFutures':
            return FXFuturesPriceAnalysisContext(self.StartDate, self.EndDate, self.TimeFrame, PreFilterDataByTime = PreFilterDataByTime,PreFilterDataStartTimeInStdUnit = PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit = PreFilterDataEndTimeInStdUnit,  TickerFilter = TickerFilter, KeepDataframeData = KeepDataframeData, PerformContangoAdjustment = False, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, KeepOnlyWeekdays = KeepOnlyWeekdays, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath)
        elif InstrumentType == 'Crypto':
            return CryptoPriceAnalysisContext(self.StartDate, self.EndDate, self.TimeFrame, PreFilterDataByTime = PreFilterDataByTime,PreFilterDataStartTimeInStdUnit = PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit = PreFilterDataEndTimeInStdUnit,  TickerFilter = TickerFilter, KeepDataframeData = KeepDataframeData, PerformContangoAdjustment = False, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, KeepOnlyWeekdays = KeepOnlyWeekdays, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath)
        
    def getCUDABacktestingSummary(self):
        if self.RapidCalibrationTopScenarioSelectedCount == 0:
            backtest_summary, pnl_matrix = CUDABacktestingSummary(self.DataMatrix['long short flag'], self.DataMatrix['entry price'], self.DataMatrix['exit price'], self.BacktestPeriodLabel, GeneratePnlMatrix = False)
            return backtest_summary, None
        else:
            backtest_summary, pnl_matrix = CUDABacktestingSummary(self.DataMatrix['long short flag'], self.DataMatrix['entry price'], self.DataMatrix['exit price'], self.BacktestPeriodLabel, GeneratePnlMatrix = True)
            backtest_rapid_calibration_summary = CUDABacktestingRapidCalibrationSummary(self.DataMatrix['long short flag'], self.DataMatrix['entry price'], self.DataMatrix['exit price'], self.DataMatrix['date id'], self.BacktestPeriodLabel, self.AnalysisContextList[0].FuturesData.TimeIDMapping, self.Scenario_IDMapping, self.RapidCalibrationTopScenarioSelectedCount, self.RapidCalibrationFrequencyTag)

            return backtest_summary, backtest_rapid_calibration_summary
        # if self.RapidCalibrationTopScenarioSelectedCount == 0:
        #     return CUDABacktestingSummary(self.DataMatrix['long short flag'], self.DataMatrix['entry price'], self.DataMatrix['exit price'], StrategyBacktest.BACKTEST_PERIOD_LABEL, GeneratePnlMatrix = False), None
        # else:
        #     return CUDABacktestingSummary(self.DataMatrix['long short flag'], self.DataMatrix['entry price'], self.DataMatrix['exit price'], StrategyBacktest.BACKTEST_PERIOD_LABEL, GeneratePnlMatrix = True), CUDABacktestingRapidCalibrationSummary(self.DataMatrix['long short flag'], self.DataMatrix['entry price'], self.DataMatrix['exit price'], self.DataMatrix['date id'], StrategyBacktest.BACKTEST_PERIOD_LABEL, self.AnalysisContextList[0].FuturesData.TimeIDMapping, self.Scenario_IDMapping, self.RapidCalibrationTopScenarioSelectedCount, self.RapidCalibrationFrequencyTag)

    def loadCommonStrategyParameters(self):

        self.InstrumentType = self.BacktestParameterDF.loc[0, 'InstrumentType']
        self.GPUMode = self.BacktestParameterDF.loc[0, 'GPUMode']
        self.GPUCore = int(self.BacktestParameterDF.loc[0, 'GPUCore'])
        
        self.TradeIDSortingSegmentKeyColumnsCount = self.BacktestParameterDF.loc[0, 'TradeIDSortingSegmentKeyColumnsCount']
        self.InitialResultCacheSize = self.BacktestParameterDF.loc[0, 'InitialTradeRecordResultCacheSize']
        self.TOP_BACKTEST_RESULT_COUNT_PER_TICKER = self.BacktestParameterDF.loc[0, 'TopResultPerTicker']
        self.MinimumTradeNumberCountForFullPeriod = self.BacktestParameterDF.loc[0, 'RequiredTradeNumberCount']

        s = self.BacktestParameterDF.loc[0, 'ParameterTrialCountPerLoop']
        try:
            self.ParameterTrialCountPerLoop = [int(e) if e.isdigit() else e for e in s.split(',')]
        except:
            self.ParameterTrialCountPerLoop = [0,0,0,0,0,0,0,0,0,0]
            
        self.TradeFilterIndicatorName = self.BacktestParameterDF.loc[0, 'TradeFilterIndicatorName']
        self.TradeFilterIndicatorDataLabel = self.BacktestParameterDF.loc[0, 'TradeFilterIndicatorDataLabel']
        
        s = self.BacktestParameterDF.loc[0, 'TradeFilterIndicatorParameter']
        if s is None:
            self.TradeFilterIndicatorParameter = None
        else:
            self.TradeFilterIndicatorParameter = IndicatorLocator.ParameterStringToListOfList(s)
        s = self.BacktestParameterDF.loc[0, 'TradeFilterIndicatorThreshold']
        if s is None:
            self.TradeFilterIndicatorThreshold = None
        else:
            self.TradeFilterIndicatorThreshold = [int(e) if e.isdigit() else e for e in s.split(',')]
        
    def getListOfList(lst, items_count_per_sub_list):
        if items_count_per_sub_list == 0:
            return [lst]
        else:
            return [lst[i:i + items_count_per_sub_list] for i in range(0, len(lst), items_count_per_sub_list)]

    def getBacktestItem( BacktestParameterDF, AnalysisContextList, TickerFilter = [], ResultOutputFolderPath = None, PerformContangoAdjustment = True, RandomNoiseTickerStdev = None, FillEveryTimeSlot = False, ActiveContractPircesTrimmedColumns = None, RapidCalibration = False, RapidCalibrationTopScenarioSelectedCount = 0, KeepOnlyWeekdays = False, DataTimeLowerBound = None, DataTimeUpperBound = None, InstrumentType = 'Futures', MarketTimeSectionTimeList = None, DebugFilepath = None, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch'):
        return BacktestItemLocator.getBacktestItem( BacktestParameterDF, AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, DataTimeLowerBound = DataTimeLowerBound, DataTimeUpperBound = DataTimeUpperBound, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList , DebugFilepath = DebugFilepath, BatchListDatabaseName = BatchListDatabaseName, BatchListTableName = BatchListTableName)
        # return BacktestItemLocator.getBacktestItem( BacktestParameterDF, AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, MinimumTradeNumberCountForFullPeriod = self.MinimumTradeNumberCountForFullPeriod, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, DataTimeLowerBound = DataTimeLowerBound, DataTimeUpperBound = DataTimeUpperBound, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList , DebugFilepath = DebugFilepath)


    def getFuturesProperty():
        sql = "SELECT * FROM `fdata_backtest_futures_property`"
        return pd.read_sql(sql,con=DBUtil.GetSQLAlchemyEngine())    

    def getPreparedTradeRecord(self, trade_record, ScenarioColumnNames, TradeIDColumnName, ascending=True):
        print('before calculating trade ID statistics at ' + str(datetime.now()))

        if isinstance(trade_record, pd.DataFrame):
            MaxTradeID = trade_record[TradeIDColumnName].max()
            MinTradeID = trade_record[TradeIDColumnName].min()
        else:
            MaxTradeID = trade_record[TradeIDColumnName].max().compute()
            MinTradeID = trade_record[TradeIDColumnName].min().compute()
            
        TradeIDCount = len(trade_record[[TradeIDColumnName]].drop_duplicates())
        print('MaxTradeID is ' + str(MaxTradeID) + ' and MinTradeID is ' + str(MinTradeID)+ ' and TradeIDCount is ' + str(TradeIDCount) + ' at ' + str(datetime.now()))
        if MaxTradeID > self.MAX_TRADE_ID:
            raise Exception("Maximum trade id too large, larger than " + str(self.MAX_TRADE_ID))
        print('before calculating AddAutoincrementalID at ' + str(datetime.now()))
        trade_record, self.Scenario_IDMapping = StrategyBacktest.AddAutoincrementalID(trade_record, ScenarioColumnNames, 'scenario id')
        print('after calculating AddAutoincrementalID at ' + str(datetime.now()))
        
        if isinstance(trade_record, pd.DataFrame):
            trade_record = trade_record.sort_values(by=['scenario id', TradeIDColumnName], ascending=ascending)
        else:
            print('TradeIDColumnName is ' + str(TradeIDColumnName))
            trade_record['scenario and trade id'] = trade_record['scenario id'] * (MaxTradeID + 10) + trade_record[TradeIDColumnName]
            trade_record = trade_record.sort_values(by='scenario and trade id', ascending=ascending).reset_index().drop(['scenario and trade id'],axis='columns')
            
       
        print('after sorting by scenario id at ' + str(datetime.now()))
        
        # from InvestmentAnalytics.TradeAnalysisLib import UpdateLastRunMaxTradeRecordSizePerSubBatch
        # UpdateLastRunMaxTradeRecordSizePerSubBatch(self.backtest_result.StrategyLabel, self.BatchGroup, self.BatchID, self.BatchSubID, len(self.backtest_result.trade_record), BatchListDatabaseName = self.BatchListDatabaseName, BatchListTableName = self.BatchListTableName)
       
        
        return trade_record
        
    # def FinishSummary(self, BacktestingSummary, ScenarioDetailColumns, SymmetricalStrategy = True, TopNumberOfResultPerTicker = self.TOP_BACKTEST_RESULT_COUNT_PER_TICKER):
    def FinishSummary(self, BacktestingSummary, ScenarioDetailColumns, SymmetricalStrategy = True):
        
        print('Start of FinishSummary at ' + str(datetime.now()))
        
        # BacktestingSummary.to_csv(r'C:\temp\BacktestingSummary beginning of FinishSummary.csv')
        BacktestingSummary['Sharpe Ratio'] = BacktestingSummary['average return per trade'] / BacktestingSummary['stdev of point return per trade']
        BacktestingSummary['Abs Sharpe Ratio'] = BacktestingSummary['Sharpe Ratio'].abs()
        
        if not isinstance(BacktestingSummary, pd.DataFrame):
            BacktestingSummary = BacktestingSummary.compute()
        if not isinstance(self.Scenario_IDMapping, pd.DataFrame):
            self.Scenario_IDMapping = self.Scenario_IDMapping.compute()
        
        BacktestingSummary = BacktestingSummary.merge(self.Scenario_IDMapping, how='left', on='scenario id')
        BacktestingSummary = BacktestingSummary.merge(self.AnalysisContext.FuturesData.TickerIDMapping, how='left', on='ticker id')
        FuturesProperty = FuturesStrategyBacktest.getFuturesProperty()
        BacktestingSummary = BacktestingSummary.merge(FuturesProperty, how='left', on='ticker')
        
        BacktestingSummary.loc[BacktestingSummary['ticker'].str.contains("RANDOM_NOISE"), 'Multiplier'] = 1
        BacktestingSummary.loc[BacktestingSummary['ticker'].str.contains("RANDOM_NOISE"), 'Commission'] = 0
        BacktestingSummary.loc[BacktestingSummary['ticker'].str.contains("RANDOM_NOISE"), 'TickSize'] = 0.1

        BacktestingSummary.loc[pd.isnull(BacktestingSummary['Multiplier']), 'Multiplier'] = 1
        BacktestingSummary.loc[pd.isnull(BacktestingSummary['Commission']), 'Commission'] = 0
        BacktestingSummary.loc[pd.isnull(BacktestingSummary['TickSize']), 'TickSize'] = 0.1

        BacktestingSummary['average return per trade after commission'] = BacktestingSummary['average return per trade']
        BacktestingSummary.loc[BacktestingSummary['average return per trade'] > 0, 'average return per trade after commission'] = BacktestingSummary['average return per trade'] - (BacktestingSummary['Commission'] * 2/ BacktestingSummary['Multiplier'])
        BacktestingSummary.loc[(BacktestingSummary['average return per trade'] > 0) & (BacktestingSummary['average return per trade after commission'] < 0), 'average return per trade after commission'] = 0
        BacktestingSummary.loc[BacktestingSummary['average return per trade'] < 0, 'average return per trade after commission'] = BacktestingSummary['average return per trade'] + (BacktestingSummary['Commission'] * 2/ BacktestingSummary['Multiplier'])
        BacktestingSummary.loc[(BacktestingSummary['average return per trade'] < 0) & (BacktestingSummary['average return per trade after commission'] > 0), 'average return per trade after commission'] = 0
        BacktestingSummary['Sharpe Ratio after commission'] = BacktestingSummary['average return per trade after commission'] / BacktestingSummary['stdev of point return per trade']
        BacktestingSummary['Abs Sharpe Ratio after commission'] = BacktestingSummary['Sharpe Ratio after commission'].abs()
        if SymmetricalStrategy:
            backtest_result_sorting_key = StrategyBacktest.SYMMETRICAL_TRADING_STRATEGY_SORTING_KEY
        else:
            backtest_result_sorting_key = StrategyBacktest.ASYMMETRICAL_TRADING_STRATEGY_SORTING_KEY
        BacktestingSummary = BacktestingSummary.sort_values(by=backtest_result_sorting_key, ascending=False)

        # BacktestingSummary.to_csv(r'C:\temp\BacktestingSummary beginning of FinishSummary sorted.csv')

        
        BacktestingSummaryDict = {}
        # for backtest_period in StrategyBacktest.BACKTEST_PERIOD_LABEL:
        for backtest_period in self.BacktestPeriodLabel:
            BacktestingSummaryDict[backtest_period] = pd.DataFrame()

        ticker_list = BacktestingSummary[['ticker']].drop_duplicates()
        for index, row in ticker_list.iterrows():
            BacktestingSummary_SingleTicker = BacktestingSummary.loc[BacktestingSummary['ticker'] == row['ticker']]
            
            for backtest_period in self.BacktestPeriodLabel:
                if backtest_period == 0:
                    MinRequiredTradeCount = self.MinimumTradeNumberCountForFullPeriod
                else:
                    MinRequiredTradeCount = backtest_period
                BacktestingSummaryDict[backtest_period] = pd.concat([BacktestingSummaryDict[backtest_period], BacktestingSummary_SingleTicker.loc[(BacktestingSummary_SingleTicker['backtest period'] == self.BacktestPeriodLabel[backtest_period]) & (BacktestingSummary_SingleTicker['number of trades'] >= MinRequiredTradeCount)].head(self.TOP_BACKTEST_RESULT_COUNT_PER_TICKER)])

        ColumnsToMerge = ScenarioDetailColumns + StrategyBacktest.COLUMNS_FOR_TRADE_RECORD_MERGING_WITH_BACKTEST_PERIOD
        BacktestPeriodColumnSuffix = self.BacktestPeriodLabel.copy()
        for backtest_period in BacktestPeriodColumnSuffix:
            BacktestPeriodColumnSuffix[backtest_period] = ' ' + BacktestPeriodColumnSuffix[backtest_period]
            
        BacktestPeriod = list(self.BacktestPeriodLabel)
        # print('BacktestPeriod is ' + str(BacktestPeriod))
            
        for BacktestPeriodIndex in range(len(self.BacktestPeriodLabel)):
            ColumnsWithPeriodLabel = []
            
            for ColumnItem in StrategyBacktest.COLUMNS_FOR_TRADE_RECORD_MERGING_WITH_BACKTEST_PERIOD:
                ColumnsWithPeriodLabel = ColumnsWithPeriodLabel + [ColumnItem]
                for BacktestPeriodIndex2 in range(len(self.BacktestPeriodLabel)):
                    if BacktestPeriodIndex != BacktestPeriodIndex2:
                        ColumnsWithPeriodLabel = ColumnsWithPeriodLabel + [ColumnItem + ' ' + self.BacktestPeriodLabel[BacktestPeriod[BacktestPeriodIndex2]]]
                        
            ColumnsToSelect = ScenarioDetailColumns + StrategyBacktest.COLUMNS_FOR_TRADE_RECORD_MERGING_WITHOUT_BACKTEST_PERIOD_HEAD + ColumnsWithPeriodLabel + StrategyBacktest.COLUMNS_FOR_TRADE_RECORD_MERGING_WITHOUT_BACKTEST_PERIOD_TAIL
            
            for BacktestPeriodIndex2 in range(len(self.BacktestPeriodLabel)):
                if BacktestPeriodIndex != BacktestPeriodIndex2:
                    BacktestingSummaryDict[BacktestPeriod[BacktestPeriodIndex]] = BacktestingSummaryDict[BacktestPeriod[BacktestPeriodIndex]].merge(BacktestingSummary.loc[BacktestingSummary['backtest period'] == self.BacktestPeriodLabel[BacktestPeriod[BacktestPeriodIndex2]]][ColumnsToMerge], how='left', on=ScenarioDetailColumns, suffixes=('', BacktestPeriodColumnSuffix[BacktestPeriod[BacktestPeriodIndex2]]))
            BacktestingSummaryDict[BacktestPeriod[BacktestPeriodIndex]] = BacktestingSummaryDict[BacktestPeriod[BacktestPeriodIndex]].sort_values(by=backtest_result_sorting_key, ascending=False)[ColumnsToSelect]
            
        return BacktestingSummaryDict

    def FillDataMatrix(self, df_data, x_matrix_column_name, y_matrix_row_names, data_sheet_names, MissingValueFilling = "Fill Zero", ModifyBackwardAsLastResort = False, data_sheet_override_mapping = None, FullIDGrid = None):
        for key in data_sheet_names:
            if isinstance(data_sheet_names, dict):
                sheet_name = data_sheet_names[key]
            else:
                sheet_name = key
            col_list = [x_matrix_column_name] + y_matrix_row_names + [key]
            df = df_data[col_list].copy()
            if FullIDGrid is not None:
                new_col_list = y_matrix_row_names.copy()
                new_col_list.append(x_matrix_column_name)
                df = FullIDGrid.merge(df, how='left', on=new_col_list)

            data_matrix = StrategyBacktest.to_numpy(df, x_matrix_column_name, y_matrix_row_names, key)
            
            data_matrix = data_matrix.copy(order="C")
            if key in ['long short flag', 'date id']:
                data_matrix = data_matrix.astype(np.int32)
            
            if MissingValueFilling == "Modified Following":
                self.DataMatrix[sheet_name] = CUDAFillModifiedFollowing(data_matrix, ModifyBackwardAsLastResort = ModifyBackwardAsLastResort)
            elif(MissingValueFilling == "Data Sheet Override"):
                self.DataMatrix[sheet_name] = CUDAFillByOverride(data_matrix, self.DataMatrix[data_sheet_override_mapping[key]], block_cutting_dimension = "Time Dimension")
            else:
                self.DataMatrix[sheet_name] = data_matrix

class BacktestItemLocator:
    def getBacktestItem(BacktestParameterDF, AnalysisContextList, TickerFilter = [], ResultOutputFolderPath = None, PerformContangoAdjustment = True, RandomNoiseTickerStdev = None, FillEveryTimeSlot = False, ActiveContractPircesTrimmedColumns = None, RapidCalibration = False, RapidCalibrationTopScenarioSelectedCount = 0, KeepOnlyWeekdays = False, DataTimeLowerBound = None, DataTimeUpperBound = None, InstrumentType = 'Futures', MarketTimeSectionTimeList = None, DebugFilepath = None, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch'):
        StrategyName =  BacktestParameterDF.loc[0, 'StrategyName']
        if (StrategyName == 'CorrelationOnSpecificTimeSectionStrategy'):
            from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy_CorrelationOnSpecificTimeSectionStrategy import BacktestCorrelationOnSpecificTimeSectionStrategy
            return BacktestCorrelationOnSpecificTimeSectionStrategy(BacktestParameterDF, AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath, BatchListDatabaseName = BatchListDatabaseName, BatchListTableName = BatchListTableName)
        if (StrategyName == 'SharpeRatioStrategy'):
            from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy_SharpeRatioStrategy import BacktestSharpeRatioStrategy
            return BacktestSharpeRatioStrategy(BacktestParameterDF, AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath, BatchListDatabaseName = BatchListDatabaseName, BatchListTableName = BatchListTableName)
        if (StrategyName == 'IndicatorStrategy'):
            from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy_IndicatorStrategy import BacktestIndicatorStrategy
            return BacktestIndicatorStrategy(BacktestParameterDF, AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath, BatchListDatabaseName = BatchListDatabaseName, BatchListTableName = BatchListTableName)
        if (StrategyName == 'MarketShockStrategy'):
            from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy_MarketShockStrategy import BacktestMarketShockStrategy
            return BacktestMarketShockStrategy(BacktestParameterDF, AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, DataTimeLowerBound = DataTimeLowerBound, DataTimeUpperBound = DataTimeUpperBound, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath, BatchListDatabaseName = BatchListDatabaseName, BatchListTableName = BatchListTableName)
        if (StrategyName == 'RangeTradeOnSpecificPastTimeRangeStrategy'):
            from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy_RangeTradeOnSpecificPastTimeRangeStrategy import BacktestRangeTradeOnSpecificPastTimeRangeStrategy
            return BacktestRangeTradeOnSpecificPastTimeRangeStrategy(BacktestParameterDF, AnalysisContextList, TickerFilter = TickerFilter, ResultOutputFolderPath = ResultOutputFolderPath, PerformContangoAdjustment = PerformContangoAdjustment, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, RapidCalibration = RapidCalibration, RapidCalibrationTopScenarioSelectedCount = RapidCalibrationTopScenarioSelectedCount, KeepOnlyWeekdays = KeepOnlyWeekdays, InstrumentType = InstrumentType, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath, BatchListDatabaseName = BatchListDatabaseName, BatchListTableName = BatchListTableName)
        
        


