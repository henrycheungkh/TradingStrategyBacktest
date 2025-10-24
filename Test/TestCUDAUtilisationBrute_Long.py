# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 09:51:03 2021

@author: Henry Cheung
"""

import os

_path = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.33.31629\bin\Hostx64\x64"

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

InitialResultCacheSize = 100000000

# Float_Numbers_matrix = np.asarray([0.005, 0.01]).astype(np.float32)
# Float_Numbers_matrix_gpu = cuda.mem_alloc(Float_Numbers_matrix.nbytes)
# cuda.memcpy_htod(Float_Numbers_matrix_gpu, Float_Numbers_matrix)
# print('Float_Numbers_matrix is')
# print(Float_Numbers_matrix)

record_result = np.zeros((InitialResultCacheSize, RESULT_COLUMN_COUNT)).astype(np.float32) 
record_result_gpu = cuda.mem_alloc(record_result.nbytes)

result_count = np.int64(0)
result_count_gpu = cuda.mem_alloc(result_count.nbytes)
cuda.memcpy_htod(result_count_gpu, result_count)

mod = SourceModule("""
  #include <cstdlib>

//  __global__ void test_cuda_atomicAdd(long InitialResultCacheSize, int RESULT_COLUMN_COUNT, int *result_count, float *record_result)
  __global__ void test_cuda_atomicAdd(long InitialResultCacheSize, int RESULT_COLUMN_COUNT, long *result_count, float *record_result)
  {
    int result_index;
    
    for (int i=0; i<3000000; i++) {
    
      result_index = atomicAdd(result_count,1);
      
      if (result_index < InitialResultCacheSize && result_index > 0) {
//      if (result_index < InitialResultCacheSize) {
        record_result[result_index * RESULT_COLUMN_COUNT] = 1;
      }
    }
  }
  """)
      
func = mod.get_function("test_cuda_atomicAdd")
func( np.int32(InitialResultCacheSize), np.int32(RESULT_COLUMN_COUNT), result_count_gpu, record_result_gpu, block=(4,16,16))

record_result = np.empty((InitialResultCacheSize, RESULT_COLUMN_COUNT), dtype=np.float32)
cuda.memcpy_dtoh(record_result, record_result_gpu)

print('record_result is with dimension ' + str(len(record_result)) + ' x ' + str(len(record_result[0])))
print(record_result)

record_result_gpu.free()