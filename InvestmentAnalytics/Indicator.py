# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 22:37:25 2021

@author: Henry Cheung
"""
import numpy as np
from InvestmentAnalytics.CUDA.IndicatorCUDALib import *
from InvestmentAnalytics.MarketDataReader import *


class TradingSignal:
    pass

class BoxBreakoutPatternSignal:
    def __init__(self, BoxBreakoutPatternIndicator):
        self.BoxBreakoutPatternIndicator = BoxBreakoutPatternIndicator
        self.SignalLabel = "TradingSignal|" + BoxBreakoutPatternIndicator.IndicatorLabel
        
    def GetLongShortSignal(self, AnalysisContext):
        LongShortSignal = []
        for ticker_id in range(len(AnalysisContext.IndicatorDataMatrix[self.BoxBreakoutPatternIndicator.IndicatorLabel])):
            for time_id in range(len(AnalysisContext.IndicatorDataMatrix[self.BoxBreakoutPatternIndicator.IndicatorLabel][0])):
                if AnalysisContext.IndicatorDataMatrix[self.BoxBreakoutPatternIndicator.IndicatorLabel][ticker_id][time_id] == 1:
                    LongShortSignal.append([ticker_id, time_id, 'Long'])
                if AnalysisContext.IndicatorDataMatrix[self.BoxBreakoutPatternIndicator.IndicatorLabel][ticker_id][time_id] == -1:
                    LongShortSignal.append([ticker_id, time_id, 'Short'])
        return pd.DataFrame(LongShortSignal, columns=['ticker id', 'date id', 'signal'])
    
class IndicatorCrossingSignal:
    def __init__(self, LeadingIndicator, LaggingIndicator):
        self.LeadingIndicator = LeadingIndicator
        self.LaggingIndicator = LaggingIndicator
        self.SignalLabel = "TradingSignal|Indicator Crossing|" + LeadingIndicator.IndicatorLabel + "|cross|" + LaggingIndicator.IndicatorLabel
    def GetLongShortSignal(self, AnalysisContext):
        LongShortSignal = []
        for ticker_id in range(len(AnalysisContext.IndicatorDataMatrix[self.LeadingIndicator.IndicatorLabel])):
            for time_id in range(len(AnalysisContext.IndicatorDataMatrix[self.LeadingIndicator.IndicatorLabel][0])):
                if AnalysisContext.IndicatorDataMatrix[self.LeadingIndicator.IndicatorLabel][ticker_id][time_id] > AnalysisContext.IndicatorDataMatrix[self.LaggingIndicator.IndicatorLabel][ticker_id][time_id]:
                    LongShortSignal.append([ticker_id, time_id, 'Long'])
                if AnalysisContext.IndicatorDataMatrix[self.LeadingIndicator.IndicatorLabel][ticker_id][time_id] < AnalysisContext.IndicatorDataMatrix[self.LaggingIndicator.IndicatorLabel][ticker_id][time_id]:
                    LongShortSignal.append([ticker_id, time_id, 'Short'])
        return pd.DataFrame(LongShortSignal, columns=['ticker id', 'date id', 'signal'])        
    

        
        
# class AnalysisIndicator:
#     def __init__(self, IndicatorLabel, LookBackPeriod):
#         self.IndicatorLabel = "Indicator|" + IndicatorLabel
#         self.LookBackPeriod = LookBackPeriod
#     def getLookBackPeriod(IndicatorList):
#         ConsolidatedLookBackPeriod = {"Adj Close":0, "High":0, "Low":0, "Open":0, "Volume":0}
#         LookBackPeriodItemList = ["Adj Close", "High", "Low", "Open", "Volume"]
#         for indicator in IndicatorList:
#             for item in LookBackPeriodItemList:
#                 if indicator.LookBackPeriod[item] > ConsolidatedLookBackPeriod[item]:
#                     ConsolidatedLookBackPeriod[item] = indicator.LookBackPeriod[item]
#         return ConsolidatedLookBackPeriod
#     def applyIndicator(self, SpotPrices):
#         return SpotPrices    
    
        
class AnalysisIndicator:
    def __init__(self, IndicatorLabel, LookBackPeriod):
        self.IndicatorLabel = "Indicator|" + IndicatorLabel
        self.LookBackPeriod = LookBackPeriod
    def getLookBackPeriod(IndicatorList):
        ConsolidatedLookBackPeriod = {"Adj Close":0, "High":0, "Low":0, "Open":0, "Volume":0, "TRADES_close_adj":0, "vol":0}
        # LookBackPeriodItemList = ["Adj Close", "High", "Low", "Open", "Volume", "TRADES_close_adj"]
        for indicator in IndicatorList:
            for item in ConsolidatedLookBackPeriod:
                if indicator.LookBackPeriod[item] > ConsolidatedLookBackPeriod[item]:
                    ConsolidatedLookBackPeriod[item] = indicator.LookBackPeriod[item]
        return ConsolidatedLookBackPeriod
    def applyIndicator(self, SpotPrices):
        return SpotPrices

class TechnicalAnalysisIndicator(AnalysisIndicator):
    pass

class FundamentalAnalysisIndicator(AnalysisIndicator):
    pass
    
class SimpleMovingAverageIndicator(TechnicalAnalysisIndicator):
    def __init__(self, MA_Day):
        super().__init__("SMA|" + str(MA_Day), {"Adj Close":MA_Day, "High":0, "Low":0, "Open":0, "Volume":0})
        self.MA_Day = MA_Day

    def GetIndicatorMatrix(self, AnalysisContext):
        return CUDASimpleMovingAverageIndicator(self.IndicatorLabel, AnalysisContext.DailyData.DataMatrix['Adj Close'], self.MA_Day)


class VolumeWeightedAveragePriceIndicator(TechnicalAnalysisIndicator):
    def __init__(self, MA_Day):
        super().__init__(self, "VWAP|" + str(MA_Day), {"Adj Close":MA_Day, "High":0, "Low":0, "Open":0, "Volume":MA_Day})
        self.MA_Day = MA_Day 
    
class PatternIndicator(AnalysisIndicator):
    pass

class SingleCandleSpikePatternIndicator(PatternIndicator):
    def __init__(self, SpikeSizePercentageThreshold, ClosePriceColumnName = "TRADES_close_adj"):
        self.SpikeSizePercentageThreshold = SpikeSizePercentageThreshold
        super().__init__(("SingleCandleSpikePattern|" + str(SpikeSizePercentageThreshold)), {ClosePriceColumnName:1})
    def GetIndicatorMatrix(self, AnalysisContext):
        return CUDASingleCandleSpikePatternIndicator(self.IndicatorLabel, AnalysisContext.FuturesData.DataMatrix['TRADES_close_adj'], AnalysisContext.FuturesData.DataMatrix['TRADES_high_adj'], AnalysisContext.FuturesData.DataMatrix['TRADES_low_adj'], AnalysisContext.FuturesData.DataMatrix['vol'], AnalysisContext.FuturesData.DataMatrix['TimeInStandardUnit'], self.SpikeSizePercentageThreshold, block_cutting_dimension = "Time Dimension")
    
    
    

class BoxBreakoutPatternIndicator(PatternIndicator):
    def __init__(self, BoxPeriod, BreakoutPeriod, BoxHeightRatio, BreakoutGainRatio, VolumeRatio, BoxMode):
        if BoxMode == "HighLow":
            super().__init__(("BoxBreakoutPattern|" + str(BoxPeriod) + "|"+ str(BreakoutPeriod)+ "|"+ str(BoxHeightRatio)+ "|"+ str(BreakoutGainRatio)+ "|"+ str(VolumeRatio)+ "|"+ str(BoxMode)), {"Adj Close":(BoxPeriod + BreakoutPeriod), "High":(BoxPeriod + BreakoutPeriod), "Low":(BoxPeriod + BreakoutPeriod), "Open":0, "Volume":(BoxPeriod + BreakoutPeriod)})
        else:
            super().__init__(("BoxBreakoutPattern|" + str(BoxPeriod) + "|"+ str(BreakoutPeriod)+ "|"+ str(BoxHeightRatio)+ "|"+ str(BreakoutGainRatio)+ "|"+ str(VolumeRatio)+ "|"+ str(BoxMode)), {"Adj Close":(BoxPeriod + BreakoutPeriod), "High":0, "Low":0, "Open":0, "Volume":(BoxPeriod + BreakoutPeriod)})
        self.Period = BoxPeriod + BreakoutPeriod
        self.BoxPeriod = BoxPeriod
        self.BreakoutPeriod = BreakoutPeriod
        self.BoxHeightRatio = BoxHeightRatio
        self.BreakoutGainRatio = BreakoutGainRatio
        self.VolumeRatio = VolumeRatio
        self.BoxMode = BoxMode
        
    def GetBullBearIndicator(self, AnalysisContext):
        BullBearIndicator = []
        for ticker_id in range(len(AnalysisContext.IndicatorDataMatrix[self.IndicatorLabel])):
            for time_id in range(len(AnalysisContext.IndicatorDataMatrix[self.IndicatorLabel][0])):
                if AnalysisContext.IndicatorDataMatrix[self.IndicatorLabel][ticker_id][time_id] == 1:
                    BullBearIndicator.append([ticker_id, time_id, 'Bull'])
                if AnalysisContext.IndicatorDataMatrix[self.IndicatorLabel][ticker_id][time_id] == -1:
                    BullBearIndicator.append([ticker_id, time_id, 'Bear'])
        return pd.DataFrame(BullBearIndicator, columns=['ticker id', 'date id', 'indicator'])
        
        
    def GetIndicatorMatrix(self, AnalysisContext):
        if self.BoxMode == "HighLow":
            return CUDABoxBreakoutPatternIndicator(self.IndicatorLabel, AnalysisContext.DailyData.DataMatrix['Adj Close'], AnalysisContext.DailyData.DataMatrix['Volume'], self.BoxPeriod, self.BreakoutPeriod, self.BoxHeightRatio, self.BreakoutGainRatio, self.VolumeRatio, HighPrice = AnalysisContext.DailyData.DataMatrix['High'], LowPrice = AnalysisContext.DailyData.DataMatrix['Low'])
        else:
            return CUDABoxBreakoutPatternIndicator(self.IndicatorLabel, AnalysisContext.DailyData.DataMatrix['Adj Close'], AnalysisContext.DailyData.DataMatrix['Volume'], self.BoxPeriod, self.BreakoutPeriod, self.BoxHeightRatio, self.BreakoutGainRatio, self.VolumeRatio)
        
    def applyIndicator(self, SpotPrices):
        pass
        # if self.IndicatorLabel in SpotPrices.columns:
        #     return SpotPrices
        # else:
        #     print('Apply Indicator ' + self.IndicatorLabel)
        #     SpotPrices[self.IndicatorLabel] = np.nan
        #     MinIndex = SpotPrices.min()['index']
        #     MaxIndex = SpotPrices.max()['index']
        #     # print('index min is ' + str(MinIndex))
        #     # print('index max is ' + str(MaxIndex))
        #     # print(SpotPrices.loc[1, ['Adj Close']][0])
        #     CurrentTicker = ''
        #     for x in range(MinIndex, MaxIndex+1):
        #         if SpotPrices.loc[x, ['ticker']][0] != CurrentTicker:
        #             CurrentTicker = SpotPrices.loc[x, ['ticker']][0]
        #             # print('Processing Ticker ' + CurrentTicker)
        #         # print('x = ' + str(x))
        #         if x > self.BoxPeriod + self.BreakoutPeriod - 1:
        #             MaxPrice = 0
        #             MinPrice = 9999999999999
        #             AverageVolume = 0
        #             for y in range(x-self.BoxPeriod-self.BreakoutPeriod+1, x-self.BreakoutPeriod+1):
        #                 # print('y = ' + str(y))
        #                 if SpotPrices.loc[y, ['ticker']][0] != SpotPrices.loc[x, ['ticker']][0]:
        #                     MaxPrice = 0
        #                     # print('break')
        #                     break
        #                 AverageVolume = AverageVolume + SpotPrices.loc[y, ['Volume']][0]
        #                 if SpotPrices.loc[y, ['High']][0] > MaxPrice:
        #                     MaxPrice = SpotPrices.loc[y, ['High']][0]
        #                 if SpotPrices.loc[y, ['Low']][0] < MinPrice:
        #                     MinPrice = SpotPrices.loc[y, ['Low']][0]
                            
        #             AverageVolume = AverageVolume / self.BoxPeriod
                        
        #             if (MaxPrice > 0):
        #                 if (SpotPrices.loc[x, ['Adj Close']][0] > MaxPrice) and (SpotPrices.loc[x, ['Volume']][0] > AverageVolume * self.VolumeRatio) and ((MaxPrice - MinPrice) / MinPrice < self.BoxHeightRatio):
        #                     print('Ticker ' + CurrentTicker + ' on date ' + str(SpotPrices.loc[x, ['Date']][0]) + ' fulfill indicator condition')
        #                     print('MaxPrice = ' + str(MaxPrice) + ', MinPrice = ' + str(MinPrice) + ', x = ' + str(x) + ', price(x) = ' + str(SpotPrices.loc[x, ['Adj Close']][0]) + ', volume(x) = ' + str(SpotPrices.loc[x, ['Volume']][0]) + ', AverageVolume = ' + str(AverageVolume))
        #                     SpotPrices.loc[x, [self.IndicatorLabel]] = True
        #                 else:
        #                     SpotPrices.loc[x, [self.IndicatorLabel]] = False
        #     return SpotPrices
