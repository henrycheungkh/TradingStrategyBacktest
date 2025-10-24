# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 00:15:59 2024

@author: Henry Cheung
"""

import pandas as pd
import numpy as np

from AdhocBacktestKeyLevelClass import AdhocBacktestKeyLevel

class AdhocBacktestKeyLevelMovingStop(AdhocBacktestKeyLevel):
    def InitStrategyAdditionalData(self):
        super().InitStrategyAdditionalData()
        self.df_SingleSeries['TrailingStopLoss Price'] = np.nan
        self.df_SingleSeries['TrailingTakeProfit Price'] = np.nan
        
    def InitParameterForSingleIteration(self):
        super().InitParameterForSingleIteration()
        self.TrailingStopLoss = self.Parameters['TrailingStopLoss']
        self.TrailingTakeProfit = self.Parameters['TrailingTakeProfit']
        self.TrailingStartTime = self.Parameters['TrailingStartTime']
        
    def TradeContinueCarryForward(self, price_step_index):
        super().TradeContinueCarryForward(price_step_index)
        PriceNow = self.df_SingleSeries.iloc[price_step_index]['price']
        if (self.TradeDuration/3 > self.TrailingStartTime):
            if self.df_SingleSeries.iloc[price_step_index]['Position'] > 0:
                self.df_SingleSeries.at[price_step_index, 'TrailingStopLoss Price'] = np.nanmax([PriceNow - self.TrailingStopLoss, self.df_SingleSeries.iloc[price_step_index+1]['TrailingStopLoss Price']])
                self.df_SingleSeries.at[price_step_index, 'TrailingTakeProfit Price'] = np.nanmin([PriceNow + self.TrailingTakeProfit, self.df_SingleSeries.iloc[price_step_index+1]['TrailingTakeProfit Price']])
            elif self.df_SingleSeries.iloc[price_step_index]['Position'] < 0:
                self.df_SingleSeries.at[price_step_index, 'TrailingStopLoss Price'] = np.nanmin([PriceNow + self.TrailingStopLoss, self.df_SingleSeries.iloc[price_step_index+1]['TrailingStopLoss Price']])
                self.df_SingleSeries.at[price_step_index, 'TrailingTakeProfit Price'] = np.nanmax([PriceNow - self.TrailingTakeProfit, self.df_SingleSeries.iloc[price_step_index+1]['TrailingTakeProfit Price']])

    def CheckForTradeExitByStrategy(self, price_step_index):
        PositionBefore = self.df_SingleSeries.iloc[price_step_index+1]['Position']
        StopLossPriceBefore = self.df_SingleSeries.iloc[price_step_index+1]['StopLoss Price']
        TakeProfitPriceBefore = self.df_SingleSeries.iloc[price_step_index+1]['TakeProfit Price']
        TrailingLossPriceBefore = self.df_SingleSeries.iloc[price_step_index+1]['TrailingStopLoss Price']
        TrailingTakeProfitPriceBefore = self.df_SingleSeries.iloc[price_step_index+1]['TrailingTakeProfit Price']
        
        if PositionBefore > 0:
            ClosestStopLoss = np.nanmax([StopLossPriceBefore, TrailingLossPriceBefore])
            ClosestTakeProfit = np.nanmin([TakeProfitPriceBefore, TrailingTakeProfitPriceBefore])
            return self.CheckForTradeExit(price_step_index, ClosestStopLoss, ClosestTakeProfit)        
        elif PositionBefore < 0:
            ClosestStopLoss = np.nanmin([StopLossPriceBefore, TrailingLossPriceBefore])
            ClosestTakeProfit = np.nanmax([TakeProfitPriceBefore, TrailingTakeProfitPriceBefore])
            return self.CheckForTradeExit(price_step_index, ClosestStopLoss, ClosestTakeProfit)        
        else:
            return (False, np.nan)
        