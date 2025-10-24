# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 09:51:03 2021

@author: Henry Cheung
"""

import os

# _path = r"D:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.28.29910\bin\Hostx64\x64"
_path = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.33.31629\bin\Hostx64\x64"
# _path = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.33.31629\bin\Hostx64"
# _path = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.33.31629\bin\Hostx64\x64\"

if os.system("cl.exe"):
    os.environ['PATH'] += ';' + _path
if os.system("cl.exe"):
    raise RuntimeError("cl.exe still not found, path probably incorrect")

import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import pandas as pd
import numpy as np

# TRADE_RESULT_COLUMN_COUNT = 15
TRADE_RESULT_COLUMN_COUNT = 4

# InitialResultCacheSize = 10000
InitialResultCacheSize = 5000
# InitialResultCacheSize = 250000000


close_price_matrix = np.zeros((1184240, 1))
date_id_matrix = np.zeros(1184240)
time_std_unit_matrix = np.zeros(1184240)
ObsPeriodMovementThreshold_matrix = np.asarray([0.005, 0.01]).astype(np.float32)
trade_result = np.zeros((InitialResultCacheSize, TRADE_RESULT_COLUMN_COUNT)).astype(np.float32) 


close_price_matrix_gpu = cuda.mem_alloc(close_price_matrix.nbytes)
date_id_matrix_gpu = cuda.mem_alloc(date_id_matrix.nbytes)
# trade_result_count_gpu = cuda.mem_alloc(trade_result_count.nbytes)
ObsPeriodMovementThreshold_matrix_gpu = cuda.mem_alloc(ObsPeriodMovementThreshold_matrix.nbytes)
time_std_unit_matrix_gpu = cuda.mem_alloc(time_std_unit_matrix.nbytes)
trade_result_gpu = cuda.mem_alloc(trade_result.nbytes)

cuda.memcpy_htod(close_price_matrix_gpu, close_price_matrix)
cuda.memcpy_htod(date_id_matrix_gpu, date_id_matrix)
# cuda.memcpy_htod(trade_result_count_gpu, trade_result_count)
cuda.memcpy_htod(ObsPeriodMovementThreshold_matrix_gpu, ObsPeriodMovementThreshold_matrix)
cuda.memcpy_htod(time_std_unit_matrix_gpu, time_std_unit_matrix)


# number_matrix = np.zeros(InitialResultCacheSize * RESULT_COLUMN_COUNT)
# number_matrix = number_matrix.astype(np.float32)

# number_matrix_gpu = cuda.mem_alloc(number_matrix.nbytes)
# cuda.memcpy_htod(number_matrix_gpu, number_matrix)

trade_result_count = np.int32(0)
trade_result_count_gpu = cuda.mem_alloc(trade_result_count.nbytes)
cuda.memcpy_htod(trade_result_count_gpu, trade_result_count)

AdditionalResultCount = np.int32(0)
AdditionalResultCount_gpu = cuda.mem_alloc(AdditionalResultCount.nbytes)

cuda.memcpy_htod(AdditionalResultCount_gpu, AdditionalResultCount)

mod = SourceModule("""
  #include <cstdlib>

  __global__ void correlation_on_specific_time_section_analysis(int *AdditionalResultCount, int block_cutting_by_time, int second_dimension_size, int GPU_CORE_BLOCK_SIZE_X, int GPU_CORE_BLOCK_SIZE_Y, int GPU_CORE_BLOCK_SIZE_Z, int gpu_core_block_count, int first_dimension_size, int StartTimeInStdUnit, int EndTimeInStdUnit, int TimeIntervalInStdUnit, int obs_movement_threshold_count, float obs_movement_range, float stop_loss, float take_profit, int obs_date_id_offset, int trade_entry_date_id_offset, int ErrorCode, int InitialResultCacheSize, int TRADE_RESULT_COLUMN_COUNT, int *trade_result_count, float *close_data, float *date_id_data, float *time_std_unit_data, float *obs_movement_threshold, float *trade_result)
  {
    ErrorCode = 0;
    int thread_Index, first_time_in_std_unit, first_date_id, second_date_id, second_time_in_std_unit, third_date_id, third_time_in_std_unit, trade_result_index, trade_result_index_offset, first_time_id, position_flag, first_time_id_offset, second_time_id_offset, third_time_id_offset, stop_time_id, temp_AdditionalResultCount;
    float first_time_close_price, second_time_close_price, third_time_close_price, abs_obs_time_price_movement;
    for (int i=0; i<2; i++) {
      trade_result_index = atomicAdd(trade_result_count,1);
      trade_result_index_offset = trade_result_index * TRADE_RESULT_COLUMN_COUNT;
      trade_result[trade_result_index_offset + 0] = trade_result_index;
      trade_result[trade_result_index_offset + 1] = trade_result_index;
      trade_result[trade_result_index_offset + 2] = 0;
      trade_result[trade_result_index_offset + 3] = 4;
    }
  }
  """)
      
func = mod.get_function("correlation_on_specific_time_section_analysis")
# func(AdditionalResultCount_gpu, np.int32(block_cutting_by_time), np.int32(second_dimension_size), np.int32(GPU_CORE_BLOCK_SIZE_X), np.int32(GPU_CORE_BLOCK_SIZE_Y), np.int32(GPU_CORE_BLOCK_SIZE_Z), np.int32(gpu_core_block_count), np.int32(first_dimension_size), np.int32(StartTimeInStdUnit), np.int32(EndTimeInStdUnit), np.int32(TimeIntervalInStdUnit), np.int32(ObsPeriodMovementThreshold_size), np.float32(ObsPeriodMovementRange), np.float32(StopLossPerTrade), np.float32(TakeProfitPerTrade), np.int32(ObsDateIDOffset), np.int32(TradeEntryDateIDOffset), np.int32(ErrorCode), np.int32(InitialResultCacheSize), np.int32(TRADE_RESULT_COLUMN_COUNT), trade_result_count_gpu, close_price_matrix_gpu, date_id_matrix_gpu, time_std_unit_matrix_gpu, ObsPeriodMovementThreshold_matrix_gpu, trade_result_gpu, block=(4,16,16))
func(AdditionalResultCount_gpu, np.int32(0), np.int32(0), np.int32(0), np.int32(0), np.int32(0), np.int32(0), np.int32(0), np.int32(0), np.int32(0), np.int32(0), np.int32(0), np.float32(0), np.float32(0), np.float32(0), np.int32(0), np.int32(0), np.int32(0), np.int32(0), np.int32(0), trade_result_count_gpu, close_price_matrix_gpu, date_id_matrix_gpu, time_std_unit_matrix_gpu, ObsPeriodMovementThreshold_matrix_gpu, trade_result_gpu, block=(4,16,16))

AdditionalResultCount_out = np.empty_like(AdditionalResultCount)
cuda.memcpy_dtoh(AdditionalResultCount_out, AdditionalResultCount_gpu)

print('AdditionalResultCount_out is ' + str(AdditionalResultCount_out))

trade_result_count_out = np.empty_like(trade_result_count)
cuda.memcpy_dtoh(trade_result_count_out, trade_result_count_gpu)

print('trade_result_count_out is ' + str(trade_result_count_out))

trade_record = np.empty((InitialResultCacheSize, TRADE_RESULT_COLUMN_COUNT), dtype=np.float32)
cuda.memcpy_dtoh(trade_record, trade_result_gpu)

print('trade_record is with dimension ' + str(len(trade_record)) + ' x ' + str(len(trade_record[0])))
print(trade_record)

# mod = SourceModule("""
#   #include <cstdlib>

#     __global__ void test_cuda_utilisation(int InitialResultCacheSize, int RESULT_COLUMN_COUNT, int *AdditionalResultCount, float *number_matrix, int *result_count)
#   {
#      int result_index, result_index_offset, ii;

#     for (int i=0; i<10; i++) {
#      result_index = atomicAdd(result_count,1);
# //     if (result_index < InitialResultCacheSize + 1) {
#        ii = atomicAdd(AdditionalResultCount,1);
#        result_index_offset = result_index * RESULT_COLUMN_COUNT;
#        number_matrix[result_index_offset + 0] = result_index;
# //       number_matrix[result_index_offset + 1] = result_count[0];
#        number_matrix[result_index_offset + 1] = ii;
#        number_matrix[result_index_offset + 2] = InitialResultCacheSize;
#        number_matrix[result_index_offset + 3] = RESULT_COLUMN_COUNT;
       
# //       AdditionalResultCount++;

# //     }
#      }
#   }
#   """)
      
# func = mod.get_function("test_cuda_utilisation")
# func(np.int32(InitialResultCacheSize), np.int32(RESULT_COLUMN_COUNT), AdditionalResultCount_gpu, number_matrix_gpu, result_count_gpu, block=(4,16,16))

# AdditionalResultCount_out = np.empty_like(AdditionalResultCount)
# cuda.memcpy_dtoh(AdditionalResultCount_out, AdditionalResultCount_gpu)

# result_count_out = np.empty_like(result_count)
# cuda.memcpy_dtoh(result_count_out, result_count_gpu)


# print('result_count_out = ' + str(result_count_out) + ' and InitialResultCacheSize = ' + str(InitialResultCacheSize) + ' and AdditionalResultCount = ' + str(AdditionalResultCount_out))

# number_matrix_out = np.empty((AdditionalResultCount_out, RESULT_COLUMN_COUNT), dtype=np.float32)
# # number_matrix_out = np.empty((InitialResultCacheSize, RESULT_COLUMN_COUNT), dtype=np.float32)
# # number_matrix_out = np.empty((result_count_out, RESULT_COLUMN_COUNT), dtype=np.float32)
# cuda.memcpy_dtoh(number_matrix_out, number_matrix_gpu)

# print('number_matrix_out is with len ' + str(len(number_matrix_out)) + ' x ' + str(len(number_matrix_out[0])))
# print(number_matrix_out)

