# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 00:06:08 2022

@author: henry
"""

from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import random


NumberOfSample = 100000000
SortByColumn = ['rand3', 'rand1', 'rand2']


pandas_df = pd.DataFrame("Happy", index=list(range(0,NumberOfSample)), columns=['x']) 
pandas_df['rand1'] = np.random.randint(0, 100000, size=NumberOfSample) / 100
pandas_df['rand2'] = np.random.randint(0, 100000, size=NumberOfSample) / 100
pandas_df['rand3'] = 1

print('before sorting by pandas for ' + str(len(pandas_df)) + ' rows at ' + str(datetime.now()))
sorted_pandas_df = pandas_df.sort_values(by=SortByColumn, ascending=True, inplace=False)

print('sorted_pandas_df after sorting is with len ' + str(len(sorted_pandas_df)))
print(sorted_pandas_df)
print('after sorting by pandas at ' + str(datetime.now()))
