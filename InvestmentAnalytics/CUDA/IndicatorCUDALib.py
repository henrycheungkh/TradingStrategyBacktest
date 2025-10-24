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
GPU_CORE_BLOCK_SIZE = 32*32

def CUDASimpleMovingAverageIndicator(IndicatorLabel, close_price_matrix, MA_Day):
    ticker_size = len(close_price_matrix)
    time_size = len(close_price_matrix[0])
    ticker_block_count = math.ceil(ticker_size/TICKER_BLOCK_SIZE)

    a1 = close_price_matrix
    b = np.zeros((ticker_size, time_size))

    a1 = a1.astype(np.float32)
    b = b.astype(np.float32)
    
    a1_gpu = cuda.mem_alloc(a1.nbytes)
    cuda.memcpy_htod(a1_gpu, a1)
    
    b_gpu = cuda.mem_alloc(b.nbytes)
    cuda.memcpy_htod(b_gpu, b)

    mod = SourceModule("""
  __global__ void get_indicator(int time_size, int ticker_block_size, int ticker_block_count, int ticker_size, float *a, float *b, int MA_day)
  {

    for (int k = 0; k < ticker_block_count; k++) {
      if (k * ticker_block_size + threadIdx.y < ticker_size) {
        for (int i = MA_day-1; i < time_size; i++) {
          for (int j = i-MA_day+1; j < i + 1; j++) {
            b[k * ticker_block_size * time_size + threadIdx.y*time_size + i] = b[k * ticker_block_size * time_size + threadIdx.y*time_size + i] + a[k * ticker_block_size * time_size + threadIdx.y*time_size + j];
          }
        }

        for (int i = MA_day-1; i < time_size; i++) {
          b[k * ticker_block_size * time_size + threadIdx.y*time_size + i] = b[k * ticker_block_size * time_size + threadIdx.y*time_size + i] / MA_day;
        }
      }
    }
  }
  """)
          
    func = mod.get_function("get_indicator")
    func(np.int32(time_size), np.int32(TICKER_BLOCK_SIZE), np.int32(ticker_block_count), np.int32(ticker_size), a1_gpu, b_gpu, np.int32(MA_Day), block=(1,TICKER_BLOCK_SIZE,1))

    indicator_matrix = np.empty_like(b)
    cuda.memcpy_dtoh(indicator_matrix, b_gpu)
    
    return {IndicatorLabel:indicator_matrix}

def CUDABoxBreakoutPatternIndicator(IndicatorLabel, close_price_matrix, volume_matrix, BoxPeriod, BreakoutPeriod, BoxHeightRatio, BreakoutGainRatio, VolumeRatio, HighPrice = None, LowPrice = None):
    if HighPrice is None:
        return CUDABoxBreakoutPatternAdjCloseIndicator(IndicatorLabel, close_price_matrix, volume_matrix, BoxPeriod, BreakoutPeriod, BoxHeightRatio, BreakoutGainRatio, VolumeRatio)
    else:
        return CUDABoxBreakoutPatternAdjHighLowIndicator(IndicatorLabel, close_price_matrix, volume_matrix, BoxPeriod, BreakoutPeriod, BoxHeightRatio, BreakoutGainRatio, VolumeRatio, HighPrice, LowPrice)


def CUDASingleCandleSpikePatternIndicator(IndicatorLabel, close_price_matrix, high_price_matrix, low_price_matrix, volume_matrix, time_std_unit_matrix, SpikeSizePercentageThreshold, block_cutting_dimension = "Ticker Dimension"):
    block_cutting_by_time = 0
    if block_cutting_dimension == "Time Dimension":
        close_price_matrix = close_price_matrix.T
        high_price_matrix = high_price_matrix.T
        low_price_matrix = low_price_matrix.T
        volume_matrix = volume_matrix.T
        time_std_unit_matrix = time_std_unit_matrix.T
        block_cutting_by_time = 1

    first_dimension_size = len(close_price_matrix)
    second_dimension_size = len(close_price_matrix[0])
    
    # print('dimension of close_price_matrix = ' + str(len(close_price_matrix)) + ' x '+ str(len(close_price_matrix[0])))
    # print('dimension of high_price_matrix = ' + str(len(high_price_matrix)) + ' x '+ str(len(high_price_matrix[0])))
    # print('dimension of low_price_matrix = ' + str(len(low_price_matrix)) + ' x '+ str(len(low_price_matrix[0])))
    # print('dimension of volume_matrix = ' + str(len(volume_matrix)) + ' x '+ str(len(volume_matrix[0])))
    # print('dimension of time_std_unit_matrix = ' + str(len(time_std_unit_matrix)) + ' x '+ str(len(time_std_unit_matrix[0])))
    # print('block_cutting_by_time = ' + str(block_cutting_by_time))

    gpu_core_block_count = math.ceil(first_dimension_size/GPU_CORE_BLOCK_SIZE)
    pending_zeros = np.zeros((GPU_CORE_BLOCK_SIZE*gpu_core_block_count - first_dimension_size, second_dimension_size))
    
    a = np.concatenate((close_price_matrix, pending_zeros))
    b = np.concatenate((high_price_matrix, pending_zeros))
    c = np.concatenate((low_price_matrix, pending_zeros))
    d = np.concatenate((volume_matrix, pending_zeros))
    e = np.concatenate((time_std_unit_matrix, pending_zeros))
    a_out = np.zeros((first_dimension_size, second_dimension_size))

    a = a.astype(np.float32)
    b = b.astype(np.float32)
    c = c.astype(np.float32)
    d = d.astype(np.float32)
    e = e.astype(np.float32)
    a_out = a_out.astype(np.float32)
    
    a_gpu = cuda.mem_alloc(a.nbytes)
    b_gpu = cuda.mem_alloc(b.nbytes)
    c_gpu = cuda.mem_alloc(c.nbytes)
    d_gpu = cuda.mem_alloc(d.nbytes)
    e_gpu = cuda.mem_alloc(e.nbytes)
    a_out_gpu = cuda.mem_alloc(a.nbytes)
    
    cuda.memcpy_htod(a_gpu, a)
    cuda.memcpy_htod(b_gpu, b)
    cuda.memcpy_htod(c_gpu, c)
    cuda.memcpy_htod(d_gpu, d)
    cuda.memcpy_htod(e_gpu, e)
    cuda.memcpy_htod(a_out_gpu, a_out)

    mod = SourceModule("""
      __global__ void get_indicator(int block_cutting_by_time, int second_dimension_size, int GPU_CORE_BLOCK_SIZE, int gpu_core_block_count, int first_dimension_size, float SpikeSizePercentageThreshold, float *close_data, float *high_data, float *low_data, float *vol_data, float *time_std_unit_data, float *indicator_matrix)
      {

        if (block_cutting_by_time == 1) {
          for (int k = 0; k < gpu_core_block_count; k++) {
            if (k * GPU_CORE_BLOCK_SIZE + threadIdx.y < first_dimension_size && k * GPU_CORE_BLOCK_SIZE + threadIdx.y > 0) {
              for (int i = 0; i < second_dimension_size; i++) {
              
                if (time_std_unit_data[k * GPU_CORE_BLOCK_SIZE * second_dimension_size + threadIdx.y*second_dimension_size + i] - time_std_unit_data[k * GPU_CORE_BLOCK_SIZE * second_dimension_size + (threadIdx.y-1)*second_dimension_size + i] == 1) {
              
                  if (high_data[k * GPU_CORE_BLOCK_SIZE * second_dimension_size + threadIdx.y*second_dimension_size + i] > close_data[k * GPU_CORE_BLOCK_SIZE * second_dimension_size + (threadIdx.y-1)*second_dimension_size + i] * (1+SpikeSizePercentageThreshold)) {
                    if (low_data[k * GPU_CORE_BLOCK_SIZE * second_dimension_size + threadIdx.y*second_dimension_size + i] < close_data[k * GPU_CORE_BLOCK_SIZE * second_dimension_size + (threadIdx.y-1)*second_dimension_size + i] * (1-SpikeSizePercentageThreshold)) {
                      indicator_matrix[k * GPU_CORE_BLOCK_SIZE * second_dimension_size + threadIdx.y*second_dimension_size + i] = 2;
                    } else {
                      indicator_matrix[k * GPU_CORE_BLOCK_SIZE * second_dimension_size + threadIdx.y*second_dimension_size + i] = -1;
                    }
                  } else {
                    if (low_data[k * GPU_CORE_BLOCK_SIZE * second_dimension_size + threadIdx.y*second_dimension_size + i] < close_data[k * GPU_CORE_BLOCK_SIZE * second_dimension_size + (threadIdx.y-1)*second_dimension_size + i] * (1-SpikeSizePercentageThreshold)) {
                      indicator_matrix[k * GPU_CORE_BLOCK_SIZE * second_dimension_size + threadIdx.y*second_dimension_size + i] = 1;
                    }
                  }
                }
                
              }
            }
          }
        } 
                  
      }
      """)

          
    func = mod.get_function("get_indicator")
    func(np.int32(block_cutting_by_time), np.int32(second_dimension_size), np.int32(GPU_CORE_BLOCK_SIZE), np.int32(gpu_core_block_count), np.int32(first_dimension_size), np.float32(SpikeSizePercentageThreshold), a_gpu, b_gpu, c_gpu, d_gpu, e_gpu, a_out_gpu, block=(1,GPU_CORE_BLOCK_SIZE,1))

    indicator_matrix = np.empty_like(a_out)
    cuda.memcpy_dtoh(indicator_matrix, a_out_gpu)
    if block_cutting_dimension == "Time Dimension":
        indicator_matrix = indicator_matrix.T
    
    return {IndicatorLabel:indicator_matrix}


def CUDABoxBreakoutPatternAdjCloseIndicator(IndicatorLabel, close_price_matrix, volume_matrix, BoxPeriod, BreakoutPeriod, BoxHeightRatio, BreakoutGainRatio, VolumeRatio):
    ticker_size = len(close_price_matrix)
    time_size = len(close_price_matrix[0])
    ticker_block_count = math.ceil(ticker_size/TICKER_BLOCK_SIZE)

    a1 = close_price_matrix
    a2 = volume_matrix
    b = np.zeros((ticker_size, time_size))

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
    
    return {IndicatorLabel:indicator_matrix}

def CUDABoxBreakoutPatternAdjHighLowIndicator(IndicatorLabel, close_price_matrix, volume_matrix, BoxPeriod, BreakoutPeriod, BoxHeightRatio, BreakoutGainRatio, VolumeRatio, HighPrice, LowPrice):
    ticker_size = len(close_price_matrix)
    time_size = len(close_price_matrix[0])
    ticker_block_count = math.ceil(ticker_size/TICKER_BLOCK_SIZE)

    a1 = close_price_matrix
    a2 = volume_matrix
    a_high = HighPrice
    a_low = LowPrice
    b = np.zeros((ticker_size, time_size))

    a1 = a1.astype(np.float32)
    a2 = a2.astype(np.float32)
    a_high = a_high.astype(np.float32)
    a_low = a_low.astype(np.float32)
    b = b.astype(np.float32)
    
    a1_gpu = cuda.mem_alloc(a1.nbytes)
    cuda.memcpy_htod(a1_gpu, a1)
    a2_gpu = cuda.mem_alloc(a2.nbytes)
    cuda.memcpy_htod(a2_gpu, a2)
    a_high_gpu = cuda.mem_alloc(a_high.nbytes)
    cuda.memcpy_htod(a_high_gpu, a_high)
    a_low_gpu = cuda.mem_alloc(a_low.nbytes)
    cuda.memcpy_htod(a_low_gpu, a_low)
    
    b_gpu = cuda.mem_alloc(b.nbytes)
    cuda.memcpy_htod(b_gpu, b)

    mod = SourceModule("""
      __global__ void get_indicator(int time_size, int ticker_block_size, int ticker_block_count, int ticker_size, float *close_price_matrix, float *high_price_matrix, float *low_price_matrix, float *volume_matrix, float *indicator_matrix, int BoxPeriod, int BreakoutPeriod, float BoxHeightRatio, float BreakoutGainRatio, float VolumeRatio)
      {
      
        float price_high, price_low, avg_volume, break_out_period_avg_volume;
        
        for (int k = 0; k < ticker_block_count; k++) {
          if (k * ticker_block_size + threadIdx.y < ticker_size) {
            for (int i = BoxPeriod + BreakoutPeriod - 1; i < time_size; i++) {
            
              price_high = high_price_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + i-BoxPeriod - BreakoutPeriod+1];
              price_low = low_price_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + i-BoxPeriod - BreakoutPeriod+1];
              avg_volume = volume_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + i-BoxPeriod - BreakoutPeriod+1];
              
              for (int j = i-BoxPeriod - BreakoutPeriod+2; j < i - BreakoutPeriod + 1; j++) {
                if (price_high < high_price_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + j]) {
                  price_high = high_price_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + j];
                }
                if (price_low > low_price_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + j]) {
                  price_low = low_price_matrix[k * ticker_block_size * time_size + threadIdx.y * time_size + j];
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
    func(np.int32(time_size), np.int32(TICKER_BLOCK_SIZE), np.int32(ticker_block_count), np.int32(ticker_size), a1_gpu, a_high_gpu, a_low_gpu, a2_gpu, b_gpu,np.int32(BoxPeriod), np.int32(BreakoutPeriod), np.float32(BoxHeightRatio), np.float32(BreakoutGainRatio), np.float32(VolumeRatio), block=(1,TICKER_BLOCK_SIZE,1))

    indicator_matrix = np.empty_like(b)
    cuda.memcpy_dtoh(indicator_matrix, b_gpu)
    
    return {IndicatorLabel:indicator_matrix}
