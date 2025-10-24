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

x_size = 6
y_size = 4

a = numpy.random.randn(x_size,y_size)
b = numpy.zeros((x_size,y_size))

a = a.astype(numpy.float32)
b = b.astype(numpy.float32)

a_gpu = cuda.mem_alloc(a.nbytes)

cuda.memcpy_htod(a_gpu, a)

b_gpu = cuda.mem_alloc(b.nbytes)

cuda.memcpy_htod(b_gpu, b)


mod = SourceModule("""
  __global__ void doublify(float *a, float *b, int x_size, int y_size)
  {
    int idx = threadIdx.x + threadIdx.y*x_size;
    b[idx] = a[idx] * 2;
  }
  """)
      
func = mod.get_function("doublify")
func(a_gpu, b_gpu, numpy.int32(x_size), numpy.int32(y_size), block=(x_size,y_size,1))

a_doubled = numpy.empty_like(b)
cuda.memcpy_dtoh(a_doubled, b_gpu)
print (a_doubled)
print (a)
