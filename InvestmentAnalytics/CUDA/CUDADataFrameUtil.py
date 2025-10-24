# -*- coding: utf-8 -*-

"""
Created on Wed Apr  3 23:52:45 2019

@author: hc39138

"""

import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import InvestmentAnalytics.CUDA.CUDAPathSetting

import pandas as pd
import numpy as np
from datetime import datetime
import math

GPU_CORE_BLOCK_SIZE = 32 * 32
DATAFRAME_BLOCK_SIZE = 2000000
# GPU_CORE_BLOCK_SIZE = 1
# DATAFRAME_BLOCK_SIZE = 2

def CUDAMapByLookup(df, lookup_key_columns, df_lookup, Debug = False, DebugKey = 0):
    df_key_columns_full = df[lookup_key_columns]
    mapped_df_all = pd.DataFrame()
    
    block_start = 0
    while block_start < len(df_key_columns_full):
        df_key_columns = df_key_columns_full.iloc[block_start:block_start+DATAFRAME_BLOCK_SIZE].copy().reset_index(drop=True)
    
        df_key_columns_matrix = df_key_columns.to_numpy()
        df_lookup_matrix = df_lookup.to_numpy()
        lookup_data_columns = df_lookup.columns.values.tolist()
        for key in lookup_key_columns:
            lookup_data_columns.remove(key)
        if Debug:
            print('lookup_data_columns is')
            print(lookup_data_columns)
        
        first_dimension_size = len(df_key_columns_matrix)
        second_dimension_size = len(lookup_key_columns)
        lookup_data_column_count = len(lookup_data_columns)
        lookup_data_row_count = len(df_lookup)
        gpu_core_block_count = math.ceil(first_dimension_size/GPU_CORE_BLOCK_SIZE)
        
        if Debug:
            print('lookup_data_column_count is ' + str(lookup_data_column_count))
    
        pending_zeros = np.zeros((GPU_CORE_BLOCK_SIZE*gpu_core_block_count - first_dimension_size, second_dimension_size))
        a = np.concatenate((df_key_columns_matrix, pending_zeros))
        
        a_out = np.zeros((GPU_CORE_BLOCK_SIZE*gpu_core_block_count,lookup_data_column_count))
        a = a.astype(np.float32)
        a = a.copy(order="C")
        df_lookup_matrix = df_lookup_matrix.astype(np.float32)
        df_lookup_matrix = df_lookup_matrix.copy(order="C")
        
        # print('df_key_columns_matrix is')
        # print(df_key_columns_matrix)
        # print('df_lookup_matrix is')
        # print(df_lookup_matrix)
        
        a_out = a_out.astype(np.float32)
        a_gpu = cuda.mem_alloc(a.nbytes)
        b_gpu = cuda.mem_alloc(df_lookup_matrix.nbytes)
        a_out_gpu = cuda.mem_alloc(a_out.nbytes)
        cuda.memcpy_htod(a_gpu, a)
        cuda.memcpy_htod(b_gpu, df_lookup_matrix)
        cuda.memcpy_htod(a_out_gpu, a_out)
        
        ErrorCode = 0
    
        mod = SourceModule("""
          __global__ void map_by_lookup(int key_column_count, int GPU_CORE_BLOCK_SIZE, int gpu_core_block_count, int data_row_count, int lookup_data_column_count, int lookup_data_row_count, int ErrorCode, float *df_key_columns_matrix, float *df_lookup_matrix, float *mapped_matrix)
          {
            //int block_start_pointer, next_block_start_pointer, block_row_offset, trade_id_index, prior_trade_id_index;
            int block_start_pointer, next_block_start_pointer;
            bool no_diff_in_key;
            
            block_start_pointer = (int) threadIdx.y * data_row_count / GPU_CORE_BLOCK_SIZE;
            next_block_start_pointer = (int) (threadIdx.y+1) * data_row_count / GPU_CORE_BLOCK_SIZE;
            if (next_block_start_pointer > data_row_count) {
              next_block_start_pointer = data_row_count;
            }
            for (int i=block_start_pointer; i<next_block_start_pointer; i++) {
              for (int j=0; j<lookup_data_row_count; j++) {
                no_diff_in_key = true;
                for (int k=0; k<key_column_count; k++) {
                  if (df_key_columns_matrix[i*key_column_count + k] != df_lookup_matrix[j*(key_column_count + lookup_data_column_count) + k]) {
                    no_diff_in_key = false;
                    break;
                  }
                }
                if (no_diff_in_key) {
                  for (int k=0; k<lookup_data_column_count; k++) {
                    mapped_matrix[i*lookup_data_column_count + k] = df_lookup_matrix[j*(key_column_count + lookup_data_column_count) + key_column_count + k];
                  }
                  break;
                }
              }
            }
          }
          """)
              
        func = mod.get_function("map_by_lookup")
        func(np.int32(second_dimension_size), np.int32(GPU_CORE_BLOCK_SIZE), np.int32(gpu_core_block_count), np.int32(first_dimension_size), np.int32(lookup_data_column_count), np.int32(lookup_data_row_count), np.int32(ErrorCode),  a_gpu,  b_gpu, a_out_gpu, block=(1,GPU_CORE_BLOCK_SIZE,1))
        
        mapped_matrix = np.empty_like(a_out)
        cuda.memcpy_dtoh(mapped_matrix, a_out_gpu)
    
        mapped_matrix = mapped_matrix[0:first_dimension_size]
        if Debug:
            print('mapped_matrix is')
            print(mapped_matrix)
            print('lookup_data_columns is')
            print(lookup_data_columns)
    
        mapped_df = pd.DataFrame(mapped_matrix,  columns=lookup_data_columns)
        
        # mapped_df.reset_index(drop=True, inplace=True)
        
        
        if Debug:
            print('mapped_df is')
            print(mapped_df)
            print('df is')
            print(df)
        
        # df_concat = pd.concat([df, mapped_df], axis=1)
        # print('df_concat is')
        # print(df_concat)
        
        # return df_concat
            
        
    
        mapped_df_all = mapped_df_all.append(mapped_df)
        
        block_start = block_start + DATAFRAME_BLOCK_SIZE
    
    df.reset_index(drop=True, inplace=True)
    mapped_df_all.reset_index(drop=True, inplace=True)
    print('df is')
    print(df)
    print('mapped_df_all is')
    print(mapped_df_all)
    
    return pd.concat([df, mapped_df_all], axis=1)
    

    

