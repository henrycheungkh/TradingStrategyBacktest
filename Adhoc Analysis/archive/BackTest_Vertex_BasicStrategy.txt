# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 19:27:01 2024

@author: Henry Cheung
"""


import pandas as pd
import numpy as np
import datetime

from AdhocBacktestKeyLevelLib import getKeyLevel, getPriceInSingleSeries, AssignKeyLevel

pd.set_option('display.max_columns', None)
pd.set_option('display.width',250)

# ticker = 'GC'
# StopLoss = 2

ticker = 'NQ'
StopLoss = 20

RewardRiskRatio = 1
TakeProfit = StopLoss * RewardRiskRatio

TradeEntryTimePeriodStart = (9*60 + 30)*6
TradeEntryTimePeriodEnd = (12*60)*6
TradeMaxDuration = 60*6

KeyLevelName = 'KL-VT-PD-LB5-MinMove120'

df_PriceDataRawFormat = pd.read_csv(r'G:\Temp\prices_' + ticker + '_10 secs_20230601_20240630_0700-1600.csv')

KeyLevelFilepath = r'G:\Temp\\' + ticker + '_KeyLevel_WithExpiryAdj_' + KeyLevelName + '_batch_full.csv'

df_KeyLevels = getKeyLevel(KeyLevelFilepath, KeyLevelName)
print(df_KeyLevels.head(20))

df_SingleSeries = getPriceInSingleSeries(df_PriceDataRawFormat)
print('len of df_SingleSeries before AssignKeyLevel is ' + str(len(df_SingleSeries)))

df_SingleSeries = AssignKeyLevel(df_SingleSeries, df_KeyLevels, KeyLevelName)
print('len of df_SingleSeries returned by AssignKeyLevel is ' + str(len(df_SingleSeries)))

df_SingleSeries['Position'] = 0
df_SingleSeries['InTradeEntryTimePeriod'] = False
df_SingleSeries['Entry Price'] = 0
df_SingleSeries['StopLoss Price'] = 0
df_SingleSeries['TakeProfit Price'] = 0
df_SingleSeries['Exit Price'] = 0
df_SingleSeries['Trade ID'] = 0

df_SingleSeries.loc[(df_SingleSeries['TimeInStandardUnit'] >= TradeEntryTimePeriodStart) & (df_SingleSeries['TimeInStandardUnit'] <= TradeEntryTimePeriodEnd), 'InTradeEntryTimePeriod'] = True

TradeID = 0

for price_step_index in range(len(df_SingleSeries)-2, -1, -1):
    if price_step_index % 10000 == 0:
        print('Running for price_step_index = ' + str(price_step_index) + ' at ' + str(datetime.datetime.now()))
    PriceNow = df_SingleSeries.iloc[price_step_index]['price']
    PositionBefore = df_SingleSeries.iloc[price_step_index+1]['Position']
    EntryPriceBefore = df_SingleSeries.iloc[price_step_index+1]['Entry Price']
    StopLossPriceBefore = df_SingleSeries.iloc[price_step_index+1]['StopLoss Price']
    TakeProfitPriceBefore = df_SingleSeries.iloc[price_step_index+1]['TakeProfit Price']
    KeyLevelDown = df_SingleSeries.iloc[price_step_index+1]['KeyLevelDown']
    KeyLevelUp = df_SingleSeries.iloc[price_step_index+1]['KeyLevelUp']
    if PositionBefore == 0:
        if df_SingleSeries.iloc[price_step_index]['InTradeEntryTimePeriod']:
            if PriceNow <= KeyLevelDown:
                print('Get into long position at price_step_index = ' + str(price_step_index))
                df_SingleSeries.at[price_step_index, 'Position'] = 1
                df_SingleSeries.at[price_step_index, 'Entry Price'] = KeyLevelDown
                df_SingleSeries.at[price_step_index, 'StopLoss Price'] = KeyLevelDown - StopLoss
                df_SingleSeries.at[price_step_index, 'TakeProfit Price'] = KeyLevelDown + TakeProfit
                # df_SingleSeries_WithPosition = df_SingleSeries[df_SingleSeries['Position'] != 0]
                # print(df_SingleSeries_WithPosition.head(100))
            if PriceNow >= KeyLevelUp:
                print('Get into short position at price_step_index = ' + str(price_step_index))
                df_SingleSeries.at[price_step_index, 'Position'] = -1
                df_SingleSeries.at[price_step_index, 'Entry Price'] = KeyLevelUp
                df_SingleSeries.at[price_step_index, 'StopLoss Price'] = KeyLevelUp + StopLoss
                df_SingleSeries.at[price_step_index, 'TakeProfit Price'] = KeyLevelUp - TakeProfit
                # df_SingleSeries_WithPosition = df_SingleSeries[df_SingleSeries['Position'] != 0]
                # print(df_SingleSeries_WithPosition.head(100))
    else:
        ExitTrade = False
        ExitPrice = 0
        if ((PositionBefore > 0) and (PriceNow <= StopLossPriceBefore)) or ((PositionBefore < 0) and (PriceNow >= StopLossPriceBefore)):
            ExitPrice = StopLossPriceBefore
            df_SingleSeries.at[price_step_index, 'PnL'] = PositionBefore * (ExitPrice - EntryPriceBefore)
            ExitTrade = True
        if ((PositionBefore > 0) and (PriceNow > TakeProfitPriceBefore)) or ((PositionBefore < 0) and (PriceNow < TakeProfitPriceBefore)):
            ExitPrice = TakeProfitPriceBefore
            df_SingleSeries.at[price_step_index, 'PnL'] = PositionBefore * (ExitPrice - EntryPriceBefore)
            ExitTrade = True

        if ExitTrade:
            TradeID = TradeID + 1
            df_SingleSeries.at[price_step_index, 'Exit Price'] = ExitPrice
            df_SingleSeries.at[price_step_index, 'Trade ID'] = TradeID
        else:
            df_SingleSeries.at[price_step_index, 'Position'] = PositionBefore
            df_SingleSeries.at[price_step_index, 'Entry Price'] = EntryPriceBefore
            df_SingleSeries.at[price_step_index, 'StopLoss Price'] = StopLossPriceBefore
            df_SingleSeries.at[price_step_index, 'TakeProfit Price'] = TakeProfitPriceBefore


df_SingleSeries['Abs Position'] = abs(df_SingleSeries['Position'])
df_SingleSeries['With Position Around'] = df_SingleSeries['Abs Position'].rolling(5, center=True).sum()

df_SingleSeries_WithPositionAround = df_SingleSeries[df_SingleSeries['With Position Around'] > 0]

print(df_SingleSeries_WithPositionAround)
print('Trade ID is ' + str(TradeID) + ', PnL Count is ' + str(df_SingleSeries['PnL'].count()) + ', mean PnL/Stop Loss is ' + str(df_SingleSeries['PnL'].mean()/StopLoss) + ', stdev PnL is ' + str(df_SingleSeries['PnL'].std()/StopLoss) + ', Sharpe Ratio is ' + str(df_SingleSeries['PnL'].mean()/df_SingleSeries['PnL'].std()))

# df_SingleSeries_WithPosition = df_SingleSeries[df_SingleSeries['Position'] != 0]

# print(df_SingleSeries_WithPosition.head(100))

# print(df_SingleSeries_WithPosition)

