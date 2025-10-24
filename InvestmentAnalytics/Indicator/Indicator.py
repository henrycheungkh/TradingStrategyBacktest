# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 22:37:25 2021

@author: Henry Cheung
"""
import numpy as np
import pandas as pd
from InvestmentAnalytics.MarketDataReader import *

import pymysql
import InvestmentAnalytics.Config as Config

class Indicator:
    TIMEFRAME_TO_UNIT_MAPPING = {'1 min':1, '5 mins':5, '30 mins':30, '60 mins':60, '1 hour':60}
    def __init__(self, IndicatorLabel, data_label, IndicatorParameterList, IndicatorTimeFrame, PriceTimeFrame):
        self.IndicatorLabel = IndicatorLabel
        self.data_label = data_label
        self.IndicatorParameterList = IndicatorParameterList
        self.ParameterCount = len(IndicatorParameterList[0])
        self.IndicatorTimeFrame = IndicatorTimeFrame
        self.PriceTimeFrame = PriceTimeFrame
    def UploadSingleIndicatorToAnalysisContext(self, AnalysisContext, DataLabel, ParameterLabel, indicator_matrix):
        AnalysisContext.IntradayPricesData.DataMatrix["Indicator|" + self.IndicatorLabel + "|" + DataLabel + "|" + ParameterLabel] = indicator_matrix
    def GetFilterIndicator(BatchGroup, BatchID, BatchSubID):
        return IndicatorLocator.GetFilterIndicator(BatchGroup, BatchID, BatchSubID)
    def UploadIndicatorToAnalysisContext(self, AnalysisContext):
        # self.SourceDataTimeFrame = AnalysisContext.TimeFrame
        for i in range(len(self.IndicatorParameterList)):
            print ('i = ' + str(i))
            print ('IndicatorParameterList = ' + ','.join(map(str, self.IndicatorParameterList[i])))
            print('indicator_values is with dimension ' + str(len(self.indicator_values[i])) + ' x ' + str(len(self.indicator_values[i][0])))
            # print(self.indicator_values[i])
            self.UploadSingleIndicatorToAnalysisContext(AnalysisContext, self.data_label, ','.join(map(str, self.IndicatorParameterList[i])), self.indicator_values[i])
    def GetFullMatrixLabel(self, IndicatorParameter, Separater = '|'):
        # print('In GetFullMatrixLabel, IndicatorParameter is ' + str(IndicatorParameter))
        return "Indicator" + Separater + self.IndicatorLabel + Separater + self.data_label + Separater + ",".join(map(str,IndicatorParameter))
        
    def GetExpandedIndicatorMatrix(self, indicator_matrix_list, IndicatorTimeFrame, PriceTimeFrame, df_all_time_mapping_to_collapsed_unit, df_last_time_per_collapsed_unit):
        if IndicatorTimeFrame is None:
            return indicator_matrix_list
        if IndicatorTimeFrame == PriceTimeFrame:
            return indicator_matrix_list
        
        df_last_time_per_collapsed_unit = df_last_time_per_collapsed_unit.reset_index()
        df_last_time_per_collapsed_unit['seqid'] = df_last_time_per_collapsed_unit.index
        df_last_time_per_collapsed_unit['prior seqid'] = df_last_time_per_collapsed_unit.seqid.shift(1)
        df1 = df_all_time_mapping_to_collapsed_unit.merge(df_last_time_per_collapsed_unit, on=['date id', 'time in collapsed unit trunc'])
        df1['final seqid'] = df1['prior seqid']
        df1.loc[df1['time in collapsed unit remainder_x'] == df1['time in collapsed unit remainder_y'], 'final seqid'] = df1['seqid']
        df1.fillna(0, inplace=True)
        df1 = df1.merge(df_last_time_per_collapsed_unit, left_on='final seqid', right_on='seqid', suffixes=('_ori', '') )
        # df1.to_csv(r'G:\TradeAnalysisProject\temp\df1.csv', index=False)
        
        # df_all_time_mapping_to_collapsed_unit.to_csv(r'd:\temp\df_all_time_mapping_to_collapsed_unit.csv', index=False)
        # df_last_time_per_collapsed_unit.to_csv(r'd:\temp\df_last_time_per_collapsed_unit.csv', index=False)
        
        new_indicator_matrix_list = []
        for i in range(len(indicator_matrix_list)):
            indicator_matrix = indicator_matrix_list[i]
            print('in GetExpandedIndicatorMatrix, i = ' + str(i) + ', indicator_matrix_list[i] is with dimension ' + str(len(indicator_matrix_list[i])) + ' x ' + str(len(indicator_matrix_list[i][0])))
            columns = []
            for j in range(len(indicator_matrix)):
                columns.append('ticker ' + str(j))
            df = pd.DataFrame(data=indicator_matrix.T, columns=columns)
            df = pd.concat([df_last_time_per_collapsed_unit[['date id', 'time in collapsed unit trunc', 'time in collapsed unit remainder']], df], axis=1)
            
            # print('df before expanding is')
            # print(df)
            # df.to_csv(r'G:\TradeAnalysisProject\temp\\BeforeExpandedbyGetExpandedIndicatorMatrix_IndicatorMatrix' + self.IndicatorLabel.replace('|','_') + '_' + str(self.IndicatorParameterList[0]) + '.csv', index=False) 
            
            # df = df.merge(df_all_time_mapping_to_collapsed_unit, on=['date id', 'time in collapsed unit trunc']).sort_values(by=['date id', 'TimeInStandardUnit'])
            df = df.merge(df1[['date id', 'time in collapsed unit trunc', 'date id_ori', 'TimeInStandardUnit']], on=['date id', 'time in collapsed unit trunc']).sort_values(by=['date id_ori', 'TimeInStandardUnit'])
            
            # print('df after expanding is')
            # print(df)
            # df.to_csv(r'G:\TradeAnalysisProject\temp\\RightAfterExpansionIndicatorMatrix' + self.IndicatorLabel.replace('|','_') + '_' + str(self.IndicatorParameterList[0]) + '.csv', index=False) 
            
            # df.drop(columns=['date id', 'TimeInStandardUnit', 'time in collapsed unit trunc', 'time in collapsed unit remainder'], inplace = True)
            # df.drop(columns=['date id', 'TimeInStandardUnit', 'time in collapsed unit trunc', 'time in collapsed unit remainder_x', 'time in collapsed unit remainder_y'], inplace = True)
            df.drop(columns=['date id','date id_ori',  'TimeInStandardUnit', 'time in collapsed unit trunc', 'time in collapsed unit remainder'], inplace = True)
            
            # print('df after expanding and dropping column is')
            # print(df)
            # df.to_csv(r'G:\TradeAnalysisProject\temp\\ExpandedIndicatorMatrix' + self.IndicatorLabel.replace('|','_') + '_' + str(self.IndicatorParameterList[0]) + '.csv', index=False)        
            
            expanded_indicator_matrix = df.to_numpy().T.copy(order="C")
            new_indicator_matrix_list.append(expanded_indicator_matrix)
        return new_indicator_matrix_list
        
    def GetCollapsedClosePriceMatrix(self, close_price_matrix, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix):
        # return self.GetCollapsedValueMatrix(close_price_matrix, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix, aggfunc = max)
        return self.GetCollapsedValueMatrix(close_price_matrix, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix, 'close price')

    # def GetCollapsedValueMatrix(self, value_matrix, IndicatorTimeFrame, ValueTimeFrame, value_date_time_in_std_unit_matrix, aggfunc = max):
    def GetCollapsedValueMatrix(self, value_matrix, IndicatorTimeFrame, ValueTimeFrame, value_date_time_in_std_unit_matrix, collapse_type):
        if IndicatorTimeFrame is None or value_date_time_in_std_unit_matrix is None:
            return value_matrix, None, None
        if IndicatorTimeFrame == ValueTimeFrame:
            return value_matrix, None, None
        collapse_ratio = Indicator.TIMEFRAME_TO_UNIT_MAPPING[IndicatorTimeFrame] / Indicator.TIMEFRAME_TO_UNIT_MAPPING[ValueTimeFrame]

        value_with_date_time_matrix = np.concatenate((value_date_time_in_std_unit_matrix.T, value_matrix), axis=0).T
        columns = ['date id', 'TimeInStandardUnit']
        ticker_columns = []
        for i in range(len(value_matrix)):
            ticker_columns.append('ticker ' + str(i))
        columns = columns + ticker_columns
        df = pd.DataFrame(data=value_with_date_time_matrix, columns=columns)
        # print('close price matrix before collapse is')
        # print(df)
        df['time in collapsed unit trunc'] = df['TimeInStandardUnit'].floordiv(collapse_ratio) * collapse_ratio
        df['time in collapsed unit remainder'] = df['TimeInStandardUnit'].mod(collapse_ratio)
        df_all_time_mapping_to_collapsed_unit = df[['date id', 'TimeInStandardUnit', 'time in collapsed unit trunc', 'time in collapsed unit remainder']]
        
        df_last_time_per_collapsed_unit = pd.pivot_table(df_all_time_mapping_to_collapsed_unit, values='time in collapsed unit remainder', index=['date id', 'time in collapsed unit trunc'], aggfunc=max).reset_index()

        # if aggfunc == max:
        if collapse_type == 'close price':
        
            df = df.merge(df_last_time_per_collapsed_unit, on=['date id', 'time in collapsed unit trunc', 'time in collapsed unit remainder']).sort_values(by=['date id', 'time in collapsed unit trunc'])
            print('close price matrix after collapse is')
            print(df)
            df.drop(columns=['date id', 'TimeInStandardUnit', 'time in collapsed unit trunc', 'time in collapsed unit remainder'], inplace = True)
        # elif aggfunc == np.sum:
        elif collapse_type == 'volume':
            print('going to collapse by sum: before collapse')
            print(df)
            # df_sum = pd.pivot_table(df, values=ticker_columns, index=['date id', 'time in collapsed unit trunc'], aggfunc=np.sum).reset_index().drop(columns=['date id', 'time in collapsed unit trunc'])
            df = pd.pivot_table(df, values=ticker_columns, index=['date id', 'time in collapsed unit trunc'], aggfunc=np.sum).reset_index().drop(columns=['date id', 'time in collapsed unit trunc'])
            print('after collapse by sum')
            print(df)
        elif collapse_type == 'high price':
            print('going to collapse by high price: before collapse')
            print(df)
            # df_sum = pd.pivot_table(df, values=ticker_columns, index=['date id', 'time in collapsed unit trunc'], aggfunc=np.sum).reset_index().drop(columns=['date id', 'time in collapsed unit trunc'])
            df = pd.pivot_table(df, values=ticker_columns, index=['date id', 'time in collapsed unit trunc'], aggfunc=max).reset_index().drop(columns=['date id', 'time in collapsed unit trunc'])
            print('after collapse by high price')
            print(df)
        elif collapse_type == 'low price':
            print('going to collapse by low price: before collapse')
            print(df)
            # df_sum = pd.pivot_table(df, values=ticker_columns, index=['date id', 'time in collapsed unit trunc'], aggfunc=np.sum).reset_index().drop(columns=['date id', 'time in collapsed unit trunc'])
            df = pd.pivot_table(df, values=ticker_columns, index=['date id', 'time in collapsed unit trunc'], aggfunc=min).reset_index().drop(columns=['date id', 'time in collapsed unit trunc'])
            print('after collapse by low price')
            print(df)
        else:
            print('collapse missed')
        
        # df.to_csv(r'G:\TradeAnalysisProject\temp\\CollapsedClosePriceMatrix' + self.IndicatorLabel.replace('|','_') + '_' + str(self.IndicatorParameterList[0]) + '.csv', index=False)        
        collapsed_matrix = df.to_numpy().T.copy(order="C")
        return collapsed_matrix, df_all_time_mapping_to_collapsed_unit, df_last_time_per_collapsed_unit

    def GetCollapsedVolumeMatrix(self, volume_matrix, IndicatorTimeFrame, PriceTimeFrame, volume_date_time_in_std_unit_matrix):
        return self.GetCollapsedValueMatrix(volume_matrix, IndicatorTimeFrame, PriceTimeFrame, volume_date_time_in_std_unit_matrix, 'volume')
        
    def GetCollapsedHighPriceMatrix(self, high_price_matrix, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix):
        return self.GetCollapsedValueMatrix(high_price_matrix, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix, 'high price')
    def GetCollapsedLowPriceMatrix(self, low_price_matrix, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix):
        return self.GetCollapsedValueMatrix(low_price_matrix, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix, 'low price')

class IndicatorClosePrice(Indicator):
    def __init__(self, data_label, close_price_matrix, ParameterList, IndicatorTimeFrame, PriceTimeFrame = None, close_price_date_time_in_std_unit_matrix = None):
        super().__init__('ClosePrice', data_label, ParameterList, IndicatorTimeFrame, PriceTimeFrame)

        # self.close_price_matrix = close_price_matrix
        close_price_matrix, df_all_time_mapping_to_collapsed_unit, df_last_time_per_collapsed_unit = self.GetCollapsedClosePriceMatrix(close_price_matrix, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix)

        # self.MA_Day_List = MA_Day_List
        # self.MA_Day_List = []
        # for MA_Day in MA_Day_List:
        #     self.MA_Day_List.append(MA_Day[0])
        # self.block_cutting_dimension = block_cutting_dimension
        # self.GPUMode = GPUMode
        # if GPUMode == "CUDA":
        #     from InvestmentAnalytics.CUDA.Indicator.CUDAIndicatorSMA import CUDAIndicatorSMA
        #     self.indicator_values = CUDAIndicatorSMA(close_price_matrix, MA_Day_List, block_cutting_dimension = block_cutting_dimension)
        self.indicator_values = []
        for i in range(len(ParameterList)):
            self.indicator_values.append(close_price_matrix)
        # self.indicator_values = self.GetExpandedIndicatorValues()
        if PriceTimeFrame is not None:
            if IndicatorTimeFrame != PriceTimeFrame:
                self.indicator_values = self.GetExpandedIndicatorMatrix(self.indicator_values, IndicatorTimeFrame, PriceTimeFrame, df_all_time_mapping_to_collapsed_unit, df_last_time_per_collapsed_unit)
        
    def GetParameterCount():
        	return 1
    def GetObsPeriod(self,Parameter):
        return Parameter[0]
    def GetParameterLabelList(self):
        	return ['period']


class IndicatorCross(Indicator):

    def __init__(self, Indicator1, Indicator2, IndicatorParameterList, IndicatorTimeFrame, PriceTimeFrame):
        self.Indicator1 = Indicator1
        self.Indicator2 = Indicator2

        super().__init__('Cross|' + self.Indicator1.IndicatorLabel + '|' + self.Indicator2.IndicatorLabel, self.Indicator1.data_label + '|' + self.Indicator2.data_label, IndicatorParameterList, IndicatorTimeFrame, PriceTimeFrame)
        
        self.indicator_values = []
        for parameter in self.IndicatorParameterList:
            parameter1 = parameter[:self.Indicator1.ParameterCount]
            parameter2 = parameter[-self.Indicator2.ParameterCount:]
            parameterindex1 = self.Indicator1.IndicatorParameterList.index(parameter1)
            parameterindex2 = self.Indicator2.IndicatorParameterList.index(parameter2)
            print('parameterindex1 is ' + str(parameterindex1) + ' and parameterindex2 is ' + str(parameterindex2))
            
            indicator_value = self.Indicator1.indicator_values[parameterindex1] - self.Indicator2.indicator_values[parameterindex2]

            if IndicatorTimeFrame is None:
                collapse_ratio = 1
            if IndicatorTimeFrame == PriceTimeFrame:
                collapse_ratio = 1
            else:
                collapse_ratio = Indicator.TIMEFRAME_TO_UNIT_MAPPING[IndicatorTimeFrame] / Indicator.TIMEFRAME_TO_UNIT_MAPPING[PriceTimeFrame]

            indicator1_obsperiod = self.Indicator1.GetObsPeriod(parameter1) 
            indicator2_obsperiod = self.Indicator1.GetObsPeriod(parameter2) 
            max_blank_period = (int) (max(indicator1_obsperiod, indicator2_obsperiod) * collapse_ratio)
            
            col_width = len(indicator_value[0])
            row_width = len(indicator_value)
            for row in range(len(indicator_value)):
                for col in range(max_blank_period):
                    indicator_value[row][col] = 0
                    
            # df = pd.DataFrame(data=indicator_value.T, columns=['ticker 0', 'ticker 1'])
            # df.to_csv(r'G:\TradeAnalysisProject\temp\\IndicatorCrossAfterPuttingTopZero.csv', index=False)        
                    
            # print('going to append indicator_value with dimension ' + str(len(indicator_value)) + ' x ' + str(len(indicator_value[0])))
            self.indicator_values.append(indicator_value)
            
    def GetIndicator(AnalysisContext, IndicatorName, IndicatorDataLabel, ParameterList, IndicatorTimeFrame, PriceTimeFrame):
        lst = IndicatorName.split("|")
        IndicatorName1 = lst[1]
        IndicatorName2 = lst[2]
        lst = IndicatorDataLabel.split("|")
        IndicatorDataLabel1 = lst[0]
        IndicatorDataLabel2 = lst[1]
        ParameterCount1 = IndicatorLocator.GetIndicatorParameterCount(IndicatorName1)
        ParameterCount2 = IndicatorLocator.GetIndicatorParameterCount(IndicatorName2)
        
        IndicatorParameterList1 = []
        IndicatorParameterList2 = []
        for parameter in ParameterList:
            	parameter1 = parameter[:ParameterCount1]
            	parameter2 = parameter[-ParameterCount2:]
            	if not parameter1 in IndicatorParameterList1:
            		IndicatorParameterList1.append(parameter1)
            	if not parameter2 in IndicatorParameterList2:
            		IndicatorParameterList2.append(parameter2)
        
        indicator1 = IndicatorLocator.GetIndicator(AnalysisContext, IndicatorName1, IndicatorDataLabel1, IndicatorParameterList1, IndicatorTimeFrame, PriceTimeFrame)
        indicator2 = IndicatorLocator.GetIndicator(AnalysisContext, IndicatorName2, IndicatorDataLabel2, IndicatorParameterList2, IndicatorTimeFrame, PriceTimeFrame)
        print('indicator1.indicator_values[0] is with dimension ' + str(len(indicator1.indicator_values[0])) + ' x ' + str(len(indicator1.indicator_values[0][0])))
        print('indicator2.indicator_values[0] is with dimension ' + str(len(indicator2.indicator_values[0])) + ' x ' + str(len(indicator2.indicator_values[0][0])))
        
        return IndicatorCross(indicator1, indicator2, ParameterList, IndicatorTimeFrame, PriceTimeFrame)

    def GetParameterLabelList(self):
        	indicator1_parameternamelist = self.Indicator1.GetParameterLabelList()
        	for i in range(len(indicator1_parameternamelist)):
        		indicator1_parameternamelist[i] = indicator1_parameternamelist[i] + ' 1'
        	indicator2_parameternamelist = self.Indicator2.GetParameterLabelList()
        	for i in range(len(indicator2_parameternamelist)):
        		indicator2_parameternamelist[i] = indicator2_parameternamelist[i] + ' 2'
        	return indicator1_parameternamelist + indicator2_parameternamelist

class IndicatorLocator:
    def GetFilterIndicator(AnalysisContext, StrategyName, BatchGroup, BatchID, BatchSubID):
        dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
        sql = "SELECT * FROM `fdata_backtest_batch` where BatchID = " + str(BatchID) + " AND BatchSubID = " + str(BatchSubID) + " AND BatchGroup = '" + BatchGroup + "' AND StrategyName = '" + StrategyName + "'"
        print(sql)
        ParameterValues = pd.read_sql_query(sql, dbcon)
        print(ParameterValues)
        IndicatorName = ParameterValues.loc[0, 'TradeFilterIndicatorName']
        IndicatorDataLabel = ParameterValues.loc[0, 'TradeFilterIndicatorDataLabel']
        IndicatorParametersString = ParameterValues.loc[0, 'TradeFilterIndicatorParameter']
        IndicatorTimeFrame = ParameterValues.loc[0, 'TradeFilterIndicatorTimeFrame']
        
        return IndicatorLocator.GetIndicator(AnalysisContext, IndicatorName, IndicatorDataLabel, IndicatorParametersString, IndicatorTimeFrame)

    def GetIndicator(AnalysisContext, IndicatorName, IndicatorDataLabel, ParameterList, IndicatorTimeFrame, PriceTimeFrame):
        if isinstance(ParameterList, str):
            ParameterList = IndicatorLocator.ParameterStringToListOfList(ParameterList)
        if (IndicatorName is None):
            print('IndicatorName is None')
            return None
        if (IndicatorName[0:6] == "Cross|"):
            return IndicatorCross.GetIndicator(AnalysisContext, IndicatorName, IndicatorDataLabel, ParameterList, IndicatorTimeFrame, PriceTimeFrame)
        else:
            IndicatorSourceDataMatrix = AnalysisContext.GetResampledDataMatrix(IndicatorDataLabel, IndicatorTimeFrame)
            close_price_date_time_in_std_unit_matrix = AnalysisContext.IntradayPricesData.TimeIDMapping[['date id', 'TimeInStandardUnit']].to_numpy()
            if (IndicatorName == "SMA"):
                from InvestmentAnalytics.Indicator.IndicatorSMA import IndicatorSMA
                return IndicatorSMA(IndicatorDataLabel, AnalysisContext.IntradayPricesData.DataMatrix[IndicatorDataLabel], ParameterList, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix )
            elif (IndicatorName == "VWAP"):
                from InvestmentAnalytics.Indicator.IndicatorVWAP import IndicatorVWAP
                return IndicatorVWAP(IndicatorDataLabel,  AnalysisContext.IntradayPricesData.DataMatrix[IndicatorDataLabel],  AnalysisContext.IntradayPricesData.DataMatrix['vol'], ParameterList, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix)
            elif (IndicatorName == "EMA"):
                from InvestmentAnalytics.Indicator.IndicatorEMA import IndicatorEMA
                return IndicatorEMA(IndicatorDataLabel, AnalysisContext.IntradayPricesData.DataMatrix[IndicatorDataLabel], ParameterList, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix )
            elif (IndicatorName == "RSI"):
                from InvestmentAnalytics.Indicator.IndicatorRSI import IndicatorRSI
                return IndicatorRSI(IndicatorDataLabel, AnalysisContext.IntradayPricesData.DataMatrix[IndicatorDataLabel], ParameterList, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix )
            elif (IndicatorName == "Normalised RSI"):
                from InvestmentAnalytics.Indicator.IndicatorRSI import IndicatorNormalisedRSI
                return IndicatorNormalisedRSI(IndicatorDataLabel, AnalysisContext.IntradayPricesData.DataMatrix[IndicatorDataLabel], ParameterList, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix )
            elif (IndicatorName == "SuperTrend"):
                from InvestmentAnalytics.Indicator.IndicatorSuperTrend import IndicatorSuperTrend
                return IndicatorSuperTrend(IndicatorDataLabel, AnalysisContext.IntradayPricesData.DataMatrix['TRADES_close_adj'], AnalysisContext.IntradayPricesData.DataMatrix['TRADES_high_adj'], AnalysisContext.IntradayPricesData.DataMatrix['TRADES_low_adj'], ParameterList, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix )
            elif (IndicatorName == "Normalised SuperTrend"):
                from InvestmentAnalytics.Indicator.IndicatorSuperTrend import IndicatorNormalisedSuperTrend
                return IndicatorNormalisedSuperTrend(IndicatorDataLabel, AnalysisContext.IntradayPricesData.DataMatrix['TRADES_close_adj'], AnalysisContext.IntradayPricesData.DataMatrix['TRADES_high_adj'], AnalysisContext.IntradayPricesData.DataMatrix['TRADES_low_adj'], ParameterList, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix )
            elif (IndicatorName == "ClosePrice"):
                return IndicatorClosePrice(IndicatorDataLabel, AnalysisContext.IntradayPricesData.DataMatrix[IndicatorDataLabel], ParameterList, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix )
            else:
                print('no indicator class found for ' + IndicatorName)
                return None
            
    def GetIndicatorParameterCount(IndicatorName):
        if (IndicatorName == "SMA"):
            from InvestmentAnalytics.Indicator.IndicatorSMA import IndicatorSMA
            return IndicatorSMA.GetParameterCount()
        elif (IndicatorName == "VWAP"):
            from InvestmentAnalytics.Indicator.IndicatorVWAP import IndicatorVWAP
            return IndicatorVWAP.GetParameterCount()
        elif (IndicatorName == "EMA"):
            from InvestmentAnalytics.Indicator.IndicatorEMA import IndicatorEMA
            return IndicatorEMA.GetParameterCount()
        elif (IndicatorName == "RSI"):
            from InvestmentAnalytics.Indicator.IndicatorRSI import IndicatorRSI
            return IndicatorRSI.GetParameterCount()
        elif (IndicatorName == "Normalised RSI"):
            from InvestmentAnalytics.Indicator.IndicatorRSI import IndicatorNormalisedRSI
            return IndicatorNormalisedRSI.GetParameterCount()
        elif (IndicatorName == "SuperTrend"):
            from InvestmentAnalytics.Indicator.IndicatorSuperTrend import IndicatorSuperTrend
            return IndicatorSuperTrend.GetParameterCount()
        elif (IndicatorName == "Normalised SuperTrend"):
            from InvestmentAnalytics.Indicator.IndicatorSuperTrend import IndicatorNormalisedSuperTrend
            return IndicatorNormalisedSuperTrend.GetParameterCount()
        else:
            return None
            
    def GetFullMatrixLabel(IndicatorName, IndicatorDataLabel, IndicatorParameter):
        print('In GetFullMatrixLabel, IndicatorParameter is ' + str(IndicatorParameter))
        return "Indicator|" + IndicatorName + "|" + IndicatorDataLabel + "|" + ",".join(map(str,IndicatorParameter))

    def ParameterStringToListOfList(ParameterString):
        ParameterListStrings = [e for e in ParameterString.split(';')]
        ParameterList = []
        for ParameterListString in ParameterListStrings:
            ParameterList.append([int(e) if e.isdigit() else e for e in ParameterListString.split(',')])
        return ParameterList
        
    def UploadIndicatorToAnalysisContext(AnalysisContext, IndicatorName, IndicatorDataLabel, ParameterList, IndicatorTimeFrame):
        if IndicatorName is not None and IndicatorDataLabel is not None and ParameterList is not None:
            if isinstance(ParameterList, str):
                ParameterList = IndicatorLocator.ParameterStringToListOfList(ParameterList)
            IndicatorToBeAddList = []
            # MatrixLabel = IndicatorLocator.GetFullMatrixLabel(IndicatorName, IndicatorDataLabel, indicator_parameter)
            for indicator_parameter in ParameterList:
                # if AnalysisContext.IntradayPricesData.DataMatrix[IndicatorLocator.GetFullMatrixLabel(IndicatorName, IndicatorDataLabel, indicator_parameter)] is None:
                if not IndicatorLocator.GetFullMatrixLabel(IndicatorName, IndicatorDataLabel, indicator_parameter) in AnalysisContext.IntradayPricesData.DataMatrix:
                    IndicatorToBeAddList.append(indicator_parameter)
            indicator = IndicatorLocator.GetIndicator(AnalysisContext, IndicatorName, IndicatorDataLabel, ParameterList, IndicatorTimeFrame)
            indicator.UploadIndicatorToAnalysisContext(AnalysisContext)
