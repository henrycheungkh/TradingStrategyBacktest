# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 00:01:35 2022

@author: Henry Cheung
"""

import pymysql
import pandas as pd
import InvestmentAnalytics.Config as Config


dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, 'finance_fdata_crypto_binance')
df = pd.read_sql_query("SELECT * FROM fdata_crypto_hist WHERE timeframe = '1d' AND ticker in ('ETHUSDT','BNBUSDT','SOLUSDT','LUNAUSDT','AVAXUSDT','MATICUSDT','TRXUSDT')", dbcon)

print(df)

df.to_csv(r'd:\temp\crypto_prices.csv', index=False)