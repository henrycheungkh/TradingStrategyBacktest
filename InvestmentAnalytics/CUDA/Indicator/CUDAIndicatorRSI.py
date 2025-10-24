
import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import math
import pandas as pd
import numpy as np
import InvestmentAnalytics.CUDA.CUDAPathSetting

GPU_CORE_BLOCK_SIZE = 32*32

# https://www.tradinformed.com/calculate-rsi-indicator-using-excel/
# https://indzara.com/2021/04/rsi-technical-indicator-excel-template/

def CUDAIndicatorRSI(close_price_matrix, Period_List, block_cutting_dimension = "Time Dimension"):
    print('In CUDAIndicatorRSI, close_price_matrix is')
    print(close_price_matrix)
    ticker_size = len(close_price_matrix)
    time_size = len(close_price_matrix[0])
    block_cutting_by_time = 0
    Period_size = len(Period_List)
    Period_matrix = np.array(Period_List).astype(np.int32)
    

    if block_cutting_dimension == "Time Dimension":
        close_price_matrix = close_price_matrix.T.copy(order="C")
        block_cutting_by_time = 1
        # print('before run')
        indicator_matrix = np.zeros((time_size * Period_size, ticker_size)).astype(np.float32)
    else:
        indicator_matrix = np.zeros((ticker_size * Period_size, time_size)).astype(np.float32)
        
    
    # print('before running, len(indicator_matrix) is ' + str(len(indicator_matrix)))
    # print('before running, len(time_size) is ' + str(time_size) + ', len(ticker_size) is ' + str(ticker_size) + ', len(MA_Day_size) is ' + str(MA_Day_size))
    # print(indicator_matrix)
    first_dimension_size = len(close_price_matrix)
    second_dimension_size = len(close_price_matrix[0])

    gpu_core_block_count = math.ceil(first_dimension_size/GPU_CORE_BLOCK_SIZE) 

        
    # ticker_block_count = math.ceil(ticker_size/GPU_CORE_BLOCK_SIZE)

    # a1 = close_price_matrix
    # b = np.zeros((ticker_size, time_size))

    close_price_matrix = close_price_matrix.astype(np.float32)
    # b = b.astype(np.float32)
    
    close_price_matrix_gpu = cuda.mem_alloc(close_price_matrix.nbytes)
    cuda.memcpy_htod(close_price_matrix_gpu, close_price_matrix)
    
    indicator_matrix_gpu = cuda.mem_alloc(indicator_matrix.nbytes)
    cuda.memcpy_htod(indicator_matrix_gpu, indicator_matrix)
    
    Period_matrix_gpu = cuda.mem_alloc(Period_matrix.nbytes)
    cuda.memcpy_htod(Period_matrix_gpu, Period_matrix)
    

  #   mod = SourceModule("""
  # __global__ void get_indicator(int block_cutting_by_time, int first_dimension_size, int second_dimension_size, int GPU_CORE_BLOCK_SIZE, int gpu_core_block_count, float *close_price_matrix, float *indicator_matrix, int *MA_Day_matrix, int MA_day_size)
  # {
  #    int time_id, MA_Day;
  #    float price_sum;
  #    if (block_cutting_by_time == 0) {
  #    } else {
  #      for (int k = 0; k < gpu_core_block_count; k++) {
  #        time_id = k * GPU_CORE_BLOCK_SIZE + threadIdx.y;
  #        if (time_id < first_dimension_size) {
  #          for (int MA_Day_index = 0; MA_Day_index < MA_day_size; MA_Day_index++) {
  #            if (time_id >= MA_Day_matrix[MA_Day_index] - 1) {
  #              for (int ticker_id = 0; ticker_id < second_dimension_size; ticker_id++) {
  #                indicator_matrix[MA_Day_index * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] = 0;
  #                for (int obs_time_id = time_id - MA_Day_matrix[MA_Day_index] + 1; obs_time_id <= time_id; obs_time_id++ ) {
  #                  indicator_matrix[MA_Day_index * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] = indicator_matrix[MA_Day_index * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] + close_price_matrix[obs_time_id * second_dimension_size + ticker_id];
  #                }
  #                indicator_matrix[MA_Day_index * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] = indicator_matrix[MA_Day_index * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] / MA_Day_matrix[MA_Day_index];
  #              }
  #            }
  #          }
  #        }
  #      }
  #    }
  # }
  # """)
          
    mod = SourceModule("""
  __global__ void get_indicator(int block_cutting_by_time, int first_dimension_size, int second_dimension_size, int GPU_CORE_BLOCK_SIZE, int gpu_core_block_count, float *close_price_matrix, float *indicator_matrix, int *Period_matrix, int Period_size)
  {

      int time_id, Period;
      float price_sum, avg_gain, avg_loss, price_diff, r_s;
      if (block_cutting_by_time == 0) {
      } else {
        for (int k = 0; k < gpu_core_block_count; k++) {
          time_id = k * GPU_CORE_BLOCK_SIZE + threadIdx.y;
          if (time_id < first_dimension_size) {
            for (int Period_index = 0; Period_index < Period_size; Period_index++) {
              Period = Period_matrix[Period_index];
              
              if (time_id < Period ) {
                for (int ticker_id = 0; ticker_id < second_dimension_size; ticker_id++) {
                  indicator_matrix[Period_index * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] = 0;
                }
              } else {
                for (int ticker_id = 0; ticker_id < second_dimension_size; ticker_id++) {
                  avg_gain = 0;
                  avg_loss = 0;
                  for (int obs_time_id = time_id - Period + 1 ; obs_time_id <= time_id; obs_time_id++ ) {
                    price_diff = close_price_matrix[obs_time_id * second_dimension_size + ticker_id] - close_price_matrix[(obs_time_id - 1) * second_dimension_size + ticker_id];
                    if ( price_diff > 0 ) {
                      avg_gain = avg_gain + price_diff;
                    }
                    if ( price_diff < 0 ) {
                      avg_loss = avg_loss - price_diff;
                    }
                  }
                  avg_gain = avg_gain / Period;
                  avg_loss = avg_loss / Period;
                  if (avg_gain == 0) {
                    avg_gain = 0.000001;
                  }
                  if (avg_loss == 0) {
                    avg_loss = 0.000001;
                  }
                  r_s = avg_gain / avg_loss;
                  indicator_matrix[Period_index * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] = 100 - 100 / (1 + r_s);
                }
              }
            }
          }
        }
      }
  }
  """)


    func = mod.get_function("get_indicator")
    func(np.int32(block_cutting_by_time), np.int32(first_dimension_size), np.int32(second_dimension_size), np.int32(GPU_CORE_BLOCK_SIZE), np.int32(gpu_core_block_count), close_price_matrix_gpu, indicator_matrix_gpu, Period_matrix_gpu, np.int32(Period_size), block=(1,GPU_CORE_BLOCK_SIZE,1))

    indicator_matrix = np.empty_like(indicator_matrix)
    cuda.memcpy_dtoh(indicator_matrix, indicator_matrix_gpu)
    
    result_list = []
    single_block_size = first_dimension_size * second_dimension_size
    
    # print('len(indicator_matrix) is ' + str(len(indicator_matrix)) + ', first_dimension_size is ' + str(first_dimension_size) + ', second_dimension_size is ' + str(second_dimension_size))
    
    for i in range(Period_size):
        if block_cutting_dimension == "Time Dimension":
            # x = indicator_matrix[i*first_dimension_size:(i+1)*first_dimension_size].T.copy(order="C")
            # print('for i = ' + str(i))
            # print(x)
            
            result_list.append(indicator_matrix[i*first_dimension_size:(i+1)*first_dimension_size].T.copy(order="C"))
        else:
            result_list.append(indicator_matrix[i*first_dimension_size:(i+1)*first_dimension_size])
    # print('len(result_list) is ' + str(len(result_list)))
    
    return result_list