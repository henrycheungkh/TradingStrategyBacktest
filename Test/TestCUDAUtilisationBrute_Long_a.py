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

InitianCount = 0

record_result = np.zeros((100000000, 4)).astype(np.float32) 
record_result_gpu = cuda.mem_alloc(record_result.nbytes)

# result_count = np.int64(0)
result_count = np.zeros(1, dtype=np.int64)
result_count_gpu = cuda.mem_alloc(result_count.nbytes)
cuda.memcpy_htod(result_count_gpu, result_count)

print('result_count.nbytes is ' + str(result_count.nbytes))

mod = SourceModule("""
  #include <cstdlib>

  __global__ void test_cuda_LongIntArray(long InitianCount, int *result_count, float *record_result)
//  __global__ void test_cuda_LongIntArray(long InitianCount, long *result_count, float *record_result)
  {
      long result_index;
      result_index = atomicAdd(result_count,1);
//      result_index = atomicAdd(&InitianCount,1);
  }
  """)
      
func = mod.get_function("test_cuda_LongIntArray")
func( np.int64(InitianCount), result_count_gpu, record_result_gpu, block=(4,16,16))

record_result = np.empty((100000000, 4), dtype=np.float32)
cuda.memcpy_dtoh(record_result, record_result_gpu)

print('record_result is with dimension ' + str(len(record_result)) + ' x ' + str(len(record_result[0])))
print(record_result)

record_result_gpu.free()