# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 19:34:06 2023

@author: Henry Cheung
"""


import InvestmentAnalytics.Config as Config
import InvestmentAnalytics.DBUtil as DBUtil
from sqlalchemy.sql import text

import pandas as pd
import time
pd.set_option('display.max_colwidth', None)

WaitAlertSent = False
WaitTime = 5

statement = text("""DELETE FROM pending_db_upload_command WHERE Uploaded = 1""")
engine = DBUtil.GetSQLAlchemyEngine()
# engine.execute(statement)
with engine.connect() as conn:
    # result = conn.execute(statement)
    conn.execute(statement)
    conn.commit()
    conn.close()
    
while True:
    df = pd.read_sql("SELECT * FROM pending_db_upload_command where Uploaded = False and Priority >= 5 and Priority < 10 ORDER BY Priority DESC",con=DBUtil.GetSQLAlchemyEngine())
    if len(df) == 0:
        if not WaitAlertSent:
            print('No pending upload command, going to wait and check again')
            WaitAlertSent = True
        time.sleep(WaitTime)
        if WaitTime <= 300:
            WaitTime = WaitTime * 2
    else:
        print(df)
        WaitAlertSent = False
        WaitTime = 5
        for index, row in df.iterrows():
            # print('Going to execute upload command ' + row['command'])
            DBUtil.DBDirectUpload(row['command'], row['DBName'], row['TableName'], DBSuffix = row['DBSuffix'] )


    