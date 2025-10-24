# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 00:11:55 2022

@author: henry
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
# import pandas as pd
import numpy as np

thread_done_count = np.int32(0)
thread_done_count_gpu = cuda.mem_alloc(thread_done_count.nbytes)
cuda.memcpy_htod(thread_done_count_gpu, thread_done_count)

a_out = np.zeros(10)
a_out = a_out.astype(np.int32)
a_out_gpu = cuda.mem_alloc(a_out.nbytes)
cuda.memcpy_htod(a_out_gpu, a_out)

mod = SourceModule("""
  __global__ void cuda_thread_wait(int *thread_done_count, int *out_matrix)
  {
     int new_thread_done_count;
     if (threadIdx.z <= 0) {
        while (thread_done_count[0] < 4) {
          __nanosleep(100);
        }
        out_matrix[0] = thread_done_count[0];
     } else {
        new_thread_done_count = atomicAdd(thread_done_count,1);
     }
  }
  """)
      
func = mod.get_function("cuda_thread_wait")
func(thread_done_count_gpu, a_out_gpu, block=(1,1,5))

returned_array = np.empty_like(a_out)
cuda.memcpy_dtoh(returned_array, a_out_gpu)
print('returned array is')
print(returned_array)