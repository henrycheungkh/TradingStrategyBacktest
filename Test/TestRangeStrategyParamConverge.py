# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 10:38:30 2022

@author: Henry Cheung
"""

import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import math
import pandas as pd

import InvestmentAnalytics.CUDA.CUDAPathSetting

import numpy as np

pd.set_option('max_columns', None)

df_time = pd.read_csv(r'd:\temp\date_time_matrix.csv')
df_time_len = len(df_time)

df_parameter = pd.read_csv(r'd:\temp\StartTradingTimeList_withBackdateTime.csv')

print(df_time)
print(df_parameter)
df_start_trading_time = df_time.merge(df_parameter, left_on='time in std unit', right_on='start trading time in std unit')
df_start_trading_time['start searching time id'] = df_start_trading_time['time id'] + df_start_trading_time['obs backdate start']
df_start_trading_time = df_start_trading_time.loc[df_start_trading_time['start searching time id'] >= 0]
df_start_trading_time['start searching time id'] = df_start_trading_time['start searching time id'].astype(int)

print(df_start_trading_time)

# df_parameter_in_ = df_start_trading_time[['date id']]

df_time_matrix = df_time.to_numpy()
df_start_trading_time_matrix = df_start_trading_time.to_numpy()

print("dimension of df_time_matrix is " + str(len(df_time_matrix)) + " x " + str(len(df_time_matrix[0])))
print(df_time_matrix)
print("dimension of df_start_trading_time_matrix is " + str(len(df_start_trading_time_matrix)) + " x " + str(len(df_start_trading_time_matrix[0])))
print(df_start_trading_time_matrix)



# TimeParameterList = []

# # print(df_time.iloc[2]['date adj time in std unit'])
# # j = df_start_trading_time.iloc[0]['start searching time id']


# for i, row in df_start_trading_time.iterrows(): 
#     if row['start searching time id'] >= 0:
#         j = row['start searching time id']
#         j = math.floor(j)
#         # print(j)
#         while df_time.iloc[j]['date adj time in std unit'] < row['date adj time in std unit'] + row['obs backdate start']:
#         # while df_time.iloc['date adj time in std unit'][j] < row['date adj time in std unit'] + row['obs backdate start']:
#             j = j + 1
#         obs_start_time_id = j
#         while j + 1 < df_time_len and df_time.iloc[j+1]['date adj time in std unit'] <= row['date adj time in std unit'] + row['obs backdate end']:
#         # while j + 1 < df_time_len and df_time.iloc['date adj time in std unit'][j+1] <= row['date adj time in std unit'] + row['obs backdate end']:
#             j = j + 1
#         obs_end_time_id = j
#         TimeParameterList.append([row['time in std unit'], row['obs backdate start'], row['obs backdate end'], obs_start_time_id, obs_end_time_id, row['time id']])
        
# df_result = pd.DataFrame(TimeParameterList, columns=['time in std unit', 'obs backdate start', 'obs backdate end', 'obs start time id', 'obs end time id', 'start trading time id'])
# print(df_result)
            
    
    