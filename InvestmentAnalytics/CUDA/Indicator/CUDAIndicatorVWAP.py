
import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import math
import pandas as pd
import numpy as np
import InvestmentAnalytics.CUDA.CUDAPathSetting

GPU_CORE_BLOCK_SIZE = 32*32

def CUDAIndicatorVWAP(close_price_matrix, volume_matrix, MA_Day_List, block_cutting_dimension = "Time Dimension"):
    ticker_size = len(close_price_matrix)
    time_size = len(close_price_matrix[0])
    block_cutting_by_time = 0
    MA_Day_size = len(MA_Day_List)
    MA_Day_matrix = np.array(MA_Day_List).astype(np.int32)

    if block_cutting_dimension == "Time Dimension":
        close_price_matrix = close_price_matrix.T.copy(order="C")
        volume_matrix = volume_matrix.T.copy(order="C")
        block_cutting_by_time = 1
        # print('before run')
        indicator_matrix = np.zeros((time_size * MA_Day_size, ticker_size)).astype(np.float32)
    else:
        indicator_matrix = np.zeros((ticker_size * MA_Day_size, time_size)).astype(np.float32)
        

    # print('in CUDAIndicatorVWAP')
    # print('close_price_matrix is with dimension ' + str(len(close_price_matrix)) + ' x '+ str(len(close_price_matrix[0])))
    # print('volume_matrix is with dimension ' + str(len(volume_matrix)) + ' x '+ str(len(volume_matrix[0])))

    
    # print('before running, len(indicator_matrix) is ' + str(len(indicator_matrix)))
    # print('before running, len(time_size) is ' + str(time_size) + ', len(ticker_size) is ' + str(ticker_size) + ', len(MA_Day_size) is ' + str(MA_Day_size))
    # print(indicator_matrix)
    first_dimension_size = len(close_price_matrix)
    second_dimension_size = len(close_price_matrix[0])

    gpu_core_block_count = math.ceil(first_dimension_size/GPU_CORE_BLOCK_SIZE) 

        
    ticker_block_count = math.ceil(ticker_size/GPU_CORE_BLOCK_SIZE)

    close_price_matrix = close_price_matrix.astype(np.float32)
    volume_matrix = volume_matrix.astype(np.float32)
    
    close_price_matrix_gpu = cuda.mem_alloc(close_price_matrix.nbytes)
    cuda.memcpy_htod(close_price_matrix_gpu, close_price_matrix)

    volume_matrix_gpu = cuda.mem_alloc(volume_matrix.nbytes)
    cuda.memcpy_htod(volume_matrix_gpu, volume_matrix)
    
            
    indicator_matrix_gpu = cuda.mem_alloc(indicator_matrix.nbytes)
    cuda.memcpy_htod(indicator_matrix_gpu, indicator_matrix)
    
    MA_Day_matrix_gpu = cuda.mem_alloc(MA_Day_matrix.nbytes)
    cuda.memcpy_htod(MA_Day_matrix_gpu, MA_Day_matrix)
    

    mod = SourceModule("""
  __global__ void get_indicator(int block_cutting_by_time, int first_dimension_size, int second_dimension_size, int GPU_CORE_BLOCK_SIZE, int gpu_core_block_count, float *close_price_matrix, float *volume_matrix, float *indicator_matrix, int *MA_Day_matrix, int MA_day_size)
  {
     int time_id, MA_Day;
     float price_sum, indicator, volume_sum;
     if (block_cutting_by_time == 0) {
     } else {
       for (int k = 0; k < gpu_core_block_count; k++) {
         time_id = k * GPU_CORE_BLOCK_SIZE + threadIdx.y;
         if (time_id < first_dimension_size) {
           for (int MA_Day_index = 0; MA_Day_index < MA_day_size; MA_Day_index++) {
             if (time_id >= MA_Day_matrix[MA_Day_index] - 1) {
               for (int ticker_id = 0; ticker_id < second_dimension_size; ticker_id++) {
                 indicator = 0;
                 volume_sum = 0;
                 for (int obs_time_id = time_id - MA_Day_matrix[MA_Day_index] + 1; obs_time_id <= time_id; obs_time_id++ ) {
                   indicator += close_price_matrix[obs_time_id * second_dimension_size + ticker_id] * volume_matrix[obs_time_id * second_dimension_size + ticker_id];
                   volume_sum += volume_matrix[obs_time_id * second_dimension_size + ticker_id];
                 }
                 indicator_matrix[MA_Day_index * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] = indicator / volume_sum;;
               }
             }
           }
         }
       }
     }
  }
  """)
          
    func = mod.get_function("get_indicator")
    func(np.int32(block_cutting_by_time), np.int32(first_dimension_size), np.int32(second_dimension_size), np.int32(GPU_CORE_BLOCK_SIZE), np.int32(gpu_core_block_count), close_price_matrix_gpu, volume_matrix_gpu, indicator_matrix_gpu, MA_Day_matrix_gpu, np.int32(MA_Day_size), block=(1,GPU_CORE_BLOCK_SIZE,1))

    indicator_matrix = np.empty_like(indicator_matrix)
    cuda.memcpy_dtoh(indicator_matrix, indicator_matrix_gpu)
    
    result_list = []
    single_block_size = first_dimension_size * second_dimension_size
    
    # print('len(indicator_matrix) is ' + str(len(indicator_matrix)) + ', first_dimension_size is ' + str(first_dimension_size) + ', second_dimension_size is ' + str(second_dimension_size))
    
    for i in range(MA_Day_size):
        if block_cutting_dimension == "Time Dimension":
            # x = indicator_matrix[i*first_dimension_size:(i+1)*first_dimension_size].T.copy(order="C")
            # print('for i = ' + str(i))
            # print(x)
            
            result_list.append(indicator_matrix[i*first_dimension_size:(i+1)*first_dimension_size].T.copy(order="C"))
        else:
            result_list.append(indicator_matrix[i*first_dimension_size:(i+1)*first_dimension_size])
    # print('len(result_list) is ' + str(len(result_list)))
    
    return result_list