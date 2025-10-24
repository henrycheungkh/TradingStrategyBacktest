# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 00:15:59 2024

@author: Henry Cheung
"""



import pandas as pd
import numpy as np
import datetime
import warnings

from KeyLevelGenerator import *
from LongShortIndicatorGenerator import *

            
class AdhocBacktestKeyLevelBaseClass:
    def __init__(self, PriceDataFilepath, Ticker, KeyLevelName = None, KeyLevel = None, ParameterList = {}, AdditionalKeyLevelColumns = [], CommissionPerTrade = 0, EconIndicatorFilepath = None, EconIndicatorParameters = {}, LongShortIndicatorFilepath = None, LongShortIndicatorParameters = {}, DebugExportFilepath = None, ResultSummaryExportFilepath = None, SimulationCounterForDebugExport = [0, 1], PriceDataTimeframe = '10 secs', GPUMode = False, KeepDataframeData = False, SkipToSimulationCounter = 0, NoOvernightTrade = True, TradeOnDayOfWeek = None, ResultOnDayOfWeek = ['Friday'], DebugShowBeforeAndAfterTimeStepCount = 3):
        self.Ticker = Ticker
        self.ParameterList = ParameterList
        self.Parameters = {}
        self.AdditionalKeyLevelColumns = AdditionalKeyLevelColumns
        self.KeyLevelName = KeyLevelName
        self.CommissionPerTrade = CommissionPerTrade
        self.DebugExportFilepath = DebugExportFilepath
        self.ResultSummaryExportFilepath = ResultSummaryExportFilepath
        self.PriceDataTimeframe = PriceDataTimeframe
        self.GPUMode = GPUMode
        self.KeepDataframeData = KeepDataframeData
        self.NoOvernightTrade = NoOvernightTrade
        self.TradeOnDayOfWeek = TradeOnDayOfWeek
        self.ResultOnDayOfWeek = ResultOnDayOfWeek
        self.DebugShowBeforeAndAfterTimeStepCount = DebugShowBeforeAndAfterTimeStepCount
        
        self.LoadEconIndicator(EconIndicatorParameters, EconIndicatorFilepath)
        
        self.LoadLongShortIndicator(LongShortIndicatorFilepath, LongShortIndicatorParameters)
        df_IndicatorValuesByDay = self.LongShortIndicator_generator.getIndicatorValuesByDay('MACD', {'Fast Length/Slow Length/Signal Smoothing' : [12,26,9], 'Source' : 'close', 'Oscillator MA Type' : 'EMA', 'Signal Line MA Type' : 'SMA', 'EMA Look back Multiple' : 1})
        df_IndicatorValuesByDay.to_csv(r'J:\temp\MACD_df_IndicatorValuesByDay.csv')

        self.df_PriceDataRawFormat = pd.read_csv(PriceDataFilepath)
        self.df_SingleSeries = self.getPriceInSingleSeries(self.df_PriceDataRawFormat)

        self.InitResultSummary()
        
        self.df_KeyLevels = self.getKeyLevel(KeyLevel, KeyLevelName)
        self.df_SingleSeries = self.AssignKeyLevel(self.df_SingleSeries, self.df_KeyLevels, self.KeyLevelName)
        
        self.TradeSimulationCounter = 0
        self.SkipToSimulationCounter = SkipToSimulationCounter
        self.SimulationCounterForDebugExport = SimulationCounterForDebugExport
        
        self.RunBacktest(self.ParameterList)
        
    def LoadLongShortIndicator(self, LongShortIndicatorFilepath, LongShortIndicatorParameters):
        self.LongShortIndicatorParameters = LongShortIndicatorParameters
        # if LongShortIndicatorFilepath is not None:
        print('LongShortIndicatorGenerator')
        self.LongShortIndicator_generator = LongShortIndicatorGenerator( LongShortIndicatorFilepath, Ticker = self.Ticker)
    
    def LoadEconIndicator(self, EconIndicatorParameters, EconIndicatorFilepath):
        self.EconIndicatorParameters = EconIndicatorParameters
        if EconIndicatorFilepath is not None:
            self.df_EconIndicator = self.ReadEconIndicator(EconIndicatorFilepath)
            self.df_EconIndicator = self.df_EconIndicator[self.df_EconIndicator['Event'].notnull()].copy()
            self.df_EconIndicator['Date'] = pd.to_datetime(self.df_EconIndicator['Date'])
            print(self.df_EconIndicator)
        
    def ReadEconIndicator(self, EconIndicatorFilepath):
        return pd.read_csv(EconIndicatorFilepath)
    
    def RunBacktestSingleIteration(self):
        self.InitParameterForSingleIteration()
        self.InitAdditionalData()
        self.RunTradeSimulation()
        self.SummariseResult()
        self.AddResultToSummary()   
        
    def PrintParameterForThisIteration(self):
        print('Running backtest for StopLoss = ' + str(self.StopLoss) + ', RewardRiskRatio = ' + str(self.RewardRiskRatio) + ', TradeEntryTimePeriodStart = ' + str(self.TradeEntryTimePeriodStart) + ', TradeEntryTimePeriodEnd = ' + str(self.TradeEntryTimePeriodEnd) + ', TradeMaxDuration = ' + str(self.TradeMaxDuration))
        
    def RunBacktest(self, ParameterList):
        if len(ParameterList) > 0:
            ParameterKeyToUse = list(ParameterList.keys())[0]
            
            ParameterListForNextLevel = ParameterList.copy()
            del ParameterListForNextLevel[ParameterKeyToUse]
    
            ParameterValues = ParameterList[ParameterKeyToUse]
            for ParameterValue in ParameterValues:
                self.InitSingleParameter(ParameterKeyToUse, ParameterValue)
                self.RunBacktest(ParameterListForNextLevel)
        else:
            print('self.TradeSimulationCounter is ' + str(self.TradeSimulationCounter) + ' and self.SkipToSimulationCounter is ' + str(self.SkipToSimulationCounter))
            if self.TradeSimulationCounter >= self.SkipToSimulationCounter:
                self.RunBacktestSingleIteration()
            self.TradeSimulationCounter = self.TradeSimulationCounter + 1
    
    def InitSingleParameter (self, ParameterKey, ParameterValue):
        self.Parameters[ParameterKey] = ParameterValue
   
    def InitResultSummary(self):
        Columns = ['Ticker', 'KeyLevelName'] + list(self.ParameterList.keys()) + ['Average PnL/Stop Loss','Sharpe Ratio']
        self.BacktestResultSummary = pd.DataFrame(columns=Columns)
        self.df_SingleSeries_WithPositionAround = None

    def getKeyLevelFromFile(self, KeyLevelFilepath):
        return pd.read_csv(KeyLevelFilepath)

    def getKeyLevel(self, KeyLevel, KeyLevelName):
        df_KeyLevels = None
        if KeyLevel is not None:
            if isinstance(KeyLevel, pd.DataFrame):
                df_KeyLevels = KeyLevel
            else:
                df_KeyLevels = self.getKeyLevelFromFile(KeyLevel)
        
            df_KeyLevels['Key Level Movement'] = df_KeyLevels[KeyLevelName].diff().shift(-1)
            if KeyLevelName + 'Layer' in df_KeyLevels.columns:
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
        
        warnings.simplefilter(action='ignore', category=FutureWarning)
    
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
        if df_KeyLevels is not None:
    
            df_SingleSeries_WithKL = df_SingleSeries.merge(df_KeyLevels[['Date',KeyLevelName] + self.AdditionalKeyLevelColumns], how='left', on=['Date'])
            
            df_SingleSeries_KLDown = df_SingleSeries_WithKL[df_SingleSeries_WithKL[KeyLevelName] < df_SingleSeries_WithKL['price']]
            df_SingleSeries_KLDown = pd.pivot_table(df_SingleSeries_KLDown, values=KeyLevelName, index=['tDateTime', 'price step key'], aggfunc="max").reset_index().rename(columns={KeyLevelName:'KeyLevelDown'}, inplace=False).sort_values(by=['tDateTime', 'price step key'], ascending=False)
            
            df_SingleSeries_KLUp = df_SingleSeries_WithKL[df_SingleSeries_WithKL[KeyLevelName] > df_SingleSeries_WithKL['price']]
            df_SingleSeries_KLUp = pd.pivot_table(df_SingleSeries_KLUp, values=KeyLevelName, index=['tDateTime', 'price step key'], aggfunc="min").reset_index().rename(columns={KeyLevelName:'KeyLevelUp'}, inplace=False).sort_values(by=['tDateTime', 'price step key'], ascending=False)
            
            df_SingleSeries = df_SingleSeries.merge(df_SingleSeries_KLDown, how='left', on=['tDateTime', 'price step key'])
            df_SingleSeries = df_SingleSeries.merge(df_SingleSeries_KLUp, how='left', on=['tDateTime', 'price step key'])
    
            df_SingleSeries = df_SingleSeries.merge(df_KeyLevels[['Date',KeyLevelName, 'KeyLevelBelow'] + self.AdditionalKeyLevelColumns], how='left', left_on=['Date', 'KeyLevelDown'], right_on=['Date', KeyLevelName]).rename(columns={'Key Level Movement':'KeyLevelDown Movement'}, inplace=False).drop([KeyLevelName], axis=1, inplace=False)
            df_SingleSeries = df_SingleSeries.merge(df_KeyLevels[['Date',KeyLevelName, 'KeyLevelAbove'] + self.AdditionalKeyLevelColumns], how='left', left_on=['Date', 'KeyLevelUp'], right_on=['Date', KeyLevelName]).rename(columns={'Key Level Movement':'KeyLevelUp Movement'}, inplace=False).drop([KeyLevelName], axis=1, inplace=False)
        
        return df_SingleSeries
    
    def InitStrategyAdditionalData(self):
        self.df_SingleSeries['StopLoss Price'] = np.nan
        self.df_SingleSeries['TakeProfit Price'] = np.nan
    
    def InitAdditionalData(self):
        self.df_SingleSeries['Position'] = 0
        self.df_SingleSeries['InTradeEntryTimePeriod'] = False

        self.df_SingleSeries['Entry Price'] = np.nan
        self.InitStrategyAdditionalData()
        self.df_SingleSeries['Exit Price'] = np.nan
        self.df_SingleSeries['Trade ID'] = 0
        self.df_SingleSeries['PnL'] = np.nan
        self.df_SingleSeries['Date'] = pd.to_datetime(self.df_SingleSeries['Date'])
        self.df_SingleSeries['day_of_week'] = self.df_SingleSeries['Date'].dt.day_name()

        
        self.df_SingleSeries.loc[(self.df_SingleSeries['TimeInStandardUnit'] >= self.TradeEntryTimePeriodStart) & (self.df_SingleSeries['TimeInStandardUnit'] <= self.TradeEntryTimePeriodEnd), 'InTradeEntryTimePeriod'] = True
        
        if self.TradeOnDayOfWeek is not None:
            for day_of_week in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                if day_of_week not in self.TradeOnDayOfWeek:
                    self.df_SingleSeries.loc[self.df_SingleSeries['day_of_week'] == day_of_week, 'InTradeEntryTimePeriod'] = False
        
        if ('EconIndicatorToTrade' in self.EconIndicatorParameters):
            EconIndicatorToTrade = '|'.join([str(ele) for ele in self.EconIndicatorParameters['EconIndicatorToTrade']])
            df_DatesWithEconIndicator = self.df_EconIndicator[self.df_EconIndicator['Event'].str.contains(EconIndicatorToTrade)][['Date']].drop_duplicates()
            df_DatesWithEconIndicator['Dummy'] = 1
            self.df_SingleSeries = self.df_SingleSeries.merge(df_DatesWithEconIndicator, how='left', on='Date')
            self.df_SingleSeries.loc[self.df_SingleSeries['Dummy'].isnull(), 'InTradeEntryTimePeriod'] = False
            self.df_SingleSeries.drop(['Dummy'], axis=1, inplace=True)
            self.Parameters['EconIndicatorToTrade'] = EconIndicatorToTrade
        elif ('EconIndicatorToAvoid' in self.EconIndicatorParameters):
            EconIndicatorToAvoid = '|'.join([str(ele) for ele in self.EconIndicatorParameters['EconIndicatorToAvoid']])
            df_DatesWithEconIndicator = self.df_EconIndicator[self.df_EconIndicator['Event'].str.contains(EconIndicatorToAvoid)][['Date']].drop_duplicates()
            df_DatesWithEconIndicator['Dummy'] = 1
            self.df_SingleSeries = self.df_SingleSeries.merge(df_DatesWithEconIndicator, how='left', on='Date')
            self.df_SingleSeries.loc[self.df_SingleSeries['Dummy'].notnull(), 'InTradeEntryTimePeriod'] = False
            self.df_SingleSeries.drop(['Dummy'], axis=1, inplace=True)
            self.Parameters['EconIndicatorToAvoid'] = EconIndicatorToAvoid
        
    def InitParameterForSingleIteration(self):
        self.StopLoss = self.Parameters['StopLoss']
        self.TakeProfit = self.Parameters['StopLoss'] * self.Parameters['RewardRiskRatio']
        self.MaxLossTradeCountPerDay = self.Parameters['MaxLossTradeCountPerDay']
        self.MaxWinTradeCountPerDay = self.Parameters['MaxWinTradeCountPerDay']
        self.TradeEntryTimePeriodStart = self.Parameters['TradeEntryTimePeriod'][0]
        self.TradeEntryTimePeriodEnd = self.Parameters['TradeEntryTimePeriod'][1]
        self.TradeMaxDuration = self.Parameters['TradeMaxDuration']
        if 'PositionMultiplier' in self.Parameters:
            self.PositionMultiplier = self.Parameters['PositionMultiplier']
        else:
            self.PositionMultiplier = 1
    
    def EnterTrade(self, price_step_index, Position, EntryPrice):
        self.TradeDuration = 0
        self.TradeID = self.TradeID + 1
        self.df_SingleSeries.at[price_step_index, 'Trade ID'] = self.TradeID
        self.df_SingleSeries.at[price_step_index, 'Position'] = Position * self.PositionMultiplier
        self.df_SingleSeries.at[price_step_index, 'Entry Price'] = EntryPrice
        self.df_SingleSeries.at[price_step_index, 'StopLoss Price'] = EntryPrice - (np.sign(Position * self.PositionMultiplier) * self.StopLoss)
        self.df_SingleSeries.at[price_step_index, 'TakeProfit Price'] = EntryPrice + (np.sign(Position * self.PositionMultiplier) * self.TakeProfit)
        
    def CheckForTradeExit(self, price_step_index, ClosestStopLoss, ClosestTakeProfit):
        ExitTrade = False
        ExitPrice = np.nan
        PriceNow = self.df_SingleSeries.iloc[price_step_index]['price']
        PositionBefore = self.df_SingleSeries.iloc[price_step_index+1]['Position']
        
        if ((PositionBefore > 0) and (PriceNow <= ClosestStopLoss)) or ((PositionBefore < 0) and (PriceNow >= ClosestStopLoss)):
            ExitPrice = ClosestStopLoss
            ExitTrade = True
        elif ((PositionBefore > 0) and (PriceNow > ClosestTakeProfit)) or ((PositionBefore < 0) and (PriceNow < ClosestTakeProfit)):
            ExitPrice = ClosestTakeProfit
            ExitTrade = True
        return (ExitTrade, ExitPrice)

    def CheckForTradeExitByStrategy(self, price_step_index):
        StopLossPriceBefore = self.df_SingleSeries.iloc[price_step_index+1]['StopLoss Price']
        TakeProfitPriceBefore = self.df_SingleSeries.iloc[price_step_index+1]['TakeProfit Price']
        return self.CheckForTradeExit(price_step_index, StopLossPriceBefore, TakeProfitPriceBefore)
    
    def CheckForTradeEntryByStrategy(self, price_step_index):
        pass
    
    def TradeContinueCarryForward(self, price_step_index):
        self.df_SingleSeries.at[price_step_index, 'Position'] = self.df_SingleSeries.iloc[price_step_index+1]['Position']
        self.df_SingleSeries.at[price_step_index, 'Entry Price'] = self.df_SingleSeries.iloc[price_step_index+1]['Entry Price']
        self.df_SingleSeries.at[price_step_index, 'StopLoss Price'] = self.df_SingleSeries.iloc[price_step_index+1]['StopLoss Price']
        self.df_SingleSeries.at[price_step_index, 'TakeProfit Price'] = self.df_SingleSeries.iloc[price_step_index+1]['TakeProfit Price']         
        
    def InitialisationBeforeRunningTradeSimulation(self):
        pass
    
    def RolloverWhenNoPosition(self,price_step_index):
        pass
        
    def RunTradeSimulation(self):
        self.TradeID = 0
        LossTradeCountPerDay = 0
        WinTradeCountPerDay = 0
        self.InitialisationBeforeRunningTradeSimulation()
        
        for price_step_index in range(len(self.df_SingleSeries)-2, -1, -1):
            if price_step_index % 100000 == 0:
                print('Running for price_step_index = ' + str(price_step_index) + ', Trade Count = ' + str(self.TradeID) + ' at ' + str(datetime.datetime.now()))
                
            if (self.df_SingleSeries.iloc[price_step_index]['Date'] != self.df_SingleSeries.iloc[price_step_index-1]['Date']):
                LossTradeCountPerDay = 0
                WinTradeCountPerDay = 0
                
            PriceNow = self.df_SingleSeries.iloc[price_step_index]['price']
            PositionBefore = self.df_SingleSeries.iloc[price_step_index+1]['Position']
            EntryPriceBefore = self.df_SingleSeries.iloc[price_step_index+1]['Entry Price']
            
            if PositionBefore == 0:
                # No Position, try Getting into Trade
                if (self.df_SingleSeries.iloc[price_step_index]['InTradeEntryTimePeriod']) and (LossTradeCountPerDay < self.MaxLossTradeCountPerDay) and (WinTradeCountPerDay < self.MaxWinTradeCountPerDay):
                    self.CheckForTradeEntryByStrategy(price_step_index)
                if self.df_SingleSeries.iloc[price_step_index]['Position'] == 0:
                    self.RolloverWhenNoPosition(price_step_index)
            else:
                # Have Position, see if the trade should be exited
                self.df_SingleSeries.at[price_step_index, 'Trade ID'] = self.TradeID
                ExitTrade = False
                ExitPrice = np.nan
                self.TradeDuration = self.TradeDuration + 1
                (ExitTrade, ExitPrice) = self.CheckForTradeExitByStrategy(price_step_index)
                if not ExitTrade:
                    if (self.TradeDuration/3 > self.TradeMaxDuration) or (price_step_index <= 0):
                        ExitPrice = PriceNow
                        ExitTrade = True
                    elif self.NoOvernightTrade and (self.df_SingleSeries.iloc[price_step_index]['Date'] != self.df_SingleSeries.iloc[price_step_index-1]['Date']):
                        ExitPrice = PriceNow
                        ExitTrade = True
        
                if ExitTrade:
                    self.df_SingleSeries.at[price_step_index, 'PnL'] = PositionBefore * (ExitPrice - EntryPriceBefore)
                    if (PositionBefore * (ExitPrice - EntryPriceBefore) > 0):
                        WinTradeCountPerDay = WinTradeCountPerDay + 1
                    else:
                        LossTradeCountPerDay = LossTradeCountPerDay + 1
                    self.df_SingleSeries.at[price_step_index, 'Exit Price'] = ExitPrice
                else:
                    self.TradeContinueCarryForward(price_step_index)  

    def SummariseResult(self):
        self.df_SingleSeries['Abs Position'] = abs(self.df_SingleSeries['Position'])
        self.df_SingleSeries['With Position Around'] = self.df_SingleSeries['Abs Position'].rolling(self.DebugShowBeforeAndAfterTimeStepCount * 2 + 1, center=True).sum()
        if self.CommissionPerTrade != 0:
            self.df_SingleSeries['PnL After Commission'] = self.df_SingleSeries['PnL'] - (2 * self.CommissionPerTrade)
            
        if self.df_SingleSeries['PnL'].std() == 0:
            print('Trade ID is ' + str(self.TradeID) + ', PnL Count is ' + str(self.df_SingleSeries['PnL'].count()) + ', mean PnL/Stop Loss is ' + str(self.df_SingleSeries['PnL'].mean()/self.StopLoss) + ', stdev PnL/Stoploss is ' + str(self.df_SingleSeries['PnL'].std()/self.StopLoss) + ', Sharpe Ratio is NAN')
        else:
            print('Trade ID is ' + str(self.TradeID) + ', PnL Count is ' + str(self.df_SingleSeries['PnL'].count()) + ', mean PnL/Stop Loss is ' + str(self.df_SingleSeries['PnL'].mean()/self.StopLoss) + ', stdev PnL/Stoploss is ' + str(self.df_SingleSeries['PnL'].std()/self.StopLoss) + ', Sharpe Ratio is ' + str(self.df_SingleSeries['PnL'].mean()/self.df_SingleSeries['PnL'].std()))
        
        if self.TradeSimulationCounter in self.SimulationCounterForDebugExport:
            df_SingleSeries_WithPositionAround = self.df_SingleSeries[self.df_SingleSeries['With Position Around'] > 0]
            df_SingleSeries_WithPositionAround['TradeSimulationCounter'] = self.TradeSimulationCounter
            df_SingleSeries_WithPositionAround['Ticker'] = self.Ticker
            df_SingleSeries_WithPositionAround['Parameters'] = str(self.Parameters)
            if self.EconIndicatorParameters is not None:
                if len(self.EconIndicatorParameters) > 0:
                    df_SingleSeries_WithPositionAround['EconIndicatorParameters'] = str(self.EconIndicatorParameters)
            if self.df_SingleSeries_WithPositionAround is None:
                self.df_SingleSeries_WithPositionAround = df_SingleSeries_WithPositionAround
            else:
                self.df_SingleSeries_WithPositionAround = pd.concat([self.df_SingleSeries_WithPositionAround, df_SingleSeries_WithPositionAround])
            
            # print(self.df_SingleSeries_WithPositionAround)
            if self.DebugExportFilepath is not None:
                self.df_SingleSeries_WithPositionAround.to_csv(self.DebugExportFilepath)

    def AddResultToSummary(self):
        data_dict = {'TradeSimulationCounter':self.TradeSimulationCounter, 'Ticker':self.Ticker, 'KeyLevelName':self.KeyLevelName, 'Trade Count':self.TradeID}

        for key in self.Parameters:
            data_dict[key] = str(self.Parameters[key])

        # data_dict.update({'Average PnL/Stop Loss' : self.df_SingleSeries['PnL'].mean()/self.StopLoss ,'stdev PnL/Stoploss' : self.df_SingleSeries['PnL'].std()/self.StopLoss,'Sharpe Ratio' : self.df_SingleSeries['PnL'].mean()/self.df_SingleSeries['PnL'].std()})
        if self.df_SingleSeries['PnL'].std() == 0:
            data_dict.update({'Average PnL/Stop Loss' : self.df_SingleSeries['PnL'].mean()/self.StopLoss ,'Sharpe Ratio' : np.nan})
        else:
            data_dict.update({'Average PnL/Stop Loss' : self.df_SingleSeries['PnL'].mean()/self.StopLoss ,'Sharpe Ratio' : self.df_SingleSeries['PnL'].mean()/self.df_SingleSeries['PnL'].std()})
        
        if self.CommissionPerTrade != 0:
            data_dict.update({'Average PnL/Stop Loss After Commission' : self.df_SingleSeries['PnL After Commission'].mean()/self.StopLoss ,'Sharpe Ratio After Commission' : self.df_SingleSeries['PnL After Commission'].mean()/self.df_SingleSeries['PnL After Commission'].std()})
        
        if self.ResultOnDayOfWeek is not None:
            for DayOfWeek in self.ResultOnDayOfWeek:
                df_SingleSeries_OnDayOfWeek = self.df_SingleSeries[(self.df_SingleSeries['day_of_week'] == DayOfWeek) & self.df_SingleSeries['PnL'].notnull()].copy()
                if df_SingleSeries_OnDayOfWeek['PnL'].std() == 0:
                    data_dict.update({'Trade Count - ' + DayOfWeek : df_SingleSeries_OnDayOfWeek['PnL'].count(), 'Average PnL/Stop Loss - ' + DayOfWeek : df_SingleSeries_OnDayOfWeek['PnL'].mean()/self.StopLoss, 'Sharpe Ratio - ' + DayOfWeek : np.nan})
                else:
                    data_dict.update({'Trade Count - ' + DayOfWeek : df_SingleSeries_OnDayOfWeek['PnL'].count(), 'Average PnL/Stop Loss - ' + DayOfWeek : df_SingleSeries_OnDayOfWeek['PnL'].mean()/self.StopLoss, 'Sharpe Ratio - ' + DayOfWeek : df_SingleSeries_OnDayOfWeek['PnL'].mean()/df_SingleSeries_OnDayOfWeek['PnL'].std()})
            
        df = pd.DataFrame(data_dict, index=[0])
        self.BacktestResultSummary = pd.concat([self.BacktestResultSummary, df])
        if self.ResultSummaryExportFilepath is not None:
            self.BacktestResultSummary.to_csv(self.ResultSummaryExportFilepath, index=False )
        
