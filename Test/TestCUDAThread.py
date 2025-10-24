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

GPU_CORE_BLOCK_SIZE_X = 8
GPU_CORE_BLOCK_SIZE_Y = 8
GPU_CORE_BLOCK_SIZE_Z = 16

a_out = np.zeros(GPU_CORE_BLOCK_SIZE_X * GPU_CORE_BLOCK_SIZE_Y * GPU_CORE_BLOCK_SIZE_Z)
a_out = a_out.astype(np.float32)
a_out = a_out.astype(np.int32)
# a_out = a_out.astype(np.int16)
a_out_gpu = cuda.mem_alloc(a_out.nbytes)
cuda.memcpy_htod(a_out_gpu, a_out)

mod = SourceModule("""
  __global__ void matrix_core_thread_trial(int GPU_CORE_BLOCK_SIZE_Y, int GPU_CORE_BLOCK_SIZE_Z, int *out_matrix)
  {
     out_matrix[threadIdx.x * GPU_CORE_BLOCK_SIZE_Y * GPU_CORE_BLOCK_SIZE_Z + threadIdx.y * GPU_CORE_BLOCK_SIZE_Z + threadIdx.z] = threadIdx.x * GPU_CORE_BLOCK_SIZE_Y * GPU_CORE_BLOCK_SIZE_Z + threadIdx.y * GPU_CORE_BLOCK_SIZE_Z + threadIdx.z + 1;
  }
  """)
      
func = mod.get_function("matrix_core_thread_trial")
func(np.int32(GPU_CORE_BLOCK_SIZE_Y), np.int32(GPU_CORE_BLOCK_SIZE_Z), a_out_gpu, block=(GPU_CORE_BLOCK_SIZE_X,GPU_CORE_BLOCK_SIZE_Y,GPU_CORE_BLOCK_SIZE_Z))

returned_array = np.empty_like(a_out)
cuda.memcpy_dtoh(returned_array, a_out_gpu)
print('returned array is')
print(returned_array)