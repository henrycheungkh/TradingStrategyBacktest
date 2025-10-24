# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 09:51:03 2021

@author: Henry Cheung
"""

from InvestmentAnalytics.CUDA.CUDADataFrameUtil import CUDAMapByLookup
from datetime import date, datetime, timedelta

# import pycuda.driver as cuda
# import pycuda.autoinit
# from pycuda.compiler import SourceModule
import pandas as pd
# import os
# import numpy as np


# data_df = pd.DataFrame(data={'a': [100, 101, 102, 103], 'b': [200, 201, 202, 203], 'c': [1, 2, 3, 1]})
# lookup_df = pd.DataFrame(data={'c': [1, 2, 3], 'd': [10, 30, 60], 'e': [10, 30, 60]})

data_df = pd.read_csv(r'd:\temp\trade_record after point A CUDA.csv')

# data_df = pd.read_csv(r'd:\temp\data.csv')
lookup_df = pd.read_csv(r'd:\temp\lookup data.csv')

# data_df = data_df.tail(2500000)

# data_df = data_df[['entry time id']].copy()
# data_df.to_csv(r'd:\temp\data.csv', index=False)

# data_df.drop(['Abs Sharpe Ratio after commission'],axis='columns')

print('data_df is')
print(data_df)
print('lookup_df is')
print(lookup_df)

CUDAMapByLookupStartTime = datetime.now()
print('CUDAMapByLookup started at ' + str(CUDAMapByLookupStartTime))


# mapped_df = CUDAMapByLookup(data_df, ['c'], lookup_df)
mapped_df = CUDAMapByLookup(data_df, ['entry time id'], lookup_df)

print('mapped_df is')
print(mapped_df)

CUDAMapByLookupEndTime = datetime.now()
print('CUDAMapByLookup ended at ' + str(CUDAMapByLookupEndTime))

print('data_df is')
print(data_df)
print('lookup_df is')
print(lookup_df)


merged_df = data_df.merge(lookup_df, on=['entry time id'])

print('merged_df is')
print(merged_df)

MergeEndTime = datetime.now()
print('Merge ended at ' + str(MergeEndTime))




# mapped_df.to_csv(r'd:\temp\mapped_df.csv', index=False)
# mapped_df_error = mapped_df.loc[mapped_df['TimeInStandardUnit'] == 0]

# print('mapped_df_error is')
# print(mapped_df_error)

