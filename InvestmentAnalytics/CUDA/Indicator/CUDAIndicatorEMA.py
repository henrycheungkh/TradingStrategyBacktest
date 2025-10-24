
import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import math
import pandas as pd
import numpy as np
import InvestmentAnalytics.CUDA.CUDAPathSetting

GPU_CORE_BLOCK_SIZE = 32*32

def CUDAIndicatorEMA(close_price_matrix, MA_Day_List):
    ticker_size = len(close_price_matrix)
    time_size = len(close_price_matrix[0])
    MA_Day_size = len(MA_Day_List)
    MA_Day_matrix = np.array(MA_Day_List).astype(np.int32)
    
    indicator_matrix = np.zeros((ticker_size * MA_Day_size, time_size)).astype(np.float32)
        
    
    # print('before running, len(indicator_matrix) is ' + str(len(indicator_matrix)))
    # print('before running, len(time_size) is ' + str(time_size) + ', len(ticker_size) is ' + str(ticker_size) + ', len(MA_Day_size) is ' + str(MA_Day_size))
    # print(indicator_matrix)
    first_dimension_size = len(close_price_matrix)
    second_dimension_size = len(close_price_matrix[0])

    gpu_core_block_count = math.ceil(first_dimension_size * MA_Day_size/GPU_CORE_BLOCK_SIZE) 

        
#     ticker_block_count = math.ceil(ticker_size/GPU_CORE_BLOCK_SIZE)

    close_price_matrix = close_price_matrix.astype(np.float32)
    
    close_price_matrix_gpu = cuda.mem_alloc(close_price_matrix.nbytes)
    cuda.memcpy_htod(close_price_matrix_gpu, close_price_matrix)

    indicator_matrix_gpu = cuda.mem_alloc(indicator_matrix.nbytes)
    cuda.memcpy_htod(indicator_matrix_gpu, indicator_matrix)
    
    MA_Day_matrix_gpu = cuda.mem_alloc(MA_Day_matrix.nbytes)
    cuda.memcpy_htod(MA_Day_matrix_gpu, MA_Day_matrix)

    mod = SourceModule("""

       #include <cstdlib>
       #include <cmath>  
  
       __global__ void get_indicator(int first_dimension_size, int second_dimension_size, int GPU_CORE_BLOCK_SIZE, int gpu_core_block_count, float *close_price_matrix, float *indicator_matrix, int *MA_Day_matrix, int MA_day_size)
   {
      int MA_Day, combined_id, ticker_id, MA_Day_index;
      float indicator, multiplier;

        for (int k = 0; k < gpu_core_block_count; k++) {
          combined_id = k * GPU_CORE_BLOCK_SIZE + threadIdx.y;
          if (combined_id < first_dimension_size * MA_day_size) {
         
            ticker_id = combined_id % first_dimension_size;
            MA_Day_index = (int) combined_id / first_dimension_size;
         
            multiplier = (float) 2.0 / (MA_Day_matrix[MA_Day_index] + 1.0);
           
            indicator = 0;
            for (int time_id = 0; time_id < MA_Day_matrix[MA_Day_index] ; time_id++) {
              indicator = indicator + close_price_matrix[ticker_id * second_dimension_size + time_id];
            }
            indicator = indicator / MA_Day_matrix[MA_Day_index] ;

//            indicator_matrix[MA_Day_index * first_dimension_size * second_dimension_size + ticker_id * second_dimension_size + MA_Day_matrix[MA_Day_index]] = indicator;
//            indicator_matrix[MA_Day_index * first_dimension_size * second_dimension_size + ticker_id * second_dimension_size + MA_Day_matrix[MA_Day_index] + 1] = multiplier;
//            indicator_matrix[MA_Day_index * first_dimension_size * second_dimension_size + ticker_id * second_dimension_size + MA_Day_matrix[MA_Day_index] + 2] = MA_Day_matrix[MA_Day_index];
//            indicator_matrix[MA_Day_index * first_dimension_size * second_dimension_size + ticker_id * second_dimension_size + MA_Day_matrix[MA_Day_index] + 3] = close_price_matrix[ticker_id * second_dimension_size + MA_Day_matrix[MA_Day_index]];
           
            for (int time_id = MA_Day_matrix[MA_Day_index] ; time_id < second_dimension_size; time_id++) {
                  indicator = multiplier * close_price_matrix[ticker_id * second_dimension_size + time_id] + (1 - multiplier) * indicator;
                  indicator_matrix[MA_Day_index * first_dimension_size * second_dimension_size + ticker_id * second_dimension_size + time_id] = indicator;
            }
           
           
          }
        }
   }
   """)
          
    func = mod.get_function("get_indicator")
    func( np.int32(first_dimension_size), np.int32(second_dimension_size), np.int32(GPU_CORE_BLOCK_SIZE), np.int32(gpu_core_block_count), close_price_matrix_gpu, indicator_matrix_gpu, MA_Day_matrix_gpu, np.int32(MA_Day_size), block=(1,GPU_CORE_BLOCK_SIZE,1))

    indicator_matrix = np.empty_like(indicator_matrix)
    cuda.memcpy_dtoh(indicator_matrix, indicator_matrix_gpu)
    
    result_list = []
    single_block_size = first_dimension_size * second_dimension_size
    
    # print('len(indicator_matrix) is ' + str(len(indicator_matrix)) + ', first_dimension_size is ' + str(first_dimension_size) + ', second_dimension_size is ' + str(second_dimension_size))
    
    for i in range(MA_Day_size):
        result_list.append(indicator_matrix[i*first_dimension_size:(i+1)*first_dimension_size])
    # print('len(result_list) is ' + str(len(result_list)))
    
    return result_list