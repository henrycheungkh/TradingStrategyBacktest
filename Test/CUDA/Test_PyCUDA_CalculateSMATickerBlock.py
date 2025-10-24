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

import numpy as np

TICKER_BLOCK_SIZE = 32*32
MA_Day = 2
# MA_Day = 20


# ticker_size = TICKER_BLOCK_SIZE * 10 - 3

# time_size = 10000
# time_size = 5

closing_prices = np.random.randn(TICKER_BLOCK_SIZE * 10 - 2, 5)


ticker_size = len(closing_prices)
time_size = len(closing_prices[0])
ticker_block_count = math.ceil(ticker_size/TICKER_BLOCK_SIZE)

print(len(closing_prices))
print(len(closing_prices[0]))

pending_zeros = np.zeros((TICKER_BLOCK_SIZE*ticker_block_count - ticker_size, time_size))

# a = closing_prices.append(pending_zeros)
a = np.concatenate((closing_prices, pending_zeros))
b = np.zeros((TICKER_BLOCK_SIZE*ticker_block_count, time_size))

# ticker_size = 6
# TICKER_BLOCK_SIZE = 5


# a = np.random.randn(TICKER_BLOCK_SIZE*ticker_block_count, time_size)
# b = np.zeros((TICKER_BLOCK_SIZE*ticker_block_count, time_size))

a = a.astype(np.float32)
b = b.astype(np.float32)

a_gpu = cuda.mem_alloc(a.nbytes)

cuda.memcpy_htod(a_gpu, a)

b_gpu = cuda.mem_alloc(b.nbytes)

cuda.memcpy_htod(b_gpu, b)

# data = (a_gpu, b_gpu, np.int32(MA_Day))

mod = SourceModule("""
  __global__ void sma(int time_size, int ticker_block_size, int ticker_block_count, int ticker_size, float *a, float *b, int MA_day)
  {

    for (int k = 0; k < ticker_block_count; k++) {
      if (k * ticker_block_size + threadIdx.y < ticker_size) {
        for (int i = MA_day-1; i < time_size; i++) {
          for (int j = i-MA_day+1; j < i + 1; j++) {
            b[k * ticker_block_size * time_size + threadIdx.y*time_size + i] = b[k * ticker_block_size * time_size + threadIdx.y*time_size + i] + a[k * ticker_block_size * time_size + threadIdx.y*time_size + j];
          }
        }

        for (int i = MA_day-1; i < time_size; i++) {
          b[k * ticker_block_size * time_size + threadIdx.y*time_size + i] = b[k * ticker_block_size * time_size + threadIdx.y*time_size + i] / MA_day;
        }
      }
    }
  }
  """)
      
func = mod.get_function("sma")
func(np.int32(time_size), np.int32(TICKER_BLOCK_SIZE), np.int32(ticker_block_count), np.int32(ticker_size), a_gpu, b_gpu, np.int32(MA_Day), block=(1,TICKER_BLOCK_SIZE,1))
# func(np.int32(time_size), np.int32(TICKER_BLOCK_SIZE), np.int32(ticker_block_count), np.int32(ticker_size), data , block=(1,TICKER_BLOCK_SIZE,1))

sma = np.empty_like(b)
cuda.memcpy_dtoh(sma, b_gpu)
sma = sma[0:ticker_size]

print (sma)
print (closing_prices)
print(sma[1][0])
print(sma[2][0])
print(sma[3][0])
