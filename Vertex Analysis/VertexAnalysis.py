# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 20:03:52 2024

@author: henry
"""

import datetime
import pandas as pd
pd.set_option('display.max_columns', None)

price_tag = ['open', 'high', 'low', 'close']

LookBackPeriod = 5
MinVertexMovementThreshold = 120
MaxNumberOfVertex = 10
ticker = 'NQ'

FuturesData = pd.read_csv(r'E:\TradeAnalysisProject\Vertex Analysis\prices_NQ_1 min_20230601_20240614_0700-1600.csv')
FuturesData = FuturesData[(FuturesData['TimeInStandardUnit'] >= (9*60+30)) & (FuturesData['TimeInStandardUnit'] <= (16*60))]
# print(FuturesData)

FuturesData.drop('date id', axis=1, inplace=True)

DateList = FuturesData[['Date']].drop_duplicates().sort_values(by=['Date'], ascending=False).reset_index(drop=True)
DateList['date id'] = DateList.index

FuturesData = FuturesData.merge(DateList, how='inner', on='Date')

df_KL = pd.DataFrame(columns=['ticker', 'date id', 'KL-VT'])





