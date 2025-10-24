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

a = np.array([[1000, 100, 200, 300], [1000, 100, 200, 300], [1000, 100, 200, 300]]).astype(np.float32).copy(order="C")

print('input array is')
print(a)
a_gpu = cuda.mem_alloc(a.nbytes)
cuda.memcpy_htod(a_gpu, a)

a_out = np.zeros(6)
a_out = a_out.astype(np.float32)
a_out_gpu = cuda.mem_alloc(a_out.nbytes)
cuda.memcpy_htod(a_out_gpu, a_out)

mod = SourceModule("""
//    #include <math.h>                   

//      #include <cstdlib>
//      #include <cmath>  

      __device__ int ceil_reinvented( float f)
      {
        int i;
        i = (int) f;
        if (f > i) {
          return i + 1;
        } else {
          return i;
        }
      }
  __global__ void test_ceil(int in_integer, float *in_matrix, float *out_matrix)
  {
     float f;
     f = static_cast<float> (in_matrix[0]/in_integer);
//     f = (float) (in_matrix[0]/in_integer);

//     out_matrix[0] = ceil( f );
     out_matrix[0] = ceil_reinvented(f);
     out_matrix[1] = ceil_reinvented(f+0.5);
     out_matrix[2] = ceil_reinvented(0);
     out_matrix[3] = f;
     out_matrix[4] = f+0.5;
     out_matrix[5] = in_integer;
 
  }
  """)
      
func = mod.get_function("test_ceil")
func(np.int32(12), a_gpu, a_out_gpu, block=(1,1,1))

returned_array = np.empty_like(a_out)
cuda.memcpy_dtoh(returned_array, a_out_gpu)
print('returned array is')
print(returned_array)