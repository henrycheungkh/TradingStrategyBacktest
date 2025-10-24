# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 09:18:07 2021

@author: Henry Cheung
"""

# https://documen.tician.de/pycuda/tutorial.html
# https://www.programmersought.com/article/62996340674/


import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import os

_path = r"D:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.28.29910\bin\Hostx64\x64"

if os.system("cl.exe"):
   os.environ['PATH'] += ';' + _path
if os.system("cl.exe"):
   raise RuntimeError("cl.exe still not found, path probably incorrect")

import numpy

BLOCK_SIZE = 2*2

x_size = 1

a = numpy.random.randn(BLOCK_SIZE)
a = a.astype(numpy.float32)
a_gpu = cuda.mem_alloc(a.nbytes)
cuda.memcpy_htod(a_gpu, a)

b = numpy.int32(0)
b_gpu = cuda.mem_alloc(b.nbytes)
cuda.memcpy_htod(b_gpu, b)

mod = SourceModule("""
  __global__ void getIndex(float *a, int x_size, int *b)
  {
    int idx = threadIdx.x + threadIdx.y*x_size;
    a[idx] = atomicAdd(b,1);
  }
  """)
      
func = mod.get_function("getIndex")

func(a_gpu, numpy.int32(x_size), b_gpu, block=(1,BLOCK_SIZE,1))

a_index = numpy.empty_like(a)
cuda.memcpy_dtoh(a_index, a_gpu)
b_index = numpy.empty_like(b)
cuda.memcpy_dtoh(b_index, b_gpu)
print (a_index)
print (x_size)
print (b_index)
