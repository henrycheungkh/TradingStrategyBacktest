# -*- coding: utf-8 -*-
"""
Created on Thu Jul 22 23:12:08 2021

@author: Henry Cheung
"""

import InvestmentAnalytics.Config as Config
import pymysql
import pandas as pd
import os
import threading

# from os import environ
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from datetime import datetime, date


# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy').setLevel(logging.ERROR)

import logging
logging.disable(logging.INFO)

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + Config.CONFIG_MYSQL_CONNECTION_USER + ':' + Config.CONFIG_MYSQL_CONNECTION_PASSWORD + '@' + Config.CONFIG_MYSQL_CONNECTION_HOST + ':' + str(Config.CONFIG_MYSQL_CONNECTION_PORT) + '/'
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + Config.CONFIG_MYSQL_CONNECTION_USER + Config.CONFIG_MYSQL_CONNECTION_PASSWORD + '@' + Config.CONFIG_MYSQL_CONNECTION_HOST + ':' + str(Config.CONFIG_MYSQL_CONNECTION_PORT) + '/'
# SQLALCHEMY_DATABASE_URI = 'mysql://' + Config.CONFIG_MYSQL_CONNECTION_USER + Config.CONFIG_MYSQL_CONNECTION_PASSWORD + '@' + Config.CONFIG_MYSQL_CONNECTION_HOST + ':' + str(Config.CONFIG_MYSQL_CONNECTION_PORT) + '/'
# SQLALCHEMY_DATABASE_URI = 'pymysql://' + Config.CONFIG_MYSQL_CONNECTION_USER + Config.CONFIG_MYSQL_CONNECTION_PASSWORD + '@' + Config.CONFIG_MYSQL_CONNECTION_HOST + ':' + str(Config.CONFIG_MYSQL_CONNECTION_PORT) + '/'

def GetSQLAlchemyEngine(DatabaseName=Config.CONFIG_MYSQL_CONNECTION_DATABASE, Override_DBHost = None, Override_DBPort = None, Override_DBUser = None, Override_DBPassword = None):
    if DatabaseName is None:
        DatabaseName = Config.CONFIG_MYSQL_CONNECTION_DATABASE
    if Override_DBHost is None and Override_DBPort is None and Override_DBUser is None and Override_DBPassword is None:
        uri = SQLALCHEMY_DATABASE_URI + DatabaseName
    else:
        if Override_DBHost is None:
            Override_DBHost = Config.CONFIG_MYSQL_CONNECTION_HOST
        if Override_DBPort is None:
            Override_DBPort = Config.CONFIG_MYSQL_CONNECTION_PORT
        if Override_DBUser is None:
            Override_DBUser = Config.CONFIG_MYSQL_CONNECTION_USER
        if Override_DBPassword is None:
            Override_DBPassword = Config.CONFIG_MYSQL_CONNECTION_PASSWORD
        uri = 'mysql+pymysql://' + Override_DBUser + ':' + Override_DBPassword + '@' + Override_DBHost + ':' + str(Override_DBPort) + '/' + DatabaseName
#    print('uri is')
#    print(uri)
    # db_uri = environ.get(uri)
    return create_engine(uri, echo=True)

def DBGetTableRecordCount(DBTableName, DatabaseName = Config.CONFIG_MYSQL_CONNECTION_DATABASE):
    # if DatabaseName is None:
    #     dbconnect = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD)
    # elif DatabaseName == Config.CONFIG_MYSQL_CONNECTION_DATABASE:
    #     dbconnect = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, DatabaseName)
    # else:
    #     dbconnect = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD)
    # if DatabaseName is None:
    #     # dbconnect = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD)
    #     # dbconnect = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD)
    #     dbconnect = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, port=Config.CONFIG_MYSQL_CONNECTION_PORT)
    # else:
    #     # dbconnect = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, DatabaseName)
    #     # dbconnect = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=DatabaseName)
    #     dbconnect = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=DatabaseName, port=Config.CONFIG_MYSQL_CONNECTION_PORT)
    dbconnect = DBGetDBInstance(DatabaseName)
    sql = "SELECT COUNT(*) AS RecordCount FROM `" + DBTableName + "`"
    RecordCount_df = pd.read_sql_query(sql, dbconnect)
    return RecordCount_df.iloc[0]['RecordCount']

def DBGetDBInstance(DatabaseName = Config.CONFIG_MYSQL_CONNECTION_DATABASE):
    if DatabaseName is None:
        # dbconnect = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD)
        # dbconnect = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD)
        dbconnect = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, port=Config.CONFIG_MYSQL_CONNECTION_PORT)
    else:
        # dbconnect = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, DatabaseName)
        # dbconnect = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=DatabaseName)
        dbconnect = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=DatabaseName, port=Config.CONFIG_MYSQL_CONNECTION_PORT)
    return dbconnect

def DBExportDirectUpload(SQLScript, DBTableName, DatabaseName = Config.CONFIG_MYSQL_CONNECTION_DATABASE, UploadToDB = True, Priority = 0):
    
    if Config.CONFIG_MYSQL_CONNECTION_PASSWORD == "":
        command = '"' + Config.CONFIG_MYSQL_PATH + '" -u ' + Config.CONFIG_MYSQL_CONNECTION_USER + ' ' + DatabaseName + ' < ' + SQLScript
    else:
        command = '"' + Config.CONFIG_MYSQL_PATH + '" -u ' + Config.CONFIG_MYSQL_CONNECTION_USER + ' -p' + Config.CONFIG_MYSQL_CONNECTION_PASSWORD + ' ' + DatabaseName + ' < ' + SQLScript

    if UploadToDB:
        print('Starting to direct upload data to DB by ' + SQLScript + ' to table ' + DBTableName)
    
        
        # command = r'd:\xampp\mysql\bin\mysql -u root ' + DatabaseName + ' < "' + SQLScript + r'"'
    
        
        # command = '"' + Config.CONFIG_MYSQL_PATH + '" -u ' + Config.CONFIG_MYSQL_CONNECTION_USER + ' ' + DatabaseName + ' < "' + SQLScript + '"'
        # command = '"' + Config.CONFIG_MYSQL_PATH + '" -u ' + Config.CONFIG_MYSQL_CONNECTION_USER + ' ' + DatabaseName + ' < "' + SQLScript + r'"'
        # command = '"' + Config.CONFIG_MYSQL_PATH + '" -u ' + Config.CONFIG_MYSQL_CONNECTION_USER + ' ' + DatabaseName + " < '" + SQLScript + r"'"
        # command = r'"' + Config.CONFIG_MYSQL_PATH + r'" -u ' + Config.CONFIG_MYSQL_CONNECTION_USER + r' ' + DatabaseName + r' < "' + SQLScript + r'"'
        # command = '"' + Config.CONFIG_MYSQL_PATH.replace("\", "\\") + '" -u ' + Config.CONFIG_MYSQL_CONNECTION_USER + ' ' + DatabaseName + ' < "' + SQLScript.replace("\", "\\") + '"'
        # command = '"' + Config.CONFIG_BASE_ProjectPath + '\\Batch\\Util\\UploadToDB.bat" ' + DatabaseName + ' "' + SQLScript + '"'
    
        # command = r'"D:\xampp\mysql\bin\mysql" -u root finance_fdata_fut_hist < "D:\Shared\TAHistoricalData\FuturesHistoricalDataBackup\20211019_10 secs_ES_3 D\UploadScript.sql"'
    
    
        print('command is')
        print(command)
        RecordCountBeforeUpload = DBGetTableRecordCount(DBTableName, DatabaseName = DatabaseName)
        os.system(command)    
        RecordCountAfterUpload = DBGetTableRecordCount(DBTableName, DatabaseName = DatabaseName)
        print('Record Count changed from ' + str(RecordCountBeforeUpload) + ' to ' + str(RecordCountAfterUpload) + ' at ' + str(datetime.now()))
    else:
        # statement = text("""INSERT IGNORE INTO pending_db_upload_command (command, DBName, TableName, Uploaded) VALUES (:command, :DBName, :TableName, False)""")
        # line = { "command": command, "DBName": DatabaseName, "TableName": DBTableName }
        statement = text("""INSERT IGNORE INTO pending_db_upload_command (command, DBName, TableName, Uploaded, Priority) VALUES (:command, :DBName, :TableName, False, :Priority)""")
        line = { "command": command, "DBName": DatabaseName, "TableName": DBTableName , "Priority": Priority}
        engine = GetSQLAlchemyEngine()
        # engine.execute(statement, **line)
        with engine.connect() as conn:
            # result = conn.execute(statement, line)
            conn.execute(statement, line)
#            print('In DBExportDirectUpload, after calling conn.execute')
#            print(statement)
#            print(line)
            conn.commit()
            conn.close()
        
#        print('Upload command uploaded to DB by DBExportDirectUpload')


def DBExportDirectUploadByBatchThread(DatafilePath, SQLScript, DBTableName, DatabaseName = Config.CONFIG_MYSQL_CONNECTION_DATABASE):
    print('Starting to direct upload data to DB by ' + SQLScript + ' to table ' + DBTableName)
    RecordCountBeforeUpload = DBGetTableRecordCount(DBTableName, DatabaseName = DatabaseName)

    if Config.CONFIG_MYSQL_CONNECTION_PASSWORD == "":
        password_string = ''
    else:
        password_string = '-p' + Config.CONFIG_MYSQL_CONNECTION_PASSWORD + ' '
    with open(DatafilePath + 'UploadToDB.bat', 'w') as the_file:
        the_file.write('"%TradeAnalysis_mysql%" -u %TradeAnalysis_DBUser% ' + password_string + DatabaseName + ' < "' + SQLScript + '"')
    print('After writing batch file ' + DatafilePath + 'UploadToDB.bat')
    command = '"' + DatafilePath + 'UploadToDB.bat"'
    print('command is')
    print(command)
    os.system(command)    
    RecordCountAfterUpload = DBGetTableRecordCount(DBTableName, DatabaseName = DatabaseName)
    print('Record Count changed from ' + str(RecordCountBeforeUpload) + ' to ' + str(RecordCountAfterUpload) + ' at ' + str(datetime.now()))

# def DBExportDirectUploadByBatch(DatafilePath, SQLScript, DBTableName, DatabaseName = Config.CONFIG_MYSQL_CONNECTION_DATABASE):
#     x = threading.Thread(target=DBExportDirectUploadByBatchThread, args=(DatafilePath, SQLScript, DBTableName, DatabaseName), daemon=True)
#     x.start()

def DBDirectUpload(command_without_quote, DatabaseName, DBTableName, DBSuffix = '', CountRecordCount = True):
    OriginalDatabaseName = DatabaseName
    DatabaseName = DatabaseName + DBSuffix
    print('Start to execute DB Upload command: ' + command_without_quote + ' to ' + DatabaseName + ' at ' + str(datetime.now()))
    command = '"' + command_without_quote + '"'
    if CountRecordCount:
        # print('Going to count record')
        RecordCountBeforeUpload = DBGetTableRecordCount(DBTableName, DatabaseName = DatabaseName)
        
    # print('Going to run command')
    os.system(command)    
    # print('After running command')
    
    if CountRecordCount:
        # print('Going to count record after')
        RecordCountAfterUpload = DBGetTableRecordCount(DBTableName, DatabaseName = DatabaseName)

    statement = text("""UPDATE pending_db_upload_command SET Uploaded = True WHERE command = :command AND DBName = :DBName AND TableName = :TableName AND DBSuffix = :DBSuffix""")
    line = { "command": command_without_quote, "DBName": OriginalDatabaseName, "TableName": DBTableName, "DBSuffix": DBSuffix }
    engine = GetSQLAlchemyEngine()
    # engine.execute(statement, **line)
    with engine.connect() as conn:
        # result = conn.execute(statement, line)
        conn.execute(statement, line)
        conn.commit()
        conn.close()
    
    print('DB Upload command executed: ' + command_without_quote + ' at ' + str(datetime.now()))
    if CountRecordCount:
        print('Record Count changed from ' + str(RecordCountBeforeUpload) + ' to ' + str(RecordCountAfterUpload) + ' at ' + str(datetime.now()))

def DBExportDirectUploadByBatch(DatafilePath, SQLScript, DBTableName, DatabaseName = Config.CONFIG_MYSQL_CONNECTION_DATABASE, UploadToDB = True, Priority = 0):
    print('Starting to direct upload data to DB by ' + SQLScript + ' to table ' + DBTableName)

    if Config.CONFIG_MYSQL_CONNECTION_PASSWORD == "":
        password_string = ''
    else:
        password_string = '-p' + Config.CONFIG_MYSQL_CONNECTION_PASSWORD + ' '
    with open(DatafilePath + 'UploadToDB.bat', 'w') as the_file:
        the_file.write('"%TradeAnalysis_mysql%" -u %TradeAnalysis_DBUser% ' + password_string + DatabaseName + ' < "' + SQLScript + '"')
    print('After writing batch file ' + DatafilePath + 'UploadToDB.bat')
    command_without_quote = DatafilePath + 'UploadToDB.bat'
    # command = '"' + DatafilePath + 'UploadToDB.bat"'
    # command = '"' + command_without_quote + '"'
    # print('command is')
    # print(command)
    if UploadToDB:
        DBDirectUpload(command_without_quote, DatabaseName, DBTableName)
        # DBDirectUpload(DBTableName, command)

        # RecordCountBeforeUpload = DBGetTableRecordCount(DBTableName, DatabaseName = DatabaseName)
        # os.system(command)    
        # RecordCountAfterUpload = DBGetTableRecordCount(DBTableName, DatabaseName = DatabaseName)
        # print('Record Count changed from ' + str(RecordCountBeforeUpload) + ' to ' + str(RecordCountAfterUpload))
    else:
        statement = text("""INSERT IGNORE INTO pending_db_upload_command (command, DBName, TableName, Uploaded, Priority) VALUES (:command, :DBName, :TableName, False, :Priority )""")
        line = { "command": command_without_quote, "DBName": DatabaseName, "TableName": DBTableName, "Priority": Priority }
        engine = GetSQLAlchemyEngine()
        # engine.execute(statement, **line)
        with engine.connect() as conn:
            # result = conn.execute(statement, line)
            conn.execute(statement, line)
#            print('In DBExportDirectUploadByBatch, after calling conn.execute')
#            print(statement)
#            print(line)
            conn.commit()
#            print('In DBExportDirectUploadByBatch, after calling conn.commit')
            conn.close()
#            print('In DBExportDirectUploadByBatch, after calling conn.close')
        
#        print('Upload command uploaded to DB by DBExportDirectUploadByBatch')

def AppendDBExportScript(DatafilePath, filepath, DBTableName, table_columns = None):
    print('In AppendDBExportScript, DBTableName = ' + DBTableName)
    with open(DatafilePath + 'UploadScript.sql', 'a') as the_file:
        filepath = filepath.replace("\\", "/")
        # the_file.write("LOAD DATA INFILE '" + filepath + "' IGNORE \n")
        the_file.write("LOAD DATA INFILE '" + filepath + "' REPLACE \n")
        the_file.write("INTO TABLE " + DBTableName + "\n")
        the_file.write("FIELDS TERMINATED BY ',' \n")
        the_file.write("LINES TERMINATED BY '\\r\\n'\n")
        the_file.write("IGNORE 1 LINES;\n\n")
#        if table_columns is None:
#           the_file.write("IGNORE 1 LINES;\n\n")
#        else:
#            the_file.write("IGNORE 1 LINES\n\n")
#            the_file.write(table_columns + ";\n\n")

