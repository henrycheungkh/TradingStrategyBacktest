# -*- coding: utf-8 -*-
"""
Created on Fri Jul 23 10:11:03 2021

@author: Henry Cheung
"""

import InvestmentAnalytics.Config as Config

from InvestmentAnalytics.DBUtil import DBExportDirectUpload
import pymysql
import pandas as pd

# DBExportDirectUpload( r'D:\Shared\TAHistoricalData\IB_20210723\UploadScript.sql', 'fdata_price_30min_ib')

dbconnect = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
sql = "SELECT DATE(DateTime), COUNT(*) AS RecordCount FROM `fdata_price_30min_ib` where DateTime >= '2021-07-22' GROUP BY DATE(DateTime)"
RecordCount_df = pd.read_sql_query(sql, dbconnect)
print(RecordCount_df)