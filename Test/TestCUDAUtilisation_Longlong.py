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

RESULT_COLUMN_COUNT = 4

# InitialResultCacheSize = 500
InitialResultCacheSize = 350000000
InitialResultCacheSize = 300000000

number_matrix = np.zeros(InitialResultCacheSize * RESULT_COLUMN_COUNT)
number_matrix = number_matrix.astype(np.float32)

number_matrix_gpu = cuda.mem_alloc(number_matrix.nbytes)
cuda.memcpy_htod(number_matrix_gpu, number_matrix)

result_count = np.zeros(1, dtype=np.int32)
# result_count = np.zeros(1, dtype=np.int64)
result_count_gpu = cuda.mem_alloc(result_count.nbytes)
cuda.memcpy_htod(result_count_gpu, result_count)

real_result_count = np.zeros(1, dtype=np.int32)
# real_result_count = np.zeros(1, dtype=np.int64)
real_result_count_gpu = cuda.mem_alloc(real_result_count.nbytes)
cuda.memcpy_htod(real_result_count_gpu, real_result_count)

mod = SourceModule("""
  #include <cstdlib>

//    __global__ void test_cuda_utilisation(int InitialResultCacheSize, int RESULT_COLUMN_COUNT, float *number_matrix, unsigned long long *result_count, unsigned long long *real_result_count)
//    __global__ void test_cuda_utilisation(int InitialResultCacheSize, int RESULT_COLUMN_COUNT, float *number_matrix, long *result_count, long *real_result_count)
    __global__ void test_cuda_utilisation(int InitialResultCacheSize, int RESULT_COLUMN_COUNT, float *number_matrix, int *result_count, int *real_result_count)
  {
     unsigned long long result_index, real_result_index, result_index_offset;
     for (int i=0; i<300000; i++) {
             
       result_index = atomicAdd(result_count, 1);
       if (result_index < InitialResultCacheSize - 30) {
         result_index_offset = result_index * RESULT_COLUMN_COUNT;
         number_matrix[result_index_offset + 0] = result_index;
         number_matrix[result_index_offset + 1] = result_count[0];
         number_matrix[result_index_offset + 2] = InitialResultCacheSize;
         number_matrix[result_index_offset + 3] = RESULT_COLUMN_COUNT;
         real_result_index = atomicAdd(real_result_count, 1);
       }             
             
    }

  }
  """)

func = mod.get_function("test_cuda_utilisation")
func(np.int32(InitialResultCacheSize), np.int32(RESULT_COLUMN_COUNT), number_matrix_gpu, result_count_gpu, real_result_count_gpu, block=(4,16,16))

result_count_out = np.empty_like(result_count)
cuda.memcpy_dtoh(result_count_out, result_count_gpu)

real_result_count_out = np.empty_like(real_result_count)
cuda.memcpy_dtoh(real_result_count_out, real_result_count_gpu)

print('result_count_out = ' + str(result_count_out) + ' and InitialResultCacheSize = ' + str(InitialResultCacheSize) + ' and real_result_count_out = ' + str(real_result_count_out))

# number_matrix_out = np.empty((InitialResultCacheSize, RESULT_COLUMN_COUNT), dtype=np.float32)
number_matrix_out = np.empty((real_result_count_out[0], RESULT_COLUMN_COUNT), dtype=np.float32)
cuda.memcpy_dtoh(number_matrix_out, number_matrix_gpu)

print('number_matrix_out is with len ' + str(len(number_matrix_out)) + ' x ' + str(len(number_matrix_out[0])))
print(number_matrix_out)

