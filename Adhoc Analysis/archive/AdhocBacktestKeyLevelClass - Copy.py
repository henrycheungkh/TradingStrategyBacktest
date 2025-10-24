# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 00:15:59 2024

@author: Henry Cheung
"""



import pandas as pd
import numpy as np
import datetime
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width',300)

class AdhocBacktestKeyLevel:
    def __init__(self, RawDataFilepath, KeyLevelName, KeyLevelFilepath, Ticker, Parameters = {}, CommissionPerTrade = 0, DebugExportFilepath = None, RawDataTimeframe = '10 secs', GPUMode = False, KeepDataframeData = False):
        self.Ticker = Ticker
        self.Parameters = Parameters
        self.KeyLevelName = KeyLevelName
        self.CommissionPerTrade = CommissionPerTrade
        self.DebugExportFilepath = DebugExportFilepath
        self.RawDataTimeframe = RawDataTimeframe
        self.GPUMode = GPUMode
        self.KeepDataframeData = KeepDataframeData
        self.df_PriceDataRawFormat = pd.read_csv(RawDataFilepath)
        self.df_SingleSeries = self.getPriceInSingleSeries(self.df_PriceDataRawFormat)

        self.InitParameter()

        self.df_KeyLevels = self.getKeyLevel(KeyLevelFilepath, KeyLevelName)
        self.df_SingleSeries = self.AssignKeyLevel(self.df_SingleSeries, self.df_KeyLevels, self.KeyLevelName)

        self.InitAdditionalData()
        self.RunTradeSimulation()
        self.SummariseResult()
        self.AddResultToSummary()
    
    def InitParameter(self):
        self.StopLoss = self.Parameters['StopLoss']
        self.TakeProfit = self.Parameters['StopLoss'] * self.Parameters['RewardRiskRatio'] 
        self.TradeEntryTimePeriodStart = self.Parameters['TradeEntryTimePeriodStart'] 
        self.TradeEntryTimePeriodEnd = self.Parameters['TradeEntryTimePeriodEnd'] 
        Columns = ['Ticker', 'KeyLevelName'] + list(self.Parameters.keys()) + ['Average PnL/Stop Loss','stdev PnL/Stoploss','Sharpe Ratio']
        self.BacktestResultSummary = pd.DataFrame(columns=Columns)

    def getKeyLevel(self, KeyLevelFilepath, KeyLevelName):
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

    def getPriceInSingleSeries(self,df):
    
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

    def AssignKeyLevel(self, df_SingleSeries, df_KeyLevels, KeyLevelName):
    
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
    
    def InitAdditionalData(self):
        self.df_SingleSeries['Position'] = 0
        self.df_SingleSeries['InTradeEntryTimePeriod'] = False
        self.df_SingleSeries['Entry Price'] = 0
        self.df_SingleSeries['StopLoss Price'] = 0
        self.df_SingleSeries['TakeProfit Price'] = 0
        self.df_SingleSeries['Exit Price'] = 0
        self.df_SingleSeries['Trade ID'] = 0
        self.df_SingleSeries['PnL'] = np.nan
        
        self.df_SingleSeries.loc[(self.df_SingleSeries['TimeInStandardUnit'] >= self.TradeEntryTimePeriodStart) & (self.df_SingleSeries['TimeInStandardUnit'] <= self.TradeEntryTimePeriodEnd), 'InTradeEntryTimePeriod'] = True
        
    def RunTradeSimulation(self):
        self.TradeID = 0
        for price_step_index in range(len(self.df_SingleSeries)-2, -1, -1):
            if price_step_index % 10000 == 0:
                print('Running for price_step_index = ' + str(price_step_index) + ' at ' + str(datetime.datetime.now()))
            PriceNow = self.df_SingleSeries.iloc[price_step_index]['price']
            PositionBefore = self.df_SingleSeries.iloc[price_step_index+1]['Position']
            EntryPriceBefore = self.df_SingleSeries.iloc[price_step_index+1]['Entry Price']
            StopLossPriceBefore = self.df_SingleSeries.iloc[price_step_index+1]['StopLoss Price']
            TakeProfitPriceBefore = self.df_SingleSeries.iloc[price_step_index+1]['TakeProfit Price']
            KeyLevelDown = self.df_SingleSeries.iloc[price_step_index+1]['KeyLevelDown']
            KeyLevelUp = self.df_SingleSeries.iloc[price_step_index+1]['KeyLevelUp']
            if PositionBefore == 0:
                if self.df_SingleSeries.iloc[price_step_index]['InTradeEntryTimePeriod']:
                    if PriceNow <= KeyLevelDown:
                        # print('Get into long position at price_step_index = ' + str(price_step_index))
                        self.df_SingleSeries.at[price_step_index, 'Position'] = 1
                        self.df_SingleSeries.at[price_step_index, 'Entry Price'] = KeyLevelDown
                        self.df_SingleSeries.at[price_step_index, 'StopLoss Price'] = KeyLevelDown - self.StopLoss
                        self.df_SingleSeries.at[price_step_index, 'TakeProfit Price'] = KeyLevelDown + self.TakeProfit
                        # self.df_SingleSeries_WithPosition = self.df_SingleSeries[self.df_SingleSeries['Position'] != 0]
                        # print(self.df_SingleSeries_WithPosition.head(100))
                    if PriceNow >= KeyLevelUp:
                        # print('Get into short position at price_step_index = ' + str(price_step_index))
                        self.df_SingleSeries.at[price_step_index, 'Position'] = -1
                        self.df_SingleSeries.at[price_step_index, 'Entry Price'] = KeyLevelUp
                        self.df_SingleSeries.at[price_step_index, 'StopLoss Price'] = KeyLevelUp + self.StopLoss
                        self.df_SingleSeries.at[price_step_index, 'TakeProfit Price'] = KeyLevelUp - self.TakeProfit
                        # self.df_SingleSeries_WithPosition = self.df_SingleSeries[self.df_SingleSeries['Position'] != 0]
                        # print(self.df_SingleSeries_WithPosition.head(100))
            else:
                ExitTrade = False
                ExitPrice = 0
                if ((PositionBefore > 0) and (PriceNow <= StopLossPriceBefore)) or ((PositionBefore < 0) and (PriceNow >= StopLossPriceBefore)):
                    ExitPrice = StopLossPriceBefore
                    self.df_SingleSeries.at[price_step_index, 'PnL'] = PositionBefore * (ExitPrice - EntryPriceBefore)
                    ExitTrade = True
                if ((PositionBefore > 0) and (PriceNow > TakeProfitPriceBefore)) or ((PositionBefore < 0) and (PriceNow < TakeProfitPriceBefore)):
                    ExitPrice = TakeProfitPriceBefore
                    self.df_SingleSeries.at[price_step_index, 'PnL'] = PositionBefore * (ExitPrice - EntryPriceBefore)
                    ExitTrade = True
        
                if ExitTrade:
                    self.TradeID = self.TradeID + 1
                    self.df_SingleSeries.at[price_step_index, 'Exit Price'] = ExitPrice
                    self.df_SingleSeries.at[price_step_index, 'Trade ID'] = self.TradeID
                else:
                    self.df_SingleSeries.at[price_step_index, 'Position'] = PositionBefore
                    self.df_SingleSeries.at[price_step_index, 'Entry Price'] = EntryPriceBefore
                    self.df_SingleSeries.at[price_step_index, 'StopLoss Price'] = StopLossPriceBefore
                    self.df_SingleSeries.at[price_step_index, 'TakeProfit Price'] = TakeProfitPriceBefore        

    def SummariseResult(self):
        self.df_SingleSeries['Abs Position'] = abs(self.df_SingleSeries['Position'])
        self.df_SingleSeries['With Position Around'] = self.df_SingleSeries['Abs Position'].rolling(5, center=True).sum()
        
        self.df_SingleSeries_WithPositionAround = self.df_SingleSeries[self.df_SingleSeries['With Position Around'] > 0]
        
        print(self.df_SingleSeries_WithPositionAround)
        print('Trade ID is ' + str(self.TradeID) + ', PnL Count is ' + str(self.df_SingleSeries['PnL'].count()) + ', mean PnL/Stop Loss is ' + str(self.df_SingleSeries['PnL'].mean()/self.StopLoss) + ', stdev PnL/Stoploss is ' + str(self.df_SingleSeries['PnL'].std()/self.StopLoss) + ', Sharpe Ratio is ' + str(self.df_SingleSeries['PnL'].mean()/self.df_SingleSeries['PnL'].std()))
        if self.DebugExportFilepath is not None:
            self.df_SingleSeries_WithPositionAround.to_csv(self.DebugExportFilepath)

    def AddResultToSummary(self):
        data_dict = {'Ticker':self.Ticker, 'KeyLevelName':self.KeyLevelName}
        data_dict.update(self.Parameters)
        data_dict.update({'Average PnL/Stop Loss' : self.df_SingleSeries['PnL'].mean()/self.StopLoss ,'stdev PnL/Stoploss' : self.df_SingleSeries['PnL'].std()/self.StopLoss,'Sharpe Ratio' : self.df_SingleSeries['PnL'].mean()/self.df_SingleSeries['PnL'].std()})
        df = pd.DataFrame(data_dict, index=[0])
        self.BacktestResultSummary = pd.concat([self.BacktestResultSummary, df])
        