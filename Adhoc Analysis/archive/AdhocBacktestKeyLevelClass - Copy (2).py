# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 00:15:59 2024

@author: Henry Cheung
"""



import pandas as pd
import numpy as np
import datetime
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

class AdhocBacktestKeyLevel:
    def __init__(self, PriceDataFilepath, KeyLevelName, KeyLevelFilepath, Ticker, ParameterList = {}, CommissionPerTrade = 0, EconIndicatorFilepath = None, EconIndicatorParameters = {}, DebugExportFilepath = None, SimulationCounterForDebugExport = [0, 1], PriceDataTimeframe = '10 secs', GPUMode = False, KeepDataframeData = False, SkipToSimulationCounter = 0, NoOvernightTrade = True, TradeOnDayOfWeek = None, ResultOnDayOfWeek = ['Friday']):
        self.Ticker = Ticker
        self.ParameterList = ParameterList
        self.Parameters = {}
        self.KeyLevelName = KeyLevelName
        self.CommissionPerTrade = CommissionPerTrade
        self.DebugExportFilepath = DebugExportFilepath
        self.PriceDataTimeframe = PriceDataTimeframe
        self.GPUMode = GPUMode
        self.KeepDataframeData = KeepDataframeData
        self.NoOvernightTrade = NoOvernightTrade
        self.TradeOnDayOfWeek = TradeOnDayOfWeek
        self.ResultOnDayOfWeek = ResultOnDayOfWeek
        self.EconIndicatorParameters = EconIndicatorParameters
        if EconIndicatorFilepath is not None:
            self.df_EconIndicator = self.ReadEconIndicator(EconIndicatorFilepath)
            self.df_EconIndicator = self.df_EconIndicator[self.df_EconIndicator['Event'].notnull()].copy()
            self.df_EconIndicator['Date'] = pd.to_datetime(self.df_EconIndicator['Date'])
            print(self.df_EconIndicator)
        
        self.df_PriceDataRawFormat = pd.read_csv(PriceDataFilepath)
        self.df_SingleSeries = self.getPriceInSingleSeries(self.df_PriceDataRawFormat)

        self.InitResultSummary()

        self.df_KeyLevels = self.getKeyLevel(KeyLevelFilepath, KeyLevelName)
        self.df_SingleSeries = self.AssignKeyLevel(self.df_SingleSeries, self.df_KeyLevels, self.KeyLevelName)
        
        self.TradeSimulationCounter = 0
        self.SkipToSimulationCounter = SkipToSimulationCounter
        self.SimulationCounterForDebugExport = SimulationCounterForDebugExport
        
        self.RunBacktest(self.ParameterList)
        
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
        Columns = ['Ticker', 'KeyLevelName'] + list(self.ParameterList.keys()) + ['Average PnL/Stop Loss','stdev PnL/Stoploss','Sharpe Ratio']
        self.BacktestResultSummary = pd.DataFrame(columns=Columns)
        self.df_SingleSeries_WithPositionAround = None

    def getKeyLevelFromFile(self, KeyLevelFilepath):
        return pd.read_csv(KeyLevelFilepath)

    def getKeyLevel(self, KeyLevelFilepath, KeyLevelName, KeyLevelParameters = None):
        df_KeyLevels = None
        # print(KeyLevelFilepath)
        if KeyLevelFilepath is not None:
            # print('Going to run self.getKeyLevelFromFile')
            df_KeyLevels = self.getKeyLevelFromFile(KeyLevelFilepath)
        
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

        self.df_SingleSeries['Entry Price'] = np.nan
        self.df_SingleSeries['StopLoss Price'] = np.nan
        self.df_SingleSeries['TakeProfit Price'] = np.nan
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
        self.TradeEntryTimePeriodStart = self.Parameters['TradeEntryTimePeriodStart']
        self.TradeEntryTimePeriodEnd = self.Parameters['TradeEntryTimePeriodEnd']
        self.TradeMaxDuration = self.Parameters['TradeMaxDuration']
    
    def RunTradeSimulation(self):
        self.TradeID = 0
        LossTradeCountPerDay = 0
        WinTradeCountPerDay = 0
        for price_step_index in range(len(self.df_SingleSeries)-2, -1, -1):
            if price_step_index % 100000 == 0:
                print('Running for price_step_index = ' + str(price_step_index) + ' at ' + str(datetime.datetime.now()))
                
            if (self.df_SingleSeries.iloc[price_step_index]['Date'] != self.df_SingleSeries.iloc[price_step_index-1]['Date']):
                LossTradeCountPerDay = 0
                WinTradeCountPerDay = 0
                
                
            PriceNow = self.df_SingleSeries.iloc[price_step_index]['price']
            PositionBefore = self.df_SingleSeries.iloc[price_step_index+1]['Position']
            EntryPriceBefore = self.df_SingleSeries.iloc[price_step_index+1]['Entry Price']
            StopLossPriceBefore = self.df_SingleSeries.iloc[price_step_index+1]['StopLoss Price']
            TakeProfitPriceBefore = self.df_SingleSeries.iloc[price_step_index+1]['TakeProfit Price']
            KeyLevelDown = self.df_SingleSeries.iloc[price_step_index+1]['KeyLevelDown']
            KeyLevelUp = self.df_SingleSeries.iloc[price_step_index+1]['KeyLevelUp']
            
            if PositionBefore == 0:
                # No Position, try Getting into Trade
                if (self.df_SingleSeries.iloc[price_step_index]['InTradeEntryTimePeriod']) and (LossTradeCountPerDay < self.MaxLossTradeCountPerDay) and (WinTradeCountPerDay < self.MaxWinTradeCountPerDay):
                    if PriceNow <= KeyLevelDown:
                        self.TradeID = self.TradeID + 1
                        TradeDuration = 0
                        self.df_SingleSeries.at[price_step_index, 'Position'] = 1
                        self.df_SingleSeries.at[price_step_index, 'Trade ID'] = self.TradeID
                        self.df_SingleSeries.at[price_step_index, 'Entry Price'] = KeyLevelDown
                        self.df_SingleSeries.at[price_step_index, 'StopLoss Price'] = KeyLevelDown - self.StopLoss
                        self.df_SingleSeries.at[price_step_index, 'TakeProfit Price'] = KeyLevelDown + self.TakeProfit
                    if PriceNow >= KeyLevelUp:
                        self.TradeID = self.TradeID + 1
                        TradeDuration = 0
                        self.df_SingleSeries.at[price_step_index, 'Position'] = -1
                        self.df_SingleSeries.at[price_step_index, 'Trade ID'] = self.TradeID
                        self.df_SingleSeries.at[price_step_index, 'Entry Price'] = KeyLevelUp
                        self.df_SingleSeries.at[price_step_index, 'StopLoss Price'] = KeyLevelUp + self.StopLoss
                        self.df_SingleSeries.at[price_step_index, 'TakeProfit Price'] = KeyLevelUp - self.TakeProfit
            else:
                # Have Position, see if the trade should be exited
                self.df_SingleSeries.at[price_step_index, 'Trade ID'] = self.TradeID
                ExitTrade = False
                ExitPrice = np.nan
                TradeDuration = TradeDuration + 1
                if ((PositionBefore > 0) and (PriceNow <= StopLossPriceBefore)) or ((PositionBefore < 0) and (PriceNow >= StopLossPriceBefore)):
                    ExitPrice = StopLossPriceBefore
                    ExitTrade = True
                elif ((PositionBefore > 0) and (PriceNow > TakeProfitPriceBefore)) or ((PositionBefore < 0) and (PriceNow < TakeProfitPriceBefore)):
                    ExitPrice = TakeProfitPriceBefore
                    ExitTrade = True
                elif (TradeDuration/3 > self.TradeMaxDuration) or (price_step_index <= 0):
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
                    self.df_SingleSeries.at[price_step_index, 'Position'] = PositionBefore
                    self.df_SingleSeries.at[price_step_index, 'Entry Price'] = EntryPriceBefore
                    self.df_SingleSeries.at[price_step_index, 'StopLoss Price'] = StopLossPriceBefore
                    self.df_SingleSeries.at[price_step_index, 'TakeProfit Price'] = TakeProfitPriceBefore        

    def SummariseResult(self):
        self.df_SingleSeries['Abs Position'] = abs(self.df_SingleSeries['Position'])
        self.df_SingleSeries['With Position Around'] = self.df_SingleSeries['Abs Position'].rolling(5, center=True).sum()
        if self.CommissionPerTrade != 0:
            self.df_SingleSeries['PnL After Commission'] = self.df_SingleSeries['PnL'] - (2 * self.CommissionPerTrade)
        # self.df_SingleSeries['day_of_week'] = self.df_SingleSeries['Date'].dt.day_name()

        print('Trade ID is ' + str(self.TradeID) + ', PnL Count is ' + str(self.df_SingleSeries['PnL'].count()) + ', mean PnL/Stop Loss is ' + str(self.df_SingleSeries['PnL'].mean()/self.StopLoss) + ', stdev PnL/Stoploss is ' + str(self.df_SingleSeries['PnL'].std()/self.StopLoss) + ', Sharpe Ratio is ' + str(self.df_SingleSeries['PnL'].mean()/self.df_SingleSeries['PnL'].std()))
        
        if self.TradeSimulationCounter in self.SimulationCounterForDebugExport:
            df_SingleSeries_WithPositionAround = self.df_SingleSeries[self.df_SingleSeries['With Position Around'] > 0]
            df_SingleSeries_WithPositionAround['TradeSimulationCounter'] = self.TradeSimulationCounter
            df_SingleSeries_WithPositionAround['Ticker'] = self.Ticker
            df_SingleSeries_WithPositionAround['Parameters'] = str(self.Parameters)
            if self.EconIndicatorParameters is not None:
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
        data_dict.update(self.Parameters)
        # data_dict.update({'Average PnL/Stop Loss' : self.df_SingleSeries['PnL'].mean()/self.StopLoss ,'stdev PnL/Stoploss' : self.df_SingleSeries['PnL'].std()/self.StopLoss,'Sharpe Ratio' : self.df_SingleSeries['PnL'].mean()/self.df_SingleSeries['PnL'].std()})
        data_dict.update({'Average PnL/Stop Loss' : self.df_SingleSeries['PnL'].mean()/self.StopLoss ,'Sharpe Ratio' : self.df_SingleSeries['PnL'].mean()/self.df_SingleSeries['PnL'].std()})
        
        if self.CommissionPerTrade != 0:
            # data_dict.update({'Average PnL/Stop Loss After Commission' : self.df_SingleSeries['PnL After Commission'].mean()/self.StopLoss ,'stdev PnL/Stoploss After Commission' : self.df_SingleSeries['PnL After Commission'].std()/self.StopLoss,'Sharpe Ratio After Commission' : self.df_SingleSeries['PnL After Commission'].mean()/self.df_SingleSeries['PnL After Commission'].std()})
            data_dict.update({'Average PnL/Stop Loss After Commission' : self.df_SingleSeries['PnL After Commission'].mean()/self.StopLoss ,'Sharpe Ratio After Commission' : self.df_SingleSeries['PnL After Commission'].mean()/self.df_SingleSeries['PnL After Commission'].std()})
        
        if self.ResultOnDayOfWeek is not None:
            for DayOfWeek in self.ResultOnDayOfWeek:
                # df_SingleSeries_OnDayOfWeek = self.df_SingleSeries[self.df_SingleSeries['day_of_week'] == DayOfWeek].copy()
                df_SingleSeries_OnDayOfWeek = self.df_SingleSeries[(self.df_SingleSeries['day_of_week'] == DayOfWeek) & self.df_SingleSeries['PnL'].notnull()].copy()
                print('df_SingleSeries_OnDayOfWeek is')
                print(df_SingleSeries_OnDayOfWeek)
                data_dict.update({'Trade Count - ' + DayOfWeek : df_SingleSeries_OnDayOfWeek['PnL'].count(), 'Average PnL/Stop Loss - ' + DayOfWeek : df_SingleSeries_OnDayOfWeek['PnL'].mean()/self.StopLoss, 'Sharpe Ratio - ' + DayOfWeek : df_SingleSeries_OnDayOfWeek['PnL'].mean()/df_SingleSeries_OnDayOfWeek['PnL'].std()})
            
        df = pd.DataFrame(data_dict, index=[0])
        print('df for backrest summary is')
        print(df)
        self.BacktestResultSummary = pd.concat([self.BacktestResultSummary, df])
        
        
class KeyLevelGenerator:
    def __init__(self, KeyLevelName, PriceDataFilepath, LookBackPeriod, KeyLevelParameters, Ticker = '', PriceDataTimeframe = '1 min', KeyLevelExportFilepath = None, GPUMode = False, KeepDataframeData = False):
        self.KeyLevelName = KeyLevelName
        self.LookBackPeriod = LookBackPeriod
        self.KeyLevelParameters = KeyLevelParameters
        self.Ticker = Ticker
        self.KeyLevelExportFilepath = KeyLevelExportFilepath
        self.PriceDataTimeframe = PriceDataTimeframe
        self.GPUMode = GPUMode
        self.KeepDataframeData = KeepDataframeData

        self.FuturesData = pd.read_csv(PriceDataFilepath)
        self.FuturesData = self.FuturesData[(self.FuturesData['TimeInStandardUnit'] >= (9*60+30)) & (self.FuturesData['TimeInStandardUnit'] <= (16*60))].reset_index(drop=True) 
        
        self.FuturesData.drop('date id', axis=1, inplace=True)
        
        #print(self.FuturesData)
        
        DateList = self.FuturesData[['Date']].drop_duplicates().sort_values(by=['Date'], ascending=False).reset_index(drop=True)
        DateList['date id'] = DateList.index

        self.FuturesData = self.FuturesData.merge(DateList, how='inner', on='Date')
        self.date_by_date_id = self.FuturesData[['date id', 'Date']].drop_duplicates()
        self.df_KL = pd.DataFrame()
        
    def getLookbackDataContangoAdjusted(self, date_id):
        historical_date_id_range = [date_id+1, date_id+self.LookBackPeriod]
        df_lookbackdata = self.FuturesData[(self.FuturesData['date id'] >= historical_date_id_range[0]) & (self.FuturesData['date id'] <= historical_date_id_range[1])].copy()
    
        df_fulllookbackdata = self.FuturesData[(self.FuturesData['date id'] >= historical_date_id_range[0]-1) & (self.FuturesData['date id'] <= historical_date_id_range[1])]
        df_fulllookbackdata_expires = df_fulllookbackdata[['expiry']].drop_duplicates()
        if len(df_fulllookbackdata_expires) > 1:
    
          df_SpotDayData = FuturesData[(FuturesData['date id'] == historical_date_id_range[0])]
          df_SpotDayData['ExpiryAdj'] = df_SpotDayData['close'] - df_SpotDayData['close_adj']
          SpotDayExpiryAdj = df_SpotDayData['ExpiryAdj'].mean()
          SpotDayExpiry = df_SpotDayData.iloc[0]['expiry']
          print('Ticker is ' + str(self.Ticker) + ' and date_id is ' + str(date_id) + ' and SpotDayExpiryAdj is ' + str(SpotDayExpiryAdj))
          df_lookbackdata1 = df_lookbackdata[df_lookbackdata['expiry'] == SpotDayExpiry]
          df_lookbackdata2 = df_lookbackdata[df_lookbackdata['expiry'] != SpotDayExpiry]
          df_lookbackdata2['close'] = df_lookbackdata2['close_adj'] + SpotDayExpiryAdj
          df_lookbackdata2['open'] = df_lookbackdata2['open_adj'] + SpotDayExpiryAdj
          df_lookbackdata2['high'] = df_lookbackdata2['high_adj'] + SpotDayExpiryAdj
          df_lookbackdata2['low'] = df_lookbackdata2['low_adj'] + SpotDayExpiryAdj
          df_lookbackdata = pd.concat([df_lookbackdata1,df_lookbackdata2])
    
        df_lookbackdata = df_lookbackdata.sort_values(by=['tDateTime']).reset_index(drop=True)
        
        return df_lookbackdata

    def getKeyLevelCalculated(self, date_id, df_lookbackdata):
        return pd.DataFrame()
        
    def generateKeyLevel(self, SkipToDateID = 0):
        for date_id in range(SkipToDateID, FuturesData['date id'].max()):
        
            if date_id % 10 == 0:
                self.df_KL = self.df_KL.merge(self.date_by_date_id, how='left', on='date id')
                if len(df_KL) > 0:
                    # df_KL.to_csv(OutputFolder + ticker + r'_KeyLevel_WithExpiryAdj_' + 'KL-VT-PD-LB' + str(LookBackPeriod) + '-MinMove' + str(MinVertexMovementThreshold) + '_batch' + str(date_id) + '.csv')
                    self.df_KL.to_csv(self.KeyLevelExportFilepath.replace('.csv', '_batch' + str(date_id) + '.csv'))
                self.df_KL.drop(['Date'], axis=1, inplace=True)        
            
            df_lookbackdata = self.getLookbackDataContangoAdjusted(date_id)
            df_KeyLevelCalculatedForSingleDateID = self.getKeyLevelCalculated(df_lookbackdata)
            
            self.df_KL = pd.concat([self.df_KL,df_KeyLevelCalculatedForSingleDateID],ignore_index=True)
            
        self.df_KL = self.df_KL.merge(self.date_by_date_id, how='left', on='date id')
        if len(self.df_KL) > 0:
            self.df_KL.to_csv(self.KeyLevelExportFilepath)            

class KeyLevelByHighLowInLookBackPeriodGenerator(KeyLevelGenerator):
    def getKeyLevelCalculated(self, date_id, df_lookbackdata):
        max_index = df_lookbackdata['high'].idxmax()
        min_index = df_lookbackdata['low'].idxmin()
        df = pd.DataFrame({'ticker' : [self.Ticker, self.Ticker], 
                           'date id' : [date_id, date_id], 
                           self.KeyLevelName : [df_lookbackdata['low'].min(), df_lookbackdata['high'].max()]})
        return df

class KeyLevelByVertexGenerator(KeyLevelGenerator):
    def getKeyLevelCalculated(self, date_id, df_lookbackdata):
        max_index = df_lookbackdata['high'].idxmax()
        min_index = df_lookbackdata['low'].idxmin()
        look_back_period_vertex_layer = [0,1,1,0]
        if max_index < min_index:
            look_back_period_vertex_index = [0, max_index, min_index, len(df_lookbackdata)-1]
            look_back_period_vertex_price_tag = [0,1,2,3]
            look_back_period_vertex_day_back = [self.LookBackPeriod,df_lookbackdata.iloc[max_index]['date id'] - date_id,df_lookbackdata.iloc[min_index]['date id'] - date_id,1]
        else:
            look_back_period_vertex_index = [0, min_index, max_index, len(df_lookbackdata)-1]
            look_back_period_vertex_price_tag = [0,2,1,3]
            look_back_period_vertex_day_back = [self.LookBackPeriod,df_lookbackdata.iloc[min_index]['date id'] - date_id,df_lookbackdata.iloc[max_index]['date id'] - date_id,1]
    
        df_lookbackdata['look back index'] = df_lookbackdata.index
    
        df_lookbackdata_section = df_lookbackdata.iloc[look_back_period_vertex_index[0]+1:look_back_period_vertex_index[1]]
    #   print(df_Lookbackdata_section)
    
        LayerCount = 2
    
        while len(look_back_period_vertex_index) - 2 < self.KeyLevelParameters['MaxNumberOfVertex']:
            MaxMovement = 0
            MaxMovementStartIndex = -1
            MaxMovementEndIndex = -1
            MaxMovementSectionlndex = -1
    
            for section_index in range(len(look_back_period_vertex_index)-1):
               if (look_back_period_vertex_price_tag[section_index] == 2) or (look_back_period_vertex_price_tag[section_index+1] == 1):
                   Section_Dir = 1
                   Section_Start_Tag = 1
                   Section_End_Tag = 2
               else:
                   Section_Dir = -1
                   Section_Start_Tag = 2
                   Section_End_Tag = 1
               for section_scan_start_index in range(look_back_period_vertex_index[section_index]+1,look_back_period_vertex_index[section_index+1]):
                   if section_scan_start_index % 800 == 0:
                       print('ticker is ' + str(ticker) + ' and date_id is ' + str(date_id) + ', LayerCount is ' + str(LayerCount) + ', section_scan_start_index is ' + str(section_scan_start_index) + ' at ' + str(datetime.datetime.now()))
                   for section_scan_end_index in range(section_scan_start_index,look_back_period_vertex_index[section_index+1]):
                       SectionMovement = -1 * Section_Dir * \
                       (df_lookbackdata.iloc[section_scan_end_index][price_tag[Section_End_Tag]] - df_lookbackdata.iloc[section_scan_start_index][price_tag[Section_Start_Tag]])
                       if (SectionMovement > MaxMovement) and (SectionMovement > self.KeyLevelParameters['MinVertexMovementThreshold']):
                           MaxMovement = SectionMovement
                           MaxMovementStartIndex = section_scan_start_index
                           MaxMovementEndIndex = section_scan_end_index
                           MaxMovementSectionIndex = section_index
    
            if MaxMovement <= 0:
               break
    
            look_back_period_vertex_index.insert(MaxMovementSectionIndex+1, MaxMovementEndIndex)
            look_back_period_vertex_index.insert(MaxMovementSectionIndex+1, MaxMovementStartIndex)
            look_back_period_vertex_layer.insert(MaxMovementSectionIndex+1, LayerCount)
            look_back_period_vertex_layer.insert(MaxMovementSectionIndex+1, LayerCount)
            LayerCount = LayerCount + 1
    
            look_back_period_vertex_day_back.insert(MaxMovementSectionIndex+1, df_lookbackdata.iloc[MaxMovementEndIndex]['date id'] - date_id)
            look_back_period_vertex_day_back.insert(MaxMovementSectionIndex+1, df_lookbackdata.iloc[MaxMovementStartIndex]['date id'] - date_id)
    
            if (look_back_period_vertex_price_tag[MaxMovementSectionIndex] == 2) or (look_back_period_vertex_price_tag[MaxMovementSectionIndex+1] == 1):
               look_back_period_vertex_price_tag.insert(MaxMovementSectionIndex+1, 2)
               look_back_period_vertex_price_tag.insert(MaxMovementSectionIndex+1, 1)
            else:
               look_back_period_vertex_price_tag.insert(MaxMovementSectionIndex+1, 1)
               look_back_period_vertex_price_tag.insert(MaxMovementSectionIndex+1, 2)
            # print(Look_bach_period_vertex_price_tag)
    
        KL = []
        for i in range(len(look_back_period_vertex_index)):
            KL.append(df_lookbackdata.iloc[look_back_period_vertex_index[i]][price_tag[look_back_period_vertex_price_tag[i]]])
            
        df_All = None
    
        df = pd.DataFrame(columns=['ticker', 'date id', self.KeyLevelName + '-DateID', self.KeyLevelName,
                                  self.KeyLevelName + 'Layer', self.KeyLevelName + 'DayBack'])
        
        for i in range(len(KL)):
            df.loc[0] = [self.Ticker, date_id, df_lookbackdata.iloc[look_back_period_vertex_index[i]]['date id'], KL[i], look_back_period_vertex_layer[i],look_back_period_vertex_day_back[i]]
            if df_All is None:
                df_All = df
            else:
                df_All = pd.concat([df_All, df])
        return df_All
    
