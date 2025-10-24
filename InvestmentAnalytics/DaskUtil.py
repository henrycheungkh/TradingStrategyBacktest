# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 18:19:33 2022

@author: henry
"""

# SelectedGroupingColumnCount = 2
# SELECTED_GROUPING_COLUMNS = GROUPING_COLUMNS[0:SelectedGroupingColumnCount]
# SELECTED_SORTING_COLUMNS = GROUPING_COLUMNS[SelectedGroupingColumnCount:] + TRADE_ID_SORTING_COLUMNS

# print('SELECTED_GROUPING_COLUMNS is ' + str(SELECTED_GROUPING_COLUMNS))
# print('SELECTED_SORTING_COLUMNS is ' + str(SELECTED_SORTING_COLUMNS))

import dask.dataframe as dd
import dask.array as da
import dask.bag as db
import pandas as pd
import math
from datetime import date, datetime, timedelta



def GroupAndSort(Data_ddf, by, SelectedGroupingColumnCount = 2, ascending=True, ScenarioColumns = [], TradeIDSortingSegmentKeyColumnsCount = 0):
    # print('Start of GroupAndSort')
    if SelectedGroupingColumnCount is None:
        SelectedGroupingColumnCount = math.floor(len(by)/2)
        
    SelectedGroupingColumns = by[0:SelectedGroupingColumnCount]
    SelectedSortingColumns = by[SelectedGroupingColumnCount:]
    
    # print('SelectedGroupingColumnCount = ' + str(SelectedGroupingColumnCount))
    # print('SelectedGroupingColumns = ' + str(SelectedGroupingColumns))
    # print('SelectedSortingColumns = ' + str(SelectedSortingColumns))
    
    # print('ddf is with len ' + str(len(ddf)))
    # print('Data_ddf is with len ' + f"{len(Data_ddf):,}" + '  at ' + str(datetime.now()))
    # print(Data_ddf.head(20))
    
    # ddf_groups = Data_ddf[GROUPING_COLUMNS].drop_duplicates()
    
    # print('ddf_groups is with len ' + f"{len(ddf_groups):,}")
    # print(ddf_groups.head(20))
    
    ddf_selected_groups = Data_ddf[SelectedGroupingColumns].drop_duplicates().sort_values(by=SelectedGroupingColumns, ascending=ascending).reset_index(drop=True)
    
    # print('ddf_selected_groups is with len ' + str(len(ddf_selected_groups)))
    # print(ddf_selected_groups.head(20))
    
    ddf_sorted_data = None
    
    df_selected_groups = ddf_selected_groups.compute()
    
    for i in range(len(df_selected_groups)):
        if i % 10 == 0:
            print('In DaskUtil.GroupAndSort, i = ' + str(i) + '/' + str(len(df_selected_groups)) + ' at ' + str(datetime.now()))
        df = df_selected_groups.iloc[[i]]
        ddf_selected_data = Data_ddf.merge(df, on=SelectedGroupingColumns)
        # if isinstance(ddf_selected_data, pd.DataFrame):
        #     print('after dask.merge, result is Dataframe')
        # else:
        #     print('after dask.merge, result is not Dataframe')
            
        df_selected_data = ddf_selected_data.compute()
        # df_selected_data = df_selected_data.sort_values(by=SelectedSortingColumns, ascending=ascending)
        df_selected_data = df_selected_data.sort_values(by=SelectedSortingColumns, ascending=ascending).reset_index(drop=True)
        
        if len(ScenarioColumns) > 0:
            df = df_selected_data[ScenarioColumns]
            from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib import CUDATradeIDAssignment
            df = CUDATradeIDAssignment(df, TradeIDSortingSegmentKeyColumnsCount)
            df_selected_data = pd.concat([df_selected_data, df], axis=1)
            
        
        # if SelectedGroupingColumnCount == 2 and i < 2:
        #     print('SelectedSortingColumns = ' + str(SelectedSortingColumns))
        #     print('df_selected_data is with len ' + f"{len(df_selected_data):,}")
        #     print(df_selected_data[['entry TimeInStandardUnit', 'exit TimeInStandardUnit', 'obs movement threshold']].head(50))  

        ddf_selected_data = dd.from_pandas(df_selected_data, npartitions=1) 
        
        # if SelectedGroupingColumnCount == 2 and i < 2:
        #     print('ddf_selected_data is with len ' + f"{len(ddf_selected_data):,}")
        #     print(ddf_selected_data[['entry TimeInStandardUnit', 'exit TimeInStandardUnit', 'obs movement threshold']].head(50))  
        #     ddf_selected_data.to_csv(r'C:\temp\dask_sort_result_SelectedGroupingColumnCount_2_i_' + str(i) + '.csv')  
           
        if ddf_sorted_data is None:
            ddf_sorted_data = ddf_selected_data
        else:
            ddf_sorted_data = dd.concat([ddf_sorted_data, ddf_selected_data])
    return ddf_sorted_data


# GROUPING_COLUMNS = ['ticker id', 'obs TimeInStandardUnit', 'entry TimeInStandardUnit', 'exit TimeInStandardUnit', 'obs movement threshold', 'obs movement range', 'stop loss', 'take profit', 'obs date id offset', 'trade entry date id offset']
# TRADE_ID_SORTING_COLUMNS = ['exit time id']


# # SelectedGroupingColumnCount = 2
# print('Before reading in dask ddf at ' + str(datetime.now()))

# ddf = dd.read_csv(r'C:\temp\self_trade_record_before_sorting_for_trade_id_assignment1-*.csv')  
# # ddf = dd.read_csv(r'C:\temp\self_trade_record_before_sorting_for_trade_id_assignment1-1.csv')  

# # ddf_sorted_data = GroupAndSort(ddf, GROUPING_COLUMNS[0:SelectedGroupingColumnCount], GROUPING_COLUMNS[SelectedGroupingColumnCount:] + TRADE_ID_SORTING_COLUMNS, ascending=False)

# # ddf_sorted_data = GroupAndSort(ddf, GROUPING_COLUMNS + TRADE_ID_SORTING_COLUMNS, SelectedGroupingColumnCount = 2, ascending=False)
# ddf_sorted_data = GroupAndSort(ddf, GROUPING_COLUMNS + TRADE_ID_SORTING_COLUMNS, ascending=False)

# print('ddf_sorted_data is with len ' + str(len(ddf_sorted_data)) + ' at ' + str(datetime.now()))
# print(ddf_sorted_data.head(20))
# ddf_sorted_data.to_csv(r'C:\temp\dask_sort_result_' + str(5) + '-*.csv')  
# # ddf_sorted_data.to_csv(r'C:\temp\dask_sort_result_' + str(floor(len(GROUPING_COLUMNS + TRADE_ID_SORTING_COLUMNS)/2)) + '-*.csv')  



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

# -------------------------------------------

# Before reading in dask ddf at 2023-01-08 06:47:21.650523
# Start of GroupAndSort
# SelectedGroupingColumnCount = 2
# SelectedGroupingColumns = ['ticker id', 'obs TimeInStandardUnit']
# SelectedSortingColumns = ['entry TimeInStandardUnit', 'exit TimeInStandardUnit', 'obs movement threshold', 'obs movement range', 'stop loss', 'take profit', 'obs date id offset', 'trade entry date id offset', 'exit time id']
# Data_ddf is with len 197,162,754  at 2023-01-08 06:48:08.506040
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
# ddf_selected_groups is with len 74
#     ticker id  obs TimeInStandardUnit
# 0         0.0                     960
# 1         0.0                     950
# 2         0.0                     940
# 3         0.0                     930
# 4         0.0                     920
# 5         0.0                     910
# 6         0.0                     900
# 7         0.0                     890
# 8         0.0                     880
# 9         0.0                     870
# 10        0.0                     860
# 11        0.0                     850
# 12        0.0                     840
# 13        0.0                     830
# 14        0.0                     820
# 15        0.0                     810
# 16        0.0                     800
# 17        0.0                     790
# 18        0.0                     780
# 19        0.0                     770
# i = 0/74 at 2023-01-08 06:50:51.043979
# SelectedSortingColumns = ['entry TimeInStandardUnit', 'exit TimeInStandardUnit', 'obs movement threshold', 'obs movement range', 'stop loss', 'take profit', 'obs date id offset', 'trade entry date id offset', 'exit time id']
# df_selected_data is with len 2,162,256
#     entry TimeInStandardUnit  exit TimeInStandardUnit  obs movement threshold
# 0                        950                      960                   0.005
# 1                        950                      960                   0.005
# 2                        950                      960                   0.005
# 3                        950                      960                   0.005
# 4                        950                      960                   0.005
# 5                        950                      960                   0.005
# 6                        950                      960                   0.005
# 7                        950                      960                   0.005
# 8                        950                      960                   0.005
# 9                        950                      960                   0.005
# 10                       950                      960                   0.005
# 11                       950                      960                   0.005
# 12                       950                      960                   0.005
# 13                       950                      960                   0.005
# 14                       950                      960                   0.005
# 15                       950                      960                   0.005
# 16                       950                      960                   0.005
# 17                       950                      960                   0.005
# 18                       950                      960                   0.005
# 19                       950                      960                   0.005
# 20                       950                      960                   0.005
# 21                       950                      960                   0.005
# 22                       950                      960                   0.005
# 23                       950                      960                   0.005
# 24                       950                      960                   0.005
# 25                       950                      960                   0.005
# 26                       950                      960                   0.005
# 27                       950                      960                   0.005
# 28                       950                      960                   0.005
# 29                       950                      960                   0.005
# 30                       950                      960                   0.005
# 31                       950                      960                   0.005
# 32                       950                      960                   0.005
# 33                       950                      960                   0.005
# 34                       950                      960                   0.005
# 35                       950                      960                   0.005
# 36                       950                      960                   0.005
# 37                       950                      960                   0.005
# 38                       950                      960                   0.005
# 39                       950                      960                   0.005
# 40                       950                      960                   0.005
# 41                       950                      960                   0.005
# 42                       950                      960                   0.005
# 43                       950                      960                   0.005
# 44                       950                      960                   0.005
# 45                       950                      960                   0.005
# 46                       950                      960                   0.005
# 47                       950                      960                   0.005
# 48                       950                      960                   0.005
# 49                       950                      960                   0.005
# ddf_selected_data is with len 2,162,256
#     entry TimeInStandardUnit  exit TimeInStandardUnit  obs movement threshold
# 0                        950                      960                   0.005
# 1                        950                      960                   0.005
# 2                        950                      960                   0.005
# 3                        950                      960                   0.005
# 4                        950                      960                   0.005
# 5                        950                      960                   0.005
# 6                        950                      960                   0.005
# 7                        950                      960                   0.005
# 8                        950                      960                   0.005
# 9                        950                      960                   0.005
# 10                       950                      960                   0.005
# 11                       950                      960                   0.005
# 12                       950                      960                   0.005
# 13                       950                      960                   0.005
# 14                       950                      960                   0.005
# 15                       950                      960                   0.005
# 16                       950                      960                   0.005
# 17                       950                      960                   0.005
# 18                       950                      960                   0.005
# 19                       950                      960                   0.005
# 20                       950                      960                   0.005
# 21                       950                      960                   0.005
# 22                       950                      960                   0.005
# 23                       950                      960                   0.005
# 24                       950                      960                   0.005
# 25                       950                      960                   0.005
# 26                       950                      960                   0.005
# 27                       950                      960                   0.005
# 28                       950                      960                   0.005
# 29                       950                      960                   0.005
# 30                       950                      960                   0.005
# 31                       950                      960                   0.005
# 32                       950                      960                   0.005
# 33                       950                      960                   0.005
# 34                       950                      960                   0.005
# 35                       950                      960                   0.005
# 36                       950                      960                   0.005
# 37                       950                      960                   0.005
# 38                       950                      960                   0.005
# 39                       950                      960                   0.005
# 40                       950                      960                   0.005
# 41                       950                      960                   0.005
# 42                       950                      960                   0.005
# 43                       950                      960                   0.005
# 44                       950                      960                   0.005
# 45                       950                      960                   0.005
# 46                       950                      960                   0.005
# 47                       950                      960                   0.005
# 48                       950                      960                   0.005
# 49                       950                      960                   0.005
# i = 1/74 at 2023-01-08 06:53:08.021844
# SelectedSortingColumns = ['entry TimeInStandardUnit', 'exit TimeInStandardUnit', 'obs movement threshold', 'obs movement range', 'stop loss', 'take profit', 'obs date id offset', 'trade entry date id offset', 'exit time id']
# df_selected_data is with len 2,167,088
#     entry TimeInStandardUnit  exit TimeInStandardUnit  obs movement threshold
# 0                        950                      960                   0.005
# 1                        950                      960                   0.005
# 2                        950                      960                   0.005
# 3                        950                      960                   0.005
# 4                        950                      960                   0.005
# 5                        950                      960                   0.005
# 6                        950                      960                   0.005
# 7                        950                      960                   0.005
# 8                        950                      960                   0.005
# 9                        950                      960                   0.005
# 10                       950                      960                   0.005
# 11                       950                      960                   0.005
# 12                       950                      960                   0.005
# 13                       950                      960                   0.005
# 14                       950                      960                   0.005
# 15                       950                      960                   0.005
# 16                       950                      960                   0.005
# 17                       950                      960                   0.005
# 18                       950                      960                   0.005
# 19                       950                      960                   0.005
# 20                       950                      960                   0.005
# 21                       950                      960                   0.005
# 22                       950                      960                   0.005
# 23                       950                      960                   0.005
# 24                       950                      960                   0.005
# 25                       950                      960                   0.005
# 26                       950                      960                   0.005
# 27                       950                      960                   0.005
# 28                       950                      960                   0.005
# 29                       950                      960                   0.005
# 30                       950                      960                   0.005
# 31                       950                      960                   0.005
# 32                       950                      960                   0.005
# 33                       950                      960                   0.005
# 34                       950                      960                   0.005
# 35                       950                      960                   0.005
# 36                       950                      960                   0.005
# 37                       950                      960                   0.005
# 38                       950                      960                   0.005
# 39                       950                      960                   0.005
# 40                       950                      960                   0.005
# 41                       950                      960                   0.005
# 42                       950                      960                   0.005
# 43                       950                      960                   0.005
# 44                       950                      960                   0.005
# 45                       950                      960                   0.005
# 46                       950                      960                   0.005
# 47                       950                      960                   0.005
# 48                       950                      960                   0.005
# 49                       950                      960                   0.005
# ddf_selected_data is with len 2,167,088
#     entry TimeInStandardUnit  exit TimeInStandardUnit  obs movement threshold
# 0                        950                      960                   0.005
# 1                        950                      960                   0.005
# 2                        950                      960                   0.005
# 3                        950                      960                   0.005
# 4                        950                      960                   0.005
# 5                        950                      960                   0.005
# 6                        950                      960                   0.005
# 7                        950                      960                   0.005
# 8                        950                      960                   0.005
# 9                        950                      960                   0.005
# 10                       950                      960                   0.005
# 11                       950                      960                   0.005
# 12                       950                      960                   0.005
# 13                       950                      960                   0.005
# 14                       950                      960                   0.005
# 15                       950                      960                   0.005
# 16                       950                      960                   0.005
# 17                       950                      960                   0.005
# 18                       950                      960                   0.005
# 19                       950                      960                   0.005
# 20                       950                      960                   0.005
# 21                       950                      960                   0.005
# 22                       950                      960                   0.005
# 23                       950                      960                   0.005
# 24                       950                      960                   0.005
# 25                       950                      960                   0.005
# 26                       950                      960                   0.005
# 27                       950                      960                   0.005
# 28                       950                      960                   0.005
# 29                       950                      960                   0.005
# 30                       950                      960                   0.005
# 31                       950                      960                   0.005
# 32                       950                      960                   0.005
# 33                       950                      960                   0.005
# 34                       950                      960                   0.005
# 35                       950                      960                   0.005
# 36                       950                      960                   0.005
# 37                       950                      960                   0.005
# 38                       950                      960                   0.005
# 39                       950                      960                   0.005
# 40                       950                      960                   0.005
# 41                       950                      960                   0.005
# 42                       950                      960                   0.005
# 43                       950                      960                   0.005
# 44                       950                      960                   0.005
# 45                       950                      960                   0.005
# 46                       950                      960                   0.005
# 47                       950                      960                   0.005
# 48                       950                      960                   0.005
# 49                       950                      960                   0.005
# i = 2/74 at 2023-01-08 06:55:46.864430
# i = 3/74 at 2023-01-08 06:58:46.162177
# i = 4/74 at 2023-01-08 07:01:53.513024
# i = 5/74 at 2023-01-08 07:04:52.858985
# i = 6/74 at 2023-01-08 07:07:50.823597
# i = 7/74 at 2023-01-08 07:10:54.193053
# i = 8/74 at 2023-01-08 07:13:58.038566
# i = 9/74 at 2023-01-08 07:16:54.011069
# i = 10/74 at 2023-01-08 07:20:00.626932
# i = 11/74 at 2023-01-08 07:23:09.338409
# i = 12/74 at 2023-01-08 07:26:20.740123
# i = 13/74 at 2023-01-08 07:29:29.821354
# i = 14/74 at 2023-01-08 07:32:34.995790
# i = 15/74 at 2023-01-08 07:35:44.418096
# i = 16/74 at 2023-01-08 07:38:49.787045
# i = 17/74 at 2023-01-08 07:41:57.678902
# i = 18/74 at 2023-01-08 07:44:59.588910
# i = 19/74 at 2023-01-08 07:48:08.269617
# i = 20/74 at 2023-01-08 07:51:13.635789
# i = 21/74 at 2023-01-08 07:54:27.116992
# i = 22/74 at 2023-01-08 07:57:39.528019
# i = 23/74 at 2023-01-08 08:00:59.510686
# i = 24/74 at 2023-01-08 08:04:13.299492
# i = 25/74 at 2023-01-08 08:07:28.332003
# i = 26/74 at 2023-01-08 08:10:47.086391
# i = 27/74 at 2023-01-08 08:13:59.652427
# i = 28/74 at 2023-01-08 08:17:14.211582
# i = 29/74 at 2023-01-08 08:20:24.893976
# i = 30/74 at 2023-01-08 08:23:43.762837
# i = 31/74 at 2023-01-08 08:27:00.398148
# i = 32/74 at 2023-01-08 08:30:13.096453
# i = 33/74 at 2023-01-08 08:33:23.143859
# i = 34/74 at 2023-01-08 08:36:45.109748
# i = 35/74 at 2023-01-08 08:40:00.998444
# i = 36/74 at 2023-01-08 08:43:21.164272
# i = 37/74 at 2023-01-08 08:46:35.407032
# i = 38/74 at 2023-01-08 08:49:53.985380
# i = 39/74 at 2023-01-08 08:53:16.918769
# i = 40/74 at 2023-01-08 08:56:34.405028
# i = 41/74 at 2023-01-08 08:59:57.517526
# i = 42/74 at 2023-01-08 09:03:22.722591
# i = 43/74 at 2023-01-08 09:06:41.957823
# i = 44/74 at 2023-01-08 09:10:06.771621
# i = 45/74 at 2023-01-08 09:13:28.465187
# i = 46/74 at 2023-01-08 09:16:35.394071
# i = 47/74 at 2023-01-08 09:19:57.230993
# i = 48/74 at 2023-01-08 09:23:14.081215
# i = 49/74 at 2023-01-08 09:26:22.256423
# i = 50/74 at 2023-01-08 09:29:40.805419
# i = 51/74 at 2023-01-08 09:32:48.702146
# i = 52/74 at 2023-01-08 09:35:56.352128
# i = 53/74 at 2023-01-08 09:39:13.482509
# i = 54/74 at 2023-01-08 09:42:36.844185
# i = 55/74 at 2023-01-08 09:46:01.653455
# i = 56/74 at 2023-01-08 09:49:27.467840
# i = 57/74 at 2023-01-08 09:52:49.229348
# i = 58/74 at 2023-01-08 09:56:11.567492
# i = 59/74 at 2023-01-08 09:59:33.628823
# i = 60/74 at 2023-01-08 10:02:51.077812
# i = 61/74 at 2023-01-08 10:06:10.043237
# i = 62/74 at 2023-01-08 10:09:36.217105
# i = 63/74 at 2023-01-08 10:13:00.048392
# i = 64/74 at 2023-01-08 10:16:17.894449
# i = 65/74 at 2023-01-08 10:19:38.385544
# i = 66/74 at 2023-01-08 10:22:57.734148
# i = 67/74 at 2023-01-08 10:26:20.138793
# i = 68/74 at 2023-01-08 10:29:40.866564
# i = 69/74 at 2023-01-08 10:33:03.813175
# i = 70/74 at 2023-01-08 10:36:12.069049
# i = 71/74 at 2023-01-08 10:39:34.204278
# i = 72/74 at 2023-01-08 10:42:59.737955
# i = 73/74 at 2023-01-08 10:46:24.544672
# ddf_sorted_data is with len 197162754 at 2023-01-08 10:49:35.874589
#     Unnamed: 0  ...  stop TimeInStandardUnit
# 0     18163684  ...                      960
# 1     19063464  ...                      960
# 2     17809966  ...                      960
# 3      2365000  ...                      960
# 4      5518665  ...                      960
# 5     17927814  ...                      960
# 6     16586457  ...                      960
# 7     19664897  ...                      960
# 8      6522999  ...                      960
# 9     10885508  ...                      960
# 10     7872731  ...                      957
# 11     2532815  ...                      960
# 12    18726039  ...                      960
# 13      521665  ...                      960
# 14    14604562  ...                      960
# 15    13524038  ...                      960
# 16     3833194  ...                      960
# 17    11868642  ...                      960
# 18     8018174  ...                      960
# 19    10571049  ...                      960

# [20 rows x 22 columns]