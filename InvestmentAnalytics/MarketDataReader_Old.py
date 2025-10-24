# -*- coding: utf-8 -*-
"""
Created on Sun Jan 24 00:37:12 2021

@author: Henry Cheung
"""
import pymysql
import InvestmentAnalytics.Config as Config
import InvestmentAnalytics.DBUtil as DBUtil

import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from InvestmentAnalytics.CUDA.MarketDataReaderCUDALib import CUDAGetTickerIDWithSufficientData, CUDAFillModifiedFollowing, CUDAFillByOverride

class DailySpotPriceAnalysisContext:
    def __init__(self, StartDate, EndDate, MarketList, DailyVolumeLimit=1000000, DailyVolumeLimitMode = ['StartDate', 'EndDate', 'Average'], TickerFilter = None, DataAvailabilityLimit = 0.95, ExcludeETF = True, GPUMode = True):
        self.DailyData = DailySpotPriceReader(StartDate, EndDate, MarketList, DailyVolumeLimit, DailyVolumeLimitMode, TickerFilter, DataAvailabilityLimit, ExcludeETF, GPUMode)
        self.AddCoreIndicatorData()
    
    def AddIndicatorData(self, IndicatorMatrix):
        self.IndicatorDataMatrix.update(IndicatorMatrix)
        
    def AddCoreIndicatorData(self):
        self.IndicatorDataMatrix = {}

class PriceReader:
    def AddAutoincrementalID(df, ColumnsToAddID, IDColumnLabel, ascending=True):
        IDMapping = df[ColumnsToAddID].drop_duplicates().sort_values(by=ColumnsToAddID, ascending=ascending).reset_index().drop(['index'],axis='columns')
        IDMapping[IDColumnLabel] = IDMapping.index
        df = df.merge(IDMapping, on=ColumnsToAddID)
        return df, IDMapping
    
    def PrintDataMatrixDetail(self, data_sheet_names):
        # print('DataMatrix of ' + data_sheet_names + ' is with size ' + str(len(self.DataMatrix[data_sheet_names])) + ' x ' + str(len(self.DataMatrix[data_sheet_names][0])))
        # print(self.DataMatrix[data_sheet_names])
        pass
        
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

            price_matrix = PriceReader.to_numpy(df, x_matrix_column_name, y_matrix_row_names, key)
            price_matrix = price_matrix.copy(order="C")
            
            if MissingValueFilling == "Modified Following":
                self.DataMatrix[sheet_name] = CUDAFillModifiedFollowing(price_matrix, ModifyBackwardAsLastResort = ModifyBackwardAsLastResort).copy(order="C")
            elif(MissingValueFilling == "Data Sheet Override"):
                self.DataMatrix[sheet_name] = CUDAFillByOverride(price_matrix, self.DataMatrix[data_sheet_override_mapping[key]], block_cutting_dimension = "Time Dimension").copy(order="C")
            else:
                self.DataMatrix[sheet_name] = price_matrix

    def to_numpy(df, x_matrix_column_name, y_matrix_row_names, value_column, FillNaNWith=0):
        df = df.fillna(FillNaNWith)
        df = pd.pivot_table(df, index=y_matrix_row_names,columns=[x_matrix_column_name], values=value_column, aggfunc=np.mean).reset_index()
        df = df.drop(y_matrix_row_names,axis='columns').to_numpy()
        where_are_NaNs = np.isnan(df)
        df[where_are_NaNs] = FillNaNWith
        return df

class SpotPriceReader(PriceReader):
    def __init__(self, StartDate, EndDate, MarketList = None, GPUMode = True):
        self.StartDate = StartDate
        self.EndDate = EndDate
        self.MarketList = MarketList
        self.SpotPrices = None
        self.GPUMode = GPUMode
        self.DataMatrix = {}
        
    def FillByModifiedFollowing(df, GroupingColumns, IndexColumn, ValueColumns, DataAvailabilityLimit = None ):
        IndexList = df[IndexColumn].copy().drop_duplicates().reset_index()
        IndexList[IndexColumn + "Index"] = IndexList.index + 1
        IndexList = IndexList[[IndexColumn + "Index", IndexColumn]]
        df = df.merge(IndexList, left_on=IndexColumn, right_on=IndexColumn)
        GroupingColumnsList = df[GroupingColumns].copy().drop_duplicates()
        IndexListWithDummy = IndexList.copy()
        IndexListWithDummy['Dummy'] = 1
        GroupingColumnsList['Dummy'] = 1
        Framework = GroupingColumnsList.merge(IndexListWithDummy, left_on='Dummy', right_on='Dummy').drop(['Dummy'], axis=1)
        
        GroupingAndIndexColumns = GroupingColumns.copy()
        GroupingAndIndexColumns.append(IndexColumn + "Index")
        GroupingAndIndexOnlyColumns = GroupingAndIndexColumns.copy()
        GroupingAndIndexColumns.append(IndexColumn)
        FullData = Framework.merge(df, how='left', on=GroupingAndIndexColumns)
        
        if (DataAvailabilityLimit is not None):
            GroupingAndIndexAndValueColumns = GroupingAndIndexColumns.copy()
            GroupingAndIndexAndValueColumns.append(ValueColumns[0])
            FullDataWithOneValueColumns = FullData[GroupingAndIndexAndValueColumns].copy()
            FullDataWithOneValueColumns = pd.pivot_table(FullDataWithOneValueColumns, index=GroupingColumns, values=[IndexColumn, ValueColumns[0]], aggfunc = "count").reset_index()
            FullDataWithOneValueColumns['DataAvailabilityPercentage'] = FullDataWithOneValueColumns[ValueColumns[0]] / FullDataWithOneValueColumns[IndexColumn]
            TickerWithSufficientData = FullDataWithOneValueColumns[FullDataWithOneValueColumns['DataAvailabilityPercentage'] >= DataAvailabilityLimit][GroupingColumns]
            FullData = FullData.merge(TickerWithSufficientData, on=GroupingColumns)
            
        NullCount = sum(FullData.isnull().values.ravel())
        FullDataColumns = FullData.columns.values.tolist()
        while NullCount > 0:
            FullDataNextDateIndex = FullData.copy()
            FullDataNextDateIndex[IndexColumn + "Index"] = FullDataNextDateIndex[IndexColumn + "Index"] + 1
            FullData = FullData.merge(FullDataNextDateIndex, how='left', on=GroupingAndIndexOnlyColumns, suffixes=('', '_DayBefore'))
            for value_col in ValueColumns:
                FullData.loc[FullData[value_col].isna(), value_col] = FullData[value_col + '_DayBefore']
            FullData = FullData[FullDataColumns].copy()
            NullCount = sum(FullData.isnull().values.ravel())
            
        return [FullData, FullDataWithOneValueColumns]

class IntradayPriceAnalysisContext:
    def __init__(self, StartDate, EndDate, TimeFrame, IntradayPricesData, GPUMode = True, KeepDataframeData = False):
        self.IntradayPricesData = IntradayPricesData
        self.AddCoreIndicatorData()
        self.TimeFrame = TimeFrame
    
    def AddIndicatorData(self, IndicatorMatrix):
        self.IndicatorDataMatrix.update(IndicatorMatrix)
        
    def AddCoreIndicatorData(self):
        self.IndicatorDataMatrix = {}
        
    def GetResampledDataMatrix(self, DataLabel, TargetTimeFrame):
        if TargetTimeFrame == self.TimeFrame:
            return self.IntradayPricesData.DataMatrix[DataLabel]
        elif self.TimeFrame == '1 min' and TargetTimeFrame == '5 mins':
            return None
        return None
    

class FuturesPriceAnalysisContext(IntradayPriceAnalysisContext):
    def __init__(self, StartDate, EndDate, TimeFrame, PreFilterDataByTime = False, PreFilterDataStartTimeInStdUnit = None, PreFilterDataEndTimeInStdUnit = None, TickerFilter = [], GPUMode = True, KeepDataframeData = False, PerformContangoAdjustment = True, RandomNoiseTickerStdev = None, FillEveryTimeSlot = False, ActiveContractPircesTrimmedColumns = None, KeepOnlyWeekdays = False, DataTimeLowerBound = None, DataTimeUpperBound = None, MarketTimeSectionTimeList = None, DebugFilepath = None):
        print('Start loading futures price data at ' + str(datetime.now()))
        self.FuturesData = IBFuturesPriceReader(StartDate, EndDate, TimeFrame, PreFilterDataByTime = PreFilterDataByTime, PreFilterDataStartTimeInStdUnit = PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit = PreFilterDataEndTimeInStdUnit, TickerFilter = TickerFilter, GPUMode = GPUMode, KeepDataframeData = KeepDataframeData, PerformContangoAdjustment = PerformContangoAdjustment, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, KeepOnlyWeekdays = KeepOnlyWeekdays, DataTimeLowerBound = DataTimeLowerBound, DataTimeUpperBound = DataTimeUpperBound, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath)
        super().__init__(StartDate, EndDate, TimeFrame, self.FuturesData, GPUMode = True, KeepDataframeData = False)

class FXFuturesPriceAnalysisContext(IntradayPriceAnalysisContext):
    def __init__(self, StartDate, EndDate, TimeFrame, PreFilterDataByTime = False, PreFilterDataStartTimeInStdUnit = None, PreFilterDataEndTimeInStdUnit = None, TickerFilter = [], GPUMode = True, KeepDataframeData = False, PerformContangoAdjustment = True, RandomNoiseTickerStdev = None, FillEveryTimeSlot = False, ActiveContractPircesTrimmedColumns = None, KeepOnlyWeekdays = False, MarketTimeSectionTimeList = None, DebugFilepath = None):
        print('Start loading FX futures price data at ' + str(datetime.now()))
        self.FuturesData = FXFuturesPriceReader(StartDate, EndDate, TimeFrame, PreFilterDataByTime = PreFilterDataByTime, PreFilterDataStartTimeInStdUnit = PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit = PreFilterDataEndTimeInStdUnit, TickerFilter = TickerFilter, GPUMode = GPUMode, KeepDataframeData = KeepDataframeData, PerformContangoAdjustment = PerformContangoAdjustment, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, KeepOnlyWeekdays = KeepOnlyWeekdays, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath)
        super().__init__(StartDate, EndDate, TimeFrame, self.FuturesData, GPUMode = True, KeepDataframeData = False)


class CryptoPriceAnalysisContext(IntradayPriceAnalysisContext):
    def __init__(self, StartDate, EndDate, TimeFrame, PreFilterDataByTime = False, PreFilterDataStartTimeInStdUnit = None, PreFilterDataEndTimeInStdUnit = None, TickerFilter = [], GPUMode = True, KeepDataframeData = False, PerformContangoAdjustment = True, RandomNoiseTickerStdev = None, FillEveryTimeSlot = False, ActiveContractPircesTrimmedColumns = None, KeepOnlyWeekdays = False, MarketTimeSectionTimeList = None, DebugFilepath = None):
        print('Start loading Crypto price data at ' + str(datetime.now()))
        self.FuturesData = CryptoPriceReader(StartDate, EndDate, TimeFrame, PreFilterDataByTime = PreFilterDataByTime, PreFilterDataStartTimeInStdUnit = PreFilterDataStartTimeInStdUnit, PreFilterDataEndTimeInStdUnit = PreFilterDataEndTimeInStdUnit, TickerFilter = TickerFilter, GPUMode = GPUMode, KeepDataframeData = KeepDataframeData, PerformContangoAdjustment = PerformContangoAdjustment, RandomNoiseTickerStdev = RandomNoiseTickerStdev, FillEveryTimeSlot = FillEveryTimeSlot, ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns, KeepOnlyWeekdays = KeepOnlyWeekdays, MarketTimeSectionTimeList = MarketTimeSectionTimeList, DebugFilepath = DebugFilepath)
        super().__init__(StartDate, EndDate, TimeFrame, self.FuturesData, GPUMode = True, KeepDataframeData = False)
    

class FuturesPriceReader(SpotPriceReader):
    # MarketTimeSection = {'Minute': pd.DataFrame({'SectionName':['HourPreOpen', 'Morning', 'Noon', 'BeforeClose'],'SectionID':[0, 1, 2, 3],
    #     'Start':[8*60+30, 9*60+30, 11*60, 15*60], 'End':[9*60+30-1, 11*60-1, 15*60-1, 16*60-1]})}
    
    
    DefaultMarketTimeSection = pd.DataFrame({'SectionID':[0, 1, 2, 3],
        'Start':[8*60+30, 9*60+30, 11*60, 15*60], 'End':[9*60+30-1, 11*60-1, 15*60-1, 16*60-1]})
    # DefaultMarketTimeSection = [8*60+30, 9*60+30, 11*60, 15*60, 16*60]
    
    
    RANDOM_NOISE_TICKER_INITIAL_PRICE = 10000
    RANDOM_NOISE_TICKER_INITIAL_VOL = 10000
    RANDOM_NOISE_TICKER_NAME = 'RANDOM_NOISE'
    # RANDOM_NOISE_TICKER_STDEV = 0.4/250/10
    RANDOM_NOISE_TICKER_MEAN = 0
    
    def __init__(self, StartDate, EndDate, TimeFrame, PreFilterDataByTime = False, PreFilterDataStartTimeInStdUnit = None, PreFilterDataEndTimeInStdUnit = None,  TickerFilter = [], GPUMode = True, KeepDataframeData = False, PerformContangoAdjustment = True, RandomNoiseTickerStdev = None, FillEveryTimeSlot = False, ActiveContractPircesTrimmedColumns = None, KeepOnlyWeekdays = False, DataTimeLowerBound = None, DataTimeUpperBound = None, LoadBidAskPrices = False, MarketTimeSectionTimeList = None, DebugFilepath = None):
        super().__init__(StartDate, EndDate, ['XUSA'], GPUMode=GPUMode)
        self.InstrumentType = self.GetInstrumentType()
        self.TickerIDMapping = None
        self.DateIDMapping = None
        self.TimeFrame = TimeFrame
        self.KeepDataframeData = KeepDataframeData
        if MarketTimeSectionTimeList is None:
            self.MarketTimeSection = FuturesPriceReader.DefaultMarketTimeSection
        else:
            self.MarketTimeSection = MarketTimeSectionTimeList
        print('self.MarketTimeSection is')
        print(self.MarketTimeSection)
        self.LoadBidAskPrices = LoadBidAskPrices
        print('self.LoadBidAskPrices is ' + str(self.LoadBidAskPrices))
        self.DebugFilepath = DebugFilepath
        self.PerformContangoAdjustment = PerformContangoAdjustment
        if TickerFilter is None:
            self.TickerFilter = []
        else:
            self.TickerFilter = TickerFilter
        self.PreFilterDataByTime = PreFilterDataByTime
        self.PreFilterDataStartTimeInStdUnit = PreFilterDataStartTimeInStdUnit
        self.PreFilterDataEndTimeInStdUnit = PreFilterDataEndTimeInStdUnit
        self.RandomNoiseTickerStdev = RandomNoiseTickerStdev
        self.FillEveryTimeSlot = FillEveryTimeSlot
        self.ActiveContractPircesTrimmedColumns = ActiveContractPircesTrimmedColumns
        self.KeepOnlyWeekdays = KeepOnlyWeekdays
        self.DataTimeLowerBound = DataTimeLowerBound
        self.DataTimeUpperBound = DataTimeUpperBound
        self.LoadRawData()
        self.AverageVolPerMarketTimeSection = None
        # self.CheckMaxVolumeHalfHourSection()
        
    def getAverageVolPerMarketTimeSection(self):
        if self.AverageVolPerMarketTimeSection is None:
            self.AverageVolPerMarketTimeSection = pd.pivot_table(self.ActiveContractPrices.loc[self.ActiveContractPrices['DataType'] == 'TRADES'], values='vol', index=['ticker id', 'MarketTimeSectionID'], aggfunc=np.mean).reset_index()
        return self.AverageVolPerMarketTimeSection
        
    # def AttachMarketTimeSection(ActiveContractPrices, TimeUnit = 'Minute', TimeInStandardUnitColumnName = 'TimeInStandardUnit'):
    #     print('Start Attaching Market Time Section')
    #     ActiveContractPrices['MarketTimeSection'] = 'Other'
    #     # for y in range(0, len(IBFuturesPriceReader.MarketTimeSection[TimeUnit])):
    #     for y in range(0, len(FuturesPriceReader.MarketTimeSection[TimeUnit])):
    #         print(y)
    #         # ActiveContractPrices.loc[(ActiveContractPrices[TimeInStandardUnitColumnName] >= IBFuturesPriceReader.MarketTimeSection[TimeUnit].loc[y, 'Start']) & (ActiveContractPrices[TimeInStandardUnitColumnName] <= IBFuturesPriceReader.MarketTimeSection[TimeUnit].loc[y, 'End']), 'MarketTimeSection'] = IBFuturesPriceReader.MarketTimeSection[TimeUnit].loc[y, 'SectionName']
    #         ActiveContractPrices.loc[(ActiveContractPrices[TimeInStandardUnitColumnName] >= FuturesPriceReader.MarketTimeSection[TimeUnit].loc[y, 'Start']) & (ActiveContractPrices[TimeInStandardUnitColumnName] <= FuturesPriceReader.MarketTimeSection[TimeUnit].loc[y, 'End']), 'MarketTimeSection'] = FuturesPriceReader.MarketTimeSection[TimeUnit].loc[y, 'SectionName']
                    
        # return ActiveContractPrices
        
        
    # def AttachMarketTimeSectionID(ActiveContractPrices, TimeUnit = 'Minute', TimeInStandardUnitColumnName = 'TimeInStandardUnit'):
    def AttachMarketTimeSectionID(self, df, TimeInStandardUnitColumnName = 'TimeInStandardUnit'):
        # print('Start Attaching Market Time Section ID')
        df['MarketTimeSectionID'] = -1
        for y in range(0, len(self.MarketTimeSection)):
            df.loc[(df[TimeInStandardUnitColumnName] >= self.MarketTimeSection.loc[y, 'Start']) & (df[TimeInStandardUnitColumnName] <= self.MarketTimeSection.loc[y, 'End']), 'MarketTimeSectionID'] = self.MarketTimeSection.loc[y, 'SectionID']

        # df['MarketTimeSectionID'] = 0
        # i = 0
        # for y in range(0, len(self.MarketTimeSection) - 1):
        #     df.loc[(df[TimeInStandardUnitColumnName] > self.MarketTimeSection[y]) & (df[TimeInStandardUnitColumnName] <= self.MarketTimeSection[y+1]), 'MarketTimeSectionID'] = y + 1
        # df.loc[df[TimeInStandardUnitColumnName] > self.MarketTimeSection[len(self.MarketTimeSection) - 1], 'MarketTimeSectionID'] = len(self.MarketTimeSection)
        return df

    def CheckMaxVolumeHalfHourSection(self):
        ActiveContractPrices_TRADES_vol = self.ActiveContractPrices[self.ActiveContractPrices['DataType'] == 'TRADES'][['ticker', 'Date', 'Hour', 'Minute', 'vol']]
        ActiveContractPrices_TRADES_vol['RoundDownMinute'] = 30
        ActiveContractPrices_TRADES_vol.loc[ActiveContractPrices_TRADES_vol['Minute'] < 30, 'RoundDownMinute'] = 0
        ActiveContractPrices_TRADES_vol_per_section = pd.pivot_table(ActiveContractPrices_TRADES_vol, values='vol', index=['ticker', 'Hour', 'RoundDownMinute'], aggfunc=np.sum).reset_index()
        ActiveContractPrices_TRADES_max_vol = pd.pivot_table(ActiveContractPrices_TRADES_vol_per_section, values='vol', index=['ticker'], aggfunc=max).reset_index()
        ActiveContractPrices_TRADES_max_vol = ActiveContractPrices_TRADES_max_vol.merge(ActiveContractPrices_TRADES_vol_per_section, on=['ticker', 'vol'])
        ActiveContractPrices_TRADES_max_vol = ActiveContractPrices_TRADES_max_vol.loc[ActiveContractPrices_TRADES_max_vol['ticker'] != IBFuturesPriceReader.RANDOM_NOISE_TICKER_NAME]
        print('Half Hour Section with Max Vol is')
        print(ActiveContractPrices_TRADES_max_vol)
        ActiveContractPrices_TRADES_vol_NQ = ActiveContractPrices_TRADES_vol[ActiveContractPrices_TRADES_vol['ticker'] == 'NQ']
        if len(ActiveContractPrices_TRADES_vol_NQ) > 0:
            ActiveContractPrices_TRADES_vol_per_section_NQ = pd.pivot_table(ActiveContractPrices_TRADES_vol_NQ, values='vol', index=['ticker', 'Hour', 'RoundDownMinute'], aggfunc=np.sum).reset_index()
            print('Half Hour Section Vol of NQ is')
            print(ActiveContractPrices_TRADES_vol_per_section_NQ)
    
    def GetDataframeFromDB(self, TickerFilter = []):
        return pd.DataFrame(columns=['ticker', 'instrumenttype', 'expiry', 'DataType', 'timeframe', 'tDateTime', 'high', 'low', 'open', 'close', 'vol', 'src'])

    def perdelta(start, end, delta):
        curr = start
        while curr < end:
            yield curr
            curr += delta
            
    def datetime_range(start, end, delta):
        current = start
        if not isinstance(delta, timedelta):
            delta = timedelta(**delta)
        while current < end:
            yield current
            current += delta
    
    def datetime_range_list(start, end, delta):
        # print('in datetime_range_list')
        # print(start)
        # print(end)
        # return list(FuturesPriceReader.datetime_range(start, end, delta))
        # return list(FuturesPriceReader.datetime_range(datetime.combine(start, datetime.min.time()), datetime.combine(end, datetime.min.time()), delta))
        return list(FuturesPriceReader.datetime_range(datetime.combine(start, datetime.min.time()), datetime.combine(end, datetime.max.time()), delta))
    
    def GetInstrumentType(self):
        return 'Futures'
    
    def GetContantPriceTicker(self):
        # date_list = [self.StartDate+timedelta(days=x) for x in range((self.EndDate-self.StartDate).days)]
        # df = pd.DataFrame(date_list, columns=['date'])
        # df['Dummy'] = 1
        if (self.TimeFrame == '1 min'):
            data = FuturesPriceReader.datetime_range_list(self.StartDate, self.EndDate,  {'minutes':1})
            # print('the first time is')
            # print(data[0])
            df = pd.DataFrame(data, columns=['tDateTime'])
        elif (self.TimeFrame == '10 secs'):
            data = FuturesPriceReader.datetime_range_list(self.StartDate, self.EndDate,  {'seconds':10})
            print('the first few times are')
            print(str([data[0], data[1], data[2], data[3]]))
            # df = pd.DataFrame()
            df = pd.DataFrame(data, columns=['tDateTime'])
        else:
            df = pd.DataFrame()
        df['DayOfWeek'] = df['tDateTime'].dt.dayofweek
        df = df.loc[df['DayOfWeek'] < 5]
        df['Hour'] = pd.to_datetime(df['tDateTime']).dt.hour
        df['Minute'] = pd.to_datetime(df['tDateTime']).dt.minute
        df = df.loc[df['Hour'] < 17]
        df['ticker'] = 'CONSTANT'
        df['instrumenttype'] = self.GetInstrumentType()
        df['expiry'] = 0
        df['DataType'] = 'TRADES'
        df['timeframe'] = self.TimeFrame
        df['high'] = 10000
        df['low'] = 10000
        df['open'] = 10000
        df['close'] = 10000
        df['vol'] = 0
        df['src'] = ''
        df.drop(columns=['DayOfWeek', 'Hour', 'Minute'], inplace=True)
        # print('In GetContantPriceTicker, df is')
        # print(df)
        return df

    def setActiveContractPrice(self, Prices_df):
        self.ActiveContract, self.RolloverDate = IBFuturesPriceReader.GetActiveExpiry(Prices_df)
        df5 = Prices_df[['ticker', 'Date', 'expiry']].drop_duplicates().merge(self.ActiveContract[['ticker', 'Date', 'Active_expiry']], left_on=['ticker', 'Date', 'expiry'], right_on=['ticker', 'Date', 'Active_expiry'])
        df5 = df5.loc[df5['Active_expiry'] != np.nan]

        self.ActiveContractPrices = Prices_df.merge(self.ActiveContract[['ticker', 'Date', 'Active_expiry']], left_on=['ticker', 'Date', 'expiry'], right_on=['ticker', 'Date', 'Active_expiry'])[['ticker', 'expiry', 'DataType', 'tDateTime', 'high', 'low', 'open', 'close', 'vol', 'Date', 'Hour', 'Minute', 'TimeInStandardUnit']]

        df4 = Prices_df[['ticker', 'Date']].drop_duplicates().merge(df5, left_on=['ticker', 'Date'], right_on=['ticker', 'Date'], how='left')
        MissingActiveContract = df4.loc[df4['Active_expiry'].isnull()]
        MissingActiveContract = Prices_df[['ticker', 'Date', 'expiry']].drop_duplicates().merge(MissingActiveContract[['ticker', 'Date']], left_on=['ticker', 'Date'], right_on=['ticker', 'Date'])
        
        if len(MissingActiveContract) > 0:
            MissingActiveContract = pd.pivot_table(MissingActiveContract, values='expiry', index=['ticker', 'Date'], aggfunc=min).reset_index().sort_values(by=['ticker', 'Date'])
            MissingActiveContractPrices = Prices_df.merge(MissingActiveContract, on=['ticker', 'Date', 'expiry'])[['ticker', 'expiry', 'DataType', 'tDateTime', 'high', 'low', 'open', 'close', 'vol', 'Date', 'Hour', 'Minute', 'TimeInStandardUnit']]
    
            # self.ActiveContractPrices = Prices_df.merge(self.ActiveContract[['ticker', 'Date', 'Active_expiry']], left_on=['ticker', 'Date', 'expiry'], right_on=['ticker', 'Date', 'Active_expiry'])[['ticker', 'expiry', 'DataType', 'tDateTime', 'high', 'low', 'open', 'close', 'vol', 'Date', 'Hour', 'Minute', 'TimeInStandardUnit']]
            # self.ActiveContractPrices = self.ActiveContractPrices.append(MissingActiveContractPrices)
            self.ActiveContractPrices = pd.concat([self.ActiveContractPrices, MissingActiveContractPrices])
    
    def LoadRawData(self):
        print('PreFilterDataByTime is ' + str(self.PreFilterDataByTime))
        print('PreFilterDataStartTimeInStdUnit is ' + str(self.PreFilterDataStartTimeInStdUnit))
        print('PreFilterDataEndTimeInStdUnit is ' + str(self.PreFilterDataEndTimeInStdUnit))

        Prices_df = self.GetDataframeFromDB(self.TickerFilter)
        # print('Data from GetDataframeFromDB is')
        # print(Prices_df)
        
        if self.FillEveryTimeSlot:
            # Prices_df = Prices_df.append(self.GetContantPriceTicker())
            Prices_df = pd.concat([Prices_df,self.GetContantPriceTicker()], ignore_index=True)
            
        Prices_df['Date'] = pd.to_datetime(Prices_df['tDateTime']).dt.date
        Volume_df = Prices_df[Prices_df['DataType'] == 'TRADES'][['ticker', 'expiry','Date', 'tDateTime', 'vol']]
        Volume_df = pd.pivot_table(Volume_df, values='vol', index=['ticker', 'Date', 'expiry'], aggfunc=np.sum).reset_index()
        # Volume_df.to_csv(r'G:\TradeAnalysisProject\temp\Volume_df_original.csv')


        if self.KeepOnlyWeekdays:
            Prices_df['DayOfWeek'] = Prices_df['tDateTime'].dt.dayofweek
            Prices_df = Prices_df.loc[Prices_df['DayOfWeek'] < 5]
        Prices_df['Hour'] = pd.to_datetime(Prices_df['tDateTime']).dt.hour
        Prices_df['Minute'] = pd.to_datetime(Prices_df['tDateTime']).dt.minute
        if (self.TimeFrame == "1 min"):
            Prices_df['TimeInStandardUnit'] = Prices_df['Hour'] * 60 + Prices_df['Minute']
        if (self.TimeFrame == "10 secs"):
            Prices_df['Second'] = pd.to_datetime(Prices_df['tDateTime']).dt.second
            Prices_df['TimeInStandardUnit'] = (Prices_df['Hour'] * 60 + Prices_df['Minute']) * 6 + Prices_df['Second'] / 10

        if self.PreFilterDataByTime:
            Prices_df = Prices_df.loc[(Prices_df['TimeInStandardUnit'] >= self.PreFilterDataStartTimeInStdUnit) & (Prices_df['TimeInStandardUnit'] <= self.PreFilterDataEndTimeInStdUnit)]
            
        self.setActiveContractPrice(Prices_df)
        
        self.ActiveContractPrices['high_adj'] = self.ActiveContractPrices['high']
        self.ActiveContractPrices['low_adj'] = self.ActiveContractPrices['low']
        self.ActiveContractPrices['open_adj'] = self.ActiveContractPrices['open']
        self.ActiveContractPrices['close_adj'] = self.ActiveContractPrices['close']
        self.ActiveContractPrices['expiry_adj'] = self.ActiveContractPrices['expiry']
        
        
        
        if self.PerformContangoAdjustment:
            # self.ActiveContractPrices = IBFuturesPriceReader.ContangoAdjustment(self.ActiveContractPrices, RolloverDate_df)
            # self.ActiveContractPrices, self.RolloverDate = IBFuturesPriceReader.ContangoAdjustment(self.ActiveContractPrices, self.RolloverDate)
            self.ActiveContractPrices, self.RolloverDate = FuturesPriceReader.ContangoAdjustment(self.ActiveContractPrices, self.RolloverDate)
            # self.ActiveContractPrices.to_csv(r'd:\temp\ActiveContractPricesAfterContangoAdj.csv')
            
        # self.ActiveContractPrices = IBFuturesPriceReader.AttachMarketTimeSectionID(self.ActiveContractPrices)
        # self.ActiveContractPrices = FuturesPriceReader.AttachMarketTimeSectionID(self.ActiveContractPrices)
        self.ActiveContractPrices = self.AttachMarketTimeSectionID(self.ActiveContractPrices)
        
        

        # self.ActiveContractPrices, self.TickerIDMapping = PriceReader.AddAutoincrementalID(self.ActiveContractPrices, ['ticker'], 'ticker id')
        # print('TickerIDMapping is')
        # print(self.TickerIDMapping)
        # self.TickerIDMapping.to_csv(r'd:\temp\TickerIDMapping.csv')
            
        self.ActiveContractPrices, self.DateIDMapping = PriceReader.AddAutoincrementalID(self.ActiveContractPrices, ['Date'], 'date id')
        self.ActiveContractPrices, self.TimeIDMapping = PriceReader.AddAutoincrementalID(self.ActiveContractPrices, ['Date', 'tDateTime'], 'time id')
        self.TimeIDMapping = self.TimeIDMapping.merge(self.DateIDMapping, on='Date')
        
        self.TimeIDMapping['Hour'] = pd.to_datetime(self.TimeIDMapping['tDateTime']).dt.hour
        self.TimeIDMapping['Minute'] = pd.to_datetime(self.TimeIDMapping['tDateTime']).dt.minute
        if (self.TimeFrame == "1 min"):
            self.TimeIDMapping['TimeInStandardUnit'] = self.TimeIDMapping['Hour'] * 60 + self.TimeIDMapping['Minute']
        if (self.TimeFrame == "10 secs"):
            self.TimeIDMapping['Second'] = pd.to_datetime(self.TimeIDMapping['tDateTime']).dt.second
            self.TimeIDMapping['TimeInStandardUnit'] = (self.TimeIDMapping['Hour'] * 60 + self.TimeIDMapping['Minute']) * 6 + self.TimeIDMapping['Second'] / 10
            self.TimeIDMapping['TimeInStandardUnit'] = self.TimeIDMapping['TimeInStandardUnit'].astype(int)
            # self.TimeIDMapping['TimeInStandardUnit'] = (int) (self.TimeIDMapping['Hour'] * 60 + self.TimeIDMapping['Minute']) * 6 + self.TimeIDMapping['Second'] / 10
        # self.TimeIDMapping = IBFuturesPriceReader.AttachMarketTimeSectionID(self.TimeIDMapping)
        self.TimeIDMapping = self.AttachMarketTimeSectionID(self.TimeIDMapping)
        
        # TimeInStandardUnitToMarketTimeSectioIDMapping = self.TimeIDMapping[['TimeInStandardUnit', 'MarketTimeSectionID']].drop_duplicates().sort_values(by=['TimeInStandardUnit'])
        TimeInStandardUnitToMarketTimeSectioIDMapping = self.TimeIDMapping[['TimeInStandardUnit', 'MarketTimeSectionID']].drop_duplicates()
        # MinTimeInStandardUnit = TimeInStandardUnitToMarketTimeSectioIDMapping['TimeInStandardUnit'].min()
        MaxTimeInStandardUnit = TimeInStandardUnitToMarketTimeSectioIDMapping['TimeInStandardUnit'].max()
        TimeInStandardUnitDf= pd.DataFrame(list(range(MaxTimeInStandardUnit + 1)), columns =['TimeInStandardUnit'])
        TimeInStandardUnitToMarketTimeSectioIDMapping = TimeInStandardUnitDf.merge(TimeInStandardUnitToMarketTimeSectioIDMapping, how='left', on='TimeInStandardUnit')
        TimeInStandardUnitToMarketTimeSectioIDMapping["MarketTimeSectionID"].fillna(-1, inplace = True)
        TimeInStandardUnitToMarketTimeSectioIDMapping = TimeInStandardUnitToMarketTimeSectioIDMapping.sort_values(by=['TimeInStandardUnit'])
        
            
        # self.FillDataMatrix(TimeInStandardUnitToMarketTimeSectioIDMapping, 'TimeInStandardUnit', ['MarketTimeSectionID'], {'close_adj': 'TRADES_close_adj', 'MarketTimeSectionID': 'MarketTimeSectionID', 'TimeInStandardUnit': 'TimeInStandardUnit'},MissingValueFilling = "Modified Following", ModifyBackwardAsLastResort = True, FullIDGrid = FullIDGrid)
        self.DataMatrix['TimeInStandardUnitToMarketTimeSectioIDMapping'] = TimeInStandardUnitToMarketTimeSectioIDMapping[['MarketTimeSectionID']].to_numpy().copy(order="C")
        
        # df = self.ActiveContractPrices.head(10)
        # df.to_csv(r'E:\TradeAnalysisProject\RoutineAnalysis\SharpeRatioStrategy\Debug\ActiveContractPrices head.csv', index=False)
        if self.DebugFilepath is not None:
            df = self.ActiveContractPrices.head(10)
            df.to_csv(self.DebugFilepath + r'\ActiveContractPrices head.csv', index=False)
        
        # print('TimeIDMapping is')
        # print(self.TimeIDMapping)
        # self.TimeIDMapping.to_csv(r'C:\temp\TimeIDMapping after AddAutoincrementalID.csv', index=False)
        
        if self.DebugFilepath is not None:
            self.TimeIDMapping.to_csv(self.DebugFilepath + r'\TimeIDMapping after AddAutoincrementalID.csv', index=False)
        
        # df_all = pd.DataFrame()
        if self.RandomNoiseTickerStdev is not None:
            NoiseTickerIndex = 1
            for stdev in self.RandomNoiseTickerStdev:
                for data_type in ['TRADES', 'BID', 'ASK']:
                    df = self.TimeIDMapping.copy()
                    df['DataType'] = data_type
                    df['ticker'] = IBFuturesPriceReader.RANDOM_NOISE_TICKER_NAME + str(NoiseTickerIndex)
                    df['expiry'] = 0
                    df['expiry_adj'] = 0
                    df['close'] = IBFuturesPriceReader.RANDOM_NOISE_TICKER_INITIAL_PRICE
                    # s = np.random.lognormal(IBFuturesPriceReader.RANDOM_NOISE_TICKER_MEAN, IBFuturesPriceReader.RANDOM_NOISE_TICKER_STDEV, len(df) - 1).tolist()
                    s = np.random.lognormal(IBFuturesPriceReader.RANDOM_NOISE_TICKER_MEAN - (stdev*stdev)/2, stdev, len(df) - 1).tolist()
                    s = [1] + s
                    for i in range(1, len(s)):
                        s[i] = s[i-1] * s[i]
                    df['close move'] = s
                    df['close'] = df['close'] * df['close move']
                    df['high'] = df['close']
                    df['low'] = df['close']
                    df['open'] = df['close']
                    df['close_adj'] = df['close']
                    df['high_adj'] = df['close']
                    df['low_adj'] = df['close']
                    df['open_adj'] = df['close']

                    if data_type == 'TRADES':
                        df['vol'] = IBFuturesPriceReader.RANDOM_NOISE_TICKER_INITIAL_VOL
                        s = np.random.lognormal(IBFuturesPriceReader.RANDOM_NOISE_TICKER_MEAN - (stdev*stdev)/2, stdev, len(df) - 1).tolist()
                        s = [1] + s
                        for i in range(1, len(s)):
                            s[i] = s[i-1] * s[i]
                        df['vol move'] = s
                        df['vol'] = df['vol'] * df['vol move']
                    else:
                        df['vol'] = 0

                    df = df[list(self.ActiveContractPrices.columns)]
                    
                    self.ActiveContractPrices = pd.concat([self.ActiveContractPrices, df])
                    # self.ActiveContractPrices = self.ActiveContractPrices.append(df)
                NoiseTickerIndex = NoiseTickerIndex + 1
                
        self.ActiveContractPrices = self.ActiveContractPrices.loc[self.ActiveContractPrices['ticker'] != 'CONSTANT']
                
        self.ActiveContractPrices, self.TickerIDMapping = PriceReader.AddAutoincrementalID(self.ActiveContractPrices, ['ticker'], 'ticker id')
        # print('TickerIDMapping is')
        # print(self.TickerIDMapping)
        
        # self.TickerIDMapping.to_csv(r'd:\temp\TickerIDMapping.csv', index=False)
        if self.DebugFilepath is not None:
            self.TickerIDMapping.to_csv(self.DebugFilepath + r'\TickerIDMapping.csv', index=False)
                
        # self.ActiveContractPrices.to_csv(r'C:\temp\ActiveContractPricesWithTimeID.csv')
        # df = self.ActiveContractPrices.loc[self.ActiveContractPrices['ticker'] == 'SI']
        # df = df.sort_values(by=['tDateTime'])
        # df.to_csv(r'G:\TradeAnalysisProject\temp\ActiveContractPricesWithTimeID_SI.csv')
        
        # self.ActiveContractPrices.loc[self.ActiveContractPrices['DataType'] == 'TRADES'].to_csv(r'd:\temp\ActiveContractPricesWithTimeID_TRADES.csv')
        
        a_df = self.TickerIDMapping[['ticker id']].copy()
        a_df['Dummy'] = 1
        b_df = self.TimeIDMapping[['time id']].copy()
        b_df['Dummy'] = 1
        FullIDGrid = a_df.merge(b_df, on='Dummy').drop(['Dummy'],axis='columns')
        # print('FullIDGrid is')
        # print(FullIDGrid)
        # FullIDGrid.to_csv(r'd:\temp\FullIDGrid.csv')
        

        if self.GPUMode:

            
            # print('before error 1')
            # print(self.ActiveContractPrices)
            # ActiveContractPrices_TRADES = self.ActiveContractPrices[self.ActiveContractPrices['DataType'] == 'TRADES' & self.ActiveContractPrices['ticker id'] == 0]
            ActiveContractPrices_TRADES = self.ActiveContractPrices[self.ActiveContractPrices['DataType'] == 'TRADES']
            # print('before error 2')
            # print(ActiveContractPrices_TRADES)
            # ActiveContractPrices_TRADES = ActiveContractPrices_TRADES[ActiveContractPrices_TRADES['ticker id'] == 0]
            # print('before error 3')
            # print(ActiveContractPrices_TRADES)
            ActiveContractPrices_TRADES = ActiveContractPrices_TRADES[['time id', 'tDateTime', 'date id', 'ticker id', 'close_adj', 'MarketTimeSectionID', 'TimeInStandardUnit', 'high_adj', 'low_adj', 'open_adj', 'vol']]
            # print('before error 4')
            # print(ActiveContractPrices_TRADES)
            
            # ActiveContractPrices_TRADES = self.ActiveContractPrices[self.ActiveContractPrices['DataType'] == 'TRADES'][['time id', 'tDateTime', 'date id', 'ticker id', 'close_adj', 'MarketTimeSectionID', 'TimeInStandardUnit', 'high_adj', 'low_adj', 'open_adj', 'vol']]
            # ActiveContractPrices_TRADES = self.ActiveContractPrices[self.ActiveContractPrices['DataType'] == 'TRADES' & self.ActiveContractPrices['ticker id'] == 0][['time id', 'tDateTime', 'date id', 'ticker id', 'close_adj', 'MarketTimeSectionID', 'TimeInStandardUnit', 'high_adj', 'low_adj', 'open_adj', 'vol']]
            
            # ActiveContractPrices_TRADES.to_csv(r'd:\temp\ActiveContractPrices_TRADESWithTimeID.csv')
            

            # ActiveContractPrices_TRADES.to_csv(r'E:\TradeAnalysisProject\RoutineAnalysis\SharpeRatioStrategy\Debug\ActiveContractPrices_TRADESWithTimeID.csv', index=False)
            
            if self.DebugFilepath is not None:
                ActiveContractPrices_TRADES.to_csv(self.DebugFilepath + r'\ActiveContractPrices_TRADESWithTimeID.csv', index=False)
                
            self.FillDataMatrix(ActiveContractPrices_TRADES, 'time id', ['ticker id'], {'close_adj': 'TRADES_close_adj', 'MarketTimeSectionID': 'MarketTimeSectionID'},MissingValueFilling = "Modified Following", ModifyBackwardAsLastResort = True, FullIDGrid = FullIDGrid)

            if self.DebugFilepath is not None:
                try:
                    close_price_matrix = self.DataMatrix['TRADES_close_adj'].T.copy(order="C")
                    df = pd.DataFrame(data=close_price_matrix, columns=['close_adj'])
                    df.to_csv(self.DebugFilepath + r'\TRADES_close_adj_AfterFillDataMatrix.csv', index=False)
                except:
                    pass


            self.DataMatrix['TimeInStandardUnit'] = self.TimeIDMapping['TimeInStandardUnit'].to_numpy()

            self.DataMatrix['date id'] = self.TimeIDMapping['date id'].to_numpy()
            
            self.PrintDataMatrixDetail('TRADES_close_adj')
            self.PrintDataMatrixDetail('MarketTimeSectionID')
            self.PrintDataMatrixDetail('TimeInStandardUnit')
            
            self.FillDataMatrix(ActiveContractPrices_TRADES, 'time id', ['ticker id'], {'high_adj': 'TRADES_high_adj', 'low_adj': 'TRADES_low_adj', 'open_adj': 'TRADES_open_adj'},MissingValueFilling = "Data Sheet Override", data_sheet_override_mapping = {'high_adj': 'TRADES_close_adj', 'low_adj': 'TRADES_close_adj', 'open_adj': 'TRADES_close_adj'}, FullIDGrid = FullIDGrid)

            if self.DebugFilepath is not None:
                try:
                    price_matrix = self.DataMatrix['TRADES_high_adj'].T.copy(order="C")
                    df = pd.DataFrame(data=price_matrix, columns=['high_adj'])
                    df.to_csv(self.DebugFilepath + r'\TRADES_high_adj_AfterFillDataMatrix.csv', index=False)
                    price_matrix = self.DataMatrix['TRADES_low_adj'].T.copy(order="C")
                    df = pd.DataFrame(data=price_matrix, columns=['low_adj'])
                    df.to_csv(self.DebugFilepath + r'\TRADES_low_adj_AfterFillDataMatrix.csv', index=False)
                except:
                    pass

            self.PrintDataMatrixDetail('TRADES_high_adj')
            self.PrintDataMatrixDetail('TRADES_low_adj')
            self.PrintDataMatrixDetail('TRADES_open_adj')
            self.FillDataMatrix(ActiveContractPrices_TRADES, 'time id', ['ticker id'], ['vol'], FullIDGrid = FullIDGrid)
            self.PrintDataMatrixDetail('vol')
            
            if self.LoadBidAskPrices:

                ActiveContractPrices_BID = self.ActiveContractPrices[self.ActiveContractPrices['DataType'] == 'BID'][['time id', 'ticker id', 'close_adj', 'MarketTimeSectionID', 'high_adj', 'low_adj', 'open_adj', 'vol']]
                self.FillDataMatrix(ActiveContractPrices_BID, 'time id', ['ticker id'], {'close_adj': 'BID_close_adj'},MissingValueFilling = "Modified Following", ModifyBackwardAsLastResort = True, FullIDGrid = FullIDGrid)
                self.PrintDataMatrixDetail('BID_close_adj')
                
                self.FillDataMatrix(ActiveContractPrices_BID, 'time id', ['ticker id'], {'high_adj': 'BID_high_adj', 'low_adj': 'BID_low_adj', 'open_adj': 'BID_open_adj'},MissingValueFilling = "Data Sheet Override", data_sheet_override_mapping = {'high_adj': 'BID_close_adj', 'low_adj': 'BID_close_adj', 'open_adj': 'BID_close_adj'}, FullIDGrid = FullIDGrid)
                self.PrintDataMatrixDetail('BID_high_adj')
                self.PrintDataMatrixDetail('BID_low_adj')
                self.PrintDataMatrixDetail('BID_open_adj')
    
                ActiveContractPrices_ASK = self.ActiveContractPrices[self.ActiveContractPrices['DataType'] == 'ASK'][['time id', 'ticker id', 'close_adj', 'MarketTimeSectionID', 'high_adj', 'low_adj', 'open_adj', 'vol']]
                self.FillDataMatrix(ActiveContractPrices_ASK, 'time id', ['ticker id'], {'close_adj': 'ASK_close_adj'},MissingValueFilling = "Modified Following", ModifyBackwardAsLastResort = True, FullIDGrid = FullIDGrid)
                self.PrintDataMatrixDetail('ASK_close_adj')
                
                self.FillDataMatrix(ActiveContractPrices_ASK, 'time id', ['ticker id'], {'high_adj': 'ASK_high_adj', 'low_adj': 'ASK_low_adj', 'open_adj': 'ASK_open_adj'},MissingValueFilling = "Data Sheet Override", data_sheet_override_mapping = {'high_adj': 'ASK_close_adj', 'low_adj': 'ASK_close_adj', 'open_adj': 'ASK_close_adj'}, FullIDGrid = FullIDGrid)
                self.PrintDataMatrixDetail('ASK_high_adj')
                self.PrintDataMatrixDetail('ASK_low_adj')
                self.PrintDataMatrixDetail('ASK_open_adj')

        if self.KeepDataframeData:
            self.Prices = Prices_df
            
        if self.ActiveContractPircesTrimmedColumns is not None:
            self.ActiveContractPrices = self.ActiveContractPrices[self.ActiveContractPircesTrimmedColumns]
        
    def ContangoAdjustment(ActiveContractPrices, RolloverDate_df):

        RolloverDate_df['Contango'] = RolloverDate_df['Rolled_expiry_close'] - RolloverDate_df['Before_Rolling_expiry_close']
        
        # ActiveContractPrices['high_adj'] = ActiveContractPrices['high']
        # ActiveContractPrices['low_adj'] = ActiveContractPrices['low']
        # ActiveContractPrices['open_adj'] = ActiveContractPrices['open']
        # ActiveContractPrices['close_adj'] = ActiveContractPrices['close']
        # ActiveContractPrices['expiry_adj'] = ActiveContractPrices['expiry']
        ActiveContractPrices = ActiveContractPrices.sort_values(by=['ticker', 'DataType', 'Date', 'tDateTime'])
        
        if len(RolloverDate_df) > 0:
        
            ActiveContractPrices = ActiveContractPrices.merge(RolloverDate_df[['ticker', 'Prior_Active_expiry', 'Active_expiry', 'Contango']], how='left', left_on=['ticker', 'expiry_adj'], right_on=['ticker', 'Prior_Active_expiry'], suffixes=('', '_y'))
            PendingContangoAdjCount = ActiveContractPrices[['Contango']].count()['Contango']
    
            while PendingContangoAdjCount > 0:
                ActiveContractPrices.loc[ActiveContractPrices['Contango'].notnull(), 'high_adj'] = ActiveContractPrices['high'] + ActiveContractPrices['Contango']
                ActiveContractPrices.loc[ActiveContractPrices['Contango'].notnull(), 'low_adj'] = ActiveContractPrices['low'] + ActiveContractPrices['Contango']
                ActiveContractPrices.loc[ActiveContractPrices['Contango'].notnull(), 'open_adj'] = ActiveContractPrices['open'] + ActiveContractPrices['Contango']
                ActiveContractPrices.loc[ActiveContractPrices['Contango'].notnull(), 'close_adj'] = ActiveContractPrices['close'] + ActiveContractPrices['Contango']
                ActiveContractPrices.loc[ActiveContractPrices['Contango'].notnull(), 'expiry_adj'] = ActiveContractPrices['Active_expiry']
    
                ActiveContractPrices = ActiveContractPrices.drop(['Prior_Active_expiry', 'Active_expiry', 'Contango'],axis='columns')
                ActiveContractPrices = ActiveContractPrices.merge(RolloverDate_df[['ticker', 'Prior_Active_expiry', 'Active_expiry', 'Contango']], how='left', left_on=['ticker', 'expiry_adj'], right_on=['ticker', 'Prior_Active_expiry'], suffixes=('', '_y'))
    
                PendingContangoAdjCount = ActiveContractPrices[['Contango']].count()['Contango']
    
            ActiveContractPrices = ActiveContractPrices.drop(['Prior_Active_expiry', 'Active_expiry', 'Contango'],axis='columns')
        
        return ActiveContractPrices, RolloverDate_df


    def GetActiveExpiry(Prices_df):
        
        # print('Prices_df is')
        # Prices_df.to_csv(r'd:\temp\Prices_df.csv')
        
        
        # Bid_df = Prices_df[Prices_df['DataType'] == 'BID'].rename(columns = {'high': 'bid_high', 'low': 'bid_low'}, inplace = False)[['ticker', 'expiry','Date', 'tDateTime', 'bid_high', 'bid_low']]
        # Ask_df = Prices_df[Prices_df['DataType'] == 'ASK'].rename(columns = {'high': 'ask_high', 'low': 'ask_low'}, inplace = False)[['ticker', 'expiry','Date', 'tDateTime', 'ask_high', 'ask_low']]
        
        # BidAsk_df = Bid_df.merge(Ask_df, on=['ticker', 'expiry','Date', 'tDateTime'])
        # BidAsk_df['spread_high'] = BidAsk_df['ask_high'] - BidAsk_df['bid_high']
        # BidAsk_df['spread_low'] = BidAsk_df['ask_low'] - BidAsk_df['bid_low']
        # # print('before error, BidAsk_df is')
        # # print(BidAsk_df)
        # BidAsk_df_high = pd.pivot_table(BidAsk_df, values='spread_high', index=['ticker', 'Date', 'expiry'], aggfunc=np.mean).reset_index()
        # BidAsk_df_low = pd.pivot_table(BidAsk_df, values='spread_low', index=['ticker', 'Date', 'expiry'], aggfunc=np.mean).reset_index()
        
        # BidAsk_df = BidAsk_df_high.merge(BidAsk_df_low, on=['ticker', 'Date', 'expiry']).sort_values(by=['ticker', 'Date', 'expiry'])
        # BidAsk_df['spread_avg'] = (BidAsk_df['spread_high'] + BidAsk_df['spread_low']) / 2
        # MinBidAsk_df = pd.pivot_table(BidAsk_df, values='spread_avg', index=['ticker', 'Date'], aggfunc=min).reset_index().sort_values(by=['ticker', 'Date'])
        # MinBidAsk_df = BidAsk_df.merge(MinBidAsk_df, on=['ticker', 'Date', 'spread_avg']).sort_values(by=['ticker', 'Date'])
        # MinBidAsk_df['Active_expiry'] = MinBidAsk_df['expiry'].shift()
        # MinBidAsk_df['Prior_Date'] = MinBidAsk_df['Date'].shift()
        # MinBidAsk_df['Prior_ticker'] = MinBidAsk_df['ticker'].shift()
        # MinBidAsk_df.loc[MinBidAsk_df['ticker'] != MinBidAsk_df['Prior_ticker'], 'Active_expiry'] =  MinBidAsk_df['expiry']
        # CountMinBidAsk_df = pd.pivot_table(MinBidAsk_df, values='Active_expiry', index=['ticker', 'Date'], aggfunc=len, fill_value=0).reset_index()
        # CountMinBidAsk_df = CountMinBidAsk_df[CountMinBidAsk_df['Active_expiry'] > 1]
        # if len(CountMinBidAsk_df) > 1:
        #     print("Multiple expiry with same average bid/ask spread")
        
        # for x in range(1, len(MinBidAsk_df)):
        #     if (MinBidAsk_df.loc[x,'ticker'] == MinBidAsk_df.loc[x-1,'ticker']) and (MinBidAsk_df.loc[x,'Active_expiry'] < MinBidAsk_df.loc[x-1,'Active_expiry']):
        #         MinBidAsk_df.loc[x,'Active_expiry'] = MinBidAsk_df.loc[x-1,'Active_expiry']

        # MinBidAsk_df.to_csv(r'G:\TradeAnalysisProject\temp\MinBidAsk_df.csv')


# --------------
        Volume_df = Prices_df[Prices_df['DataType'] == 'TRADES'][['ticker', 'expiry','Date', 'tDateTime', 'vol']]
        Volume_df = pd.pivot_table(Volume_df, values='vol', index=['ticker', 'Date', 'expiry'], aggfunc=np.sum).reset_index()
        MaxVolume_df = pd.pivot_table(Volume_df, values='vol', index=['ticker', 'Date'], aggfunc=max).reset_index().sort_values(by=['ticker', 'Date'])
        MaxVolume_df = Volume_df.merge(MaxVolume_df, on=['ticker', 'Date', 'vol']).sort_values(by=['ticker', 'Date'])
        MaxVolume_df['Active_expiry'] = MaxVolume_df['expiry'].shift()
        MaxVolume_df['Prior_Date'] = MaxVolume_df['Date'].shift()
        MaxVolume_df['Prior_ticker'] = MaxVolume_df['ticker'].shift()
        MaxVolume_df.loc[MaxVolume_df['ticker'] != MaxVolume_df['Prior_ticker'], 'Active_expiry'] =  MaxVolume_df['expiry']

        CountMinVolume_df = pd.pivot_table(MaxVolume_df, values='Active_expiry', index=['ticker', 'Date'], aggfunc=len, fill_value=0).reset_index()
        CountMinVolume_df = CountMinVolume_df[CountMinVolume_df['Active_expiry'] > 1]
        if len(CountMinVolume_df) > 1:
            print("Multiple expiry with same average bid/ask spread")
        
        for x in range(1, len(MaxVolume_df)):
            if (MaxVolume_df.loc[x,'ticker'] == MaxVolume_df.loc[x-1,'ticker']) and (MaxVolume_df.loc[x,'Active_expiry'] < MaxVolume_df.loc[x-1,'Active_expiry']):
                MaxVolume_df.loc[x,'Active_expiry'] = MaxVolume_df.loc[x-1,'Active_expiry']

        # Volume_df.to_csv(r'G:\TradeAnalysisProject\temp\Volume_df.csv')
        # MaxVolume_df.to_csv(r'G:\TradeAnalysisProject\temp\MaxVolume_df.csv')

# ------------------

        
        # RolloverDate_df = MinBidAsk_df.copy()
        RolloverDate_df = MaxVolume_df.copy()
        RolloverDate_df['Prior_Active_expiry'] = RolloverDate_df['Active_expiry'].shift()
        RolloverDate_df = RolloverDate_df[(RolloverDate_df['Prior_Active_expiry'] != RolloverDate_df['Active_expiry']) & (RolloverDate_df['ticker'] == RolloverDate_df['Prior_ticker'])]
        RolloverDate_df['Active_expiry'] = RolloverDate_df['Active_expiry'].astype(np.int64)
        RolloverDate_df['Prior_Active_expiry'] = RolloverDate_df['Prior_Active_expiry'].astype(np.int64)
        # RolloverDate_df.to_csv(r'G:\TradeAnalysisProject\temp\RolloverDate_df_new.csv')
        
        
        Shortened_Trades_df = Prices_df[Prices_df['DataType'] == 'TRADES'][['ticker', 'expiry', 'Date', 'close']]
        # Shortened_Trades_df.to_csv(r'd:\temp\Shortened_Trades_df.csv')
        
        RolledExpiryClose_df = RolloverDate_df.merge(Shortened_Trades_df, left_on=['ticker', 'Active_expiry', 'Prior_Date'], right_on=['ticker', 'expiry', 'Date'], suffixes=('', '_y'))
        RolledExpiryClose_df.rename(columns = {'close': 'Rolled_expiry_close'}, inplace = True)
        RolledExpiryClose_df.drop(columns=['expiry_y', 'Date_y'], inplace = True)
        
        RolledExpiryClose_df = pd.pivot_table(RolledExpiryClose_df, values='Rolled_expiry_close', index=['ticker', 'Date', 'Active_expiry'], aggfunc=np.mean).reset_index()
        
        BeforeRollingExpiryClose_df = RolloverDate_df.merge(Shortened_Trades_df, left_on=['ticker', 'Prior_Active_expiry', 'Prior_Date'], right_on=['ticker', 'expiry', 'Date'], suffixes=('', '_y'))
        BeforeRollingExpiryClose_df.rename(columns = {'close': 'Before_Rolling_expiry_close'}, inplace = True)
        BeforeRollingExpiryClose_df.drop(columns=['expiry_y', 'Date_y'], inplace = True)
        
        BeforeRollingExpiryClose_df = pd.pivot_table(BeforeRollingExpiryClose_df, values='Before_Rolling_expiry_close', index=['ticker', 'Date', 'Prior_Date', 'Prior_Active_expiry'], aggfunc=np.mean).reset_index()


        
        if len(RolloverDate_df) > 0:

            RolloverDate_df = RolloverDate_df.merge(RolledExpiryClose_df, on=['ticker', 'Date', 'Active_expiry'])
            RolloverDate_df = RolloverDate_df.merge(BeforeRollingExpiryClose_df, on=['ticker', 'Date', 'Prior_Active_expiry'])
            # RolloverDate_df['Contango'] = RolloverDate_df['Rolled_expiry_close'] - RolloverDate_df['Before_Rolling_expiry_close']

        # return MinBidAsk_df, RolloverDate_df
        return MaxVolume_df, RolloverDate_df

class IBFuturesPriceReader(FuturesPriceReader):
    def GetDataframeFromDB(self, TickerFilter = []):
        DATABASE_FUT_HIST_10SECS_SUFFIX = {2021:"_2021", 2022:""}
        if len(TickerFilter) == 0:
            TickerFilterString = ''
        else:
            TickerFilterString = "ticker in ('" +   "', '".join(TickerFilter) + "') and "
        # dbcon = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
        print("Start downloading price data " + str(datetime.now()))
        if self.TimeFrame == '10 secs':
            DBName = Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST_10SECS
            TableName = 'fdata_fut_hist'
            # TickerFilterString = TickerFilterString + "TIME(tDateTime) >= '" + self.DataTimeLowerBound + "' AND TIME(tDateTime) <= '" + self.DataTimeUpperBound + "' AND "
            if self.DataTimeLowerBound is not None:
                TickerFilterString = TickerFilterString + "TIME(tDateTime) >= '" + self.DataTimeLowerBound + "' AND "
            if self.DataTimeUpperBound is not None:
                TickerFilterString = TickerFilterString + "TIME(tDateTime) <= '" + self.DataTimeUpperBound + "' AND "
        else:
            DBName = Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST
            TableName = 'fdata_fut_hist'
        if self.LoadBidAskPrices:
            DataTypeFilter = ''
        else:
            DataTypeFilter = " AND DataType = 'TRADES'"
            
        full_sql = ""
        
        if self.TimeFrame == '10 secs':
            for data_year in DATABASE_FUT_HIST_10SECS_SUFFIX:
                if (self.StartDate.year <= data_year and self.EndDate.year >= data_year):
                    if (full_sql == ""):
                        full_sql = "SELECT * FROM " + DBName + DATABASE_FUT_HIST_10SECS_SUFFIX[data_year] + "." + TableName + " where " + TickerFilterString + " tDateTime BETWEEN '" + self.StartDate.strftime("%Y-%m-%d") + " 00:00:00' AND '" + self.EndDate.strftime("%Y-%m-%d") + " 23:59:59' AND timeframe = '" + self.TimeFrame + "'" + DataTypeFilter
                    else:
                        full_sql = full_sql + " UNION ALL SELECT * FROM " + DBName + DATABASE_FUT_HIST_10SECS_SUFFIX[data_year] + "." + TableName + " where " + TickerFilterString + " tDateTime BETWEEN '" + self.StartDate.strftime("%Y-%m-%d") + " 00:00:00' AND '" + self.EndDate.strftime("%Y-%m-%d") + " 23:59:59' AND timeframe = '" + self.TimeFrame + "'" + DataTypeFilter
            pass
        else:
            full_sql = "SELECT * FROM " + DBName + "." + TableName + " where " + TickerFilterString + " tDateTime BETWEEN '" + self.StartDate.strftime("%Y-%m-%d") + " 00:00:00' AND '" + self.EndDate.strftime("%Y-%m-%d") + " 23:59:59' AND timeframe = '" + self.TimeFrame + "'" + DataTypeFilter
        
            
        # sql = "SELECT * FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST + ".fdata_fut_hist where " + TickerFilterString + " tDateTime BETWEEN '" + self.StartDate.strftime("%Y-%m-%d") + " 00:00:00' AND '" + self.EndDate.strftime("%Y-%m-%d") + " 23:59:59' AND timeframe = '" + self.TimeFrame + "'"
        # sql = "SELECT * FROM " + DBName + "." + TableName + " where " + TickerFilterString + " tDateTime BETWEEN '" + self.StartDate.strftime("%Y-%m-%d") + " 00:00:00' AND '" + self.EndDate.strftime("%Y-%m-%d") + " 23:59:59' AND timeframe = '" + self.TimeFrame + "'" + DataTypeFilter

        # return pd.read_sql_query(full_sql, dbcon)#
        # print('full_sql is')
        # print(full_sql)
        return pd.read_sql(full_sql,con=DBUtil.GetSQLAlchemyEngine()) 

    # def CalculateMeanAndStdev(self, KeepDataframeData = False):
    #     print('In CalculateMeanAndStdev')
    #     # self.Prices = Prices_df
        
    #     # print('self.Prices is')
    #     # print(self.Prices)
        
        
    #     print('self.ActiveContractPrices is')
    #     print(self.ActiveContractPrices)
    #     print('self.ActiveContractPrices is with max and min TimeInStandardUnit of ' + str(self.ActiveContractPrices['TimeInStandardUnit'].max()) + ' and ' + str(self.ActiveContractPrices['TimeInStandardUnit'].min()) )


    #     # ticker_list = self.ActiveContractPrices[['ticker']].drop_duplicates()['ticker'].to_list()
    #     # print('ticker_list is ' + str(ticker_list))
    #     # TimeInStandardUnit_list = self.ActiveContractPrices[['TimeInStandardUnit']].drop_duplicates()['TimeInStandardUnit'].to_list()
    #     # df = pd.DataFrame(columns=['ticker', 'TimeInStandardUnit', 'vol mean', 'vol stdev', 'shock mean', 'shock stdev'])
    #     # for ticker in ticker_list:
    #     #     for TimeInStandardUnit in TimeInStandardUnit_list:
    #     #         ActiveContractPrices_ticker = self.ActiveContractPrices.loc[self.ActiveContractPrices['ticker'] == ticker & self.ActiveContractPrices['TimeInStandardUnit'] == TimeInStandardUnit]
    #     #         vol_mean = ActiveContractPrices_ticker['vol'].mean()
    #     #         vol_stdev = ActiveContractPrices_ticker['vol'].std()
    #     #         ActiveContractPrices_ticker['open_close_width'] = abs(ActiveContractPrices_ticker['close_adj'] - ActiveContractPrices_ticker['open_adj'])
    #     #         shock_mean = ActiveContractPrices_ticker['open_close_width'].mean()
    #     #         shock_stdev = ActiveContractPrices_ticker['open_close_width'].std()
                
    #     #         ls = [ticker, TimeInStandardUnit, vol_mean, vol_stdev, shock_mean, shock_stdev]
    #     #         # Create a pandas series from the list
    #     #         row = pd.Series(ls, index=df.columns)
    #     #         df = df.append(row, ignore_index=True)

    #     #         # print(ticker + ': ' + str(vol_mean) + ', ' + str(vol_stdev))
        

        
    #     ticker_list = self.ActiveContractPrices[['ticker']].drop_duplicates()['ticker'].to_list()
    #     print('ticker_list is ' + str(ticker_list))
    #     df_stat = pd.DataFrame(columns=['ticker', 'vol mean', 'vol stdev', 'shock mean', 'shock stdev'])
    #     for ticker in ticker_list:
    #         ActiveContractPrices_ticker = self.ActiveContractPrices.loc[self.ActiveContractPrices['ticker'] == ticker]
    #         vol_mean = ActiveContractPrices_ticker['vol'].mean()
    #         vol_stdev = ActiveContractPrices_ticker['vol'].std()
    #         ActiveContractPrices_ticker['open_close_width'] = abs(ActiveContractPrices_ticker['close_adj'] - ActiveContractPrices_ticker['open_adj'])
    #         shock_mean = ActiveContractPrices_ticker['open_close_width'].mean()
    #         shock_stdev = ActiveContractPrices_ticker['open_close_width'].std()
            
    #         ls = [ticker, vol_mean, vol_stdev, shock_mean, shock_stdev]
    #         # Create a pandas series from the list
    #         row = pd.Series(ls, index=df_stat.columns)
    #         df_stat = df_stat.append(row, ignore_index=True)

    #             # print(ticker + ': ' + str(vol_mean) + ', ' + str(vol_stdev))
        
    #     print('vol and shock mean and stdev is')
    #     print(df_stat)
    #     df_stat.to_csv(r'G:\Temp\df_stat.csv', index=False)
        
    #     df = self.ActiveContractPrices.merge(df_stat, on='ticker')
    #     df = df.loc[df['vol'] > df['vol mean'] + 3 * df['vol stdev']]
    #     df['open_close_width'] = abs(df['close_adj'] - df['open_adj'])
    #     df = df.loc[df['open_close_width'] > df['shock mean'] + 3 * df['shock stdev']]
    #     # df = df.loc[abs(ActiveContractPrices_ticker['close_adj'] - ActiveContractPrices_ticker['open_adj']) > df['shock mean'] + df['shock stdev']]
        
    #     print('filtered candles are')
    #     print(df)
    #     df.to_csv(r'G:\Temp\filtered_candles.csv', index=False)
        
        
        
    #     if not KeepDataframeData:
    #         self.Prices = None


class FXFuturesPriceReader(FuturesPriceReader):
    def GetDataframeFromDB(self, TickerFilter = []):
        if len(TickerFilter) == 0:
            TickerFilterString = ''
        else:
            TickerFilterString = "ticker in ('" +   "', '".join(TickerFilter) + "') and "
        dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
        print("Start downloading price data " + str(datetime.now()))
        sql = "SELECT ticker, 'FUT' AS instrumenttype, 0 AS expiry, 'TRADES' AS DataType, '1 min' as timeframe, Datetime as tDateTime, High as high, Low as low, Open as open, Close as close, Volume as vol, 'Yahoo' as src FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_1MIN_FX + ".fdata_price_1min where ticker like '%=X' AND " + TickerFilterString + " Datetime BETWEEN '" + self.StartDate.strftime("%Y-%m-%d") + " 00:00:00' AND '" + self.EndDate.strftime("%Y-%m-%d") + " 23:59:59'"
        return pd.read_sql_query(sql, dbcon)
    
    def setActiveContractPrice(self, Prices_df):
        self.ActiveContractPrices = Prices_df.copy()[['ticker', 'expiry', 'DataType', 'tDateTime', 'high', 'low', 'open', 'close', 'vol', 'Date', 'Hour', 'Minute', 'TimeInStandardUnit']]

class CryptoPriceReader(FuturesPriceReader):
    
    # self.TimeFrame
    TIME_FRAME_MAPPING = {'1 min':'1m'}
    
    def GetDataframeFromDB(self, TickerFilter = []):
        if len(TickerFilter) == 0:
            TickerFilterString = ''
        else:
            TickerFilterString = "ticker in ('" +   "', '".join(TickerFilter) + "') AND "
        # dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
        print("Start downloading price data " + str(datetime.now()))
        # sql = "SELECT ticker, 'FUT' AS instrumenttype, 0 AS expiry, 'TRADES' AS DataType, '" + self.TimeFrame + "' as timeframe, tDateTime, high, low, open, close, vol, 'Binance' as src FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_CRYPTO_BINANCE + ".fdata_crypto_hist where " + TickerFilterString + " tDateTime BETWEEN '" + self.StartDate.strftime("%Y-%m-%d") + " 00:00:00' AND '" + self.EndDate.strftime("%Y-%m-%d") + " 23:59:59'"
        full_sql = "SELECT ticker, 'Crypto' AS instrumenttype, 0 AS expiry, 'TRADES' AS DataType, '" + self.TimeFrame + "' as timeframe, tDateTime, high, low, open, close, vol, 'Binance' as src FROM " + Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_CRYPTO_BINANCE + ".fdata_crypto_hist where timeframe = '" + CryptoPriceReader.TIME_FRAME_MAPPING[self.TimeFrame] + "' AND " + TickerFilterString + " tDateTime BETWEEN '" + self.StartDate.strftime("%Y-%m-%d") + " 00:00:00' AND '" + self.EndDate.strftime("%Y-%m-%d") + " 23:59:59'"
        # return pd.read_sql_query(sql, dbcon)
        return pd.read_sql(full_sql,con=DBUtil.GetSQLAlchemyEngine()) 
    
    def setActiveContractPrice(self, Prices_df):
        self.ActiveContractPrices = Prices_df.copy()[['ticker', 'expiry', 'DataType', 'tDateTime', 'high', 'low', 'open', 'close', 'vol', 'Date', 'Hour', 'Minute', 'TimeInStandardUnit']]

    def GetInstrumentType(self):
        return 'Crypto'
    
class DailySpotPriceReader(SpotPriceReader):
    DATECOLUMNNAME = 'Date'
    ColumnRename = {'Datetime':'Date'}
    def __init__(self, StartDate, EndDate, MarketList, DailyVolumeLimit=1000000, DailyVolumeLimitMode = ['StartDate', 'EndDate', 'Average'], TickerFilter = None, DataAvailabilityLimit = 0.95, ExcludeETF = True, GPUMode = True):
        super().__init__(StartDate, EndDate, MarketList, GPUMode=GPUMode)
        self.TickerIDMapping = None
        self.DateIDMapping = None
        self.DailyVolumeLimit = DailyVolumeLimit
        self.DailyVolumeLimitMode = DailyVolumeLimitMode
        self.TickerFilter = TickerFilter
        self.DataAvailabilityLimit = DataAvailabilityLimit
        self.ExcludeETF = ExcludeETF
        self.LoadRawData()
        
    def LoadRawData(self):
        dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
        market_string = ""
        for market in self.MarketList:
            if (len(market_string) == 0):
                market_string = "'" + market + "'"
            else:
                market_string = market_string + ", '" + market + "'"

        print("Start downloading price data " + str(datetime.now()))
        
        if self.ExcludeETF:
            # SELECT * FROM (SELECT `fdata_price_dayend`.* FROM `fdata_tickers` inner join `fdata_price_dayend` on `fdata_tickers`.Ticker = `fdata_price_dayend`.Ticker WHERE Volume > 0 AND `fdata_tickers`.Market in ('XUSA', 'XHKG') AND Datetime <= '2021-01-15' AND Datetime >= '2021-01-04') A left join (SELECT * FROM `fdata_tickers_property` WHERE `Property_Type` = 'Yahoo_legalType' and `Property` = 'Exchange Traded Fund') B ON A.ticker = B.Ticker where B.Property is NULL
            # sql = "SELECT AA.*, BB.Market FROM (SELECT A.* FROM (SELECT `fdata_price_dayend`.* FROM `fdata_tickers` inner join `fdata_price_dayend` on `fdata_tickers`.Ticker = `fdata_price_dayend`.Ticker WHERE Volume > 0 AND `fdata_tickers`.Market in (" + market_string + ") AND Datetime <= '" + self.EndDate.strftime("%Y-%m-%d") + "' AND Datetime >= '" + self.StartDate.strftime("%Y-%m-%d") + "') A left join (SELECT * FROM `fdata_tickers_property` WHERE `Property_Type` = 'Yahoo_legalType' and `Property` = 'Exchange Traded Fund') B ON A.ticker = B.Ticker where B.Property is NULL) AA inner join `fdata_tickers` BB on AA.ticker = BB.Ticker"
            sql = "SELECT A.* FROM (SELECT `fdata_price_dayend`.*, `fdata_tickers`.Market FROM `fdata_tickers` inner join `fdata_price_dayend` on `fdata_tickers`.Ticker = `fdata_price_dayend`.Ticker WHERE Volume > 0 AND `fdata_tickers`.Market in (" + market_string + ") AND Datetime <= '" + self.EndDate.strftime("%Y-%m-%d") + "' AND Datetime >= '" + self.StartDate.strftime("%Y-%m-%d") + "') A left join (SELECT * FROM `fdata_tickers_property` WHERE `Property_Type` = 'Yahoo_legalType' and `Property` = 'Exchange Traded Fund') B ON A.ticker = B.Ticker where B.Property is NULL"
        else:
            sql = "SELECT `fdata_price_dayend`.*, `fdata_tickers`.Market FROM `fdata_tickers` inner join `fdata_price_dayend` on `fdata_tickers`.Ticker = `fdata_price_dayend`.Ticker WHERE Volume > 0 AND `fdata_tickers`.Market in (" + market_string + ") AND Datetime <= '" + self.EndDate.strftime("%Y-%m-%d") + "' AND Datetime >= '" + self.StartDate.strftime("%Y-%m-%d") + "'"
        Prices = pd.read_sql_query(sql, dbcon)
        Prices.rename(columns = DailySpotPriceReader.ColumnRename, inplace = True) 
        
        # Filter data with Ticker Filter
        if (self.TickerFilter is not None):
            Prices = Prices[Prices['ticker'].isin(self.TickerFilter)]
                   
        # Convert Date column for date format
        Prices[DailySpotPriceReader.DATECOLUMNNAME]= pd.to_datetime(Prices[DailySpotPriceReader.DATECOLUMNNAME])
        
        print("Start filtering data with price on both Start Date and End Date " + str(datetime.now()))
        # Filter data with price on both Start Date and End Date
        ThisMarketStartDate = Prices[DailySpotPriceReader.DATECOLUMNNAME].min()
        ThisMarketEndDate = Prices[DailySpotPriceReader.DATECOLUMNNAME].max()
        MaxMinDates = pd.pivot_table(Prices, index='ticker', values=DailySpotPriceReader.DATECOLUMNNAME, aggfunc=[np.max, np.min])
        MaxMinDates.columns = MaxMinDates.columns.to_series().str.join('_')
        MaxMinDates = MaxMinDates.reset_index()
        MaxMinDates = MaxMinDates[MaxMinDates['amax_'+DailySpotPriceReader.DATECOLUMNNAME] == ThisMarketEndDate]
        MaxMinDates = MaxMinDates[MaxMinDates['amin_'+DailySpotPriceReader.DATECOLUMNNAME] == ThisMarketStartDate]
        TickersWithFullData = MaxMinDates[['ticker']]
        print("Total count of ticker is " + str(len(TickersWithFullData)))
        Prices = Prices.merge(TickersWithFullData, left_on='ticker', right_on='ticker')
        # print('Prices before StartDate Volume screening')
        # print(Prices)
        
        print("Start filtering stock with sufficient trading volume " + str(datetime.now()))
        # Filter stock with sufficient trading volume
        if ('StartDate' in self.DailyVolumeLimitMode):
            print('Screening by StartDate Volume')
            VolumeCheck = Prices[Prices[DailySpotPriceReader.DATECOLUMNNAME] == ThisMarketStartDate].copy()
            VolumeCheck['MoneyVolume'] = VolumeCheck['Adj Close'] * VolumeCheck['Volume']
            VolumeCheck = VolumeCheck[VolumeCheck['MoneyVolume'] >= self.DailyVolumeLimit]
            TickersWithTradingVolume = VolumeCheck[['ticker']]
            Prices = Prices.merge(TickersWithTradingVolume, left_on='ticker', right_on='ticker')
            
        Prices, self.TickerIDMapping = PriceReader.AddAutoincrementalID(Prices, ['ticker', 'Market'], 'ticker id')
        Prices, self.DateIDMapping = PriceReader.AddAutoincrementalID(Prices, [DailySpotPriceReader.DATECOLUMNNAME], 'date id')
            
 
        # print("Start filling by modified following " + str(datetime.now()))
        if self.GPUMode:
            self.FillDataMatrix(Prices, 'date id', ['ticker id'], ['Adj Close'])
            
            TickerIDWithSufficientData = CUDAGetTickerIDWithSufficientData(self.DataMatrix['Adj Close'], self.DataAvailabilityLimit)
            Prices = Prices.merge(TickerIDWithSufficientData[['ticker id']], on='ticker id').drop(['ticker id'],axis='columns')
            
            Prices, self.TickerIDMapping = PriceReader.AddAutoincrementalID(Prices, ['ticker', 'Market'], 'ticker id')
            
            self.FillDataMatrix(Prices, 'date id', ['ticker id'], ['Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume'],MissingValueFilling = "Modified Following")
            
        else:

            PricesList = SpotPriceReader.FillByModifiedFollowing(Prices, ['ticker', 'Market'], DailySpotPriceReader.DATECOLUMNNAME, ['Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume'], self.DataAvailabilityLimit)
            Prices, self.TickerIDMapping = PriceReader.AddAutoincrementalID(PricesList[0], ['ticker', 'Market'], 'ticker id')
            
            self.FillDataMatrix(Prices, 'date id', ['ticker id'], ['Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume'],MissingValueFilling = "Modified Following")
