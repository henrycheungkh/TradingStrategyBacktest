# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 22:51:08 2022

@author: Henry Cheung
"""

import yahoo_fin.stock_info as si
import pandas as pd

pd.set_option('max_columns', None)


earnings_in_week = si.get_earnings_in_date_range("01/16/2022", "02/23/2022")

df = pd.DataFrame(earnings_in_week)

print(df)



# df1 = df[df['ticker'] == 'GOOG']

# print(df1)

# print(earnings_in_week)
