# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 07:36:33 2024

@author: Henry Cheung
"""

from os import environ
from sqlalchemy import create_engine
import pandas as pd

# uri = 'mysql+pymysql://root:@localhost/finance_fdata_fut_hist_10secs_2023'

# engine = create_engine(uri, echo=True)

# # sql = "DELETE FROM finance_fdata_fut_hist_10secs_2023.fdata_fut_hist where tDateTime >= '2024-01-01'"
# sql = "INSERT IGNORE INTO finance_fdata_fut_hist_10secs_2023.fdata_fut_hist SELECT * FROM finance_fdata_fut_hist_10secs_2023_h1.fdata_fut_hist"

# engine.execute(sql)


# uri = 'mysql+pymysql://root:@localhost/finance_fdata_price_1min_ib_2023'

# engine = create_engine(uri, echo=True)

# sql = "DELETE FROM finance_fdata_price_1min_ib_2023.fdata_price_1min_ib where DateTime >= '2024-01-01'"
# # sql = "INSERT IGNORE INTO finance_fdata_fut_hist_10secs_2023.fdata_fut_hist SELECT * FROM finance_fdata_fut_hist_10secs_2023_h1.fdata_fut_hist"


# engine.execute(sql)

# uri = 'mysql+pymysql://root:@localhost/finance_fdata_price_1min_ib_2023'

# engine = create_engine(uri, echo=True)

# df = pd.read_sql("SELECT MIN(DateTime), MAX(DateTime) FROM fdata_price_1min_ib", con=engine)    

# print(df)


uri = 'mysql+pymysql://root:@localhost/finance_fdata_fut_hist'

engine = create_engine(uri, echo=True)

sql = "DELETE FROM finance_fdata_fut_hist.fdata_fut_hist where timeframe = '5 secs'"

engine.execute(sql)

uri = 'mysql+pymysql://root:@localhost/finance_fdata_fut_hist'

engine = create_engine(uri, echo=True)

df = pd.read_sql("SELECT `timeframe` FROM `fdata_fut_hist` GROUP BY `timeframe`", con=engine)    

print(df)





