# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 15:36:42 2022

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


def CUDADaskSortByFloatColumns(df, by, ascending = True, GPU_CORE_BLOCK_SIZE = 32*32):

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
        
    # print('GPU_CORE_BLOCK_SIZE_X x GPU_CORE_BLOCK_SIZE_Y x GPU_CORE_BLOCK_SIZE_Z = ' + str(GPU_CORE_BLOCK_SIZE_X*GPU_CORE_BLOCK_SIZE_Y*GPU_CORE_BLOCK_SIZE_Z) )
    
    df_by = df[by]
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
    
    first_dimension_size = len(df_by_matrix)
    second_dimension_size = len(df_by_matrix[0])
    
    odd_even_indicator = np.int32(0)
    thread_done_count = np.int32(0)
    swap_done_count = np.int32(0)
    sorting_done_indicator = np.int32(0)
    
    df_by_matrix_gpu = cuda.mem_alloc(df_by_matrix.nbytes)
    rank_matrix_gpu = cuda.mem_alloc(int(first_dimension_size * 4))
    odd_even_indicator_gpu = cuda.mem_alloc(odd_even_indicator.nbytes)
    thread_done_count_gpu = cuda.mem_alloc(thread_done_count.nbytes)
    swap_done_count_gpu = cuda.mem_alloc(swap_done_count.nbytes)
    sorting_done_indicator_gpu = cuda.mem_alloc(sorting_done_indicator.nbytes)

    cuda.memcpy_htod(df_by_matrix_gpu, df_by_matrix)
    # cuda.memcpy_htod(rank_matrix_gpu, rank_matrix)
    cuda.memcpy_htod(odd_even_indicator_gpu, odd_even_indicator)
    cuda.memcpy_htod(thread_done_count_gpu, thread_done_count)
    cuda.memcpy_htod(swap_done_count_gpu, swap_done_count)
    cuda.memcpy_htod(sorting_done_indicator_gpu, sorting_done_indicator)

    mod = SourceModule("""
      __global__ void dataframe_sort_by_cuda_enumeration(int first_dimension_size, int second_dimension_size, int GPU_CORE_BLOCK_SIZE_X, int GPU_CORE_BLOCK_SIZE_Y, int GPU_CORE_BLOCK_SIZE_Z, int ErrorCode, float *df_by_matrix, int *rank_matrix)
      {
        int thread_Index, Total_Thread_count;
        bool diff_found;
        ErrorCode = 0;
        Total_Thread_count = GPU_CORE_BLOCK_SIZE_X * GPU_CORE_BLOCK_SIZE_Y * GPU_CORE_BLOCK_SIZE_Z;
        thread_Index = threadIdx.x * GPU_CORE_BLOCK_SIZE_Y * GPU_CORE_BLOCK_SIZE_Z + threadIdx.y * GPU_CORE_BLOCK_SIZE_Z + threadIdx.z;
        
        while (thread_Index < first_dimension_size) {
            rank_matrix[thread_Index] = 0;
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
                        rank_matrix[thread_Index]++;
                        break;
                    }
                  }
                  if (!diff_found && check_index < thread_Index) {
                    rank_matrix[thread_Index]++;
                  }
                }
            }
            thread_Index = thread_Index + Total_Thread_count;
        }
      }
    """)
          
    func = mod.get_function("dataframe_sort_by_cuda_enumeration")
    func(np.int32(first_dimension_size), np.int32(second_dimension_size), np.int32(GPU_CORE_BLOCK_SIZE_X), np.int32(GPU_CORE_BLOCK_SIZE_Y), np.int32(GPU_CORE_BLOCK_SIZE_Z), np.int32(ErrorCode), df_by_matrix_gpu, rank_matrix_gpu, block=(GPU_CORE_BLOCK_SIZE_X,GPU_CORE_BLOCK_SIZE_Y,GPU_CORE_BLOCK_SIZE_Z))

    print('after running dataframe_sort_by_cuda at ' + str(datetime.now()))

    rank_matrix = np.zeros(first_dimension_size, dtype=np.int32)
    cuda.memcpy_dtoh(rank_matrix, rank_matrix_gpu)

    print('after memcpy_dtoh rank_matrix at ' + str(datetime.now()))

    df_by_matrix_gpu.free()
    rank_matrix_gpu.free()
    
    print('after freeing GPU memory, before creating df_sorted_index at ' + str(datetime.now()))

    df_sorted_index = pd.DataFrame(rank_matrix, columns=['rank'])
    df['rank'] = df_sorted_index['rank']

    print('before sort by ranking at ' + str(datetime.now()))

    df = df.sort_values(by=['rank'], ascending=True, inplace=False).drop(columns=['rank'])  
    print('after running sorting of df at ' + str(datetime.now()))
    return df