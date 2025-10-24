# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 10:22:22 2023

@author: henry
"""

from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import pymysql
import mysql.connector


import InvestmentAnalytics.Config as Config
import InvestmentAnalytics.DBUtil as DBUtil

# pd.set_option('display.max_columns', None)

mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
mycursor = mydb.cursor()


def UpdateLastRunTradeRecordSizePerSubBatch(StrategyName, BatchGroup, BacktestBatchID, BatchSubID, LastRunTradeRecordResultSize, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch'):
    if BatchListDatabaseName is None:
        FullBatchListTableName = BatchListTableName
    else:
        FullBatchListTableName = BatchListDatabaseName + '.' + BatchListTableName
    sql = "UPDATE " + FullBatchListTableName + " SET LastRunMaxTradeRecordResultSize = " + str(LastRunTradeRecordResultSize) + " WHERE StrategyName = '" + StrategyName + "' AND BatchGroup = '" + BatchGroup + "' AND BatchID = " + str(BacktestBatchID) + " AND BatchSubID = " + str(BatchSubID)
    DBUtil.GetSQLAlchemyEngine().execute(sql)

    # sql = "UPDATE fdata_backtest_batch SET LastBestAbsSharpeRatio = %s WHERE StrategyName = %s AND BatchGroup = %s AND BatchID = %s AND BatchSubID = %s"
    # val = (LastRunTradeRecordResultSize, StrategyName, BatchGroup, BacktestBatchID, BatchSubID)
    # mycursor.execute(sql, val)
    # mydb.commit()   

def UpdateLastRunMaxTradeRecordSizePerSubBatch(StrategyName, BatchGroup, BacktestBatchID, BatchSubID, MaxLastRunTradeRecordResultSize, BatchListDatabaseName = 'finance_fdata_master', BatchListTableName = 'fdata_backtest_batch'):
    # dbcon = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
    # sql = "SELECT * FROM `fdata_backtest_batch` where StrategyName = '" + StrategyName + "' AND BatchID = " + str(BacktestBatchID) + " AND BatchGroup = '" + BatchGroup + "' AND BatchSubID = " + str(BatchSubID)
    # AnalysisContextParameters = pd.read_sql_query(sql, dbcon)
    
    if BatchListDatabaseName is None:
        FullBatchListTableName = BatchListTableName
    else:
        FullBatchListTableName = BatchListDatabaseName + '.' + BatchListTableName

    AnalysisContextParameters = pd.read_sql("SELECT * FROM " + FullBatchListTableName + " where StrategyName = '" + StrategyName + "' AND BatchID = " + str(BacktestBatchID) + " AND BatchGroup = '" + BatchGroup + "' AND BatchSubID = " + str(BatchSubID),con=DBUtil.GetSQLAlchemyEngine())    
    # AnalysisContextParameters = pd.read_sql("SELECT * FROM `fdata_backtest_batch` where StrategyName = '" + StrategyName + "' AND BatchID = " + str(BacktestBatchID) + " AND BatchGroup = '" + BatchGroup + "' AND BatchSubID = " + str(BatchSubID),con=DBUtil.GetSQLAlchemyEngine())    
    
    try:
        PriorLastRunMaxTradeRecordResultSize = AnalysisContextParameters.loc[0, 'LastRunMaxTradeRecordResultSize']
    except:
        PriorLastRunMaxTradeRecordResultSize = 0
    if PriorLastRunMaxTradeRecordResultSize is None:
        PriorLastRunMaxTradeRecordResultSize = 0
    if MaxLastRunTradeRecordResultSize > PriorLastRunMaxTradeRecordResultSize:
        # print('MaxLastRunTradeRecordResultSize = ' + str(MaxLastRunTradeRecordResultSize))
        # print('type of MaxLastRunTradeRecordResultSize is ' + str(type(MaxLastRunTradeRecordResultSize)))
        # print('StrategyName = ' + str(StrategyName))
        # print('type of StrategyName is ' + str(type(StrategyName)))
        # print('BatchGroup = ' + str(BatchGroup))
        # print('type of BatchGroup is ' + str(type(BatchGroup)))
        if str(type(BacktestBatchID)) == "<class 'numpy.int64'>":
            BacktestBatchID = BacktestBatchID.item()
        # print('BacktestBatchID = ' + str(BacktestBatchID))
        # print('type of BacktestBatchID is ' + str(type(BacktestBatchID)))
        if str(type(BatchSubID)) == "<class 'numpy.int64'>":
            BatchSubID = BatchSubID.item()
        # print('BatchSubID = ' + str(BatchSubID))
        # print('type of BatchSubID is ' + str(type(BatchSubID)))
        # if 
        # MaxLastRunTradeRecordResultSize = MaxLastRunTradeRecordResultSize.item()
# mycursor = mydb.cursor()

        sql = "UPDATE " + FullBatchListTableName + " SET LastRunMaxTradeRecordResultSize = " + str(MaxLastRunTradeRecordResultSize) + " WHERE StrategyName = '" + StrategyName + "' AND BatchGroup = '" + BatchGroup + "' AND BatchID = " + str(BacktestBatchID) + " AND BatchSubID = " + str(BatchSubID)
        DBUtil.GetSQLAlchemyEngine().execute(sql)

        # sql = "UPDATE fdata_backtest_batch SET LastRunMaxTradeRecordResultSize = %s WHERE StrategyName = %s AND BatchGroup = %s AND BatchID = %s AND BatchSubID = %s"
        # val = (MaxLastRunTradeRecordResultSize, StrategyName, BatchGroup, BacktestBatchID, BatchSubID)
        # # val = (0, StrategyName, BatchGroup, BacktestBatchID, BatchSubID)
        # mycursor.execute(sql, val)
        # mydb.commit()