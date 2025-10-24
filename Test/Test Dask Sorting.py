# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 18:19:33 2022

@author: henry
"""

GROUPING_COLUMNS = ['ticker id', 'obs TimeInStandardUnit', 'entry TimeInStandardUnit', 'exit TimeInStandardUnit', 'obs movement threshold', 'obs movement range', 'stop loss', 'take profit', 'obs date id offset', 'trade entry date id offset']
TRADE_ID_SORTING_COLUMNS = ['exit time id']
SelectedGroupingColumnCount = 2
SELECTED_GROUPING_COLUMNS = GROUPING_COLUMNS[0:SelectedGroupingColumnCount]
SELECTED_SORTING_COLUMNS = GROUPING_COLUMNS[SelectedGroupingColumnCount:] + TRADE_ID_SORTING_COLUMNS

print('SELECTED_GROUPING_COLUMNS is ' + str(SELECTED_GROUPING_COLUMNS))
print('SELECTED_SORTING_COLUMNS is ' + str(SELECTED_SORTING_COLUMNS))

import dask.dataframe as dd
import dask.array as da
import dask.bag as db
import pandas as pd

ddf = dd.read_csv(r'C:\temp\self_trade_record_before_sorting_for_trade_id_assignment1-*.csv')  
# ddf = dd.read_csv(r'C:\temp\self_trade_record_before_sorting_for_trade_id_assignment1-1.csv')  

# print('ddf is with len ' + str(len(ddf)))
print('ddf is with len ' + f"{len(ddf):,}")
print(ddf.head(20))

ddf_groups = ddf[GROUPING_COLUMNS].drop_duplicates()

print('ddf_groups is with len ' + f"{len(ddf_groups):,}")
print(ddf_groups.head(20))

ddf_selected_groups = ddf_groups[SELECTED_GROUPING_COLUMNS].drop_duplicates()

print('ddf_selected_groups is with len ' + str(len(ddf_selected_groups)))
print(ddf_selected_groups.head(20))

ddf_sorted_data = None

df_selected_groups = ddf_selected_groups.compute()

for i in range(len(df_selected_groups)):
    print('i = ' + str(i))
    df = df_selected_groups.iloc[[i]]
    ddf_selected_data = ddf.merge(df, on=SELECTED_GROUPING_COLUMNS)
    # if isinstance(ddf_selected_data, pd.DataFrame):
    #     print('after dask.merge, result is Dataframe')
    # else:
    #     print('after dask.merge, result is not Dataframe')
        
    df_selected_data = ddf_selected_data.compute()
    df_selected_data = df_selected_data.sort_values(by=SELECTED_SORTING_COLUMNS, ascending=False)
    ddf_selected_data = dd.from_pandas(df_selected_data, npartitions=1) 
    
    if i < 2:
        print('Sliced df for i = ' + str(i) + ' is ')
        print(df.head(20))
        print('df_selected_data is with len ' + f"{len(ddf_selected_data):,}")
        print(ddf_selected_data.head(20))    
       
    if ddf_sorted_data is None:
        ddf_sorted_data = ddf_selected_data
    else:
        ddf_sorted_data = dd.concat([ddf_sorted_data, ddf_selected_data])



print('ddf_sorted_data is with len ' + str(len(ddf_sorted_data)))
print(ddf_sorted_data.head(20))
ddf_sorted_data.to_csv(r'C:\temp\dask_sort_result-*.csv')  



# df is with len 197162754
#     Unnamed: 0  ...  stop TimeInStandardUnit
# 0            0  ...                       10
# 1            1  ...                       10
# 2            2  ...                       10
# 3            3  ...                       10
# 4            4  ...                       10
# 5            5  ...                       10
# 6            6  ...                       10
# 7            7  ...                       10
# 8            8  ...                       10
# 9            9  ...                       10
# 10          10  ...                       10
# 11          11  ...                       10
# 12          12  ...                       10
# 13          13  ...                       10
# 14          14  ...                       10
# 15          15  ...                       10
# 16          16  ...                       10
# 17          17  ...                       10
# 18          18  ...                       10
# 19          19  ...                       10

# [20 rows x 22 columns]
# df_groups is with len 344544
#     ticker id  ...  trade entry date id offset
# 0         0.0  ...                         0.0
# 1         0.0  ...                         0.0
# 2         0.0  ...                         0.0
# 3         0.0  ...                         0.0
# 4         0.0  ...                         0.0
# 5         0.0  ...                         0.0
# 6         0.0  ...                         0.0
# 7         0.0  ...                         0.0
# 8         0.0  ...                         0.0
# 9         0.0  ...                         0.0
# 10        0.0  ...                         0.0
# 11        0.0  ...                         0.0
# 12        0.0  ...                         0.0
# 13        0.0  ...                         0.0
# 14        0.0  ...                         0.0
# 15        0.0  ...                         0.0
# 16        0.0  ...                         0.0
# 17        0.0  ...                         0.0
# 18        0.0  ...                         0.0
# 19        0.0  ...                         0.0


# ---------------

# SELECTED_GROUPING_COLUMNS is ['ticker id', 'obs TimeInStandardUnit']
# SELECTED_SORTING_COLUMNS is ['entry TimeInStandardUnit', 'exit TimeInStandardUnit', 'obs movement threshold', 'obs movement range', 'stop loss', 'take profit', 'obs date id offset', 'trade entry date id offset', 'exit time id']
# ddf is with len 197,162,754
#     Unnamed: 0  ...  stop TimeInStandardUnit
# 0            0  ...                       10
# 1            1  ...                       10
# 2            2  ...                       10
# 3            3  ...                       10
# 4            4  ...                       10
# 5            5  ...                       10
# 6            6  ...                       10
# 7            7  ...                       10
# 8            8  ...                       10
# 9            9  ...                       10
# 10          10  ...                       10
# 11          11  ...                       10
# 12          12  ...                       10
# 13          13  ...                       10
# 14          14  ...                       10
# 15          15  ...                       10
# 16          16  ...                       10
# 17          17  ...                       10
# 18          18  ...                       10
# 19          19  ...                       10

# [20 rows x 22 columns]
# ddf_groups is with len 344544
#     ticker id  ...  trade entry date id offset
# 0         0.0  ...                         0.0
# 1         0.0  ...                         0.0
# 2         0.0  ...                         0.0
# 3         0.0  ...                         0.0
# 4         0.0  ...                         0.0
# 5         0.0  ...                         0.0
# 6         0.0  ...                         0.0
# 7         0.0  ...                         0.0
# 8         0.0  ...                         0.0
# 9         0.0  ...                         0.0
# 10        0.0  ...                         0.0
# 11        0.0  ...                         0.0
# 12        0.0  ...                         0.0
# 13        0.0  ...                         0.0
# 14        0.0  ...                         0.0
# 15        0.0  ...                         0.0
# 16        0.0  ...                         0.0
# 17        0.0  ...                         0.0
# 18        0.0  ...                         0.0
# 19        0.0  ...                         0.0

# [20 rows x 10 columns]
# ddf_selected_groups is with len 74
#     ticker id  obs TimeInStandardUnit
# 0         0.0                     920
# 1         0.0                     680
# 2         0.0                     910
# 3         0.0                     840
# 4         0.0                     860
# 5         0.0                     960
# 6         0.0                     460
# 7         0.0                     620
# 8         0.0                     900
# 9         0.0                     380
# 10        0.0                     660
# 11        0.0                     820
# 12        0.0                     650
# 13        0.0                     410
# 14        0.0                     810
# 15        0.0                     570
# 16        0.0                     850
# 17        0.0                     640
# 18        0.0                     400
# 19        0.0                     800
# i = 0
# Sliced df for i = 0 is 
#    ticker id  obs TimeInStandardUnit
# 0        0.0                     920
# df_selected_data is with len 2,202,891
#    Unnamed: 0  ...  stop TimeInStandardUnit
# 0           0  ...                       10
# 0    16497909  ...                      100
# 0     4302623  ...                      100
# 0     8815573  ...                      519
# 0    11999760  ...                      110
# 0    15736983  ...                      150
# 0     8777480  ...                      513
# 0      470781  ...                      517
# 0      109142  ...                      120
# 0     9087136  ...                      543
# 0      523796  ...                      600
# 0     6109661  ...                      510
# 0    17589652  ...                      510
# 0     6096985  ...                      493
# 0    15827990  ...                      511
# 0    14562201  ...                      497
# 0     5206091  ...                      146
# 0     5082085  ...                      275
# 0    14061620  ...                      505
# 0    18789530  ...                      550

# [20 rows x 22 columns]
# i = 1
# Sliced df for i = 1 is 
#    ticker id  obs TimeInStandardUnit
# 1        0.0                     680
# df_selected_data is with len 2,632,209
#    Unnamed: 0  ...  stop TimeInStandardUnit
# 0           1  ...                       10
# 0    16466265  ...                       10
# 0    16215800  ...                      241
# 0    16464583  ...                       10
# 0     9660747  ...                      520
# 0     8964896  ...                      473
# 0    15954478  ...                       10
# 0    13217605  ...                      120
# 0     9862785  ...                      120
# 0    11386496  ...                      157
# 0    12329855  ...                      470
# 0     4162931  ...                      480
# 0    17434094  ...                      480
# 0     8447990  ...                      480
# 0    18312446  ...                      490
# 0    16490622  ...                       10
# 0     2360012  ...                      542
# 0    16150863  ...                       10
# 0    17733922  ...                      304
# 0    15978314  ...                      150

# [20 rows x 22 columns]
# i = 2
# i = 3
# i = 4
# i = 5
# i = 6
# i = 7
# i = 8
# i = 9
# i = 10
# i = 11
# i = 12
# i = 13
# i = 14
# i = 15
# i = 16
# i = 17
# i = 18
# i = 19
# i = 20
# i = 21
# i = 22
# i = 23
# i = 24
# i = 25
# i = 26
# i = 27
# i = 28
# i = 29
# i = 30
# i = 31
# i = 32
# i = 33
# i = 34
# i = 35
# i = 36
# i = 37
# i = 38
# i = 39
# i = 40
# i = 41
# i = 42
# i = 43
# i = 44
# i = 45
# i = 46
# i = 47
# i = 48
# i = 49
# i = 50
# i = 51
# i = 52
# i = 53
# i = 54
# i = 55
# i = 56
# i = 57
# i = 58
# i = 59
# i = 60
# i = 61
# i = 62
# i = 63
# i = 64
# i = 65
# i = 66
# i = 67
# i = 68
# i = 69
# i = 70
# i = 71
# i = 72
# i = 73
# ddf_sorted_data is with len 197162754
#    Unnamed: 0  ...  stop TimeInStandardUnit
# 0           0  ...                       10
# 0    16497909  ...                      100
# 0     4302623  ...                      100
# 0     8815573  ...                      519
# 0    11999760  ...                      110
# 0    15736983  ...                      150
# 0     8777480  ...                      513
# 0      470781  ...                      517
# 0      109142  ...                      120
# 0     9087136  ...                      543
# 0      523796  ...                      600
# 0     6109661  ...                      510
# 0    17589652  ...                      510
# 0     6096985  ...                      493
# 0    15827990  ...                      511
# 0    14562201  ...                      497
# 0     5206091  ...                      146
# 0     5082085  ...                      275
# 0    14061620  ...                      505
# 0    18789530  ...                      550

# [20 rows x 22 columns]

