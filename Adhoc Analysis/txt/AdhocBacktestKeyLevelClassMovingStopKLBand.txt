# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 00:15:59 2024

@author: Henry Cheung
"""

import pandas as pd
import numpy as np

from AdhocBacktestKeyLevelClassMovingStop import AdhocBacktestKeyLevelMovingStop

class AdhocBacktestKeyLevelMovingStopKLBand(AdhocBacktestKeyLevelMovingStop):
    def InitStrategyAdditionalData(self):
        super().InitStrategyAdditionalData()
        self.df_SingleSeries['Sticky KeyLevelDown'] = np.nan
        self.df_SingleSeries['Sticky KeyLevelUp'] = np.nan

    def InitialisationBeforeRunningTradeSimulation(self):
        super().InitialisationBeforeRunningTradeSimulation()
        self.KeyLevelUpBandStayingTime = 0
        self.KeyLevelDownBandStayingTime = 0

    def InitParameterForSingleIteration(self):
        super().InitParameterForSingleIteration()
        self.KeyLevelBandwidth = self.Parameters['KeyLevelBandwidth']
        self.KeyLevelBandStayingTime = self.Parameters['KeyLevelBandStayingTime']
        self.TradeEntryByKeyLevelOffset = self.Parameters['TradeEntryByKeyLevelOffset']

    def RolloverWhenNoPosition(self, price_step_index):
        super().RolloverWhenNoPosition(price_step_index)

    def TradeContinueCarryForward(self, price_step_index):
        super().TradeContinueCarryForward(price_step_index)
        self.RolloverStickyKeyLevel(price_step_index)
    
    def RolloverStickyKeyLevel(self, price_step_index):
        PriceNow = self.df_SingleSeries.iloc[price_step_index]['price']
        KeyLevelDown = self.df_SingleSeries.iloc[price_step_index+1]['KeyLevelDown']
        KeyLevelUp = self.df_SingleSeries.iloc[price_step_index+1]['KeyLevelUp']
        StickyKeyLevelDown = self.df_SingleSeries.iloc[price_step_index+1]['Sticky KeyLevelDown']
        StickyKeyLevelUp = self.df_SingleSeries.iloc[price_step_index+1]['Sticky KeyLevelUp']
        if np.isnan(StickyKeyLevelDown):
            StickyKeyLevelDown = self.df_SingleSeries.iloc[price_step_index+1]['KeyLevelDown']
        if np.isnan(StickyKeyLevelUp):
            StickyKeyLevelUp = self.df_SingleSeries.iloc[price_step_index+1]['KeyLevelUp']

        if (PriceNow >= StickyKeyLevelDown - self.KeyLevelBandwidth / 2) and (PriceNow <= StickyKeyLevelDown + self.KeyLevelBandwidth / 2) and (StickyKeyLevelDown != self.df_SingleSeries.iloc[price_step_index+1]['Sticky KeyLevelUp']):
            self.KeyLevelDownBandStayingTime = self.KeyLevelDownBandStayingTime + 1
            self.df_SingleSeries.at[price_step_index, 'Sticky KeyLevelDown'] = StickyKeyLevelDown
        else:
            self.KeyLevelDownBandStayingTime = 0
            
        if (PriceNow >= StickyKeyLevelUp - self.KeyLevelBandwidth / 2) and (PriceNow <= StickyKeyLevelUp + self.KeyLevelBandwidth / 2) and (StickyKeyLevelUp != self.df_SingleSeries.iloc[price_step_index+1]['Sticky KeyLevelDown']):
            self.KeyLevelUpBandStayingTime = self.KeyLevelUpBandStayingTime + 1
            self.df_SingleSeries.at[price_step_index, 'Sticky KeyLevelUp'] = StickyKeyLevelUp
        else:
            self.KeyLevelUpBandStayingTime = 0
        
    def CheckForTradeEntryByStrategy(self, price_step_index):
        PriceBefore = self.df_SingleSeries.iloc[price_step_index+1]['price']
        PriceNow = self.df_SingleSeries.iloc[price_step_index]['price']
        StickyKeyLevelDown = self.df_SingleSeries.iloc[price_step_index+1]['Sticky KeyLevelDown']
        StickyKeyLevelUp = self.df_SingleSeries.iloc[price_step_index+1]['Sticky KeyLevelUp']
        if np.isnan(StickyKeyLevelDown):
            StickyKeyLevelDown = self.df_SingleSeries.iloc[price_step_index+1]['KeyLevelDown']
        if np.isnan(StickyKeyLevelUp):
            StickyKeyLevelUp = self.df_SingleSeries.iloc[price_step_index+1]['KeyLevelUp']
        
        self.RolloverStickyKeyLevel(price_step_index)
        
        if (self.KeyLevelDownBandStayingTime/3 > self.KeyLevelBandStayingTime) and (PriceNow <= StickyKeyLevelDown + self.TradeEntryByKeyLevelOffset):
            if PriceBefore > StickyKeyLevelDown + self.TradeEntryByKeyLevelOffset:
                self.EnterTrade(price_step_index, 1, StickyKeyLevelDown + self.TradeEntryByKeyLevelOffset)
            else:
                self.EnterTrade(price_step_index, 1, PriceNow)

        if (self.KeyLevelUpBandStayingTime/3 > self.KeyLevelBandStayingTime) and (PriceNow >= StickyKeyLevelUp - self.TradeEntryByKeyLevelOffset):
            if PriceBefore < StickyKeyLevelUp - self.TradeEntryByKeyLevelOffset:
                self.EnterTrade(price_step_index, -1, StickyKeyLevelUp - self.TradeEntryByKeyLevelOffset)
            else:
                self.EnterTrade(price_step_index, -1, PriceNow)