# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 23:17:42 2021

@author: Henry Cheung
"""

from InvestmentAnalytics.MarketDataReader import IBFuturesPriceReader, FuturesPriceAnalysisContext
import pandas as pd
import numpy as np
import math
import InvestmentAnalytics.Config as Config
from InvestmentAnalytics.CUDA.Strategy.Futures.KeyLevelCUDALib import CUDAIdentifyKeyLevelPivot


class KeyLevelContext:
    def __init__(self, AnalysisContext,  ResultOutputFolderPath = None, KeyLevelTypeScaler = pd.DataFrame({'key level type': ['Pivot'], 'key level type scaler': [1]}), GeneralKeyLevelScoreScaler = 100, MinimumKeyLevelScore = 0.5, DecayPerTimeID = 0.999, MinimumGroupedKeyLevelIntervalPct = 0.001, KeyLevelGroupingIgnoreScoreThreshold = 0.6, KeyLevelMergingScaleUp = 0.2):
        self.AnalysisContext = AnalysisContext
        self.ResultOutputFolderPath = ResultOutputFolderPath
        self.GeneralKeyLevelScoreScaler = GeneralKeyLevelScoreScaler
        self.MinimumKeyLevelScore = MinimumKeyLevelScore
        self.KeyLevelTypeScaler = KeyLevelTypeScaler
        self.DecayPerTimeID = DecayPerTimeID
        self.MinimumGroupedKeyLevelIntervalPct = MinimumGroupedKeyLevelIntervalPct
        self.KeyLevelGroupingIgnoreScoreThreshold = KeyLevelGroupingIgnoreScoreThreshold
        self.KeyLevelMergingScaleUp = KeyLevelMergingScaleUp
        self.TickerIDList = []
        self.KeyLevelPriceList = []
        self.KeyLevelScoreList = []
        self.KeyLevelTimeList = []
        self.KeyLevelList = []
        self.SetupKeyLevel()
        
    def SetupKeyLevel(self):
        self.KeyLevelList.append(KeyLevelPivot(self.AnalysisContext, self.ResultOutputFolderPath )) 
       
    def MergeKeyLevel(self, ValueDateTimeID):
        KeyLevelBeforeMerging = pd.DataFrame(columns=['ticker id', 'identified time id', 'key level price', 'pressure up', 'key level type specific score', 'key level type'])
    # IDENTIFIED_KEY_LEVELS_COLUMNS = ['ticker id', 'identified time id', 'key level price', 'pivot point down', 'observe high low price', 'minimum slope', 'first consecutive boundary breach tolerances', 'wing length', 'pivot area to wing volume ratio', 'pivot area to pre wing volume ratio', 'key level type specific score']
        for key_levels in self.KeyLevelList:
            print('going to concat key_levels.KeyLevels of len ' + str(len(key_levels.KeyLevels)))
            print(key_levels.KeyLevels)
            KeyLevelBeforeMerging = pd.concat([KeyLevelBeforeMerging, key_levels.KeyLevels])
        print('after concat, KeyLevelBeforeMerging is')
        print(KeyLevelBeforeMerging)
        print('in MergeKeyLevel, ValueDateTimeID = ' + str(ValueDateTimeID))
        # KeyLevelBeforeMerging = KeyLevelBeforeMerging.merge(self.AnalysisContext.DailyData.TimeIDMapping, left_on='identified time id', right_on='time id')
        KeyLevelBeforeMerging = KeyLevelBeforeMerging.loc[KeyLevelBeforeMerging['identified time id'] < ValueDateTimeID]
        print('after loc screening, KeyLevelBeforeMerging is')
        print(KeyLevelBeforeMerging)
        
        KeyLevelBeforeMerging = pd.pivot_table(KeyLevelBeforeMerging, values='key level type specific score', index=['ticker id', 'identified time id', 'key level price', 'pressure up', 'key level type'], aggfunc=max).reset_index().sort_values(by=['ticker id', 'identified time id', 'key level type specific score'], ascending=False)
        KeyLevelBeforeMerging = KeyLevelBeforeMerging.merge(self.KeyLevelTypeScaler, on='key level type', how='left')
        # KeyLevelBeforeMerging['time decay scaler'] = self.DecayPerTimeID.pow(ValueDateTimeID - KeyLevelBeforeMerging['identified time id'])
        # KeyLevelBeforeMerging['time decay scaler'] = math.pow(self.DecayPerTimeID, ValueDateTimeID - KeyLevelBeforeMerging['identified time id'])
        KeyLevelBeforeMerging['time decay scaler'] = self.DecayPerTimeID
        KeyLevelBeforeMerging['time decay day count'] = ValueDateTimeID - KeyLevelBeforeMerging['identified time id']
        KeyLevelBeforeMerging['time decay scaler'] = KeyLevelBeforeMerging['time decay scaler'].pow(KeyLevelBeforeMerging['time decay day count'])
        KeyLevelBeforeMerging['key level score'] = KeyLevelBeforeMerging['key level type specific score'] * KeyLevelBeforeMerging['key level type scaler'] * KeyLevelBeforeMerging['time decay scaler'] * self.GeneralKeyLevelScoreScaler
        KeyLevelBeforeMerging = KeyLevelBeforeMerging.loc[KeyLevelBeforeMerging['key level score'] > self.MinimumKeyLevelScore]
        KeyLevelBeforeMerging.sort_values(by=['ticker id', 'key level price','key level score'], ascending=False, inplace = True)
        # KeyLevelBeforeMerging['Keep'] = True
        # PriorPos = 0
        # PriorScore = KeyLevelBeforeMerging.iloc[0]['key level score']
        return KeyLevelBeforeMerging
    
    def AddGroupedKeyLevel(self, TickerID, KeyLevelPrice, KeyLevelScore, KeyLevelTime):
        self.TickerIDList.append(TickerID)
        self.KeyLevelPriceList.append(KeyLevelPrice)
        self.KeyLevelScoreList.append(KeyLevelScore)
        self.KeyLevelTimeList.append(KeyLevelTime)
        
    def UpdateGroupedKeyLevel(self, KeyLevelPrice, KeyLevelScore):
        self.KeyLevelPriceList[-1] = KeyLevelPrice
        self.KeyLevelScoreList[-1] = KeyLevelScore

    
    def GroupKeyLevel(self, KeyLevelBeforeMerging):
        self.AddGroupedKeyLevel(KeyLevelBeforeMerging.iloc[0]['ticker id'], KeyLevelBeforeMerging.iloc[0]['key level price'], KeyLevelBeforeMerging.iloc[0]['key level score'], KeyLevelBeforeMerging.iloc[0]['identified time id'])
        
        # TickerIDList = [KeyLevelBeforeMerging.iloc[0]['ticker id']]
        # KeyLevelPriceList = [KeyLevelBeforeMerging.iloc[0]['key level price']]
        # KeyLevelScoreList = [KeyLevelBeforeMerging.iloc[0]['key level score']]
        
        for i in range(1, len(KeyLevelBeforeMerging)):
            if (KeyLevelBeforeMerging.iloc[i]['ticker id'] != self.TickerIDList[-1]):
                self.AddGroupedKeyLevel(KeyLevelBeforeMerging.iloc[i]['ticker id'], KeyLevelBeforeMerging.iloc[i]['key level price'], KeyLevelBeforeMerging.iloc[i]['key level score'], KeyLevelBeforeMerging.iloc[i]['identified time id'])
            elif ((self.KeyLevelPriceList[-1] - KeyLevelBeforeMerging.iloc[i]['key level price']) / self.KeyLevelPriceList[-1] > self.MinimumGroupedKeyLevelIntervalPct):
                self.AddGroupedKeyLevel(KeyLevelBeforeMerging.iloc[i]['ticker id'], KeyLevelBeforeMerging.iloc[i]['key level price'], KeyLevelBeforeMerging.iloc[i]['key level score'], KeyLevelBeforeMerging.iloc[i]['identified time id'])
            elif (KeyLevelBeforeMerging.iloc[i]['key level score'] > self.KeyLevelScoreList[-1] * self.KeyLevelGroupingIgnoreScoreThreshold):
                self.UpdateGroupedKeyLevel(((KeyLevelBeforeMerging.iloc[i]['key level price'] * KeyLevelBeforeMerging.iloc[i]['key level score']) + (self.KeyLevelPriceList[-1] * self.KeyLevelScoreList[-1])) / (KeyLevelBeforeMerging.iloc[i]['key level score'] + self.KeyLevelScoreList[-1]), self.KeyLevelScoreList[-1] + self.KeyLevelMergingScaleUp * KeyLevelBeforeMerging.iloc[i]['key level score'])
        df = pd.DataFrame(data={'ticker id': self.TickerIDList, 'key level price': self.KeyLevelPriceList, 'key level score': self.KeyLevelScoreList, 'identified time id': self.KeyLevelTimeList})
        df = df.merge(self.AnalysisContext.FuturesData.TimeIDMapping, left_on='identified time id', right_on='time id')
        return df

    
    def GetKeyLevel(self, ValueDateTimeID):
        KeyLevelBeforeMerging = self.MergeKeyLevel(ValueDateTimeID)
        KeyLevelBeforeMerging.to_csv(r'd:\temp\KeyLevelBeforeMerging.csv')
        print('KeyLevelBeforeMerging is')
        print(KeyLevelBeforeMerging)
        return self.GroupKeyLevel(KeyLevelBeforeMerging)
        
    

class KeyLevel:
    def __init__(self, KeyLevelLabel, AnalysisContext,  ResultOutputFolderPath = None):
        self.KeyLevelLabel = KeyLevelLabel
        self.AnalysisContext = AnalysisContext
        self.ResultOutputFolderPath = ResultOutputFolderPath
        pass

class KeyLevelPivot(KeyLevel):
    def __init__(self, AnalysisContext, ResultOutputFolderPath = None, minimum_slopes = [0.001, 0.002], first_consecutive_boundary_breach_tolerances = [3], GPUMode = True):
        super().__init__("KeyLevelPivot", AnalysisContext, ResultOutputFolderPath = ResultOutputFolderPath)
        self.GPUMode = GPUMode
        self.minimum_slopes = minimum_slopes
        self.first_consecutive_boundary_breach_tolerances = first_consecutive_boundary_breach_tolerances
        # print('in init, minimum_slopes is')
        # print(minimum_slopes)
        # print('in init, self.minimum_slopes is')
        # print(self.minimum_slopes)
        self.IdentifyKeyLevel()
        
    def IdentifyKeyLevel(self):
        if self.GPUMode:
            # print('self.minimum_slopes is')
            # print(self.minimum_slopes)
            self.KeyLevels = CUDAIdentifyKeyLevelPivot(self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_close_adj'], self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_high_adj'], self.AnalysisContext.IntradayPricesData.DataMatrix['TRADES_low_adj'], self.AnalysisContext.IntradayPricesData.DataMatrix['vol'], self.minimum_slopes, self.first_consecutive_boundary_breach_tolerances, key_level_score_multiplier = [1, 1, 1, 1, 1])
        
    