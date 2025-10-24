# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 22:31:08 2020

@author: Henry Cheung
"""
import os
import pymysql
import pandas as pd

CONFIG_LOCAL_TIMEZONE = os.getenv('TradeAnalysis_LocalTimezone')

# CONFIG_MYSQL_CONNECTION_HOST = "localhost"
# CONFIG_MYSQL_CONNECTION_USER = "root"
# CONFIG_MYSQL_CONNECTION_PASSWORD = ""

CONFIG_MYSQL_CONNECTION_HOST = os.getenv('TradeAnalysis_DBHost')
CONFIG_MYSQL_CONNECTION_USER = os.getenv('TradeAnalysis_DBUser')
CONFIG_MYSQL_CONNECTION_PORT = int(os.getenv('TradeAnalysis_DBPort'))
DBPassword = os.getenv('TradeAnalysis_DBPassword')
if DBPassword == "None":
    CONFIG_MYSQL_CONNECTION_PASSWORD = ""
else:
    CONFIG_MYSQL_CONNECTION_PASSWORD = DBPassword
CONFIG_MYSQL_PATH = os.getenv('TradeAnalysis_mysql')
    
    
CONFIG_MYSQL_CONNECTION_DATABASE = "finance_fdata_master"
CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST = "finance_fdata_fut_hist"
CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST_10SECS = "finance_fdata_fut_hist_10secs"
CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST_5SECS = "finance_fdata_fut_hist_5secs"
CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_1MIN = "finance_fdata_price_1min"
CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_DAYEND = "finance_fdata_price_dayend"
CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_30MIN = "finance_fdata_price_30min"
CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_30MIN_IB = "finance_fdata_price_30min_ib"
CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_1MIN_IB = "finance_fdata_price_1min_ib"
CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_DAYEND_IB = "finance_fdata_price_dayend_ib"
CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_1MIN_FX = "finance_fdata_price_1min_fx"
CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_2MIN_FX = "finance_fdata_price_2min_fx"
CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_5MIN_FX = "finance_fdata_price_5min_fx"
CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_CRYPTO_BINANCE = "finance_fdata_crypto_binance"

CONFIG_BASE_DatafilePath = os.getenv('TradeAnalysis_DownloadFileBuffer')
CONFIG_BASE_FuturesDatafilePath = os.getenv('TradeAnalysis_DownloadFuturesFileBuffer')

CONFIG_BASE_ProjectPath = os.getenv('TradeAnalysis_ProjectPath')
CONFIG_BASE_CCompilerPath = os.getenv('TradeAnalysis_CCompilerPath')

CONFIG_CUDA_ThreadCount = int(os.getenv('TradeAnalysis_CUDAThreadCount'))


CONFIG_IB_USGAPPER_SCAN_END_TIME = os.getenv('TradeAnalysis_USGapperScanEndTime')

CONFIG_HL_BASE_URL = 'https://www.hl.co.uk/shares/shares-search-results/'

def GetUSFuturesContractList(lastTradeDateOrContractMonth):

        return {
                        "ES":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "NQ":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "RTY":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "YM":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "ZN":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "ZT":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "GC":[{"secType":"FUT", "exchange":"COMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "SI":[{"secType":"FUT", "exchange":"COMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth, "Multiplier":"5000"}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "CL":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "NG":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "RB":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "HO":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "PL":[{"secType":"FUT", "exchange":"NYMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "HE":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "ZW":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "ZR":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "ZL":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "ZS":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "ZC":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "KC":[{"secType":"FUT", "exchange":"NYBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "SB":[{"secType":"FUT", "exchange":"NYBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "OJ":[{"secType":"FUT", "exchange":"NYBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "CT":[{"secType":"FUT", "exchange":"NYBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "HG":[{"secType":"FUT", "exchange":"COMEX", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "GF":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "MBT":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        # "MET":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "ETHUSDRR":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        # "VIX":[{"secType":"FUT", "exchange":"CFE", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        # "DX":[{"secType":"FUT", "exchange":"NYBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "2YY":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "10Y":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                        "30Y":[{"secType":"FUT", "exchange":"CBOT", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}]
                        }



FuturesContractConfig = {
                "ES":{"secType":"FUT", "exchange":"CME", "currency":"USD"},
                "NQ":{"secType":"FUT", "exchange":"CME", "currency":"USD"},
                "RTY":{"secType":"FUT", "exchange":"CME", "currency":"USD"},
                "YM":{"secType":"FUT", "exchange":"CBOT", "currency":"USD"},
                "ZN":{"secType":"FUT", "exchange":"CBOT", "currency":"USD"},
                "ZT":{"secType":"FUT", "exchange":"CBOT", "currency":"USD"},
                "GC":{"secType":"FUT", "exchange":"COMEX", "currency":"USD"},
                "SI":{"secType":"FUT", "exchange":"COMEX", "currency":"USD"},
                "CL":{"secType":"FUT", "exchange":"NYMEX", "currency":"USD"},
                "NG":{"secType":"FUT", "exchange":"NYMEX", "currency":"USD"},
                "RB":{"secType":"FUT", "exchange":"NYMEX", "currency":"USD"},
                "HO":{"secType":"FUT", "exchange":"NYMEX", "currency":"USD"},
                "ZW":{"secType":"FUT", "exchange":"CBOT", "currency":"USD"},
                "ZS":{"secType":"FUT", "exchange":"CBOT", "currency":"USD"},
                "ZC":{"secType":"FUT", "exchange":"CBOT", "currency":"USD"},
                "HG":{"secType":"FUT", "exchange":"COMEX", "currency":"USD"},
                "KC":{"secType":"FUT", "exchange":"NYBOT", "currency":"USD"},
                "SB":{"secType":"FUT", "exchange":"NYBOT", "currency":"USD"},
                "CT":{"secType":"FUT", "exchange":"NYBOT", "currency":"USD"},
                "MBT":{"secType":"FUT", "exchange":"CME", "currency":"USD"},
                # "MET":[{"secType":"FUT", "exchange":"CME", "currency":"USD", "lastTradeDateOrContractMonth":lastTradeDateOrContractMonth}, {"LocalTimeZone":Config.CONFIG_LOCAL_TIMEZONE, "MarketTimeZone":'America/New_York'}],
                "ETHUSDRR":{"secType":"FUT", "exchange":"CME", "currency":"USD"},
                "2YY":{"secType":"FUT", "exchange":"CBOT", "currency":"USD"},
                "10Y":{"secType":"FUT", "exchange":"CBOT", "currency":"USD"},
                "30Y":{"secType":"FUT", "exchange":"CBOT", "currency":"USD"}
                }

def SplitDataframe(df, RowsPerBatch):
    i = 0
    dfAfterSplit = [df.loc[0:RowsPerBatch-1]]
    while len(df) > i + RowsPerBatch:
        i = i + RowsPerBatch
        dfAfterSplit.append(df.loc[i:i+RowsPerBatch-1])
    return dfAfterSplit

def TimeToTimezone(from_time, to_timezone = 'America/New_York'):
    return from_time

def TimeToLocalzone(from_time, to_timezone = CONFIG_LOCAL_TIMEZONE):
    return from_time




    
    
    