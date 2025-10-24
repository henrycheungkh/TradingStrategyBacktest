# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 00:59:07 2021

@author: Henry Cheung
"""

from InvestmentAnalytics.Indicator.Indicator import Indicator

class IndicatorSuperTrend(Indicator):
    def __init__(self, data_label, close_price_matrix, high_price_matrix, low_price_matrix, ParameterList, IndicatorTimeFrame, PriceTimeFrame = None, close_price_date_time_in_std_unit_matrix = None, GPUMode = "CUDA"):

        super().__init__('SuperTrend', data_label, ParameterList, IndicatorTimeFrame, PriceTimeFrame)

        # self.close_price_matrix = close_price_matrix
        close_price_matrix, df_all_time_mapping_to_collapsed_unit, df_last_time_per_collapsed_unit = self.GetCollapsedClosePriceMatrix(close_price_matrix, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix)
        high_price_matrix, df_all_time_mapping_to_collapsed_unit, df_last_time_per_collapsed_unit = self.GetCollapsedHighPriceMatrix(high_price_matrix, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix)
        low_price_matrix, df_all_time_mapping_to_collapsed_unit, df_last_time_per_collapsed_unit = self.GetCollapsedLowPriceMatrix(low_price_matrix, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix)

        # self.MA_Day_List = MA_Day_List
        self.ParameterList = ParameterList
        # self.Period_List = []
        # for parameter in ParameterList:
        #     self.Period_List.append(parameter[0])
        # self.block_cutting_dimension = block_cutting_dimension
        self.GPUMode = GPUMode
        if GPUMode == "CUDA":
            from InvestmentAnalytics.CUDA.Indicator.CUDAIndicatorSuperTrend import CUDAIndicatorSuperTrend
            # print('In IndicatorRSI, before calling CUDAIndicatorRSI, close_price_matrix is')
            # print(close_price_matrix)

            self.indicator_values, self.signal_values = CUDAIndicatorSuperTrend(close_price_matrix, high_price_matrix, low_price_matrix, ParameterList)
        # self.indicator_values = self.GetExpandedIndicatorValues()
        if PriceTimeFrame is not None:
            if IndicatorTimeFrame != PriceTimeFrame:
                self.indicator_values = self.GetExpandedIndicatorMatrix(self.indicator_values, IndicatorTimeFrame, PriceTimeFrame, df_all_time_mapping_to_collapsed_unit, df_last_time_per_collapsed_unit)
                self.signal_values = self.GetExpandedIndicatorMatrix(self.signal_values, IndicatorTimeFrame, PriceTimeFrame, df_all_time_mapping_to_collapsed_unit, df_last_time_per_collapsed_unit)
        
    def GetParameterCount():
        	return 2
    def GetObsPeriod(self,Parameter):
        return Parameter[0]
    def GetParameterLabelList(self):
        	return ['ATR Length', 'Factor']

class IndicatorNormalisedSuperTrend(Indicator):
    def __init__(self, data_label, close_price_matrix, high_price_matrix, low_price_matrix, ParameterList, IndicatorTimeFrame, PriceTimeFrame = None, close_price_date_time_in_std_unit_matrix = None, GPUMode = "CUDA"):
        # print('IndicatorNormalisedRSI.init')
        self.SuperTrendIndicator = IndicatorSuperTrend(data_label, close_price_matrix, high_price_matrix, low_price_matrix, ParameterList, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix, GPUMode)
        
        # print('after setting self.RSIIndicator')
        super().__init__('Normalised SuperTrend', data_label, ParameterList, IndicatorTimeFrame, PriceTimeFrame)
        self.indicator_values = self.SuperTrendIndicator.signal_values
        # indicator_values = self.SuperTrendIndicator.indicator_values
        # for i in range(len(indicator_values)):
        #     indicator_value = -1 * (indicator_values[i] - 50)
        #     self.indicator_values.append(indicator_value)

    def GetParameterCount():
        	return 2
    def GetObsPeriod(self,Parameter):
        return Parameter[0]
    def GetParameterLabelList(self):
        	return ['ATR Length', 'Factor']
        