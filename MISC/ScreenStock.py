# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 23:31:26 2021

@author: Henry Cheung
"""
from InvestmentAnalytics.MarketDataReader import DailySpotPriceReader
from InvestmentAnalytics.InstrumentScreener import *
from InvestmentAnalytics.Indicator import *
from datetime import date, datetime, timedelta
import pandas as pd

pd.set_option('display.max_columns', None)

StartDate = datetime(2020, 1, 1)
EndDate = datetime(2021, 1, 15)
# EndDate = today = date.today()
# StartDate = (today - timedelta(days=60))
print('StartDate = ' + str(StartDate) + ' and EndDate = '+ str(EndDate))
MarketList = ['XUSA', 'XHKG']

# indicator_list = [BoxBreakoutPatternIndicator(60, 1, 0.1, 0.03, 2, 'Close'), BoxBreakoutPatternIndicator(22*6, 1, 0.2, 0.03, 2, 'Close')]
# indicator_list = [BoxBreakoutPatternIndicator(60, 1, 0.1, 0.03, 2, 'HighLow'), BoxBreakoutPatternIndicator(22*6, 1, 0.2, 0.03, 2, 'HighLow')]

BoxBreakoutPatternIndicator_list = [BoxBreakoutPatternIndicator(60, 1, 0.1, 0.03, 2, 'HighLow'), BoxBreakoutPatternIndicator(22*6, 1, 0.2, 0.03, 2, 'HighLow'),
                  BoxBreakoutPatternIndicator(60, 1, 0.1, 0.03, 2, 'Close'), BoxBreakoutPatternIndicator(22*6, 1, 0.2, 0.03, 2, 'Close')]

SMAIndicator_list = [SimpleMovingAverageIndicator(20), SimpleMovingAverageIndicator(60), SimpleMovingAverageIndicator(120)]

indicator_list = []
signal_list = []

for indicator in BoxBreakoutPatternIndicator_list:
    indicator_list.append(indicator)
    signal_list.append(BoxBreakoutPatternSignal(indicator))

for indicator in SMAIndicator_list:
    indicator_list.append(indicator)

signal_list.append(IndicatorCrossingSignal(SMAIndicator_list[0],SMAIndicator_list[1]))
signal_list.append(IndicatorCrossingSignal(SMAIndicator_list[1],SMAIndicator_list[2]))

screener = InstrumentScreener("Box Breakout and SMA Screener", indicator_list, signal_list)

# screenerlist = InstrumentScreenerList(StartDate, EndDate, MarketList, TickerFilter = {'XUSA': ['AA', 'AAL', 'AAN', 'AAP']}, ScreenerList = [screener])

screenerlist = InstrumentScreenerList(StartDate, EndDate, MarketList, ScreenerList = [screener])
# screenerlist = InstrumentScreenerList(StartDate, EndDate, MarketList, ScreenerList = [screener], TickerFilter = ['0003.HK', '0035.HK'])


print('ConsolidatedLookBackPeriod is')
print(screenerlist.ConsolidatedLookBackPeriod)
print('AnalysisContext.DailyData.DataMatrix is')
print(screenerlist.AnalysisContext.DailyData.DataMatrix)
print('AnalysisContext.IndicatorDataMatrix '+ ' at ' + str(datetime.now()) + ' is')
print(screenerlist.AnalysisContext.IndicatorDataMatrix)

for screener in screenerlist.ScreenerList:
    screener.PrepareLongShortSignal(screenerlist.AnalysisContext)
    for SignalLabel in screener.LongShortSignalDF:
        print('LongShortSignal of ' + SignalLabel + ' at ' + str(datetime.now()))
        print(screener.LongShortSignalDF[SignalLabel])

print('TickerIDMapping is ')
print(screenerlist.AnalysisContext.DailyData.TickerIDMapping)

print('DateIDMapping is ')
print(screenerlist.AnalysisContext.DailyData.DateIDMapping)




# SELECT * FROM `fdata_price_dayend` WHERE ticker = '0035.HK' and Datetime <= '2020-11-11' ORDER BY Datetime DESC

# LongIndicator = np.where(screenerlist.AnalysisContext.IndicatorDataMatrix == 1.0)
# print('Long Indicator at')
# print(LongIndicator)

# ShortIndicator = np.where(screenerlist.AnalysisContext.IndicatorDataMatrix == -1.0)
# print('Short Indicator at')
# print(ShortIndicator)


# for market in screenerlist.DailySpotPrices.SpotPrices:
#     print(screenerlist.DailySpotPrices.SpotPrices[market])   
# for market in screenerlist.DailySpotPrices.SpotPrices:
#     df = screenerlist.DailySpotPrices.SpotPrices[market]
#     # screenedData = df.loc[df['Indicator|BoxBreakoutPattern|10|1|0.2|2.0'] == True]
#     screenedData = df.loc[df[indicator.IndicatorLabel] == True]
#     print(screenedData)
#     filepath = r'D:\PythonProjects\TradeAnalysis\AnalysisResult\ScreenedData_' + str(StartDate) + '_' + str(EndDate) + '_' + indicator.IndicatorLabel + '_' + market + '.xlsx'
#     filepath = filepath.replace("|", "_")
#     screenedData.to_excel(filepath)  