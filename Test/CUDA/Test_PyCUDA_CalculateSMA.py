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
import math

_path = r"D:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.28.29910\bin\Hostx64\x64"

if os.system("cl.exe"):
   os.environ['PATH'] += ';' + _path
if os.system("cl.exe"):
   raise RuntimeError("cl.exe still not found, path probably incorrect")

import numpy

# ticker_size = 32*32*2 - 1
time_size = 5
ticker_block_size = 10
# ticker_block_count = math.ceil(ticker_size/ticker_block_size)
# print("ticker_block_count = " + str(ticker_block_count))
MA_Day = 2
# MA_Day = 20

a = numpy.random.randn(ticker_block_size, time_size)
b = numpy.zeros((ticker_block_size, time_size))

a = a.astype(numpy.float32)
b = b.astype(numpy.float32)

a_gpu = cuda.mem_alloc(a.nbytes)

cuda.memcpy_htod(a_gpu, a)

b_gpu = cuda.mem_alloc(b.nbytes)

cuda.memcpy_htod(b_gpu, b)

mod = SourceModule("""
  __global__ void sma(float *a, float *b, int time_size, int ticker_block_size, int MA_day)
  {

      for (int i = MA_day-1; i < time_size; i++) {
        for (int j = i-MA_day+1; j < i + 1; j++) {
          b[threadIdx.y*time_size + i] = b[threadIdx.y*time_size + i] + a[threadIdx.y*time_size + j];
        }
      }

      for (int i = MA_day-1; i < time_size; i++) {
        b[threadIdx.y*time_size + i] = b[threadIdx.y*time_size + i] / MA_day;
      }
  }
  """)
      
func = mod.get_function("sma")
func(a_gpu, b_gpu, numpy.int32(time_size), numpy.int32(ticker_block_size), numpy.int32(MA_Day), block=(1,ticker_block_size,1))

sma = numpy.empty_like(b)
cuda.memcpy_dtoh(sma, b_gpu)
print (sma)
print (a)
print(sma[1][0])
print(sma[2][0])
print(sma[3][0])