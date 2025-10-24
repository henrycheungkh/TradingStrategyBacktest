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

import numpy as np

a = np.zeros(1000000000).astype(np.float32)
a_gpu = cuda.mem_alloc(a.nbytes)
cuda.memcpy_htod(a_gpu, a)

mod = SourceModule("""
  __global__ void func1(float *a)
  {
    a[0] = 1;
  }
  """)
      
func = mod.get_function("func1")
func(a_gpu, block=(1,1,1))

a_out = np.empty_like(a)
cuda.memcpy_dtoh(a_out, a_gpu)
print (a_out)

# a_gpu.free()

# cuda.free()
print(cuda.mem_get_info())

# Memory release code wanted here

b = np.zeros(1000000000).astype(np.float32)
b_gpu = cuda.mem_alloc(b.nbytes)
cuda.memcpy_htod(b_gpu, b)

mod = SourceModule("""
  __global__ void func2(float *b)
  {
    b[1] = 1;
  }
  """)
      
func = mod.get_function("func2")
func(b_gpu, block=(1,1,1))

b_out = np.empty_like(b)
cuda.memcpy_dtoh(b_out, b_gpu)
print (b_out)


