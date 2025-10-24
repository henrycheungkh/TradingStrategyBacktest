# -*- coding: utf-8 -*-
"""
Created on Sun Jul  7 00:15:59 2024

@author: Henry Cheung
"""



import pandas as pd
import numpy as np
import datetime

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

        self.LookbackTimePeriodStart = 0
        self.LookbackTimePeriodEnd = 9999999
        if ('LookbackTimePeriodStart' in KeyLevelParameters):
            self.LookbackTimePeriodStart = KeyLevelParameters['LookbackTimePeriodStart']
        if ('LookbackTimePeriodEnd' in KeyLevelParameters):
            self.LookbackTimePeriodEnd = KeyLevelParameters['LookbackTimePeriodEnd']

        # self.FuturesData = self.FuturesData[(self.FuturesData['TimeInStandardUnit'] >= (9*60+30)) & (self.FuturesData['TimeInStandardUnit'] <= (16*60))].reset_index(drop=True) 
        # self.FuturesData = self.FuturesData[(self.FuturesData['TimeInStandardUnit'] >= self.LookbackTimePeriodStart) & (self.FuturesData['TimeInStandardUnit'] <= self.LookbackTimePeriodEnd)].reset_index(drop=True) 
            
        self.FilterPriceDataByTimePeriod()
        
        self.ResetDateID()
        
        # self.FuturesData.drop('date id', axis=1, inplace=True)
        
        # DateList = self.FuturesData[['Date']].drop_duplicates().sort_values(by=['Date'], ascending=False).reset_index(drop=True)
        # DateList['date id'] = DateList.index

        # self.FuturesData = self.FuturesData.merge(DateList, how='inner', on='Date')
        # self.date_by_date_id = self.FuturesData[['date id', 'Date']].drop_duplicates()

        self.df_KL = pd.DataFrame()
    
    def FilterPriceDataByTimePeriod(self):    
        self.FuturesData = self.FuturesData[(self.FuturesData['TimeInStandardUnit'] >= self.LookbackTimePeriodStart) & (self.FuturesData['TimeInStandardUnit'] <= self.LookbackTimePeriodEnd)].reset_index(drop=True) 
    
    def ResetDateID(self):
        self.FuturesData.drop('date id', axis=1, inplace=True)
        
        DateList = self.FuturesData[['Date']].drop_duplicates().sort_values(by=['Date'], ascending=False).reset_index(drop=True)
        DateList['date id'] = DateList.index

        self.FuturesData = self.FuturesData.merge(DateList, how='inner', on='Date')
        self.date_by_date_id = self.FuturesData[['date id', 'Date']].drop_duplicates()
        
    def getLookbackDataContangoAdjusted(self, date_id):
        historical_date_id_range = [date_id+1, date_id+self.LookBackPeriod]
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

    def getKeyLevelCalculatedForSingleDate(self, date_id, df_lookbackdata):
        return pd.DataFrame()
        
    def generateKeyLevel(self, SkipToDateID = 0):
        for date_id in range(SkipToDateID, self.FuturesData['date id'].max()):
        
            if (date_id % 10) and (len(self.df_KL) > 0) == 0:
                self.df_KL = self.df_KL.merge(self.date_by_date_id, how='left', on='date id')
                if len(df_KL) > 0:
                    # df_KL.to_csv(OutputFolder + ticker + r'_KeyLevel_WithExpiryAdj_' + 'KL-VT-PD-LB' + str(LookBackPeriod) + '-MinMove' + str(MinVertexMovementThreshold) + '_batch' + str(date_id) + '.csv')
                    if self.KeyLevelExportFilepath is not None:
                        self.df_KL.to_csv(self.KeyLevelExportFilepath.replace('.csv', '_batch' + str(date_id) + '.csv'))
                self.df_KL.drop(['Date'], axis=1, inplace=True)        
            
            df_lookbackdata = self.getLookbackDataContangoAdjusted(date_id)
            df_KeyLevelCalculatedForSingleDateID = self.getKeyLevelCalculatedForSingleDate(date_id, df_lookbackdata)
            
            self.df_KL = pd.concat([self.df_KL,df_KeyLevelCalculatedForSingleDateID],ignore_index=True)
            
        self.df_KL = self.df_KL.merge(self.date_by_date_id, how='left', on='date id')
        if len(self.df_KL) > 0:
            if self.KeyLevelExportFilepath is not None:
                self.df_KL.to_csv(self.KeyLevelExportFilepath)         
            else:
                print('Key Levels generated are')
                print(self.df_KL)

class KeyLevelByHighLowInLookBackPeriodGenerator(KeyLevelGenerator):
    def getKeyLevelCalculatedForSingleDate(self, date_id, df_lookbackdata):
        max_index = df_lookbackdata['high'].idxmax()
        min_index = df_lookbackdata['low'].idxmin()
        df = pd.DataFrame({'ticker' : [self.Ticker, self.Ticker], 
                           'date id' : [date_id, date_id], 
                           'type' : ['Prior Low', 'Prior High'],
                           self.KeyLevelName : [df_lookbackdata['low'].min(), df_lookbackdata['high'].max()]})
        return df

class KeyLevelByVertexGenerator(KeyLevelGenerator):
    def getKeyLevelCalculatedForSingleDate(self, date_id, df_lookbackdata):
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
    
