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

a = np.asarray([1, 2])
a = a.astype(np.int32)
a_gpu = cuda.mem_alloc(a.nbytes)
cuda.memcpy_htod(a_gpu, a)

b = np.zeros(1).astype(np.int32)
b_gpu = cuda.mem_alloc(b.nbytes)
cuda.memcpy_htod(b_gpu, b)

mod = SourceModule("""
  __global__ void array_declaration(int *in_matrix, int *out_matrix, int in_integer)
  {
    //int d[1];
    int d[in_integer];
    //int d[in_matrix[0]];
    out_matrix[0] = in_matrix[0];
  }
  """)
      
func = mod.get_function("array_declaration")
func(a_gpu, b_gpu, np.int32(1), block=(1,1,1))

b_out = np.empty_like(b)
cuda.memcpy_dtoh(b_out, b_gpu)
print(b_out)
