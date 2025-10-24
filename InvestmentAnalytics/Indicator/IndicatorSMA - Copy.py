# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 00:59:07 2021

@author: Henry Cheung
"""


from InvestmentAnalytics.CUDA.Indicator.CUDAIndicatorSMA import CUDAIndicatorSMA

class IndicatorSMA:
    def __init__(self, close_price_matrix, MA_Day_List, block_cutting_dimension = "Time Dimension", GPUMode = True):
        self.IndicatorLabelPrefix = 'Indicator|SMA|'
        self.close_price_matrix = close_price_matrix
        self.MA_Day_List = MA_Day_List
        self.block_cutting_dimension = block_cutting_dimension
        self.GPUMode = GPUMode
        self.indicator_values = CUDAIndicatorSMA(close_price_matrix, MA_Day_List, block_cutting_dimension = block_cutting_dimension)
        
        

