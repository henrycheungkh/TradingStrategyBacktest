# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 13:22:03 2020

@author: Henry Cheung
"""


from InvestmentAnalytics.Download_HL import DownloadNewsBatch 
from InvestmentAnalytics.Download_HL import GetTickersList 

BaseURL = 'https://www.hl.co.uk/shares/shares-search-results/'
DaysOfNews = 3

# dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
Tickers, TickersOfHolding, TickersOfNonHolding = GetTickersList()

# t = Tickers.loc[Tickers['Ticker'] == 'BDEV.L']
# print(t)
# DownloadNewsBatch(BaseURL, t, DaysOfNews)


print('----------News for Holding----------')
DownloadNewsBatch(BaseURL, TickersOfHolding, DaysOfNews)
print('----------News for Other Stock----------')
DownloadNewsBatch(BaseURL, TickersOfNonHolding, DaysOfNews)