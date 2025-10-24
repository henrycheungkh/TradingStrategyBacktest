# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 19:27:01 2024

@author: Henry Cheung
"""


import pandas as pd
import numpy as np
import datetime
pd.set_option('display.max_columns', None)
pd.set_option('display.width',300)

ticker = 'GC'
StopLoss = 2
RewardRiskRatio = 1
TakeProfit = StopLoss * RewardRiskRatio


df_PriceDataRawFormat = pd.read_csv(r'G:\Temp\prices_' + ticker + '_10 secs_20230601_20240630_0700-1600.csv')

KeyLevelFilepath = r'G:\Temp\\' + ticker + '_KeyLevel_WithExpiryAdj_KL-VT-PD-LB5-MinMove12_batch20.csv'
KeyLevelName = 'KL-VT-PD-LB5-MinMove12'



def getKeyLevel(KeyLevelFilepath, KeyLevelName):
    df_KeyLevels = pd.read_csv(KeyLevelFilepath)
    
    
    df_KeyLevels['Key Level Movement'] = df_KeyLevels[KeyLevelName].diff().shift(-1)
    df_KeyLevels = df_KeyLevels[df_KeyLevels[KeyLevelName + 'Layer'] != 0].reset_index()
    
    df_KeyLevels = df_KeyLevels.sort_values(by=['Date', KeyLevelName], ascending=True, inplace=False).reset_index()
    df_KeyLevels['KeyLevelBelow'] = df_KeyLevels[KeyLevelName].shift(1)
    df_KeyLevels['KeyLevelAbove'] = df_KeyLevels[KeyLevelName].shift(-1)
    df_KeyLevels['KeyLevelBelowDate'] = df_KeyLevels['Date'].shift(1)
    df_KeyLevels['KeyLevelAboveDate'] = df_KeyLevels['Date'].shift(-1)
    df_KeyLevels.loc[df_KeyLevels['Date'] != df_KeyLevels['KeyLevelBelowDate'], 'KeyLevelBelow'] = np.nan
    df_KeyLevels.loc[df_KeyLevels['Date'] != df_KeyLevels['KeyLevelAboveDate'], 'KeyLevelAbove'] = np.nan
    
    return df_KeyLevels

def getPriceInSingleSeries(df):

    df['price step 1'] = df['close']
    df['price step 2'] = df['close']
    df.loc[df['close'] > df['open'], 'price step 1'] = df['low']
    df.loc[df['close'] > df['open'], 'price step 2'] = df['high']
    df.loc[df['close'] <= df['open'], 'price step 1'] = df['high']
    df.loc[df['close'] <= df['open'], 'price step 2'] = df['low']
    
    ColumnsToKeep = ['expiry', 'tDateTime', 'TimeInStandardUnit', 'date id', 'MarketTimeSectionID', 'vol', 'Date']
    
    df_1 = df[ColumnsToKeep + ['price step 1']]
    df_1['vol'] = 0
    df_1['price'] = df_1['price step 1']
    df_1['price step key'] = 1
    
    df_2 = df[ColumnsToKeep + ['price step 2']]
    df_2['vol'] = 0
    df_2['price'] = df_2['price step 2']
    df_2['price step key'] = 2
    
    df_3 = df[ColumnsToKeep + ['close']]
    df_3['price'] = df_3['close']
    df_3['price step key'] = 3
    
    df_SingleSeries = pd.concat([df_1, df_2, df_3])
    
    df_SingleSeries.sort_values(by=['tDateTime', 'price step key'], ascending=False, inplace=True)
    
    df_SingleSeries = df_SingleSeries[ColumnsToKeep + ['price', 'price step key']].copy().reset_index()
    
    return df_SingleSeries

def AssignKeyLevel(df_SingleSeries, df_KeyLevels, KeyLevelName):

    df_SingleSeries_WithKL = df_SingleSeries.merge(df_KeyLevels[['Date',KeyLevelName, 'Key Level Movement']], how='left', on=['Date'])
    
    df_SingleSeries_KLDown = df_SingleSeries_WithKL[df_SingleSeries_WithKL[KeyLevelName] < df_SingleSeries_WithKL['price']]
    df_SingleSeries_KLDown = pd.pivot_table(df_SingleSeries_KLDown, values=KeyLevelName, index=['tDateTime', 'price step key'], aggfunc="max").reset_index().rename(columns={KeyLevelName:'KeyLevelDown'}, inplace=False).sort_values(by=['tDateTime', 'price step key'], ascending=False)
    
    df_SingleSeries_KLUp = df_SingleSeries_WithKL[df_SingleSeries_WithKL[KeyLevelName] > df_SingleSeries_WithKL['price']]
    df_SingleSeries_KLUp = pd.pivot_table(df_SingleSeries_KLUp, values=KeyLevelName, index=['tDateTime', 'price step key'], aggfunc="min").reset_index().rename(columns={KeyLevelName:'KeyLevelUp'}, inplace=False).sort_values(by=['tDateTime', 'price step key'], ascending=False)
    
    df_SingleSeries = df_SingleSeries.merge(df_SingleSeries_KLDown, how='left', on=['tDateTime', 'price step key'])
    df_SingleSeries = df_SingleSeries.merge(df_SingleSeries_KLUp, how='left', on=['tDateTime', 'price step key'])
    df_SingleSeries = df_SingleSeries.merge(df_KeyLevels[['Date',KeyLevelName, 'Key Level Movement', 'KeyLevelBelow']], how='left', left_on=['Date', 'KeyLevelDown'], right_on=['Date', KeyLevelName]).rename(columns={'Key Level Movement':'KeyLevelDown Movement'}, inplace=False).drop([KeyLevelName], axis=1, inplace=False)
    df_SingleSeries = df_SingleSeries.merge(df_KeyLevels[['Date',KeyLevelName, 'Key Level Movement', 'KeyLevelAbove']], how='left', left_on=['Date', 'KeyLevelUp'], right_on=['Date', KeyLevelName]).rename(columns={'Key Level Movement':'KeyLevelUp Movement'}, inplace=False).drop([KeyLevelName], axis=1, inplace=False)
    
    return df_SingleSeries


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
df_SingleSeries['PnL'] = 0

df_SingleSeries.loc[(df_SingleSeries['TimeInStandardUnit'] >= TradeEntryTimePeriodStart) & (df_SingleSeries['TimeInStandardUnit'] <= TradeEntryTimePeriodEnd), 'InTradeEntryTimePeriod'] = True

for price_step_index in range(len(df_SingleSeries)-2, -1, -1):
    PriceNow = df_SingleSeries.iloc[price_step_index]['price']
    PositionBefore = df_SingleSeries.iloc[price_step_index+1]['Position']
    StopLossPriceBefore = df_SingleSeries.iloc[price_step_index+1]['StopLoss Price']
    TakeProfitPriceBefore = df_SingleSeries.iloc[price_step_index+1]['TakeProfit Price']
    KeyLevelDown = df_SingleSeries.iloc[price_step_index+1]['KeyLevelDown']
    KeyLevelUp = df_SingleSeries.iloc[price_step_index+1]['KeyLevelUp']
    if PositionBefore == 0:
        if df_SingleSeries.iloc[price_step_index]['InTradeEntryTimePeriod']:
            if PriceNow <= KeyLevelDown:
                df_SingleSeries.iloc[price_step_index]['Position'] = 1
                df_SingleSeries.iloc[price_step_index]['Entry Price'] = KeyLevelDown
                df_SingleSeries.iloc[price_step_index]['StopLoss Price'] = KeyLevelDown - StopLoss
                df_SingleSeries.iloc[price_step_index]['TakeProfit Price'] = KeyLevelDown + TakeProfit
            if PriceNow >= KeyLevelUp:
                df_SingleSeries.iloc[price_step_index]['Position'] = -1
                df_SingleSeries.iloc[price_step_index]['Entry Price'] = KeyLevelUp
                df_SingleSeries.iloc[price_step_index]['StopLoss Price'] = KeyLevelUp + StopLoss
                df_SingleSeries.iloc[price_step_index]['TakeProfit Price'] = KeyLevelUp - TakeProfit
    else:
        ExitTrade = False
        if ((PositionBefore > 0) and (PriceNow <= StopLossPriceBefore)) or ((PositionBefore < 0) and (PriceNow >= StopLossPriceBefore)):
            df_SingleSeries.iloc[price_step_index]['PnL'] = df_SingleSeries.iloc[price_step_index]['Position'] * (StopLossPriceBefore - df_SingleSeries.iloc[price_step_index]['Entry Price'])
            ExitTrade = True
        if ((PositionBefore > 0) and (PriceNow > TakeProfitPriceBefore)) or ((PositionBefore < 0) and (PriceNow < TakeProfitPriceBefore)):
            df_SingleSeries.iloc[price_step_index]['PnL'] = df_SingleSeries.iloc[price_step_index]['Position'] * (TakeProfitPriceBefore - df_SingleSeries.iloc[price_step_index]['Entry Price'])
            ExitTrade = True

        if ExitTrade:
            df_SingleSeries.iloc[price_step_index]['Position'] = 0
            df_SingleSeries.iloc[price_step_index]['Entry Price'] = 0
            df_SingleSeries.iloc[price_step_index]['StopLoss Price'] = 0
            df_SingleSeries.iloc[price_step_index]['TakeProfit Price'] = 0



print(df_SingleSeries.head(100))

print(df_SingleSeries)

