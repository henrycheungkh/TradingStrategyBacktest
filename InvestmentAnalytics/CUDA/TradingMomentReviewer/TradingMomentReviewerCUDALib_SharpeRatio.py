# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 16:14:22 2021

@author: Henry Cheung
"""

from datetime import date, datetime, timedelta
import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import math
import pandas as pd

import InvestmentAnalytics.Config as Config
import InvestmentAnalytics.CUDA.CUDAPathSetting
import numpy as np
    
def CUDATradingMomentReviewerSharpeRatio(sharpe_threshold, return_threshold, obs_period, moment_period, after_moment_period, close_price_matrix, time_std_unit_matrix, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = 50000000):
    GPU_CORE_TOTAL_THREAD_SIZE = Config.CONFIG_CUDA_ThreadCount
    GPU_CORE_BLOCK_SIZE = min(1024,GPU_CORE_TOTAL_THREAD_SIZE)
    GPU_CORE_GRID_SIZE = math.ceil(GPU_CORE_TOTAL_THREAD_SIZE / 1024)
    print('GPU_CORE_TOTAL_THREAD_SIZE is ' + str(GPU_CORE_TOTAL_THREAD_SIZE) + ', GPU_CORE_BLOCK_SIZE is ' + str(GPU_CORE_BLOCK_SIZE) + ', GPU_CORE_GRID_SIZE is ' + str(GPU_CORE_GRID_SIZE))

    print('Start of CUDATradingMomentReviewerSharpeRatio')
    print('sharpe_threshold is ' + str(sharpe_threshold) + ', return_threshold is ' + str(return_threshold) + ', obs_period is ' + str(obs_period) + ', moment_period is ' + str(moment_period) + ', after_moment_period is ' + str(after_moment_period))

    TRADE_RESULT_COLUMNS = ['ticker id', 'obs start time id']
    TRADE_RESULT_COLUMN_COUNT = len(TRADE_RESULT_COLUMNS)

    # print('len(close_price_matrix) is ' + str(len(close_price_matrix)))
    ticker_count = len(close_price_matrix)

    if block_cutting_dimension == "Time Dimension":
        close_price_matrix = close_price_matrix.T.copy(order="C")
        time_std_unit_matrix = time_std_unit_matrix.T.copy(order="C")
    # print('close_price_matrix is with dimension ' + str(len(close_price_matrix)) + ' x ' + str(len(close_price_matrix[0])))
    time_dimension_size = len(close_price_matrix)
    ticker_dimension_size = len(close_price_matrix[0])
    print('time_dimension_size = ' + str(time_dimension_size) + ' and ticker_dimension_size = ' + str(ticker_dimension_size))

    print('InitialResultCacheSize is ' +  f"{InitialResultCacheSize:,}")
    trade_result_count = np.zeros(1, dtype=np.int32)

    trade_record_out = np.zeros((InitialResultCacheSize, TRADE_RESULT_COLUMN_COUNT)).astype(np.float32) 
    print('TRADE_RESULT_COLUMN_COUNT is ' + str(TRADE_RESULT_COLUMN_COUNT) + ' at ' + str(datetime.now()))

    
    close_price_matrix = close_price_matrix.astype(np.float32)
    time_std_unit_matrix = time_std_unit_matrix.astype(np.float32)

    close_price_matrix_gpu = cuda.mem_alloc(close_price_matrix.nbytes)
    time_std_unit_matrix_gpu = cuda.mem_alloc(time_std_unit_matrix.nbytes)
    trade_record_out_gpu = cuda.mem_alloc(trade_record_out.nbytes)
    trade_result_count_gpu = cuda.mem_alloc(trade_result_count.nbytes)
    
    cuda.memcpy_htod(close_price_matrix_gpu, close_price_matrix)
    cuda.memcpy_htod(time_std_unit_matrix_gpu, time_std_unit_matrix)
    cuda.memcpy_htod(trade_record_out_gpu, trade_record_out)
    cuda.memcpy_htod(trade_result_count_gpu, trade_result_count)
    
    
    mod = SourceModule("""
      #include <cstdlib>
      #include <cmath>  

      __device__ int add_moment(unsigned long long *trade_result_count, int TRADE_RESULT_COLUMN_COUNT, float *trade_result, int ticker_id, int time_id)
      {
        int trade_result_index, trade_result_index_offset;
                        trade_result_index = atomicAdd(trade_result_count,1);
                        trade_result_index_offset = trade_result_index * TRADE_RESULT_COLUMN_COUNT ;
                        trade_result[trade_result_index_offset + 0] = ticker_id;
                        trade_result[trade_result_index_offset + 1] = time_id;
                    return 0;
      }

      __device__ float get_mean_in_obs_period( int start_time_id, int end_time_id, int ticker_size, int ticker_id, float *close_data)
      {
        float mean_in_obs_period;
        mean_in_obs_period = 0;
        for (int obs_time_id = start_time_id + 1; obs_time_id <= end_time_id; obs_time_id++) {
          mean_in_obs_period = mean_in_obs_period + (close_data[obs_time_id * ticker_size + ticker_id] - close_data[(obs_time_id - 1) * ticker_size + ticker_id]) / close_data[(obs_time_id - 1) * ticker_size + ticker_id];
        }
        return mean_in_obs_period / (end_time_id - start_time_id);
      }

      __device__ float get_stdev_in_obs_period( int start_time_id, int end_time_id, int ticker_size, int ticker_id, float *close_data, float mean_in_obs_period)
      {
        float stdev_in_obs_period;
        stdev_in_obs_period = 0;
        for (int obs_time_id = start_time_id + 1; obs_time_id <= end_time_id; obs_time_id++) {
          stdev_in_obs_period = stdev_in_obs_period + pow( (close_data[obs_time_id * ticker_size + ticker_id] - close_data[(obs_time_id - 1) * ticker_size + ticker_id]) / close_data[(obs_time_id - 1) * ticker_size + ticker_id] - mean_in_obs_period, 2);
        }
        return pow(stdev_in_obs_period / (end_time_id - start_time_id), 0.5);
      }

      __device__ float get_sharpe_ratio( int start_time_id, int end_time_id, int ticker_size, int ticker_id, float *close_data, float min_mean_in_obs_period)
      {
        float mean_in_obs_period, stdev_in_obs_period;
        mean_in_obs_period = get_mean_in_obs_period(start_time_id, end_time_id, ticker_size, ticker_id, close_data);

        if (abs(mean_in_obs_period) < min_mean_in_obs_period) {
          return 0;
        }
        stdev_in_obs_period = get_stdev_in_obs_period( start_time_id, end_time_id, ticker_size, ticker_id, close_data, mean_in_obs_period);
        if (mean_in_obs_period == 0) {
          return 0;
        } else {
          return mean_in_obs_period / (stdev_in_obs_period + 0.00000001);
        }
      }

     __global__ void get_trading_moment_sharpe_ratio(int ticker_dimension_size, int time_dimension_size, float sharpe_threshold, float return_threshold, int obs_period, int moment_period, int after_moment_period, int TRADE_RESULT_COLUMN_COUNT, unsigned long long *trade_result_count, float *trade_result,  float *close_data, float *time_std_unit_matrix)
      {
        int time_Index;
        float obs_time_length_in_std_unit, sharpe_ratio;

//        add_moment(trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, -100, 0);
        
        time_Index = blockIdx.x * blockDim.x + threadIdx.x;
        while (time_Index + obs_period + moment_period + after_moment_period < time_dimension_size) {
                
               obs_time_length_in_std_unit = time_std_unit_matrix[time_Index + obs_period + moment_period] - time_std_unit_matrix[time_Index + obs_period];
               if (obs_time_length_in_std_unit <= moment_period) {
                   for (int ticker_id = 0; ticker_id < ticker_dimension_size; ticker_id++) {
                       sharpe_ratio = get_sharpe_ratio( time_Index + obs_period, time_Index + obs_period + moment_period, ticker_dimension_size, ticker_id, close_data, return_threshold/moment_period);
                       if (abs(sharpe_ratio) > sharpe_threshold) {
                             add_moment(trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, ticker_id, time_Index);
                       }
                   }
               }
               time_Index = time_Index + (blockDim.x * gridDim.x);
        }
      }
      """)

    func = mod.get_function("get_trading_moment_sharpe_ratio")
    func(np.int32(ticker_dimension_size), np.int32(time_dimension_size), np.float32(sharpe_threshold), np.float32(return_threshold), np.int32(obs_period), np.int32(moment_period), np.int32(after_moment_period), np.int32(TRADE_RESULT_COLUMN_COUNT), trade_result_count_gpu, trade_record_out_gpu, close_price_matrix_gpu, time_std_unit_matrix_gpu, block=(GPU_CORE_BLOCK_SIZE,1,1), grid=(GPU_CORE_GRID_SIZE, 1))

    trade_result_count_out = np.empty_like(trade_result_count)
    cuda.memcpy_dtoh(trade_result_count_out, trade_result_count_gpu)
    print('trade result count is ' + str(trade_result_count_out))

    trade_record = np.empty_like(trade_record_out)
    cuda.memcpy_dtoh(trade_record, trade_record_out_gpu)
    trade_record = trade_record[0:trade_result_count_out[0]]

    df = pd.DataFrame(data=trade_record, columns=TRADE_RESULT_COLUMNS)
    # print(df)
    
    close_price_matrix_gpu.free()
    time_std_unit_matrix_gpu.free()
    trade_record_out_gpu.free()
    trade_result_count_gpu.free()

    return df