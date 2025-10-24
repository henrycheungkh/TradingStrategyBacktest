# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 10:41:27 2024

@author: Henry Cheung
"""

import pandas as pd
import numpy as np







class LongShortIndicator:
    def __init__(self, LongShortIndicatorName, LongShortIndicatorsParameters, GPUMode = False, KeepDataframeData = False):
        self.LookBackPeriodPerDay = 0
    def getIndicatorValuesOfSingleDay(self, ContangoAdjustedPriceData):
        return None
    def getIndicatorValuesAfterFinishUpCalculation(self, IndicatorValuesByValueDate):
        return None
    
    def getLastCandlePerDay(self, ContangoAdjustedPriceData):
        df = pd.pivot_table(ContangoAdjustedPriceData, values='tDateTime', index=['date id'], aggfunc="max")
        return ContangoAdjustedPriceData.merge(df, how='inner', on='tDateTime').sort_values(by='tDateTime', ascending=False, inplace=False).reset_index(drop=True)

# MACD
# https://indzara.com/free-excel-template-for-macd-technical-indicator/

# MACD Line = (12-day EMA – 26-day EMA)
# Signal Line = 9-day EMA of MACD Line
# MACD Histogram = MACD Line – Signal Line

# A general interpretation of MACD is that when MACD is positive and the histogram value is increasing, then upside momentum is increasing. 
# When MACD is negative and the histogram value is decreasing, then downside momentum is increasing.


# https://www.investopedia.com/terms/e/ema.asp

class LongShortIndicatorMACD(LongShortIndicator):
    def __init__(self, LongShortIndicatorName, LongShortIndicatorsParameters, GPUMode = False, KeepDataframeData = False):
        self.FastLength = LongShortIndicatorsParameters['Fast Length/Slow Length/Signal Smoothing'][0]
        self.SlowLength = LongShortIndicatorsParameters['Fast Length/Slow Length/Signal Smoothing'][1]
        self.SignalSmoothing = LongShortIndicatorsParameters['Fast Length/Slow Length/Signal Smoothing'][2]
        self.Source = LongShortIndicatorsParameters['Source']
        self.OscillatorMAType = LongShortIndicatorsParameters['Oscillator MA Type']
        self.SignalLineMAType = LongShortIndicatorsParameters['Signal Line MA Type']
        
        if 'EMA Smoothing' in LongShortIndicatorsParameters:
            self.EMASmoothing = LongShortIndicatorsParameters['EMA Smoothing']
        else:
            self.EMASmoothing = 2
            
        if 'EMA Look back Multiple' in LongShortIndicatorsParameters:
            self.EMALookBackMultiple = LongShortIndicatorsParameters['EMA Look back Multiple']
        else:
            if self.OscillatorMAType == 'EMA':
                self.EMALookBackMultiple = 3
            else:
                self.EMALookBackMultiple = 1
                
        # print('self.EMALookBackMultiple is ' + str(self.EMALookBackMultiple))
        # print('in LongShortIndicatorMACD.init, self.OscillatorMAType is ' + str(self.OscillatorMAType))
        
        self.LookBackPeriodPerDay = self.SlowLength * self.EMALookBackMultiple
        
    def getIndicatorValuesOfSingleDay(self, date_id, ContangoAdjustedPriceData):
        
        if self.Source == 'close':
            
            if self.OscillatorMAType == 'SMA':
                df_SlowLengthMA = self.getLastCandlePerDay(ContangoAdjustedPriceData[ContangoAdjustedPriceData['date id'] <= date_id + self.SlowLength])
                df_FastLengthMA = self.getLastCandlePerDay(ContangoAdjustedPriceData[ContangoAdjustedPriceData['date id'] <= date_id + self.FastLength])
                SlowLengthMA = df_SlowLengthMA['close'].mean()
                FastLengthMA = df_FastLengthMA['close'].mean()
            elif self.OscillatorMAType == 'EMA':
                df_FullLengthMA = self.getLastCandlePerDay(ContangoAdjustedPriceData[ContangoAdjustedPriceData['date id'] <= date_id + self.LookBackPeriodPerDay])
                dates_count = len(df_FullLengthMA)
                
                SlowLengthMA = df_FullLengthMA.tail(self.SlowLength)['close'].mean()
                for i in range(dates_count - self.SlowLength - 1, 0, -1):
                    # print('i = ' + str(i))
                    # CurrentPrice = df_FullLengthMA.iloc[i]['close']
                    # print('CurrentPrice is')
                    # print(CurrentPrice)
                    SlowLengthMA = df_FullLengthMA.iloc[i]['close'] * self.EMASmoothing / (1 + self.SlowLength) + SlowLengthMA * (1-(self.EMASmoothing / (1 + self.SlowLength)))
                    
                FastLengthMA = df_FullLengthMA.tail(self.FastLength)['close'].mean()
                for i in range(dates_count - self.FastLength - 1, 0, -1):
                    FastLengthMA = df_FullLengthMA.iloc[i]['close'] * self.EMASmoothing / (1 + self.FastLength) + FastLengthMA * (1-(self.EMASmoothing / (1 + self.FastLength)))
                    
                df_FastLengthMA = self.getLastCandlePerDay(ContangoAdjustedPriceData[ContangoAdjustedPriceData['date id'] <= date_id + self.FastLength])
                # print('self.OscillatorMAType == EMA')
                # SlowLengthMA = df_SlowLengthMA['close'].mean()
                # FastLengthMA = df_FastLengthMA['close'].mean()
                
                # print('SlowLengthMA is ' + str(SlowLengthMA) + ' and FastLengthMA is ' + str(FastLengthMA))
                
            
            return pd.DataFrame({'value date id' : [date_id], 'SlowLengthMA' : [SlowLengthMA], 'FastLengthMA' : [FastLengthMA]}, index=[0])
        else:
            return None

    def getIndicatorValuesAfterFinishUpCalculation(self, df_IndicatorValuesByDay, date_by_date_id):
        for i in range(self.SignalSmoothing-1):
            df_IndicatorValuesByDay = pd.concat([df_IndicatorValuesByDay, pd.DataFrame({'value date id' : [-1-i], 'SlowLengthMA' : [0], 'FastLengthMA' : [0]}, index=[0])])
        df_IndicatorValuesByDay = df_IndicatorValuesByDay.sort_values(by='value date id', ascending=True, inplace=False).reset_index(drop=True)
        # df_IndicatorValuesByDay.to_csv(r'J:\temp\df_IndicatorValuesByDay_Before_MACD.csv')
        
        df_IndicatorValuesByDay['MACD'] = df_IndicatorValuesByDay['FastLengthMA'] - df_IndicatorValuesByDay['SlowLengthMA']
        if self.SignalLineMAType == 'SMA':
            df_IndicatorValuesByDay['MACD Shifted'] = df_IndicatorValuesByDay['MACD'].shift(-1*self.SignalSmoothing + 1)
            df_IndicatorValuesByDay['MACD Signal'] = df_IndicatorValuesByDay.rolling(window=self.SignalSmoothing)['MACD Shifted'].mean()
            df_IndicatorValuesByDay['MACD Histogram'] = df_IndicatorValuesByDay['MACD'] - df_IndicatorValuesByDay['MACD Signal']
            df_IndicatorValuesByDay.drop(['MACD Shifted'], axis=1, inplace=True)
            df_IndicatorValuesByDay = df_IndicatorValuesByDay[(df_IndicatorValuesByDay['value date id'] >= 0) & (df_IndicatorValuesByDay['MACD Signal'].notnull())].rename(columns={"value date id": "date id"}).copy()
        elif self.SignalLineMAType == 'EMA':
            df_IndicatorValuesByDay['MACD Signal'] = 0
            df_IndicatorValuesByDay.at[len(df_IndicatorValuesByDay) - self.SignalSmoothing, 'MACD Signal'] = df_IndicatorValuesByDay.tail(self.SignalSmoothing)['MACD'].mean()
            for i in range(len(df_IndicatorValuesByDay) - self.SignalSmoothing - 1, 0, -1):
                df_IndicatorValuesByDay.at[i, 'MACD Signal'] = df_IndicatorValuesByDay.iloc[i]['MACD'] * self.EMASmoothing / (1 + self.SignalSmoothing) + df_IndicatorValuesByDay.iloc[i+1]['MACD'] * (1-(self.EMASmoothing / (1 + self.SignalSmoothing)))
        return df_IndicatorValuesByDay.merge(date_by_date_id, how='inner', on='date id')
    
    
    
    
    
    