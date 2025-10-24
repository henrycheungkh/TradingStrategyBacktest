# -*- coding: utf-8 -*-
"""
Created on Thu Oct 28 00:27:12 2021

@author: Henry Cheung
"""

from InvestmentAnalytics.TradeAnalysisLib import RunTradeAnalysisBatch

# def RunTradeAnalysisBatch(BatchGroup, BatchType, ResultOutputFolderPath, TimeFrameList = [], InstrumentTypeList = [], StrategyNameList = [], BatchIDList = [], BatchSubIDList = [], KeepOnlyWeekdays = True, FillEveryTimeSlot = False):



# RunTradeAnalysisBatch('Henry Routine', 'Full', r'G:\TradeAnalysisProject\RoutineAnalysis\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], BatchIDList = [12], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry Routine', 'Full', r'G:\TradeAnalysisProject\RoutineAnalysis\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], BatchIDList = [13], ClearDataAfterEachSubBatch = True)
RunTradeAnalysisBatch('Henry Routine', 'Full', r'G:\TradeAnalysisProject\RoutineAnalysis\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], BatchIDList = [14], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry Routine', 'Full', r'G:\TradeAnalysisProject\RoutineAnalysis\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], BatchIDList = [15], ClearDataAfterEachSubBatch = True)


# RunTradeAnalysisBatch('Henry Routine', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['RangeTradeOnSpecificPastTimeRangeStrategy'], BatchIDList = [210], ClearDataAfterEachSubBatch = True)


