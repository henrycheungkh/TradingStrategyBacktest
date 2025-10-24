# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 00:59:07 2021

@author: Henry Cheung
"""

from InvestmentAnalytics.Indicator.Indicator import Indicator


class IndicatorSMA(Indicator):
    def __init__(self, data_label, close_price_matrix, MA_Day_List, IndicatorTimeFrame, PriceTimeFrame = None, close_price_date_time_in_std_unit_matrix = None, block_cutting_dimension = "Time Dimension", GPUMode = "CUDA"):
        super().__init__('SMA', data_label, MA_Day_List, IndicatorTimeFrame, PriceTimeFrame)

        # self.close_price_matrix = close_price_matrix
        close_price_matrix, df_all_time_mapping_to_collapsed_unit, df_last_time_per_collapsed_unit = self.GetCollapsedClosePriceMatrix(close_price_matrix, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix)

        # self.MA_Day_List = MA_Day_List
        self.MA_Day_List = []
        for MA_Day in MA_Day_List:
            self.MA_Day_List.append(MA_Day[0])
        self.block_cutting_dimension = block_cutting_dimension
        self.GPUMode = GPUMode
        if GPUMode == "CUDA":
            from InvestmentAnalytics.CUDA.Indicator.CUDAIndicatorSMA import CUDAIndicatorSMA
            self.indicator_values = CUDAIndicatorSMA(close_price_matrix, MA_Day_List, block_cutting_dimension = block_cutting_dimension)
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
        