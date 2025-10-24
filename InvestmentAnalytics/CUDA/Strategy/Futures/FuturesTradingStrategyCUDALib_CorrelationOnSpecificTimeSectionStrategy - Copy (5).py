# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 15:37:06 2021

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


TOTAL_TIME_IN_STD_UNIT_PER_DAY = {"1 min":24*60, "10 secs":24*60*60}

import operator as op
from functools import reduce

def ncr(n, r):
    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    return numer // denom

def CUDACorrelationOnSpecificTimeSectionStrategy(close_price_matrix, date_id_matrix, time_std_unit_matrix, StartTimeInStdUnit, EndTimeInStdUnit, TimeIntervalInStdUnit, DateCount, ObsPeriodMovementThreshold = [0], ObsPeriodMovementRange = 0, ObsPeriodExponentialStep = 0, StopLossPerTrade = 0, TakeProfitPerTrade = 0, ObsDateIDOffset = 0, TradeEntryDateIDOffset = 0, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = None, TimeFrame = "1 min"):
    # print('GPU_CORE_BLOCK_SIZE = ' + str(GPU_CORE_BLOCK_SIZE))
    # if GPU_CORE_BLOCK_SIZE <= 16:
    #     GPU_CORE_BLOCK_SIZE_Z = GPU_CORE_BLOCK_SIZE
    #     GPU_CORE_BLOCK_SIZE_X = 1
    #     GPU_CORE_BLOCK_SIZE_Y = 1
    # else:
    #     GPU_CORE_BLOCK_SIZE_Z = 16
    #     GPU_CORE_BLOCK_SIZE_Y = int( GPU_CORE_BLOCK_SIZE / 16)
    #     GPU_CORE_BLOCK_SIZE_X = 1
    # if GPU_CORE_BLOCK_SIZE_Y > 8:
    #     GPU_CORE_BLOCK_SIZE_X = int( GPU_CORE_BLOCK_SIZE_Y / 8)
    #     GPU_CORE_BLOCK_SIZE_Y = 8
    # print('GPU_CORE_BLOCK_SIZE_X = ' + str(GPU_CORE_BLOCK_SIZE_X))
    # print('GPU_CORE_BLOCK_SIZE_Y = ' + str(GPU_CORE_BLOCK_SIZE_Y))
    # print('GPU_CORE_BLOCK_SIZE_Z = ' + str(GPU_CORE_BLOCK_SIZE_Z))

    GPU_CORE_TOTAL_THREAD_SIZE = Config.CONFIG_CUDA_ThreadCount
    GPU_CORE_BLOCK_SIZE = min(1024,GPU_CORE_TOTAL_THREAD_SIZE)
    GPU_CORE_GRID_SIZE = math.ceil(GPU_CORE_TOTAL_THREAD_SIZE / 1024)
    print('GPU_CORE_TOTAL_THREAD_SIZE is ' + str(GPU_CORE_TOTAL_THREAD_SIZE) + ', GPU_CORE_BLOCK_SIZE is ' + str(GPU_CORE_BLOCK_SIZE) + ', GPU_CORE_GRID_SIZE is' + str(GPU_CORE_GRID_SIZE))


    
    TRADE_RESULT_COLUMNS = ['long short flag', 'ticker id', 'obs time id', 'obs price', 'entry time id', 'entry price', 'exit time id', 'exit price', 'obs movement threshold', 'obs movement range', 'stop loss', 'take profit', 'obs date id offset', 'trade entry date id offset', 'stop time id']
    TRADE_RESULT_COLUMN_COUNT = len(TRADE_RESULT_COLUMNS)
    block_cutting_by_time = 0
    ErrorCode = 0
    ticker_count = len(close_price_matrix)

    if block_cutting_dimension == "Time Dimension":
        close_price_matrix = close_price_matrix.T.copy(order="C")
        date_id_matrix = date_id_matrix.T.copy(order="C")
        time_std_unit_matrix = time_std_unit_matrix.T.copy(order="C")
        block_cutting_by_time = 1

    ObsPeriodMovementThreshold_size = len(ObsPeriodMovementThreshold)
    
    if InitialResultCacheSize is None:

        InitialResultCacheSize = ncr(math.floor((EndTimeInStdUnit - StartTimeInStdUnit + (ObsDateIDOffset + TradeEntryDateIDOffset) * TOTAL_TIME_IN_STD_UNIT_PER_DAY[TimeFrame])/TimeIntervalInStdUnit) + 1, 3) * DateCount * ticker_count * ObsPeriodMovementThreshold_size

    print('InitialResultCacheSize is ' +  f"{InitialResultCacheSize:,}")
    print('TRADE_RESULT_COLUMN_COUNT is ' + str(TRADE_RESULT_COLUMN_COUNT) + ' at ' + str(datetime.now()))

    time_size = len(close_price_matrix)
    ticker_size = len(close_price_matrix[0])

#     gpu_core_block_count = math.ceil(time_size/GPU_CORE_BLOCK_SIZE)
    gpu_core_block_count = math.ceil(time_size/(GPU_CORE_BLOCK_SIZE * GPU_CORE_GRID_SIZE))

    trade_result = np.zeros((InitialResultCacheSize, TRADE_RESULT_COLUMN_COUNT)).astype(np.float32) 
    
    close_price_matrix = close_price_matrix.astype(np.float32)
    date_id_matrix = date_id_matrix.astype(np.float32)
    ObsPeriodMovementThreshold_matrix = np.asarray(ObsPeriodMovementThreshold).astype(np.float32)
    time_std_unit_matrix = time_std_unit_matrix.astype(np.float32)
    
    close_price_matrix_gpu = cuda.mem_alloc(close_price_matrix.nbytes)
    date_id_matrix_gpu = cuda.mem_alloc(date_id_matrix.nbytes)
    ObsPeriodMovementThreshold_matrix_gpu = cuda.mem_alloc(ObsPeriodMovementThreshold_matrix.nbytes)
    time_std_unit_matrix_gpu = cuda.mem_alloc(time_std_unit_matrix.nbytes)
    trade_result_gpu = cuda.mem_alloc(trade_result.nbytes)
    
    cuda.memcpy_htod(close_price_matrix_gpu, close_price_matrix)
    cuda.memcpy_htod(date_id_matrix_gpu, date_id_matrix)
    cuda.memcpy_htod(ObsPeriodMovementThreshold_matrix_gpu, ObsPeriodMovementThreshold_matrix)
    cuda.memcpy_htod(time_std_unit_matrix_gpu, time_std_unit_matrix)

    trade_result = None

    trade_result_count = np.zeros(1, dtype=np.int32)
    trade_result_count_gpu = cuda.mem_alloc(trade_result_count.nbytes)
    cuda.memcpy_htod(trade_result_count_gpu, trade_result_count)

    AdditionalResultCount = np.zeros(1, dtype=np.int32)
    AdditionalResultCount_gpu = cuda.mem_alloc(AdditionalResultCount.nbytes)
    cuda.memcpy_htod(AdditionalResultCount_gpu, AdditionalResultCount)

    mod = SourceModule("""
      #include <cstdlib>
    
       __device__ int add_trade(unsigned long long *AdditionalResultCount, unsigned long long *trade_result_count, int TRADE_RESULT_COLUMN_COUNT, float *trade_result, int long_short_flag, int ticker_id, int first_time_id, float first_time_close_price, int second_time_id, float second_time_close_price, int third_time_id, float third_time_close_price, float obs_movement_threshold, float obs_movement_range, float stop_loss, float take_profit, int obs_date_id_offset, int trade_entry_date_id_offset, int stop_time_id)
//       __device__ int add_trade(unsigned long long *AdditionalResultCount, int *trade_result_count, int TRADE_RESULT_COLUMN_COUNT, float *trade_result)
//       __device__ int add_trade(unsigned long long *AdditionalResultCount, int *trade_result_count)
//       __device__ int add_trade(unsigned long long *AdditionalResultCount, unsigned long long *trade_result_count)
//       __device__ int add_trade(unsigned long long *AdditionalResultCount)
//       __device__ int add_trade()
        {
          int trade_result_index, trade_result_index_offset, temp_AdditionalResultCount;

          trade_result_index = atomicAdd(trade_result_count,1);
          trade_result_index_offset = trade_result_index * TRADE_RESULT_COLUMN_COUNT ;

          trade_result[trade_result_index_offset + 0] = long_short_flag;
          trade_result[trade_result_index_offset + 1] = ticker_id;
          trade_result[trade_result_index_offset + 2] = first_time_id;
          trade_result[trade_result_index_offset + 3] = first_time_close_price;
          trade_result[trade_result_index_offset + 4] = second_time_id;
          trade_result[trade_result_index_offset + 5] = second_time_close_price;
          trade_result[trade_result_index_offset + 6] = third_time_id;
          trade_result[trade_result_index_offset + 7] = third_time_close_price;
          trade_result[trade_result_index_offset + 8] = obs_movement_threshold;
                                
          trade_result[trade_result_index_offset + 9] = obs_movement_range;
                                
          trade_result[trade_result_index_offset + 10] = stop_loss;
          trade_result[trade_result_index_offset + 11] = take_profit;
          trade_result[trade_result_index_offset + 12] = obs_date_id_offset;
          trade_result[trade_result_index_offset + 13] = trade_entry_date_id_offset;
          trade_result[trade_result_index_offset + 14] = stop_time_id;

         temp_AdditionalResultCount = atomicAdd(AdditionalResultCount,1);
          
          return 0;
        }

      __global__ void correlation_on_specific_time_section_analysis(unsigned long long *AdditionalResultCount, int ticker_size, int gpu_core_block_count, int time_size, int StartTimeInStdUnit, int EndTimeInStdUnit, int TimeIntervalInStdUnit, int obs_movement_threshold_count, float obs_movement_range, float ObsPeriodExponentialStep, float stop_loss, float take_profit, int obs_date_id_offset, int trade_entry_date_id_offset, int ErrorCode, int InitialResultCacheSize, int TRADE_RESULT_COLUMN_COUNT, unsigned long long *trade_result_count, float *close_data, float *date_id_data, float *time_std_unit_data, float *obs_movement_threshold, float *trade_result)
      {
      }

        
        __global__ void correlation_on_specific_time_section_analysis_linear(unsigned long long *AdditionalResultCount, int ticker_size, int gpu_core_block_count, int time_size, int StartTimeInStdUnit, int EndTimeInStdUnit, int TimeIntervalInStdUnit, int obs_movement_threshold_count, float obs_movement_range, float stop_loss, float take_profit, int obs_date_id_offset, int trade_entry_date_id_offset, int ErrorCode, int InitialResultCacheSize, int TRADE_RESULT_COLUMN_COUNT, unsigned long long *trade_result_count, float *close_data, float *date_id_data, float *time_std_unit_data, float *obs_movement_threshold, float *trade_result)
      {
        ErrorCode = 0;
        int thread_Index, first_time_in_std_unit, first_date_id, second_date_id, second_time_in_std_unit, third_date_id, third_time_in_std_unit, first_time_id, position_flag, first_time_id_offset, second_time_id_offset, third_time_id_offset, stop_time_id, temp_AdditionalResultCount;
        float first_time_close_price, second_time_close_price, third_time_close_price, abs_obs_time_price_movement;
        unsigned long long trade_result_index, trade_result_index_offset;

        thread_Index = blockIdx.x * blockDim.x + threadIdx.x;

          for (int k = 0; k < gpu_core_block_count; k++) {
            first_time_id = k * blockDim.x * gridDim.x + thread_Index;
            first_time_id_offset = first_time_id * ticker_size;
            if (first_time_id < time_size && first_time_id > 0) {
            
              for (int obs_movement_threshold_index = 0; obs_movement_threshold_index < obs_movement_threshold_count; obs_movement_threshold_index++ ) {
            
                for (int ticker_id = 0; ticker_id < ticker_size; ticker_id++) {
                  first_time_in_std_unit = time_std_unit_data[first_time_id];
                  if (first_time_in_std_unit >= StartTimeInStdUnit && first_time_in_std_unit <= EndTimeInStdUnit && (first_time_in_std_unit - StartTimeInStdUnit) % TimeIntervalInStdUnit == 0) {
                    first_time_close_price = close_data[first_time_id_offset + ticker_id];
                    first_date_id = date_id_data[first_time_id];
                    for (int second_time_id = first_time_id + 1; second_time_id < time_size; second_time_id++) {
                      second_time_id_offset = second_time_id * ticker_size;
                      second_date_id = date_id_data[second_time_id];
                      if (second_date_id > first_date_id + obs_date_id_offset) {
                        break;
                      }
                      second_time_in_std_unit = time_std_unit_data[second_time_id];
                      if (second_date_id == first_date_id + obs_date_id_offset && (second_time_in_std_unit > first_time_in_std_unit || obs_date_id_offset > 0) && second_time_in_std_unit <= EndTimeInStdUnit && (second_time_in_std_unit - StartTimeInStdUnit) % TimeIntervalInStdUnit == 0) {
                        second_time_close_price = close_data[second_time_id_offset + ticker_id];
                        for (int third_time_id = second_time_id + 1; third_time_id < time_size; third_time_id++) {
                          third_time_id_offset = third_time_id * ticker_size;
                          third_date_id = date_id_data[third_time_id];
                          if (third_date_id > second_date_id + trade_entry_date_id_offset) {
                            break;
                          } else {
                            third_time_in_std_unit = time_std_unit_data[third_time_id];
                            if (third_date_id == second_date_id + trade_entry_date_id_offset && (third_time_in_std_unit > second_time_in_std_unit || trade_entry_date_id_offset > 0) && third_time_in_std_unit <= EndTimeInStdUnit && (third_time_in_std_unit - StartTimeInStdUnit) % TimeIntervalInStdUnit == 0) {
                              abs_obs_time_price_movement = abs(second_time_close_price - first_time_close_price) / first_time_close_price;
                              if( abs_obs_time_price_movement >= obs_movement_threshold[obs_movement_threshold_index] && (obs_movement_range == 0 || abs_obs_time_price_movement <= obs_movement_threshold[obs_movement_threshold_index] + obs_movement_range)) {
                                if (second_time_close_price > first_time_close_price) {
                                  position_flag = 1;
                                } else if (second_time_close_price < first_time_close_price) {
                                  position_flag = -1;
                                } else {
                                  position_flag = 0;
                                }
                              } else {
                                  position_flag = 0;
                              }
                              if (position_flag != 0) {
                                third_time_close_price = 0;
                                if((stop_loss != 0) || (take_profit != 0)) {
                                  for (int path_scan_time_id = second_time_id + 1; path_scan_time_id < third_time_id; path_scan_time_id++) {
                                    if (((position_flag > 0) && (((stop_loss != 0) && (close_data[path_scan_time_id * ticker_size + ticker_id] <= (close_data[second_time_id_offset + ticker_id] * (1 - stop_loss)))) || ((take_profit != 0) && (close_data[path_scan_time_id * ticker_size + ticker_id] >= (close_data[second_time_id_offset + ticker_id] * (1 + take_profit)))))) || ((position_flag < 0) && (((stop_loss != 0) && (close_data[path_scan_time_id * ticker_size + ticker_id] >= (close_data[second_time_id_offset + ticker_id] * (1 + stop_loss)))) || ((take_profit != 0) && (close_data[path_scan_time_id * ticker_size + ticker_id] <= (close_data[second_time_id_offset + ticker_id] * (1 - take_profit))))))) {
                                      stop_time_id = path_scan_time_id;
                                      third_time_close_price = close_data[path_scan_time_id * ticker_size + ticker_id];
                                      break;
                                    }
                                  }
                                } 
                                if (third_time_close_price == 0) {
                                  third_time_close_price = close_data[third_time_id_offset + ticker_id];
                                  stop_time_id = third_time_id;
                                }                

//       __device__ int add_trade(unsigned long long *AdditionalResultCount, int *trade_result_count, int TRADE_RESULT_COLUMN_COUNT, float *trade_result, int long_short_flag, int ticker_id, int first_time_id, float first_time_close_price, int second_time_id, float second_time_close_price, int third_time_id, float third_time_close_price, float obs_movement_threshold, float obs_movement_range, float stop_loss, float take_profit, int obs_date_id_offset, int trade_entry_date_id_offset, int stop_time_id)
                                add_trade(AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, position_flag, ticker_id, first_time_id, first_time_close_price, second_time_id, second_time_close_price, third_time_id, third_time_close_price, obs_movement_threshold[obs_movement_threshold_index], obs_movement_range, stop_loss, take_profit, obs_date_id_offset, trade_entry_date_id_offset, stop_time_id);
//                                add_trade(AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result);
//                                add_trade(AdditionalResultCount, trade_result_count);
//                                add_trade(AdditionalResultCount);
//                                add_trade();


//                                trade_result_index = atomicAdd(trade_result_count,1);
//                                trade_result_index_offset = trade_result_index * TRADE_RESULT_COLUMN_COUNT ;

//                                if (trade_result_index < InitialResultCacheSize && trade_result_index >= 0 && trade_result_index_offset >= 0) {

//                                  trade_result[trade_result_index_offset + 0] = position_flag;
//                                  trade_result[trade_result_index_offset + 1] = ticker_id;
//                                  trade_result[trade_result_index_offset + 2] = first_time_id;
//                                  trade_result[trade_result_index_offset + 3] = first_time_close_price;
//                                  trade_result[trade_result_index_offset + 4] = second_time_id;
//                                  trade_result[trade_result_index_offset + 5] = second_time_close_price;
//                                  trade_result[trade_result_index_offset + 6] = third_time_id;
//                                  trade_result[trade_result_index_offset + 7] = third_time_close_price;
//                                  trade_result[trade_result_index_offset + 8] = obs_movement_threshold[obs_movement_threshold_index];
                                
//                                  trade_result[trade_result_index_offset + 9] = obs_movement_range;
                                
//                                  trade_result[trade_result_index_offset + 10] = stop_loss;
//                                  trade_result[trade_result_index_offset + 11] = take_profit;
//                                  trade_result[trade_result_index_offset + 12] = obs_date_id_offset;
//                                  trade_result[trade_result_index_offset + 13] = trade_entry_date_id_offset;
//                                  trade_result[trade_result_index_offset + 14] = stop_time_id;
////    TRADE_RESULT_COLUMNS = ['long short flag', 'ticker id', 'obs time id', 'obs price', 'entry time id', 'entry price', 'exit time id', 'exit price', 'obs movement threshold', 'stop loss', 'take profit', 'obs date id offset', 'trade entry date id offset', 'stop time id']
//                                  temp_AdditionalResultCount = atomicAdd(AdditionalResultCount,1);

//                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }              
            }
          }
      }
      """)
          
      
    if ObsPeriodExponentialStep <= 0:
        func = mod.get_function("correlation_on_specific_time_section_analysis_linear")
        func(AdditionalResultCount_gpu, np.int32(ticker_size), np.int32(gpu_core_block_count), np.int32(time_size), np.int32(StartTimeInStdUnit), np.int32(EndTimeInStdUnit), np.int32(TimeIntervalInStdUnit), np.int32(ObsPeriodMovementThreshold_size), np.float32(ObsPeriodExponentialStep), np.float32(StopLossPerTrade), np.float32(TakeProfitPerTrade), np.int32(ObsDateIDOffset), np.int32(TradeEntryDateIDOffset), np.int32(ErrorCode), np.int32(InitialResultCacheSize), np.int32(TRADE_RESULT_COLUMN_COUNT), trade_result_count_gpu, close_price_matrix_gpu, date_id_matrix_gpu, time_std_unit_matrix_gpu, ObsPeriodMovementThreshold_matrix_gpu, trade_result_gpu, block=(GPU_CORE_BLOCK_SIZE,1,1), grid=(GPU_CORE_GRID_SIZE, 1))
    else:
        func = mod.get_function("correlation_on_specific_time_section_analysis")
        func(AdditionalResultCount_gpu, np.int32(ticker_size), np.int32(gpu_core_block_count), np.int32(time_size), np.int32(StartTimeInStdUnit), np.int32(EndTimeInStdUnit), np.int32(TimeIntervalInStdUnit), np.int32(ObsPeriodMovementThreshold_size), np.float32(ObsPeriodMovementRange), np.float32(ObsPeriodExponentialStep), np.float32(StopLossPerTrade), np.float32(TakeProfitPerTrade), np.int32(ObsDateIDOffset), np.int32(TradeEntryDateIDOffset), np.int32(ErrorCode), np.int32(InitialResultCacheSize), np.int32(TRADE_RESULT_COLUMN_COUNT), trade_result_count_gpu, close_price_matrix_gpu, date_id_matrix_gpu, time_std_unit_matrix_gpu, ObsPeriodMovementThreshold_matrix_gpu, trade_result_gpu, block=(GPU_CORE_BLOCK_SIZE,1,1), grid=(GPU_CORE_GRID_SIZE, 1))

    AdditionalResultCount_out = np.empty_like(AdditionalResultCount)
    cuda.memcpy_dtoh(AdditionalResultCount_out, AdditionalResultCount_gpu)

    print('AdditionalResultCount_out[0] is ' + f"{AdditionalResultCount_out[0]:,}")
    print()

    trade_result_count_out = np.empty_like(trade_result_count)
    cuda.memcpy_dtoh(trade_result_count_out, trade_result_count_gpu)

    print('trade_result_count_out[0] = ' + f"{trade_result_count_out[0]:,}" + ' and InitialResultCacheSize is ' + f"{InitialResultCacheSize:,}" + ' and AdditionalResultCount_out[0] is ' + f"{AdditionalResultCount_out[0]:,}" + ' at ' + str(datetime.now()))
    
    if (AdditionalResultCount_out[0] > InitialResultCacheSize - 2):
        print()
        print('InitialResultCacheSize not large enough')
        print()
        raise Exception("InitialResultCacheSize not large enough")

    trade_record = np.empty((InitialResultCacheSize, TRADE_RESULT_COLUMN_COUNT), dtype=np.float32)
    cuda.memcpy_dtoh(trade_record, trade_result_gpu)
    
    trade_result_gpu.free()
    close_price_matrix_gpu.free()
    date_id_matrix_gpu.free()
    trade_result_count_gpu.free()
    AdditionalResultCount_gpu.free()
    ObsPeriodMovementThreshold_matrix_gpu.free()
    time_std_unit_matrix_gpu.free()
    trade_result = None
    
    return pd.DataFrame(data=trade_record[0:AdditionalResultCount_out[0]], columns=TRADE_RESULT_COLUMNS)

    # return pd.DataFrame(data=trade_record[0:trade_result_count_out], columns=TRADE_RESULT_COLUMNS)

    # df = pd.DataFrame(data=trade_record[0:trade_result_count_out], columns=TRADE_RESULT_COLUMNS)
    # print('trade record is')
    # print(df)
    # return df