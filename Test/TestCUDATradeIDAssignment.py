# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 11:21:09 2022

@author: henry
"""

from InvestmentAnalytics.CUDA.Strategy.Futures.FuturesTradingStrategyCUDALib import CUDATradeIDAssignment

import pandas as pd


# l = ['ticker id', 'obs TimeInStandardUnit', 'entry TimeInStandardUnit', 'exit TimeInStandardUnit', 'obs movement threshold', 'obs movement range', 'stop loss', 'take profit', 'obs date id offset', 'trade entry date id offset']
df = pd.read_csv(r'C:\temp\InputToCUDATradeIDAssignment2.csv')
# print('input df is')
# print(df)



# it works if number_of_segment_key_column = 2
# number_of_segment_key_column = 2
number_of_segment_key_column = 1

# i = 0
# while i < len(df):
#     df3 = df.iloc[i:i + 1000000]
#     df3.to_csv(r'C:\temp\InputToCUDATradeIDAssignment2_' + str(number_of_segment_key_column) + '_' + str(i) + '.csv')
#     i = i + 1000000

df2 = CUDATradeIDAssignment(df, number_of_segment_key_column)

# df2.to_csv(r'C:\temp\OutputFromCUDATradeIDAssignment2.csv')

print('output trade id with number_of_segment_key_column = ' + str(number_of_segment_key_column) + ' is')
print(df2)

# i = 0
# while i < len(df2):
#     df3 = df2.iloc[i:i + 1000000]
#     df3.to_csv(r'C:\temp\OutputFromCUDATradeIDAssignment3_' + str(number_of_segment_key_column) + '_' + str(i) + '.csv')
#     i = i + 1000000



# Start CUDATradeIDAssignment with number_of_segment_key_column = 2 at 2022-11-25 13:23:10.823497
# segment_key_column_names is ['ticker id', 'obs TimeInStandardUnit']
# segment_unique_keys is
#           ticker id  obs TimeInStandardUnit
# 0               0.0                     965
# 152979          0.0                     950
# 317730          0.0                     935
# 490785          0.0                     920
# 669570          0.0                     905
# 854634          0.0                     890
# 1054245         0.0                     875
# 1269526         0.0                     860
# 1488508         0.0                     845
# 1710676         0.0                     830
# 1941810         0.0                     815
# 2180494         0.0                     800
# 2427594         0.0                     785
# 2692892         0.0                     770
# 2958662         0.0                     755
# 3238390         0.0                     740
# 3510111         0.0                     725
# 3794242         0.0                     710
# 4086040         0.0                     695
# 4396926         0.0                     680
# 4714226         0.0                     665
# 5052592         0.0                     650
# 5397319         0.0                     635
# 5747316         0.0                     620
# 6115395         0.0                     605
# 6511052         0.0                     590
# 6926527         0.0                     575
# 7331514         0.0                     560
# 7748779         0.0                     545
# 8167378         0.0                     530
# 8588448         0.0                     515
# 9021089         0.0                     500
# 9477104         0.0                     485
# 9944008         0.0                     470
# 10413162        0.0                     455
# 10885797        0.0                     440
# 11366434        0.0                     425
# 11844811        0.0                     410
# 12326570        0.0                     395
# 12807591        0.0                     380
# 13291455        0.0                     365
# 13777185        0.0                     350
# 14254932        0.0                     335
# 14736103        0.0                     320
# 15216431        0.0                     305
# 15702119        0.0                     290
# 16187061        0.0                     275
# 16674050        0.0                     260
# 17163699        0.0                     245
# 17657149        0.0                     230
# output trade id with number_of_segment_key_column = 2 is
#           trade id
# 0                0
# 1                1
# 2                2
# 3                3
# 4                4
#            ...
# 18157344       126
# 18157345       127
# 18157346       128
# 18157347       129
# 18157348       130

# [18157349 rows x 1 columns]



# Start CUDATradeIDAssignment with number_of_segment_key_column = 1 at 2022-11-25 13:27:08.462175
# segment_key_column_names is ['ticker id']
# segment_unique_keys is
#    ticker id
# 0        0.0
# output trade id with number_of_segment_key_column = 1 is
#           trade id
# 0                0
# 1                1
# 2                2
# 3                3
# 4                4
#            ...
# 18157344         0
# 18157345         0
# 18157346         0
# 18157347         0
# 18157348         0

# [18157349 rows x 1 columns]

