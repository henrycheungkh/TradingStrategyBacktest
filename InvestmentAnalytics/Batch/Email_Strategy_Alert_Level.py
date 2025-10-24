# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 02:33:37 2020

@author: Henry Cheung
"""
from InvestmentAnalytics.EmailModule import SendEmail
from datetime import date, datetime, timedelta

# from os import environ
# from sqlalchemy import create_engine

import InvestmentAnalytics.Config as Config

# uri = 'mysql+pymysql://root:@localhost/finance_fdata_fut_hist'

# engine = create_engine(uri, echo=True)

Message = ''
Appendix = ''

# import pandas as pd

from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy_CorrelationOnSpecificTimeSectionStrategy import CorrelationOnSpecificTimeSectionStrategy

mes, app = CorrelationOnSpecificTimeSectionStrategy.PrepareEmailAlert(1, 'CorrelationOnSpecificTimeSectionStrategy, Mean Reversal<BR>ticker = ES, Obs Time = 12:05:00, Obs Movement = 1.9%, Take Profit = 25bps, Stop Loss = 25bps', 'ES', '12:05:00', 0.019, 25, 25, '6:21am NY time', TickSize = 0.25, AppendixFirstLine = 'For CorrelationOnSpecificTimeSectionStrategy, Batch ID 13<BR>Obs Movement = 1.9%, ticker = ES, Take Profit = 25bps, Stop Loss = 25bps', TradeForceExitTime = '7:21am NY time', BackTestSharpeRatio = 0.80242866, BackTestTradeSampleSize = 56, BackTestPeriod='2019-01-01 to 2023-03-31', UpdateStrategyExecutionConfig = True)
Message = Message + mes
Appendix = Appendix + app

mes, app = CorrelationOnSpecificTimeSectionStrategy.PrepareEmailAlert(2, 'CorrelationOnSpecificTimeSectionStrategy, Mean Reversal<BR>ticker = ES, Obs Time = 12:36:00, Obs Movement = 1.75%, Take Profit = 25bps, Stop Loss = 50bps', 'ES', '12:05:00', 0.0175, 25, 50, '0:36am NY time', TickSize = 0.25, AppendixFirstLine = 'For CorrelationOnSpecificTimeSectionStrategy, Batch ID 12<BR>Obs Movement = 1.75%, ticker = ES, Take Profit = 25bps, Stop Loss = 50bps', TradeForceExitTime = '4:21am NY time', BackTestSharpeRatio = 0.75152737, BackTestTradeSampleSize = 53, BackTestPeriod='2019-01-01 to 2023-03-31')
Message = Message + mes
Appendix = Appendix + app

mes, app = CorrelationOnSpecificTimeSectionStrategy.PrepareEmailAlert(3, 'CorrelationOnSpecificTimeSectionStrategy, Mean Reversal<BR>ticker = GC, Obs Time = 08:55:00, Obs Movement = 1.5%, Take Profit = 25bps, Stop Loss = 50bps', 'GC', '08:55:00', 0.015, 25, 50, '2:01am NY time', TickSize = 0.1, AppendixFirstLine = 'For CorrelationOnSpecificTimeSectionStrategy, Batch ID 11<BR>Obs Movement = 1.5%, ticker = GC, Take Profit = 25bps, Stop Loss = 50bps', TradeForceExitTime = '2:26am NY time', BackTestSharpeRatio = 0.616056, BackTestTradeSampleSize = 69, BackTestPeriod='2019-01-01 to 2023-03-31')
Message = Message + mes
Appendix = Appendix + app

from InvestmentAnalytics.Strategy.Futures.FuturesTradingStrategy_RangeTradeOnSpecificPastTimeRangeStrategy import RangeTradeOnSpecificPastTimeRangeStrategy

# mes, app = RangeTradeOnSpecificPastTimeRangeStrategy.PrepareEmailAlert(4, 'RangeTradeOnSpecificPastTimeRangeStrategy, Breakthrough, Max profit trades per day = 3, Max loss trades per day = 3<BR>ticker = ES', 'ES', -1320, -1080, 750, 300, 0.02, 0.05, 100, 150, True, '12:30pm NY time', TickSize = 0.25, AppendixFirstLine = 'For RangeTradeOnSpecificPastTimeRangeStrategy, Batch ID 20805<BR>ticker = ES, Take Profit = 10% of range, Stop Loss = 150% of range', TradeForceExitTime = '5:30pm NY time', BackTestSharpeRatio = 1.1871157, BackTestTradeSampleSize = 56, BackTestPeriod='2019-01-01 to 2022-12-31', isMeanReversing=False)
mes, app = RangeTradeOnSpecificPastTimeRangeStrategy.PrepareEmailAlert(4, 'RangeTradeOnSpecificPastTimeRangeStrategy, Breakthrough, Max profit trades per day = 3, Max loss trades per day = 3<BR>ticker = ES', 'ES', -1320, -1080, 750, 300, 0.02, 0.05, 100, 150, True, '12:30pm NY time', TickSize = 0.25, AppendixFirstLine = 'For RangeTradeOnSpecificPastTimeRangeStrategy, Batch ID 10<BR>ticker = ES, Take Profit = 10% of range, Stop Loss = 15% of range', TradeForceExitTime = '5:30pm NY time', BackTestSharpeRatio = 0.9505752, BackTestTradeSampleSize = 62, BackTestPeriod='2019-01-01 to 2023-03-31', isMeanReversing=False)
Message = Message + mes
Appendix = Appendix + app


# print(Message)

SendEmail(['henry.cheungkh@gmail.com'], 'Pre Open Strategy Alert Summary - CorrelationOnSpecificTimeSectionStrategy - ' + date.today().strftime("%B %d, %Y"), Message + "<BR><BR><h2>Appendix</h2>" + Appendix)

