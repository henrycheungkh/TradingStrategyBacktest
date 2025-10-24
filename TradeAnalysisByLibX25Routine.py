# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 07:53:53 2023

@author: henry
"""

import logging
logging.disable(logging.INFO)



from InvestmentAnalytics.TradeAnalysisLib import RunTradeAnalysisBatch

# RunTradeAnalysisBatch('Henry Routine X25', 'Full', r'E:\TradeAnalysisProject\RoutineAnalysis\CorrelationOnSpecificTimeSectionStrategy\\', BatchIDList = [10], TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], ClearDataAfterEachSubBatch = True, BatchListDatabaseName = 'finance_fdata_master_x25', BatchListTableName = 'fdata_backtest_corr_on_specific_time_section')
# RunTradeAnalysisBatch('Henry Routine X25', 'Full', r'E:\TradeAnalysisProject\RoutineAnalysis\CorrelationOnSpecificTimeSectionStrategy\\', BatchIDList = [12], TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], ClearDataAfterEachSubBatch = True, BatchListDatabaseName = 'finance_fdata_master_x25', BatchListTableName = 'fdata_backtest_corr_on_specific_time_section')
# RunTradeAnalysisBatch('Henry Routine X25', 'Full', r'E:\TradeAnalysisProject\RoutineAnalysis\CorrelationOnSpecificTimeSectionStrategy\\', BatchIDList = [13], TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['CorrelationOnSpecificTimeSectionStrategy'], ClearDataAfterEachSubBatch = True, BatchListDatabaseName = 'finance_fdata_master_x25', BatchListTableName = 'fdata_backtest_corr_on_specific_time_section')


RunTradeAnalysisBatch('Henry Routine', 'Full', r'E:\TradeAnalysisProject\RoutineAnalysis\RangeTradeOnTimeRange\\', BatchIDList = [21102], TimeFrameList = ['1 min'], InstrumentTypeList = ['Futures'], StrategyNameList = ['RangeTradeOnSpecificPastTimeRangeStrategy'], ClearDataAfterEachSubBatch = True, BatchListDatabaseName = 'finance_fdata_master_x25', BatchListTableName = 'fdata_backtest_range_trade_on_time_range')
