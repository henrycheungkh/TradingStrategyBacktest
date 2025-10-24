# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 14:57:11 2021

@author: Henry Cheung
"""


# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 15:37:06 2021

@author: Henry Cheung
"""


import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import os
import math
import pandas as pd

_path = r"D:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.28.29910\bin\Hostx64\x64"

if os.system("cl.exe"):
   os.environ['PATH'] += ';' + _path
if os.system("cl.exe"):
   raise RuntimeError("cl.exe still not found, path probably incorrect")

import numpy as np

TICKER_BLOCK_SIZE = 32*32

# def CUDABoxBreakoutPatternIndicator(IndicatorLabel, close_price_matrix, volume_matrix, BoxPeriod, BreakoutPeriod, BoxHeightRatio, BreakoutGainRatio, VolumeRatio):

close_price_matrix = np.random.randn(100, 60)
volume_matrix = np.random.randn(100, 60)
BoxPeriod = 30
BreakoutPeriod = 1
BoxHeightRatio = 0.1
BreakoutGainRatio = 0.1
VolumeRatio = 2


ticker_size = len(close_price_matrix)
time_size = len(close_price_matrix[0])
ticker_block_count = math.ceil(ticker_size/TICKER_BLOCK_SIZE)

a1 = close_price_matrix
a2 = volume_matrix
b = np.zeros((ticker_size, time_size))


# pending_zeros = np.zeros((TICKER_BLOCK_SIZE*ticker_block_count - ticker_size, time_size))
# a1 = np.concatenate((close_price_matrix, pending_zeros))
# a2 = np.concatenate((volume_matrix, pending_zeros))
# b = np.zeros((TICKER_BLOCK_SIZE*ticker_block_count,time_size))

# print("b is")
# print(b)

a1 = a1.astype(np.float32)
a2 = a2.astype(np.float32)
b = b.astype(np.float32)

a1_gpu = cuda.mem_alloc(a1.nbytes)
cuda.memcpy_htod(a1_gpu, a1)
a2_gpu = cuda.mem_alloc(a2.nbytes)
cuda.memcpy_htod(a2_gpu, a2)

b_gpu = cuda.mem_alloc(b.nbytes)
cuda.memcpy_htod(b_gpu, b)

mod = SourceModule("""
  __global__ void get_indicator(int time_size, int ticker_block_size, int ticker_block_count, int ticker_size, float *close_price_matrix, float *volume_matrix, float *indicator_matrix, int BoxPeriod, int BreakoutPeriod, float BoxHeightRatio, float BreakoutGainRatio, float VolumeRatio)
  {
  
    float price_high, price_low, avg_volume, break_out_period_avg_volume;
    
        for (int k = 0; k < ticker_block_count; k++) {
          if (k * ticker_block_size + threadIdx.y < ticker_size) {
            for (int i = BoxPeriod + BreakoutPeriod - 1; i < time_size; i++) {
              price_high = close_price_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + i-BoxPeriod - BreakoutPeriod+1];
              price_low = close_price_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + i-BoxPeriod - BreakoutPeriod+1];
              avg_volume = volume_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + i-BoxPeriod - BreakoutPeriod+1];

              for (int j = i-BoxPeriod - BreakoutPeriod+2; j < i - BreakoutPeriod + 1; j++) {
                if (price_high < close_price_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + j]) {
                  price_high = close_price_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + j];
                }
                if (price_low > close_price_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + j]) {
                  price_low = close_price_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + j];
                }
                avg_volume = avg_volume + volume_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + j];
              }
              
              avg_volume = avg_volume / BoxPeriod;
              break_out_period_avg_volume = volume_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + i - BreakoutPeriod+1];
              
              for (int j=i - BreakoutPeriod+2; j < i + 1; j++) {
                break_out_period_avg_volume = break_out_period_avg_volume + volume_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + j];
              }

              break_out_period_avg_volume = break_out_period_avg_volume/BreakoutPeriod;
              if ((price_high - price_low)/price_high < BoxHeightRatio && break_out_period_avg_volume/avg_volume > VolumeRatio) {
                if ((close_price_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + i] - price_high)/price_high > BreakoutGainRatio) {
                   indicator_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + i] = 1;
                }
                if ((price_low - close_price_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + i])/price_low > BreakoutGainRatio) {
                   indicator_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + i] = -1;
                }
              }
          
          
          
            }
          
          }
        }
    
  }
  """)
      
func = mod.get_function("get_indicator")
func(np.int32(time_size), np.int32(TICKER_BLOCK_SIZE), np.int32(ticker_block_count), np.int32(ticker_size), a1_gpu, a2_gpu, b_gpu,np.int32(BoxPeriod), np.int32(BreakoutPeriod), np.float32(BoxHeightRatio), np.float32(BreakoutGainRatio), np.float32(VolumeRatio), block=(1,TICKER_BLOCK_SIZE,1))

indicator_matrix = np.empty_like(b)
cuda.memcpy_dtoh(indicator_matrix, b_gpu)

print('indicator_matrix is')
print(indicator_matrix)

# return {IndicatorLabel:indicator_matrix}
