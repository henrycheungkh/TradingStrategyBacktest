# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 01:20:39 2021

@author: Henry Cheung
"""


from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import pymysql
import InvestmentAnalytics.Config as Config

from InvestmentAnalytics.MarketDataReader import IBFuturesPriceReader, FuturesPriceAnalysisContext
# from InvestmentAnalytics.CUDA.BacktestingCUDALib import CUDABacktestingSummary, CUDABacktestingRapidCalibrationSummary

# from InvestmentAnalytics.Indicator.IndicatorSMA import IndicatorSMA

pd.set_option('display.max_columns', None)

StartDate = datetime(2021, 3, 22)
EndDate = datetime(2021, 11, 13)
MA_Day_List = [3, 5]
TimeFrame = '1 min'
TickerFilter = None
# TickerFilter = ['CL', 'RTY']
# TickerFilter = ['NQ', 'ES']

AnalysisStartTime = datetime.now()
print('Analysis started at ' + str(AnalysisStartTime))


AnalysisContext = FuturesPriceAnalysisContext(StartDate, EndDate, TimeFrame, TickerFilter = TickerFilter)
MaxTimeID = AnalysisContext.FuturesData.TimeIDMapping['time id'].max()

from InvestmentAnalytics.Indicator.Indicator import IndicatorLocator
# indicator = IndicatorLocator.GetFilterIndicator(AnalysisContext, 'SharpeRatioStrategy', 'Henry', 2101, 0)
indicator = IndicatorLocator.GetFilterIndicator(AnalysisContext, 'SharpeRatioStrategy', 'Henry', 2100, 0, '1 min', '1 min')



df = pd.DataFrame(AnalysisContext.IntradayPricesData.DataMatrix['TRADES_close_adj'].T.copy(order="C"), columns=AnalysisContext.FuturesData.TickerIDMapping['ticker'].tolist())
df.to_csv(r'G:\TradeAnalysisProject\temp\closing_price.csv', index=False)


# indicator = IndicatorSMA('TRADES_close_adj', AnalysisContext.IntradayPricesData.DataMatrix['TRADES_close_adj'], MA_Day_List, block_cutting_dimension = "Time Dimension")
indicator_values = indicator.indicator_values

# print(indicator_values)

indicator.UploadIndicatorToAnalysisContext(AnalysisContext)

AnalysisEndTime = datetime.now()
analysis_minutes_diff = round((AnalysisEndTime - AnalysisStartTime).total_seconds() / 60.0)

print('Analysis ended at ' + str(AnalysisEndTime) + ', and ' + str(analysis_minutes_diff) + ' minutes taken')

for i in range(len(indicator.IndicatorParameterList)):
    # df = pd.DataFrame(indicator.indicator_values[i].T.copy(order="C"), columns=AnalysisContext.FuturesData.TickerIDMapping['ticker'].tolist())
    s = indicator.GetFullMatrixLabel(indicator.IndicatorParameterList[i])
    # df = pd.DataFrame(AnalysisContext.IntradayPricesData.DataMatrix["Indicator|SMA|TRADES_close_adj|" + str(MA_Day_List[i])].T.copy(order="C"), columns=AnalysisContext.FuturesData.TickerIDMapping['ticker'].tolist())
    df = pd.DataFrame(AnalysisContext.IntradayPricesData.DataMatrix[s].T.copy(order="C"), columns=AnalysisContext.FuturesData.TickerIDMapping['ticker'].tolist())

    # print(indicator.IndicatorLabel + '(' + str(MA_Day_List[i]) + ') is')
    print(indicator.IndicatorLabel + '(' + str(indicator.IndicatorParameterList[i]) + ') is')

    print(df)
    df.to_csv(r'G:\TradeAnalysisProject\temp\\' + indicator.IndicatorLabel.replace('|','_') + '_' + str(indicator.IndicatorParameterList[i]) + '.csv', index=False)

