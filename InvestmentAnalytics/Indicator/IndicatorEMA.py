# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 00:59:07 2021

@author: Henry Cheung
"""

# https://www.investopedia.com/terms/e/ema.asp

from InvestmentAnalytics.Indicator.Indicator import Indicator
import pandas as pd


class IndicatorEMA(Indicator):
    def __init__(self, data_label, close_price_matrix, MA_Day_List, IndicatorTimeFrame, PriceTimeFrame = None, close_price_date_time_in_std_unit_matrix = None, GPUMode = "CUDA"):

        super().__init__('EMA', data_label, MA_Day_List, IndicatorTimeFrame, PriceTimeFrame)

        close_price_matrix, df_all_time_mapping_to_collapsed_unit, df_last_time_per_collapsed_unit = self.GetCollapsedClosePriceMatrix(close_price_matrix, IndicatorTimeFrame, PriceTimeFrame, close_price_date_time_in_std_unit_matrix)
        # self.MA_Day_List = MA_Day_List
        self.MA_Day_List = []
        for MA_Day in MA_Day_List:
            self.MA_Day_List.append(MA_Day[0])
        self.GPUMode = GPUMode
        if GPUMode == "CUDA":
            from InvestmentAnalytics.CUDA.Indicator.CUDAIndicatorEMA import CUDAIndicatorEMA
            self.indicator_values = CUDAIndicatorEMA(close_price_matrix, MA_Day_List)
            
        # for i in range(len(self.MA_Day_List)):
        #     df = pd.DataFrame(data=self.indicator_values[i].T, columns=['ticker 0', 'ticker 1'])
        #     df.to_csv(r'G:\TradeAnalysisProject\temp\\BeforeExpansionIndicatorMatrix' + self.IndicatorLabel.replace('|','_') + '_' + str(self.MA_Day_List[i]) + '.csv', index=False)        
        
        
        if PriceTimeFrame is not None:
            if IndicatorTimeFrame != PriceTimeFrame:
                self.indicator_values = self.GetExpandedIndicatorMatrix(self.indicator_values, IndicatorTimeFrame, PriceTimeFrame, df_all_time_mapping_to_collapsed_unit, df_last_time_per_collapsed_unit)

    # def GetExpandedIndicatorMatrix(self, indicator_matrix, parameter_set_count, IndicatorTimeFrame, PriceTimeFrame, df_all_time_mapping_to_collapsed_unit, df_last_time_per_collapsed_unit):

            
    def GetParameterCount():
        	return 1
    def GetObsPeriod(self,Parameter):
        return Parameter[0] + 1        
    def GetParameterLabelList(self):
        	return ['period']
