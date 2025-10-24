# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 22:58:07 2021

@author: Henry Cheung
"""
from InvestmentAnalytics.MarketDataReader import *
from InvestmentAnalytics.Indicator import *

class InstrumentScreener:
    def __init__(self, ScreenerLabel, IndicatorList = [], SignalList = []):
        self.ScreenerLabel = ScreenerLabel
        self.IndicatorEntrySignalLookbackPeriod = AnalysisIndicator.getLookBackPeriod(IndicatorList)
        self.IndicatorList = {}
        for indicator in IndicatorList:
            self.IndicatorList[indicator.IndicatorLabel] = indicator
        self.SignalList = {}
        for signal in SignalList:
            self.SignalList[signal.SignalLabel] = signal
        
    def append(self, indicator):
        # self.IndicatorList.append(indicator)
        self.IndicatorList[indicator.IndicatorLabel] = indicator
        
    def PrepareBullBearIndicator(self,AnalysisContext):
        BullBearIndicator = {}
        self.BullBearIndicatorDF = {}
        
        for IndicatorLabel in self.IndicatorList:
            df = self.IndicatorList[IndicatorLabel].GetBullBearIndicator(AnalysisContext)
            df = df.merge(AnalysisContext.DailyData.TickerIDMapping, on='ticker id')
            df = df.merge(AnalysisContext.DailyData.DateIDMapping, on='date id')
            self.BullBearIndicatorDF[IndicatorLabel] = df

    def PrepareLongShortSignal(self,AnalysisContext):
        LongShortSignal = {}
        self.LongShortSignalDF = {}
        
        for SignalLabel in self.SignalList:
            df = self.SignalList[SignalLabel].GetLongShortSignal(AnalysisContext)
            df = df.merge(AnalysisContext.DailyData.TickerIDMapping, on='ticker id')
            df = df.merge(AnalysisContext.DailyData.DateIDMapping, on='date id')
            self.LongShortSignalDF[SignalLabel] = df            
        

        
        
    # def getLookBackPeriod(self):
    #     return AnalysisIndicator.getLookBackPeriod(self.IndicatorList)
    

    
class InstrumentScreenerList:
    def __init__(self, StartDate, EndDate, MarketList, DataInterval = ["1d"], TickerFilter = None, ScreenerList = []):
        self.StartDate = StartDate
        self.EndDate = EndDate
        self.MarketList = MarketList
        self.DataInterval = DataInterval
        self.TickerFilter = TickerFilter
        self.ScreenerList = ScreenerList
        if len(ScreenerList) > 0:
            self.ConsolidatedLookBackPeriod = self.getLookBackPeriod()
        else:
            self.ConsolidatedLookBackPeriod = {"Adj Close":0, "High":0, "Low":0, "Open":0, "Volume":0}
        self.LoadData()
        # self.attachHistoricalDataColumns()
        
        # self.ReOrderDailyPrice()
        self.ApplyIndicator()

    # def ReOrderDailyPrice(self):
    #     for market in self.DailySpotPrices.SpotPrices:
    #         self.DailySpotPrices.SpotPrices[market] = self.DailySpotPrices.SpotPrices[market].sort_values(by=['ticker', 'DateIndex']).reset_index()

    def ApplyIndicator(self):
        for screener in self.ScreenerList:
            # for indicator in screener.IndicatorList:
            #     self.AnalysisContext.AddIndicatorData(indicator.GetIndicatorMatrix(self.AnalysisContext))
            for IndicatorLabel in screener.IndicatorList:
                self.AnalysisContext.AddIndicatorData(screener.IndicatorList[IndicatorLabel].GetIndicatorMatrix(self.AnalysisContext))
                
                
    #             for market in self.DailySpotPrices.SpotPrices:
    #                 self.DailySpotPrices.SpotPrices[market] = indicator.applyIndicator(self.DailySpotPrices.SpotPrices[market])
        
    def LoadData(self):
        if "1d" in self.DataInterval:
            self.AnalysisContext = DailySpotPriceAnalysisContext(self.StartDate, self.EndDate, self.MarketList, TickerFilter = self.TickerFilter)
            # for market in self.DailySpotPrices.SpotPrices:
            #     print(self.DailySpotPrices.SpotPrices[market])   
                
    def getLookBackPeriod(self):
        ConsolidatedLookBackPeriod = {"Adj Close":0, "High":0, "Low":0, "Open":0, "Volume":0}
        LookBackPeriodItemList = ["Adj Close", "High", "Low", "Open", "Volume"]
        for screener in self.ScreenerList:
            ScreenerLookBackPeriod = screener.IndicatorEntrySignalLookbackPeriod
            for item in ScreenerLookBackPeriod:
                if ScreenerLookBackPeriod[item] > ConsolidatedLookBackPeriod[item]:
                    ConsolidatedLookBackPeriod[item] = ScreenerLookBackPeriod[item]
        return ConsolidatedLookBackPeriod   

    def appendScreener(self, Screener):
        self.ScreenerList.append(Screener)
        
    # def attachHistoricalDataColumns(self):
    #     for market in self.DailySpotPrices.SpotPrices:
    #         print('Attaching Historical Data Columns for market ' + market)
    #         # df = self.DailySpotPrices.SpotPrices[market]
    #         # LastValueDateIndex = df["DateIndex"].max()
    #         # print("Last Value Date Index = " + str(LastValueDateIndex))
    #         # for DataLabel in ["Adj Close", "High", "Low", "Open", "Volume"]:
    #         #     print('Start filling for ' + DataLabel)
    #         #     if self.ConsolidatedLookBackPeriod[DataLabel] > 0:
    #         #         for x in range(1, self.ConsolidatedLookBackPeriod[DataLabel]+1):
    #         #             print('x = ' + str(x))
    #         #             df_copy = df.copy()
    #         #             df_copy["DateIndex"] = df_copy["DateIndex"] + x
    #         #             df_copy = df_copy[['ticker', 'DateIndex', DataLabel]].rename({DataLabel: DataLabel + "|" + str(x)})
    #         #             df = df.merge(df_copy, how='left', on='DateIndex')
        
        