# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 00:59:07 2021

@author: Henry Cheung
"""

from InvestmentAnalytics.Indicator.Indicator import Indicator



class IndicatorRSI(Indicator):
    def __init__(self, data_label, close_price_matrix, ParameterList, IndicatorTimeFrame, PriceTimeFrame = None, close_price_date_time_in_std_unit_matrix = None, block_cutting_dimension = "Time Dimension", GPUMode = "CUDA"):
        print('In RSI init, close_price_matrix is')
        print(close_price_matrix)

        super().__init__('RSI', data_label, ParameterList, IndicatorTimeFrame, PriceTimeFrame)

        # self.close_price_matrix = close_price_matrix
        close_price_matrix, df_all_time_mapping_to_collapsed_unit, df_last_time_per_collapsed_unit = self.GetCollapsedClosePriceMatrix(close_price_matrix, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix)

        # self.MA_Day_List = MA_Day_List
        self.Period_List = []
        for parameter in ParameterList:
            self.Period_List.append(parameter[0])
        self.block_cutting_dimension = block_cutting_dimension
        self.GPUMode = GPUMode
        if GPUMode == "CUDA":
            from InvestmentAnalytics.CUDA.Indicator.CUDAIndicatorRSI import CUDAIndicatorRSI
            print('In IndicatorRSI, before calling CUDAIndicatorRSI, close_price_matrix is')
            print(close_price_matrix)

            self.indicator_values = CUDAIndicatorRSI(close_price_matrix, ParameterList, block_cutting_dimension = block_cutting_dimension)
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

class IndicatorNormalisedRSI(Indicator):
    def __init__(self, data_label, close_price_matrix, ParameterList, IndicatorTimeFrame, PriceTimeFrame = None, close_price_date_time_in_std_unit_matrix = None, block_cutting_dimension = "Time Dimension", GPUMode = "CUDA"):
        print('IndicatorNormalisedRSI.init')
        self.RSIIndicator = IndicatorRSI(data_label, close_price_matrix, ParameterList, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix, block_cutting_dimension, GPUMode)
        print('after setting self.RSIIndicator')
        super().__init__('Normalised RSI', data_label, ParameterList, IndicatorTimeFrame, PriceTimeFrame)
        self.indicator_values = []
        indicator_values = self.RSIIndicator.indicator_values
        for i in range(len(indicator_values)):
            indicator_value = -1 * (indicator_values[i] - 50)
            self.indicator_values.append(indicator_value)
        
        
        # self.indicator_values = self.RSIIndicator.indicator_values.copy()
        # for indicator_value in self.indicator_values:
        #     indicator_value = -1 * (indicator_value - 50)

    def GetParameterCount():
        	return 1
    def GetObsPeriod(self,Parameter):
        return Parameter[0]
    def GetParameterLabelList(self):
        	return ['period']
        