# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 15:37:06 2021

@author: Henry Cheung
"""


import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import math
import pandas as pd
import InvestmentAnalytics.CUDA.CUDAPathSetting
import numpy as np
import InvestmentAnalytics.Config as Config

# GPU_CORE_BLOCK_SIZE = 32*32
GPU_CORE_TOTAL_THREAD_SIZE = Config.CONFIG_CUDA_ThreadCount
GPU_CORE_BLOCK_SIZE = min(1024,GPU_CORE_TOTAL_THREAD_SIZE)
GPU_CORE_GRID_SIZE = math.ceil(GPU_CORE_TOTAL_THREAD_SIZE / 1024)

def CUDAFillModifiedFollowing(data_matrix, block_cutting_dimension = "First Dimension", ModifyBackwardAsLastResort = False):
    if ModifyBackwardAsLastResort:
        ModifyBackwardAsLastResortFlag = 1
    else:
        ModifyBackwardAsLastResortFlag = 0
        
    ticker_size = len(data_matrix)
    time_size = len(data_matrix[0])
    # gpu_core_block_count = math.ceil(ticker_size/GPU_CORE_BLOCK_SIZE)
    gpu_core_block_count = math.ceil(ticker_size/(GPU_CORE_BLOCK_SIZE * GPU_CORE_GRID_SIZE))

    # pending_zeros = np.zeros((GPU_CORE_BLOCK_SIZE*gpu_core_block_count - ticker_size, time_size))
    
    data_matrix = data_matrix.astype(np.float32).copy(order="C")
    # a = a.astype(np.float32)
    # a = a.copy(order="C")
    
    data_matrix_gpu = cuda.mem_alloc(data_matrix.nbytes)
    cuda.memcpy_htod(data_matrix_gpu, data_matrix)

    mod = SourceModule("""
      __global__ void fill_modified_following(int time_size, int gpu_core_block_count, int ticker_size, float *data, int ModifyBackwardAsLastResortFlag)
      {
        int thread_Index, GPU_CORE_BLOCK_SIZE;
        GPU_CORE_BLOCK_SIZE = blockDim.x * gridDim.x;
        thread_Index = blockIdx.x * blockDim.x + threadIdx.x;
        for (int k = 0; k < gpu_core_block_count; k++) {
          if (k * GPU_CORE_BLOCK_SIZE + thread_Index < ticker_size) {
            for (int i = 1; i < time_size; i++) {
              if (data[k * GPU_CORE_BLOCK_SIZE * time_size + thread_Index*time_size + i] == 0) {
                data[k * GPU_CORE_BLOCK_SIZE * time_size + thread_Index*time_size + i] = data[k * GPU_CORE_BLOCK_SIZE * time_size + thread_Index*time_size + i - 1];
              }
            }
          }
        }
        
        if (ModifyBackwardAsLastResortFlag == 1) {
          for (int k = 0; k < gpu_core_block_count; k++) {
            if (k * GPU_CORE_BLOCK_SIZE + thread_Index < ticker_size) {
              for (int i = time_size - 1; i >= 1; i--) {
                if (data[k * GPU_CORE_BLOCK_SIZE * time_size + thread_Index*time_size + i - 1] == 0) {
                  data[k * GPU_CORE_BLOCK_SIZE * time_size + thread_Index*time_size + i - 1] = data[k * GPU_CORE_BLOCK_SIZE * time_size + thread_Index*time_size + i];
                }
              }
            }
          }
        }
      }
      """)
          
    func = mod.get_function("fill_modified_following")
    func(np.int32(time_size), np.int32(gpu_core_block_count), np.int32(ticker_size), data_matrix_gpu, np.int32(ModifyBackwardAsLastResortFlag), block=(GPU_CORE_BLOCK_SIZE,1,1), grid=(GPU_CORE_GRID_SIZE, 1))

    data_matrix_after_modified_following = np.empty_like(data_matrix)
    cuda.memcpy_dtoh(data_matrix_after_modified_following, data_matrix_gpu)
    
    data_matrix_gpu.free()
    
    return data_matrix_after_modified_following[0:ticker_size]

def CUDAFillByOverride(data_matrix, override_matrix, block_cutting_dimension = "Ticker Dimension"):
    if block_cutting_dimension == "Time Dimension":
        data_matrix = data_matrix.T
        override_matrix = override_matrix.T
    first_dimension_size = len(data_matrix)
    second_dimension_size = len(data_matrix[0])
    
    # gpu_core_block_count = math.ceil(first_dimension_size/GPU_CORE_BLOCK_SIZE)
    gpu_core_block_count = math.ceil(first_dimension_size/(GPU_CORE_BLOCK_SIZE * GPU_CORE_GRID_SIZE))
    # pending_zeros = np.zeros((GPU_CORE_BLOCK_SIZE*gpu_core_block_count - first_dimension_size, second_dimension_size))
    
    data_matrix = data_matrix.astype(np.float32)
    override_matrix = override_matrix.astype(np.float32)
    # a = a.astype(np.float32)
    # b = b.astype(np.float32)
    
    data_matrix_gpu = cuda.mem_alloc(data_matrix.nbytes)
    override_matrix_gpu = cuda.mem_alloc(override_matrix.nbytes)
    
    cuda.memcpy_htod(data_matrix_gpu, data_matrix)
    cuda.memcpy_htod(override_matrix_gpu, override_matrix)

    mod = SourceModule("""
      __global__ void fill_by_override(int second_dimension_size, int gpu_core_block_count, int first_dimension_size, float *data, float *override_data)
      {
        int thread_Index, GPU_CORE_BLOCK_SIZE;
        GPU_CORE_BLOCK_SIZE = blockDim.x * gridDim.x;
        thread_Index = blockIdx.x * blockDim.x + threadIdx.x;
    
        for (int k = 0; k < gpu_core_block_count; k++) {
          if (k * GPU_CORE_BLOCK_SIZE + thread_Index < first_dimension_size) {
            for (int i = 0; i < second_dimension_size; i++) {
              if (data[k * GPU_CORE_BLOCK_SIZE * second_dimension_size + thread_Index*second_dimension_size + i] == 0) {
                data[k * GPU_CORE_BLOCK_SIZE * second_dimension_size + thread_Index*second_dimension_size + i] = override_data[k * GPU_CORE_BLOCK_SIZE * second_dimension_size + thread_Index*second_dimension_size + i];
              }
            }
          }
        }
      }
      """)
          
    func = mod.get_function("fill_by_override")
    func(np.int32(second_dimension_size), np.int32(gpu_core_block_count), np.int32(first_dimension_size), data_matrix_gpu, override_matrix_gpu, block=(GPU_CORE_BLOCK_SIZE,1,1), grid=(GPU_CORE_GRID_SIZE, 1))

    data_matrix_after_fill_by_override = np.empty_like(data_matrix)
    cuda.memcpy_dtoh(data_matrix_after_fill_by_override, data_matrix_gpu)
    
    return_matrix = data_matrix_after_fill_by_override[0:first_dimension_size]
    if block_cutting_dimension == "Time Dimension":
        return_matrix = return_matrix.T
        
    data_matrix_gpu.free()
    override_matrix_gpu.free()
    
    return return_matrix
    

def CUDAGetTickerIDWithSufficientData(data_matrix, DataAvailabilityPercentageLimit):
    ticker_size = len(data_matrix)
    time_size = len(data_matrix[0])
    # gpu_core_block_count = math.ceil(ticker_size/GPU_CORE_BLOCK_SIZE)
    gpu_core_block_count = math.ceil(ticker_size/(GPU_CORE_BLOCK_SIZE * GPU_CORE_GRID_SIZE))
    
    pending_zeros = np.zeros((GPU_CORE_BLOCK_SIZE*gpu_core_block_count - ticker_size, time_size))
    
    # a = np.concatenate((data_matrix, pending_zeros))
    available_pct_matrix = np.zeros(GPU_CORE_BLOCK_SIZE*gpu_core_block_count).astype(np.float32)
    
    data_matrix = data_matrix.astype(np.float32)
    # a = a.copy(order="C")
    # b = b.astype(np.float32)
    
    data_matrix_gpu = cuda.mem_alloc(data_matrix.nbytes)
    
    cuda.memcpy_htod(data_matrix_gpu, data_matrix)
    
    available_pct_matrix_gpu = cuda.mem_alloc(available_pct_matrix.nbytes)
    
    cuda.memcpy_htod(available_pct_matrix_gpu, available_pct_matrix)

    mod = SourceModule("""
      __global__ void get_data_available_pct(int time_size, int gpu_core_block_count, int ticker_size, float *data, float *available_pct)
      {
    
        int thread_Index, GPU_CORE_BLOCK_SIZE;
        GPU_CORE_BLOCK_SIZE = blockDim.x * gridDim.x;
        thread_Index = blockIdx.x * blockDim.x + threadIdx.x;
        
        for (int k = 0; k < gpu_core_block_count; k++) {
          if (k * GPU_CORE_BLOCK_SIZE + thread_Index < ticker_size) {
            for (int i = 0; i < time_size; i++) {
              if (data[k * GPU_CORE_BLOCK_SIZE * time_size + thread_Index*time_size + i] != 0) {
                available_pct[k * GPU_CORE_BLOCK_SIZE + thread_Index]++;
              }
            }
            available_pct[k * GPU_CORE_BLOCK_SIZE + thread_Index] = available_pct[k * GPU_CORE_BLOCK_SIZE + thread_Index] / time_size;
          }
        }
      }
      """)
          
    func = mod.get_function("get_data_available_pct")
    func(np.int32(time_size), np.int32(gpu_core_block_count), np.int32(ticker_size), data_matrix_gpu, available_pct_matrix_gpu, block=(GPU_CORE_BLOCK_SIZE,1,1), grid=(GPU_CORE_GRID_SIZE, 1))

    available_pct = np.empty_like(available_pct_matrix)
    cuda.memcpy_dtoh(available_pct, available_pct_matrix_gpu)
    
    df = pd.DataFrame(available_pct, columns=['available_pct'])
    df['ticker id'] = df.index
    df = df.loc[df['available_pct'] > DataAvailabilityPercentageLimit]
    
    data_matrix_gpu.free()
    available_pct_matrix_gpu.free()
    
    return df
