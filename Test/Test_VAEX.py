
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 23:52:30 2021

@author: Henry Cheung
"""

import vaex

import pandas as pd  
  
# assign data of lists.  
data = {'Name': ['Tom', 'Joseph', 'Krish', 'John'], 'Age': [20, 21, 19, 18]}  
  
# Create DataFrame  
pandas_df = pd.DataFrame(data)  
  
# Print the output.  
print(pandas_df)  

# df = vaex.from_pandas(df=pandas_df, copy_index=True)
df = vaex.from_pandas(df=pandas_df, copy_index=False)
print('df vaex')
print(df)  

df = df.join(df, on='Name', rsuffix='_y')
# df = df.join(pandas_df1, on='Name', rsuffix='_y')
print('df after join')
print(df)  
df = df.rename('Name', 'Name2')
print('df after rename')
print(df)  
# import numpy as np
# from timeit import default_timer as timer
# from numba import vectorize

# @vectorize(["float32(float32, float32)"], target='cuda')
# def VectorAdd(a, b):
#         return a + b

# def main():
#     N = 320000000

#     A = np.ones(N, dtype=np.float32)
#     B = np.ones(N, dtype=np.float32)
#     C = np.zeros(N, dtype=np.float32)

#     start = timer()
#     C = VectorAdd(A, B)
#     vectoradd_timer = timer() - start

#     print("C[:5] = " + str(C[:5]))
#     print("C[-5:] = " + str(C[-5:]))

#     print("VectorAdd took %f seconds" % vectoradd_timer)

# if __name__ == '__main__':
#     main()