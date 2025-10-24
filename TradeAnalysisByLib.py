# -*- coding: utf-8 -*-
"""
Created on Thu Oct 28 00:27:12 2021

@author: Henry Cheung
"""

from InvestmentAnalytics.TradeAnalysisLib import RunTradeAnalysisBatch

# def RunTradeAnalysisBatch(BatchGroup, BatchType, ResultOutputFolderPath, TimeFrameList = [], InstrumentTypeList = [], StrategyNameList = [], BatchIDList = [], BatchSubIDList = [], KeepOnlyWeekdays = True, FillEveryTimeSlot = False):


# RunTradeAnalysisBatch('Henry', 'Full', r'd:\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Crypto'], StrategyNameList = ['SharpeRatioStrategy'], KeepOnlyWeekdays = True, FillEveryTimeSlot = False)

# RunTradeAnalysisBatch('Henry', 'Full', r'd:\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['SharpeRatioStrategy'], KeepOnlyWeekdays = True, FillEveryTimeSlot = False)


# RunTradeAnalysisBatch('Henry', 'Full', r'd:\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures', 'Crypto'], StrategyNameList = ['SharpeRatioStrategy'], KeepOnlyWeekdays = True, FillEveryTimeSlot = False)


# RunTradeAnalysisBatch('Henry', 'Selected', r'd:\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], KeepOnlyWeekdays = True, FillEveryTimeSlot = False)




# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Crypto'], StrategyNameList = ['SharpeRatioStrategy'])

# RunTradeAnalysisBatch('Henry', 'Selected', r'd:\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'])

# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], BatchIDList = [3,4])

# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], BatchIDList = [3], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], BatchIDList = [4], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], BatchIDList = [5], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], BatchIDList = [9], ClearDataAfterEachSubBatch = True)

# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], BatchIDList = [8], ClearDataAfterEachSubBatch = True)

# RunTradeAnalysisBatch('Henry Routine', 'Full', r'G:\TradeAnalysisProject\RoutineAnalysis\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], BatchIDList = [12], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry Routine', 'Full', r'G:\TradeAnalysisProject\RoutineAnalysis\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], BatchIDList = [13], ClearDataAfterEachSubBatch = True)
RunTradeAnalysisBatch('Henry Routine', 'Full', r'G:\TradeAnalysisProject\RoutineAnalysis\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], BatchIDList = [14], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry Routine', 'Full', r'G:\TradeAnalysisProject\RoutineAnalysis\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], BatchIDList = [15], ClearDataAfterEachSubBatch = True)


# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], BatchIDList = [6], ClearDataAfterEachSubBatch = True)



# RunTradeAnalysisBatch('Henry', 'UAT', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['SharpeRatioStrategy'], BatchIDList = [2101])

# RunTradeAnalysisBatch('Henry', 'UAT', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], BatchIDList = [2011], ClearDataAfterEachSubBatch = True)

# RunTradeAnalysisBatch('Henry', 'UAT', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['IndicatorStrategy'], BatchIDList = [2200], ClearDataAfterEachSubBatch = True, DebugFilepath = r'G:\TradeAnalysisProject\temp\\')

# RunTradeAnalysisBatch('Henry', 'UAT', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['IndicatorStrategy'], BatchIDList = [2202], ClearDataAfterEachSubBatch = True, DebugFilepath = r'G:\TradeAnalysisProject\temp\\')

# RunTradeAnalysisBatch('Henry', 'UAT', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['IndicatorStrategy'], BatchIDList = [2203], ClearDataAfterEachSubBatch = True, DebugFilepath = r'G:\TradeAnalysisProject\temp\\')

# RunTradeAnalysisBatch('Henry', 'UAT', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['IndicatorStrategy'], BatchIDList = [2204], ClearDataAfterEachSubBatch = True, DebugFilepath = r'G:\TradeAnalysisProject\temp\\')

# RunTradeAnalysisBatch('Henry', 'UAT', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['IndicatorStrategy'], BatchIDList = [2205], ClearDataAfterEachSubBatch = True, DebugFilepath = r'G:\TradeAnalysisProject\temp\\')

# RunTradeAnalysisBatch('Henry', 'UAT', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Crypto'], StrategyNameList = ['IndicatorStrategy'], BatchIDList = [2206], ClearDataAfterEachSubBatch = True, DebugFilepath = r'G:\TradeAnalysisProject\temp\\')


# RunTradeAnalysisBatch('Henry', 'UAT', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['IndicatorStrategy'], BatchIDList = [2207], ClearDataAfterEachSubBatch = True, DebugFilepath = r'G:\TradeAnalysisProject\temp\\')

# RunTradeAnalysisBatch('Henry', 'UAT', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['IndicatorStrategy'], BatchIDList = [2208], ClearDataAfterEachSubBatch = True, DebugFilepath = r'G:\TradeAnalysisProject\temp\\')






# RunTradeAnalysisBatch('Indicator Standalone', 'Full', r'G:\TradeAnalysisProject\IndicatorStandalone\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Crypto'], StrategyNameList = ['IndicatorStrategy'], BatchIDList = [0], ClearDataAfterEachSubBatch = True, DebugFilepath = r'G:\TradeAnalysisProject\IndicatorStandalone\\')

# RunTradeAnalysisBatch('Indicator Standalone', 'Full', r'G:\TradeAnalysisProject\IndicatorStandalone\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Crypto'], StrategyNameList = ['IndicatorStrategy'], BatchIDList = [1], ClearDataAfterEachSubBatch = True, DebugFilepath = r'G:\TradeAnalysisProject\IndicatorStandalone\\')


# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['10 secs'], InstrumentTypeList = ['Futures'], StrategyNameList = ['MarketShockStrategy'], BatchIDList = [71], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['10 secs'], InstrumentTypeList = ['Futures'], StrategyNameList = ['MarketShockStrategy'], BatchIDList = [70], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['10 secs'], InstrumentTypeList = ['Futures'], StrategyNameList = ['MarketShockStrategy'], BatchIDList = [73], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['10 secs'], InstrumentTypeList = ['Futures'], StrategyNameList = ['MarketShockStrategy'], BatchIDList = [75], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['10 secs'], InstrumentTypeList = ['Futures'], StrategyNameList = ['MarketShockStrategy'], BatchIDList = [76], ClearDataAfterEachSubBatch = True)



# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['RangeTradeOnSpecificPastTimeRangeStrategy'], BatchIDList = [201], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['RangeTradeOnSpecificPastTimeRangeStrategy'], BatchIDList = [202], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['RangeTradeOnSpecificPastTimeRangeStrategy'], BatchIDList = [203], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['RangeTradeOnSpecificPastTimeRangeStrategy'], BatchIDList = [204], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['RangeTradeOnSpecificPastTimeRangeStrategy'], BatchIDList = [205], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['RangeTradeOnSpecificPastTimeRangeStrategy'], BatchIDList = [206], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['RangeTradeOnSpecificPastTimeRangeStrategy'], BatchIDList = [207], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['RangeTradeOnSpecificPastTimeRangeStrategy'], BatchIDList = [208], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['RangeTradeOnSpecificPastTimeRangeStrategy'], BatchIDList = [209], ClearDataAfterEachSubBatch = True)
# RunTradeAnalysisBatch('Henry', 'Full', r'G:\TradeAnalysisProject\temp\\', TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['RangeTradeOnSpecificPastTimeRangeStrategy'], BatchIDList = [210], ClearDataAfterEachSubBatch = True)


