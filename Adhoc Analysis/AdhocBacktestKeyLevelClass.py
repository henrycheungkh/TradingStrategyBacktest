# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 00:15:59 2024

@author: Henry Cheung
"""

from AdhocBacktestKeyLevelBaseClass import AdhocBacktestKeyLevelBaseClass

class AdhocBacktestKeyLevel(AdhocBacktestKeyLevelBaseClass):
    def CheckForTradeEntryByStrategy(self, price_step_index):
        PriceNow = self.df_SingleSeries.iloc[price_step_index]['price']
        KeyLevelDown = self.df_SingleSeries.iloc[price_step_index+1]['KeyLevelDown']
        KeyLevelUp = self.df_SingleSeries.iloc[price_step_index+1]['KeyLevelUp']
        if PriceNow <= KeyLevelDown:
            self.EnterTrade(price_step_index, 1, KeyLevelDown)
        elif PriceNow >= KeyLevelUp:
            self.EnterTrade(price_step_index, -1, KeyLevelUp)        