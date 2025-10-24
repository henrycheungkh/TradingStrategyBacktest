# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 08:30:03 2022

@author: henry
"""
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import random

import dask.dataframe as dd
import dask.array as da
import dask.bag as db

import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import InvestmentAnalytics.CUDA.CUDAPathSetting

# def CUDADaskSortByFloatColumns(df, by, ascending = True, GPU_CORE_BLOCK_SIZE = 32*32*2):
def CUDADaskSortByFloatColumns(df, by, ascending = True, GPU_CORE_BLOCK_SIZE = 32*32):
# def CUDADaskSortByFloatColumns(df, by, ascending = True, GPU_CORE_BLOCK_SIZE = 10):

    print('before running CUDADaskSortByFloatColumns with ' + str(len(df)) + ' rows at ' + str(datetime.now()))

    ErrorCode = 0
    if GPU_CORE_BLOCK_SIZE <= 16:
        GPU_CORE_BLOCK_SIZE_Z = GPU_CORE_BLOCK_SIZE
        GPU_CORE_BLOCK_SIZE_X = 1
        GPU_CORE_BLOCK_SIZE_Y = 1
    else:
        GPU_CORE_BLOCK_SIZE_Z = 16
        GPU_CORE_BLOCK_SIZE_Y = int( GPU_CORE_BLOCK_SIZE / 16)
        GPU_CORE_BLOCK_SIZE_X = 1
    if GPU_CORE_BLOCK_SIZE_Y > 8:
        GPU_CORE_BLOCK_SIZE_X = int( GPU_CORE_BLOCK_SIZE_Y / 8)
        GPU_CORE_BLOCK_SIZE_Y = 8
        
    print('GPU_CORE_BLOCK_SIZE_X x GPU_CORE_BLOCK_SIZE_Y x GPU_CORE_BLOCK_SIZE_Z = ' + str(GPU_CORE_BLOCK_SIZE_X*GPU_CORE_BLOCK_SIZE_Y*GPU_CORE_BLOCK_SIZE_Z) )

    
    df_by = df[by]
    # print('in CUDADaskSortByFloatColumns, df_by is')
    # print(df_by.head(20))
    if isinstance(ascending, list):
        i = 0
        while i < len(df_by.columns):
            if not ascending[i]:
                df_by[df_by.columns[i]] = -1 * df_by[df_by.columns[i]]
            i += 1
    else:
        if not ascending:
            i = 0
            while i < len(df_by.columns):
                df_by[df_by.columns[i]] = -1 * df_by[df_by.columns[i]]
                i += 1            
    
    
    if isinstance(df, pd.DataFrame):
        df_by_matrix = df_by.to_numpy()
    else:
        df_by_matrix = np.asarray(df_by)
    df_by_matrix = df_by_matrix.astype(np.float32)
    df_by_matrix = df_by_matrix.copy(order="C")
    
    # print('in CUDADaskSortByFloatColumns, df_by_matrix is')
    # print(df_by_matrix)
    
    first_dimension_size = len(df_by_matrix)
    second_dimension_size = len(df_by_matrix[0])
    print('first_dimension_size is ' + str(first_dimension_size) + ' and second_dimension_size is ' + str(second_dimension_size))
    
    sorted_index_matrix = np.arange(0,first_dimension_size)
    # print('in CUDADaskSortByFloatColumns, sorted_index_matrix is')
    # print(sorted_index_matrix)

    debug_matrix_gpu = cuda.mem_alloc(int(100 * 4))

    
    odd_even_indicator = np.int32(0)
    thread_done_count = np.int32(0)
    swap_done_count = np.int32(0)
    sorting_done_indicator = np.int32(0)

    
    df_by_matrix_gpu = cuda.mem_alloc(df_by_matrix.nbytes)
    # sorted_index_matrix_gpu = cuda.mem_alloc(sorted_index_matrix.nbytes)
    sorted_index_matrix_gpu = cuda.mem_alloc(int(first_dimension_size * 4))
    odd_even_indicator_gpu = cuda.mem_alloc(odd_even_indicator.nbytes)
    thread_done_count_gpu = cuda.mem_alloc(thread_done_count.nbytes)
    swap_done_count_gpu = cuda.mem_alloc(swap_done_count.nbytes)
    sorting_done_indicator_gpu = cuda.mem_alloc(sorting_done_indicator.nbytes)

    cuda.memcpy_htod(df_by_matrix_gpu, df_by_matrix)
    cuda.memcpy_htod(sorted_index_matrix_gpu, sorted_index_matrix)
    cuda.memcpy_htod(odd_even_indicator_gpu, odd_even_indicator)
    cuda.memcpy_htod(thread_done_count_gpu, thread_done_count)
    cuda.memcpy_htod(swap_done_count_gpu, swap_done_count)
    cuda.memcpy_htod(sorting_done_indicator_gpu, sorting_done_indicator)
    

    
    bubble_deestination_index_matrix = np.arange(0,GPU_CORE_BLOCK_SIZE)
    bubble_deestination_index_matrix_gpu = cuda.mem_alloc(bubble_deestination_index_matrix.nbytes)
    cuda.memcpy_htod(bubble_deestination_index_matrix_gpu, bubble_deestination_index_matrix)
    bubble_location_index_matrix_gpu = cuda.mem_alloc(bubble_deestination_index_matrix.nbytes)

    # print('in CUDADaskSortByFloatColumns, bubble_deestination_index_matrix is')
    # print(bubble_deestination_index_matrix)

    mod = SourceModule("""
      __global__ void dataframe_sort_by_cuda_enumeration(int first_dimension_size, int second_dimension_size, int GPU_CORE_BLOCK_SIZE_X, int GPU_CORE_BLOCK_SIZE_Y, int GPU_CORE_BLOCK_SIZE_Z, int ErrorCode, float *df_by_matrix, int *sorted_index_matrix, float *debug_matrix)
      {
        int thread_Index, Total_Thread_count;
        bool diff_found;
        ErrorCode = 0;
        Total_Thread_count = GPU_CORE_BLOCK_SIZE_X * GPU_CORE_BLOCK_SIZE_Y * GPU_CORE_BLOCK_SIZE_Z;
        thread_Index = threadIdx.x * GPU_CORE_BLOCK_SIZE_Y * GPU_CORE_BLOCK_SIZE_Z + threadIdx.y * GPU_CORE_BLOCK_SIZE_Z + threadIdx.z;
        
        while (thread_Index < first_dimension_size) {
            sorted_index_matrix[thread_Index] = 0;
            for (int check_index = 0; check_index < first_dimension_size; check_index++) {
                if (thread_Index != check_index) {
                  diff_found = false;
                  for (int i=0; i<second_dimension_size; i++) {
                    if (df_by_matrix[check_index * second_dimension_size + i] > df_by_matrix[thread_Index * second_dimension_size + i]) {
                        diff_found = true;
                        break;
                    }
                    if (df_by_matrix[check_index * second_dimension_size + i] < df_by_matrix[thread_Index * second_dimension_size + i]) {
                        diff_found = true;
                        sorted_index_matrix[thread_Index]++;
                        break;
                    }
                  }
                  if (!diff_found && check_index < thread_Index) {
                    sorted_index_matrix[thread_Index]++;
                  }
                }
            }
            thread_Index = thread_Index + Total_Thread_count;
        }
      }

      __global__ void dataframe_sort_by_cuda_odd_even(int first_dimension_size, int second_dimension_size, int GPU_CORE_BLOCK_SIZE_X, int GPU_CORE_BLOCK_SIZE_Y, int GPU_CORE_BLOCK_SIZE_Z, int ErrorCode, int *odd_even_indicator, int *thread_done_count, int *swap_done_count, int *sorting_done_indicator, float *df_by_matrix, int *sorted_index_matrix, float *debug_matrix)
      {
        int loop_count, thread_Index, Total_Thread_count, sort_swap_index, new_thread_done_count, new_swap_done_count, odd_even_indicator_to_run, swap_index_temp, accumulated_no_swap_count;
        float swap_temp;
        loop_count = 0;
        ErrorCode = 0;
        Total_Thread_count = GPU_CORE_BLOCK_SIZE_X * GPU_CORE_BLOCK_SIZE_Y * GPU_CORE_BLOCK_SIZE_Z - 1;
        thread_Index = threadIdx.x * GPU_CORE_BLOCK_SIZE_Y * GPU_CORE_BLOCK_SIZE_Z + threadIdx.y * GPU_CORE_BLOCK_SIZE_Z + threadIdx.z;
        
        if (thread_Index == 0) {
            accumulated_no_swap_count = 0;
            while (thread_done_count[0] < Total_Thread_count || accumulated_no_swap_count >= 2) {
                    while (thread_done_count[0] < Total_Thread_count) { 
                      __nanosleep(10);
                    }
                    if (swap_done_count[0] > 0) {
                        accumulated_no_swap_count = 0;
                        swap_done_count[0] = 0;
                        odd_even_indicator[0] = (odd_even_indicator[0] + 1) % 2;
                        thread_done_count[0] = 0;
                    } else {
                        accumulated_no_swap_count++;
                    }
//                    for (int i=0; i<first_dimension_size; i++) {
//                        debug_matrix[loop_count*first_dimension_size + i] = sorted_index_matrix[i];
//                    }
//                    loop_count++;
            }
            sorting_done_indicator[0] = 1;

        } else {
            while (sorting_done_indicator[0] <= 0) {
              odd_even_indicator_to_run = odd_even_indicator[0];
              sort_swap_index = (thread_Index - 1) * 2 + odd_even_indicator_to_run;
              
              
              while (sort_swap_index +  1 < first_dimension_size) {
                    
                  for (int i=0; i<second_dimension_size; i++) {
                    if (df_by_matrix[(sort_swap_index + 1) * second_dimension_size + i] > df_by_matrix[sort_swap_index * second_dimension_size + i]) {
                        break;
                    }
                    if (df_by_matrix[(sort_swap_index + 1) * second_dimension_size + i] < df_by_matrix[sort_swap_index * second_dimension_size + i]) {
                      new_swap_done_count = atomicAdd(swap_done_count,1);
                      for (int j=0; j<second_dimension_size; j++) {
                        swap_temp = df_by_matrix[(sort_swap_index + 1) * second_dimension_size + j];
                        df_by_matrix[(sort_swap_index + 1) * second_dimension_size + j] = df_by_matrix[sort_swap_index * second_dimension_size + j];
                        df_by_matrix[sort_swap_index * second_dimension_size + j] = swap_temp;
                      }
                      swap_index_temp = sorted_index_matrix[sort_swap_index + 1];
                      sorted_index_matrix[sort_swap_index + 1] = sorted_index_matrix[sort_swap_index];
                      sorted_index_matrix[sort_swap_index] = swap_index_temp;
                      break;
                    }
                  }
                  sort_swap_index = sort_swap_index + (Total_Thread_count * 2);
              }
              
              new_thread_done_count = atomicAdd(thread_done_count,1);
              while (sorting_done_indicator[0] <= 0 && odd_even_indicator_to_run == odd_even_indicator[0]) { 
                 __nanosleep(100);
              }
              odd_even_indicator_to_run = odd_even_indicator[0];
              sort_swap_index = (thread_Index - 1) * 2 + odd_even_indicator_to_run;

            }
            
        }
      }

      __global__ void dataframe_sort_by_cuda_bubble(int first_dimension_size, int second_dimension_size, int GPU_CORE_BLOCK_SIZE_X, int GPU_CORE_BLOCK_SIZE_Y, int GPU_CORE_BLOCK_SIZE_Z, int ErrorCode, int *bubble_deestination_index, int *bubble_location_index, float *df_by_matrix, int *sorted_index_matrix, float *debug_matrix)
      {
        int sleep_time, thread_Index, prior_thread_Index, Total_Thread_count, swap_index_temp, loop_count;
        float swap_temp;
        ErrorCode = 0;
        sleep_time = 10;
        Total_Thread_count = GPU_CORE_BLOCK_SIZE_X * GPU_CORE_BLOCK_SIZE_Y * GPU_CORE_BLOCK_SIZE_Z;
        thread_Index = threadIdx.x * GPU_CORE_BLOCK_SIZE_Y * GPU_CORE_BLOCK_SIZE_Z + threadIdx.y * GPU_CORE_BLOCK_SIZE_Z + threadIdx.z;
        if (thread_Index == 0) {
          prior_thread_Index = Total_Thread_count - 1;
        } else {
          prior_thread_Index = thread_Index - 1;
        }
        
        while (bubble_deestination_index[thread_Index] < first_dimension_size - 1) {
                    
            bubble_location_index[thread_Index] = first_dimension_size - 2;
            while (bubble_location_index[thread_Index] >= bubble_deestination_index[thread_Index]) {
                    
              while (bubble_deestination_index[prior_thread_Index] < bubble_deestination_index[thread_Index] && bubble_location_index[prior_thread_Index] >= bubble_location_index[thread_Index] - 1) {
                  __nanosleep(sleep_time);
              }


              if (thread_Index == 0) {
                debug_matrix[0] = (float) prior_thread_Index;
                debug_matrix[1] = (float) bubble_location_index[prior_thread_Index];
                debug_matrix[2] = (float) bubble_location_index[thread_Index];
              }

                  for (int i=0; i<second_dimension_size; i++) {

                    if (df_by_matrix[(bubble_location_index[thread_Index] + 1) * second_dimension_size + i] > df_by_matrix[bubble_location_index[thread_Index] * second_dimension_size + i]) {
                        break;
                    }

                    if (df_by_matrix[(bubble_location_index[thread_Index] + 1) * second_dimension_size + i] < df_by_matrix[bubble_location_index[thread_Index] * second_dimension_size + i]) {
                            
                      for (int j=0; j<second_dimension_size; j++) {
                        swap_temp = df_by_matrix[(bubble_location_index[thread_Index] + 1) * second_dimension_size + j];
                        df_by_matrix[(bubble_location_index[thread_Index] + 1) * second_dimension_size + j] = df_by_matrix[bubble_location_index[thread_Index] * second_dimension_size + j];
                        df_by_matrix[bubble_location_index[thread_Index] * second_dimension_size + j] = swap_temp;
                      }

                      swap_index_temp = sorted_index_matrix[bubble_location_index[thread_Index] + 1];
                      sorted_index_matrix[bubble_location_index[thread_Index] + 1] = sorted_index_matrix[bubble_location_index[thread_Index]];
                      sorted_index_matrix[bubble_location_index[thread_Index]] = swap_index_temp;
                      break;
                    }
                  }
              bubble_location_index[thread_Index]--;
            }
            bubble_deestination_index[thread_Index] = bubble_deestination_index[thread_Index] + Total_Thread_count;
        }
      }            
    """)

          
    # func = mod.get_function("dataframe_sort_by_cuda_odd_even")
    # func(np.int32(first_dimension_size), np.int32(second_dimension_size), np.int32(GPU_CORE_BLOCK_SIZE_X), np.int32(GPU_CORE_BLOCK_SIZE_Y), np.int32(GPU_CORE_BLOCK_SIZE_Z), np.int32(ErrorCode), odd_even_indicator_gpu, thread_done_count_gpu, swap_done_count_gpu, sorting_done_indicator_gpu, df_by_matrix_gpu, sorted_index_matrix_gpu, debug_matrix_gpu, block=(GPU_CORE_BLOCK_SIZE_X,GPU_CORE_BLOCK_SIZE_Y,GPU_CORE_BLOCK_SIZE_Z))

    # func = mod.get_function("dataframe_sort_by_cuda_bubble")
    # func(np.int32(first_dimension_size), np.int32(second_dimension_size), np.int32(GPU_CORE_BLOCK_SIZE_X), np.int32(GPU_CORE_BLOCK_SIZE_Y), np.int32(GPU_CORE_BLOCK_SIZE_Z), np.int32(ErrorCode), bubble_deestination_index_matrix_gpu, bubble_location_index_matrix_gpu, df_by_matrix_gpu, sorted_index_matrix_gpu, debug_matrix_gpu, block=(GPU_CORE_BLOCK_SIZE_X,GPU_CORE_BLOCK_SIZE_Y,GPU_CORE_BLOCK_SIZE_Z))

    func = mod.get_function("dataframe_sort_by_cuda_enumeration")
    func(np.int32(first_dimension_size), np.int32(second_dimension_size), np.int32(GPU_CORE_BLOCK_SIZE_X), np.int32(GPU_CORE_BLOCK_SIZE_Y), np.int32(GPU_CORE_BLOCK_SIZE_Z), np.int32(ErrorCode), df_by_matrix_gpu, sorted_index_matrix_gpu, debug_matrix_gpu, block=(GPU_CORE_BLOCK_SIZE_X,GPU_CORE_BLOCK_SIZE_Y,GPU_CORE_BLOCK_SIZE_Z))

    print('after running dataframe_sort_by_cuda at ' + str(datetime.now()))

    # sorted_index_matrix = np.empty(first_dimension_size, dtype=np.int32)
    cuda.memcpy_dtoh(sorted_index_matrix, sorted_index_matrix_gpu)

    print('after memcpy_dtoh sorted_index_matrix at ' + str(datetime.now()))

    # print('result of sorted_index_matrix is')
    # print(sorted_index_matrix)

    # debug_matrix = np.empty(100, dtype=np.float32)
    # cuda.memcpy_dtoh(debug_matrix, debug_matrix_gpu)
    # print('result of debug_matrix is')
    # print(debug_matrix)

    df_by_matrix_gpu.free()
    sorted_index_matrix_gpu.free()
    debug_matrix_gpu.free()
    
    # print('df before adding sorting index is')
    # print(df.head(20,2))
    
    print('after freeing GPU memory, before creating df_sorted_index at ' + str(datetime.now()))

    # df_sorted_index = pd.DataFrame(sorted_index_matrix, columns=['sorted_index'])
    # df_sorted_index['rank'] = list(range(0, len(df_sorted_index)))
    
    # print('before running sorting of df_sorted_index at ' + str(datetime.now()))
    
    # df_sorted_index = df_sorted_index.sort_values(by=['sorted_index'], ascending=True, inplace=False).reset_index(drop=True)

    # print('after running sorting of df_sorted_index at ' + str(datetime.now()))


    df_sorted_index = pd.DataFrame(sorted_index_matrix, columns=['rank'])

    # print('df_sorted_index is')
    # print(df_sorted_index.head(20))
    
    df['rank'] = df_sorted_index['rank']

    # print('df after adding rank is')
    # print(df.head(20,2))

    print('before sort by ranking at ' + str(datetime.now()))

    df = df.sort_values(by=['rank'], ascending=True, inplace=False).drop(columns=['rank'])  

    print('after running sorting of df at ' + str(datetime.now()))
      
    return df

print('Start')

NumberOfSample = 200000
# NumberOfPartition = 2
NumberOfPartition = 20
SortByColumn = ['rand3', 'rand1', 'rand2']


# NumberOfSample = 50000

# before running CUDADaskSortByFloatColumns at 2022-11-12 22:13:34.982125
# after running dataframe_sort_by_cuda at 2022-11-12 22:13:37.006282
# after memcpy_dtoh sorted_index_matrix at 2022-11-12 22:13:56.224814
# after freeing GPU memory, before creating df_sorted_index at 2022-11-12 22:13:56.224814
# before running sorting of df_sorted_index at 2022-11-12 22:13:56.224814
# after running sorting of df_sorted_index at 2022-11-12 22:13:56.240442
# after running sorting of df at 2022-11-12 22:13:56.256231
# after running CUDADaskSortByFloatColumns at 2022-11-12 22:13:56.256231

# NumberOfSample = 100000

# before running CUDADaskSortByFloatColumns at 2022-11-12 22:19:00.210756
# after running dataframe_sort_by_cuda at 2022-11-12 22:19:02.317081
# after memcpy_dtoh sorted_index_matrix at 2022-11-12 22:20:19.117368
# after freeing GPU memory, before creating df_sorted_index at 2022-11-12 22:20:19.117368
# before running sorting of df_sorted_index at 2022-11-12 22:20:19.133384
# after running sorting of df_sorted_index at 2022-11-12 22:20:19.143246
# after running sorting of df at 2022-11-12 22:20:19.167820
# after running CUDADaskSortByFloatColumns at 2022-11-12 22:20:19.169241

# NumberOfSample = 200000

# before running CUDADaskSortByFloatColumns at 2022-11-12 22:25:17.193458
# after running dataframe_sort_by_cuda at 2022-11-12 22:25:19.161962
# after memcpy_dtoh sorted_index_matrix at 2022-11-12 22:30:27.348460
# after freeing GPU memory, before creating df_sorted_index at 2022-11-12 22:30:27.348460
# before running sorting of df_sorted_index at 2022-11-12 22:30:27.394047
# after running sorting of df_sorted_index at 2022-11-12 22:30:27.421551
# after running sorting of df at 2022-11-12 22:30:27.466486
# after running CUDADaskSortByFloatColumns at 2022-11-12 22:30:27.467487

# NumberOfSample = 500000

# before running CUDADaskSortByFloatColumns at 2022-11-12 22:32:20.317164
# after running dataframe_sort_by_cuda at 2022-11-12 22:32:23.801310
# after memcpy_dtoh sorted_index_matrix at 2022-11-12 23:04:40.767990
# after freeing GPU memory, before creating df_sorted_index at 2022-11-12 23:04:40.767990
# before running sorting of df_sorted_index at 2022-11-12 23:04:40.860404
# after running sorting of df_sorted_index at 2022-11-12 23:04:40.908558
# after running sorting of df at 2022-11-12 23:04:40.971194
# after running CUDADaskSortByFloatColumns at 2022-11-12 23:04:40.971194



# 50000 by bubble
# before running CUDADaskSortByFloatColumns at 2022-11-16 00:02:55.191287
# first_dimension_size is 50000 and second_dimension_size is 3
# after running dataframe_sort_by_cuda at 2022-11-16 00:02:55.272203
# after memcpy_dtoh sorted_index_matrix at 2022-11-16 00:07:13.949521
# after freeing GPU memory, before creating df_sorted_index at 2022-11-16 00:07:14.020953
# before running sorting of df_sorted_index at 2022-11-16 00:07:14.042966
# after running sorting of df_sorted_index at 2022-11-16 00:07:14.056871
# after running sorting of df at 2022-11-16 00:07:14.121742
# after running CUDADaskSortByFloatColumns at 2022-11-16 00:07:14.127851


# 50000 by enumeration
# before running CUDADaskSortByFloatColumns at 2022-11-19 13:20:11.849962
# after running dataframe_sort_by_cuda at 2022-11-19 13:20:11.943684
# after memcpy_dtoh sorted_index_matrix at 2022-11-19 13:20:30.840625
# after freeing GPU memory, before creating df_sorted_index at 2022-11-19 13:20:30.840625
# after running sorting of df at 2022-11-19 13:20:30.888884
# after running CUDADaskSortByFloatColumns at 2022-11-19 13:20:30.904420


# 100000 by enumeration, partitioin = 2
# before running CUDADaskSortByFloatColumns at 2022-11-19 13:22:11.225716
# after running dataframe_sort_by_cuda at 2022-11-19 13:22:11.313864
# after memcpy_dtoh sorted_index_matrix at 2022-11-19 13:23:27.355890
# after freeing GPU memory, before creating df_sorted_index at 2022-11-19 13:23:27.355890
# after running sorting of df at 2022-11-19 13:23:27.420123
# after running CUDADaskSortByFloatColumns at 2022-11-19 13:23:27.426796

# 100000 by enumeration, partitioin = 10
# before running CUDADaskSortByFloatColumns at 2022-11-19 13:31:24.702884
# after running dataframe_sort_by_cuda at 2022-11-19 13:31:24.827048
# after memcpy_dtoh sorted_index_matrix at 2022-11-19 13:32:40.840165
# after freeing GPU memory, before creating df_sorted_index at 2022-11-19 13:32:40.854178
# before sort by ranking at 2022-11-19 13:32:40.862057
# after running sorting of df at 2022-11-19 13:32:40.950746
# after running CUDADaskSortByFloatColumns at 2022-11-19 13:32:40.950746

# 200000 by enumeration, partitioin = 10
# before running CUDADaskSortByFloatColumns at 2022-11-19 13:34:11.010806
# after running dataframe_sort_by_cuda at 2022-11-19 13:34:11.162051
# after memcpy_dtoh sorted_index_matrix at 2022-11-19 13:39:26.154246
# after freeing GPU memory, before creating df_sorted_index at 2022-11-19 13:39:26.155890
# before sort by ranking at 2022-11-19 13:39:26.169204
# after running sorting of df at 2022-11-19 13:39:26.264395
# after running CUDADaskSortByFloatColumns at 2022-11-19 13:39:26.264395

pandas_df = pd.DataFrame("Happy", index=list(range(0,NumberOfSample)), columns=['x']) 
pandas_df['rand1'] = np.random.randint(0, 100000, size=NumberOfSample) / 100
pandas_df['rand2'] = np.random.randint(0, 100000, size=NumberOfSample) / 100
# pandas_df['rand3'] = np.random.randint(0, 10000, size=NumberOfSample) / 10
pandas_df['rand3'] = 1

print('pandas_df with constant value is')
print(pandas_df)  

ddf = dd.from_pandas(pandas_df, npartitions=NumberOfPartition)

print('ddf before sorting is with len ' + str(len(ddf)))
print(ddf.head(NumberOfSample, NumberOfPartition))


# ddf_sorted = CUDADaskSortByFloatColumns(ddf, by=SortByColumn)
# ddf_sorted = CUDADaskSortByFloatColumns(ddf, ascending=False, by=SortByColumn)
# ddf_sorted = CUDADaskSortByFloatColumns(ddf, ascending=[True,False,True], by=SortByColumn)
ddf_sorted = CUDADaskSortByFloatColumns(ddf, ascending=[True,True,False], by=SortByColumn)

print('after running CUDADaskSortByFloatColumns at ' + str(datetime.now()))

print('ddf_sorted after sorting is with len ' + str(len(ddf)))
print(ddf_sorted.head(NumberOfSample, NumberOfPartition))




# ddf_sorted2 = ddf.copy()
# ddf_sorted2['rank'] = 0

# # ddf_sorted2 = ddf.sort_values(by=['rand3'], ascending=True, inplace=False)

# for by_col in SortByColumn:
#     print('by_col is ' + by_col)
#     ddf_sorted2['rank'] = ddf_sorted2['rank'] * len(ddf_sorted2)
#     try:
#         ddf_sorted2 = ddf_sorted2.sort_values(by=[by_col], ascending=True, inplace=False)
#     except:
#         pass

#     ddf_sorted2[by_col + '_rank'] = ddf_sorted2.assign(partition_count=1).partition_count.cumsum()
#     ddf_sorted2[by_col + '_rank'] = ddf_sorted2[by_col + '_rank'] - 1
#     print('ddf with by_col = ' + by_col + ' is')
#     print(ddf_sorted2.head(NumberOfSample, NumberOfPartition))
    
#     ddf_sorted2['rank'] = ddf_sorted2['rank'] + ddf_sorted2[by_col + '_rank']

# print('ddf_sorted2 after adding rank is with len ' + str(len(ddf)))
# print(ddf_sorted2.head(NumberOfSample, NumberOfPartition))

# ddf_sorted2 = ddf_sorted2.sort_values(by=['rank'], ascending=True, inplace=False)

# print('ddf_sorted2 after sorting is with len ' + str(len(ddf)))
# print(ddf_sorted2.head(NumberOfSample, NumberOfPartition))

# temp_df = ddf_sorted2.iloc[:, 2]
# print(temp_df.head(20))
# print(str(ddf_sorted2.iloc[49, 'rank']))
# 




