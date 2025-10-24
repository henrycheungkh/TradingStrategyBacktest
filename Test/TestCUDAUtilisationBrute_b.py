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

TRADE_RESULT_COLUMN_COUNT = 4

InitialResultCacheSize = 100000000
# InitialResultCacheSize = 5000
# InitialResultCacheSize = 250000000


ObsPeriodMovementThreshold_matrix = np.asarray([0.005, 0.01]).astype(np.float32)
ObsPeriodMovementThreshold_matrix_gpu = cuda.mem_alloc(ObsPeriodMovementThreshold_matrix.nbytes)
cuda.memcpy_htod(ObsPeriodMovementThreshold_matrix_gpu, ObsPeriodMovementThreshold_matrix)

trade_result = np.zeros((InitialResultCacheSize, TRADE_RESULT_COLUMN_COUNT)).astype(np.float32) 
trade_result_gpu = cuda.mem_alloc(trade_result.nbytes)

trade_result_count = np.int32(0)
trade_result_count_gpu = cuda.mem_alloc(trade_result_count.nbytes)
cuda.memcpy_htod(trade_result_count_gpu, trade_result_count)

mod = SourceModule("""
  #include <cstdlib>

  __global__ void correlation_on_specific_time_section_analysis(int InitialResultCacheSize, int TRADE_RESULT_COLUMN_COUNT, int *trade_result_count, float *trade_result)
  {
    int trade_result_index;
    
    for (int i=0; i<3000000; i++) {
//    for (int i=0; i<2000000; i++) {
    
      trade_result_index = atomicAdd(trade_result_count,1);
      
      if (trade_result_index < InitialResultCacheSize) {
        trade_result[trade_result_index * TRADE_RESULT_COLUMN_COUNT] = InitialResultCacheSize;
      }
    }
  }
  """)
      
func = mod.get_function("correlation_on_specific_time_section_analysis")
func( np.int32(InitialResultCacheSize), np.int32(TRADE_RESULT_COLUMN_COUNT), trade_result_count_gpu, trade_result_gpu, block=(4,16,16))

trade_record = np.empty((InitialResultCacheSize, TRADE_RESULT_COLUMN_COUNT), dtype=np.float32)
cuda.memcpy_dtoh(trade_record, trade_result_gpu)

print('trade_record is with dimension ' + str(len(trade_record)) + ' x ' + str(len(trade_record[0])))
print(trade_record)