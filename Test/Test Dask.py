# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 08:30:03 2022

@author: henry
"""

import numpy as np
import pandas as pd

import dask.dataframe as dd
import dask.array as da
import dask.bag as db

print('Start')

pandas_df = pd.DataFrame({'Name': ['Tom', 'Joseph', 'Krish', 'John'], 'Last Name': ['Johnson', 'Cameron', 'Biden', 'Washington'], 'Age': [20, 21, 19, 18], 'Weight': [60.0, 61.0, 62.0, 63.0]})  
print('pandas_df is')
print(pandas_df)  


ddf = dd.from_pandas(pandas_df, npartitions=2)

ddf.to_csv(r'C:\temp\test_dask_b' + '-*.csv')

print('ddf is')
print(ddf.head(10))

ddf2 = ddf.merge(pandas_df, on=['Age', 'Weight'], suffixes=('', '_y'))

print('ddf after merge is')
print(ddf2.head(10))

ddf3 = ddf2.drop(['Name_y', 'Last Name_y'], axis=1)

print('ddf after drop is')
print(ddf3.head(10))

ddf4 = ddf3.rename(columns={"Last Name": "LastName"})  

print('ddf after rename is')
print(ddf4.head(10))

print('len of ddf is')
print(len(ddf4))

print('max Age is')
print(str(ddf4['Age'].max().compute()))

ddf5 = ddf4.sort_values(by=['Age'], ascending=False, inplace=False)

print('ddf after sort is')
print(ddf5.head(10))

col_list = ddf5.columns[:2].values.tolist()

print('col list is')
print(col_list)

ddf6 = ddf4.sort_values(by=['Age', 'Weight'], ascending=False, inplace=False)

print('ddf after multi dimension sort is')
print(ddf6.head(10))


