# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 17:20:43 2024

@author: Henry Cheung
"""

import InvestmentAnalytics.IB.DownloadFuturesFromIBLib as DownloadFuturesFromIBLib


from datetime import date, datetime, timedelta
import pandas as pd
import InvestmentAnalytics.DBUtil as DBUtil
from sqlalchemy.sql import text

pd.set_option('display.max_columns', None)

today = date.today()
DataEndDate = today.strftime("%Y%m%d")

statement = text("""DELETE FROM daily_futures_download_patching WHERE Uploaded = 1""")
engine = DBUtil.GetSQLAlchemyEngine()
# engine.execute(statement)
with engine.connect() as conn:
    # result = conn.execute(statement)
    conn.execute(statement)
    conn.commit()
    conn.close()
    

df = pd.read_sql("SELECT * FROM daily_futures_download_patching where Uploaded = False",con=DBUtil.GetSQLAlchemyEngine())

print(df)
    
for index, row in df.iterrows():
    BarSize = row['timeframe']
    if BarSize == "5 secs":
        HistoricalPeriod = "2 D"
    else:
        HistoricalPeriod = "3 D"
    SingleTicker = row['ticker']
    DownloadFuturesFromIBLib.DownloadFuturesFromIBByLib(BarSize, HistoricalPeriod, today, SingleTicker, DataEndDate, "DirectUpload", lastTradeDateOrContractMonths = None)

    
statement = text("""UPDATE daily_futures_download_patching SET Uploaded = 1""")
engine = DBUtil.GetSQLAlchemyEngine()
# engine.execute(statement)
with engine.connect() as conn:
    # result = conn.execute(statement)
    conn.execute(statement)
    conn.commit()
    conn.close()
    


