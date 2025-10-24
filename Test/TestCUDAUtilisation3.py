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

# InitialResultCacheSize = 10000
InitialResultCacheSize = 500


number_matrix = np.zeros(InitialResultCacheSize * RESULT_COLUMN_COUNT)
number_matrix = number_matrix.astype(np.float32)

number_matrix_gpu = cuda.mem_alloc(number_matrix.nbytes)
cuda.memcpy_htod(number_matrix_gpu, number_matrix)

result_count = 0

mod = SourceModule("""
  #include <cstdlib>

    __global__ void test_cuda_utilisation(int InitialResultCacheSize, int RESULT_COLUMN_COUNT, int result_count, float *number_matrix)
  {
     int result_index, result_index_offset;
     
     result_index = atomicAdd(&result_count,1);
     if (result_index < InitialResultCacheSize - 1) {
       result_index_offset = result_index * RESULT_COLUMN_COUNT;
       number_matrix[result_index_offset + 0] = result_index;
       number_matrix[result_index_offset + 1] = result_count;
       number_matrix[result_index_offset + 2] = InitialResultCacheSize;
       number_matrix[result_index_offset + 3] = RESULT_COLUMN_COUNT;
     }
  }
  """)
      
func = mod.get_function("test_cuda_utilisation")
func(np.int32(InitialResultCacheSize), np.int32(RESULT_COLUMN_COUNT), np.int32(result_count), number_matrix_gpu, block=(4,16,16))

print('result_count = ' + str(result_count) + ' and InitialResultCacheSize = ' + str(InitialResultCacheSize))

# number_matrix_out = np.empty((InitialResultCacheSize, RESULT_COLUMN_COUNT), dtype=np.float32)
# # number_matrix_out = np.empty((result_count_out, RESULT_COLUMN_COUNT), dtype=np.float32)
# cuda.memcpy_dtoh(number_matrix_out, number_matrix_gpu)

# print('number_matrix_out is with len ' + str(len(number_matrix_out)) + ' x ' + str(len(number_matrix_out[0])))
# print(number_matrix_out)

