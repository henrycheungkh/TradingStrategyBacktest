# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 08:27:05 2024

@author: Henry Cheung
"""


import pandas as pd
import numpy as np
import datetime

from LongShortIndicators import *

class LongShortIndicatorGenerator:
    def __init__(self, PriceDataFilepath, Ticker = '', PriceDataTimeframe = '1 min', KeyLevelExportFilepath = None, GPUMode = False, KeepDataframeData = False):
        self.Ticker = Ticker
        self.AllFuturesData = pd.read_csv(PriceDataFilepath)
        
        self.LookBackPeriod = 1


    def FilterPriceDataByTimePeriod(self, LookbackTimePeriodStart = (9*60 + 30), LookbackTimePeriodEnd = (16*60)):    
        self.FuturesData = self.AllFuturesData[(self.AllFuturesData['TimeInStandardUnit'] >= LookbackTimePeriodStart) & (self.AllFuturesData['TimeInStandardUnit'] <= LookbackTimePeriodEnd)].reset_index(drop=True) 
    
    def ResetDateID(self):
        self.FuturesData.drop('date id', axis=1, inplace=True)
        
        DateList = self.FuturesData[['Date']].drop_duplicates().sort_values(by=['Date'], ascending=False).reset_index(drop=True)
        DateList['date id'] = DateList.index

        self.FuturesData = self.FuturesData.merge(DateList, how='inner', on='Date')
        self.date_by_date_id = self.FuturesData[['date id', 'Date']].drop_duplicates()

# df_IndicatorValuesByDay = self.LongShortIndicator_generator.getIndicatorValuesByDay('MACD', {'Fast Length/Slow Length/Signal Smoothing' : [12,26,9], 'Source' : 'close', 'Oscillator MA Type' : 'SMA', 'Signal Line MA Type' : 'SMA'})
    def getIndicatorValuesByDay(self, LongShortIndicatorName, LongShortIndicatorsParameters):
        self.FilterPriceDataByTimePeriod()
        self.ResetDateID()
        df_IndicatorValuesByDay = None
        if LongShortIndicatorName == 'MACD':
            LongShortIndicator = LongShortIndicatorMACD(LongShortIndicatorName, LongShortIndicatorsParameters)

            for date_id in range(self.FuturesData['date id'].max() - LongShortIndicator.LookBackPeriodPerDay):
                
                df_lookbackdata = self.getLookbackDataContangoAdjusted(date_id, LongShortIndicator.LookBackPeriodPerDay)
                df_lookbackdata['value date id'] = date_id
                
                df_IndicatorValuesByDayForSingleDay = LongShortIndicator.getIndicatorValuesOfSingleDay(date_id, df_lookbackdata)
                    
                if df_IndicatorValuesByDay is None and df_IndicatorValuesByDayForSingleDay is not None:
                    df_IndicatorValuesByDay = df_IndicatorValuesByDayForSingleDay
                else:
                    df_IndicatorValuesByDay = pd.concat([df_IndicatorValuesByDay, df_IndicatorValuesByDayForSingleDay])
                    
            df_IndicatorValuesByDay = LongShortIndicator.getIndicatorValuesAfterFinishUpCalculation(df_IndicatorValuesByDay, self.date_by_date_id)
            
        elif LongShortIndicatorName == 'RSI':
            pass
        
        return df_IndicatorValuesByDay
    
    def getLookbackDataContangoAdjusted(self, date_id, LookBackPeriod):
        historical_date_id_range = [date_id + 1, date_id + LookBackPeriod]
        df_lookbackdata = self.FuturesData[(self.FuturesData['date id'] >= historical_date_id_range[0]) & (self.FuturesData['date id'] <= historical_date_id_range[1])].copy()
        
        df_fulllookbackdata = self.FuturesData[(self.FuturesData['date id'] >= historical_date_id_range[0]-1) & (self.FuturesData['date id'] <= historical_date_id_range[1])]
        df_fulllookbackdata_expires = df_fulllookbackdata[['expiry']].drop_duplicates()
        
        if len(df_fulllookbackdata_expires) > 1:
    
          df_SpotDayData = self.FuturesData[(self.FuturesData['date id'] == historical_date_id_range[0])]
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
    
    
    