# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 09:51:03 2021

@author: Henry Cheung
"""
import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import os
import numpy as np

_path = r"D:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.28.29910\bin\Hostx64\x64"

if os.system("cl.exe"):
    os.environ['PATH'] += ';' + _path
if os.system("cl.exe"):
    raise RuntimeError("cl.exe still not found, path probably incorrect")

a_out = np.zeros(6)
a_out = a_out.astype(np.int32)
a_out_gpu = cuda.mem_alloc(a_out.nbytes)
cuda.memcpy_htod(a_out_gpu, a_out)

mod = SourceModule("""
//  #include <algorithm> 

  __global__ void try_algorithm_lib(int in_integer1, int in_integer2, int *out_matrix)
  {
     out_matrix[0] = in_integer1;
     out_matrix[1] = in_integer1;
     out_matrix[2] = in_integer1;
     out_matrix[3] = in_integer1;
     out_matrix[4] = in_integer1;
     out_matrix[5] = in_integer1;
  }

  """)
      
func = mod.get_function("try_algorithm_lib")
func(np.int32(1), np.int32(2), a_out_gpu, block=(1,1,1))

returned_array = np.empty_like(a_out)
cuda.memcpy_dtoh(returned_array, a_out_gpu)
print('returned array is')
print(returned_array)