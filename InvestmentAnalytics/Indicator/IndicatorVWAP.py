# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 00:59:07 2021

@author: Henry Cheung
"""

from InvestmentAnalytics.Indicator.Indicator import Indicator


class IndicatorVWAP(Indicator):
    def __init__(self, data_label, close_price_matrix, volume_matrix, MA_Day_List, IndicatorTimeFrame, PriceTimeFrame = None, close_price_date_time_in_std_unit_matrix = None, block_cutting_dimension = "Time Dimension", GPUMode = "CUDA"):
        super().__init__('VWAP', data_label, MA_Day_List, IndicatorTimeFrame, PriceTimeFrame)

        close_price_matrix, df_all_time_mapping_to_collapsed_unit, df_last_time_per_collapsed_unit = self.GetCollapsedClosePriceMatrix(close_price_matrix, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix)
        volume_matrix, df_all_time_mapping_to_collapsed_unit, df_last_time_per_collapsed_unit = self.GetCollapsedVolumeMatrix(volume_matrix, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix)
        # print('In IndicatorVWAP.init')
        # print('close_price_matrix is with dimension ' + str(len(close_price_matrix)) + ' x ' + str(len(close_price_matrix[0])))
        # print('volume_matrix is with dimension ' + str(len(volume_matrix)) + ' x ' + str(len(volume_matrix[0])))

        # self.MA_Day_List = MA_Day_List
        self.MA_Day_List = []
        for MA_Day in MA_Day_List:
            self.MA_Day_List.append(MA_Day[0])
        self.block_cutting_dimension = block_cutting_dimension
        self.GPUMode = GPUMode
        if GPUMode == "CUDA":
            from InvestmentAnalytics.CUDA.Indicator.CUDAIndicatorVWAP import CUDAIndicatorVWAP
            self.indicator_values = CUDAIndicatorVWAP(close_price_matrix, volume_matrix, MA_Day_List, block_cutting_dimension = block_cutting_dimension)

        if PriceTimeFrame is not None:
            if IndicatorTimeFrame != PriceTimeFrame:
                self.indicator_values = self.GetExpandedIndicatorMatrix(self.indicator_values, IndicatorTimeFrame, PriceTimeFrame, df_all_time_mapping_to_collapsed_unit, df_last_time_per_collapsed_unit)
        
            
    def GetParameterCount():
        	return 1
    def GetObsPeriod(self,Parameter):
        return Parameter[0]
    def GetParameterLabelList(self):
        	return ['period']
