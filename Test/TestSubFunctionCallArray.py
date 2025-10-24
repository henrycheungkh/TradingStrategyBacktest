# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 09:51:03 2021

@author: Henry Cheung
"""
import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import pandas as pd
import os
import numpy as np

_path = r"D:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.28.29910\bin\Hostx64\x64"

if os.system("cl.exe"):
    os.environ['PATH'] += ';' + _path
if os.system("cl.exe"):
    raise RuntimeError("cl.exe still not found, path probably incorrect")

# input_matrix = pd.read_csv(r'd:\temp\scenario segment 2.csv')
# input_matrix = pd.DataFrame(data={'a': [1, 1, 1], 'b': [100, 100, 100]})
# a = input_matrix.to_numpy()
# pending_zeros = np.zeros((3, 2))
# a = np.concatenate((a, pending_zeros))


# input_matrix = pd.DataFrame(data={'a': [1, 1, 1], 'b': [100, 100, 100], 'c': [200, 200, 200], 'd': [300, 300, 300]})
# a = input_matrix.to_numpy()

a = np.array([[1, 100, 200, 300], [1, 100, 200, 300], [1, 100, 200, 300]])

a = a.astype(np.float32)
# a = a.astype(np.int32)
# a = a.astype(np.int16)
a = a.copy(order="C")
print('input array is')
print(a)
a_gpu = cuda.mem_alloc(a.nbytes)
cuda.memcpy_htod(a_gpu, a)

a_out = np.zeros(6)
a_out = a_out.astype(np.float32)
# a_out = a_out.astype(np.int32)
# a_out = a_out.astype(np.int16)
a_out_gpu = cuda.mem_alloc(a_out.nbytes)
cuda.memcpy_htod(a_out_gpu, a_out)

mod = SourceModule("""

    #include <math.h>                   

  __device__ float* assign_array( float *input_float)
  {
    float *d = new float[6];
    d[0] = input_float[0] + 1000;
    d[1] = input_float[1] + 1000;;
    d[2] = input_float[2] + 1000;;
    d[3] = input_float[3] + 1000;;
    d[4] = input_float[4] + 1000;;
    d[5] = input_float[5] + 1000;;
    
    return d;
  }


  __global__ void matrix_location_trial(float *in_matrix, float *out_matrix)
  {
     float *temp_matrix = assign_array(in_matrix);
//     out_matrix[0] = ceil(temp_matrix[0]/10);
     out_matrix[0] = temp_matrix[0];
     out_matrix[1] = temp_matrix[1];
     out_matrix[2] = temp_matrix[2];
     out_matrix[3] = temp_matrix[3];
     out_matrix[4] = temp_matrix[4];
     out_matrix[5] = temp_matrix[5];
     delete temp_matrix;
  }
  
  """)
      
func = mod.get_function("matrix_location_trial")
func(a_gpu, a_out_gpu, block=(1,1,1))

returned_array = np.empty_like(a_out)
cuda.memcpy_dtoh(returned_array, a_out_gpu)
print('returned array is')
print(returned_array)