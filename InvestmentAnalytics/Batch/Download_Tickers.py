# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 14:15:42 2021

@author: Henry Cheung
"""
from bs4 import BeautifulSoup
import requests
import pymysql
import pandas as pd
from datetime import datetime, date, timedelta
import mysql.connector
from decimal import Decimal
import locale
import InvestmentAnalytics.Config as Config
from InvestmentAnalytics.Download_Yahoo import *

BaseURLs = [['http://eoddata.com/stocklist/NASDAQ/', 'XUSA', 'Nasdaq']
            , ['http://eoddata.com/stocklist/NYSE/', 'XUSA', 'NYSE']
            , ['http://eoddata.com/stocklist/AMEX/', 'XUSA', 'AMEX']
            , ['http://eoddata.com/stocklist/LSE/', 'XLON', 'LSE']]

EngChars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

# HKGBaseURL = 'http://eoddata.com/stocklist/HKEX.htm'

# US_IPO_BaseURL = 'https://stockanalysis.com/ipos/2021/'
US_IPO_BaseURL = 'https://stockanalysis.com/ipos/' + str(datetime.now().year) + '/'

mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
mycursor = mydb.cursor()

def GetRecentData(sql, DatabaseName = Config.CONFIG_MYSQL_CONNECTION_DATABASE):
    if DatabaseName is None:
        dbconnect = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD)
    else:
        dbconnect = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=DatabaseName)
    # sql = "SELECT COUNT(*) AS RecordCount FROM `" + DBTableName + "`"
    # print(pd.read_sql_query(sql, dbconnect))
    return pd.read_sql_query(sql, dbconnect)

def ImportTickerToDB(ticker, market):
    sql = "INSERT IGNORE INTO fdata_tickers (Ticker, Market, DateAdded) VALUES (%s, %s, %s)"
    val = (ticker, market, datetime.now())
    mycursor.execute(sql, val)
    mydb.commit()
    # print(ticker + ' in market ' + market+ ' added')

def ImportTicker(url, market):
    try:
        source = requests.get(url).text
        soup = BeautifulSoup(source, 'lxml')
        d = soup.find('div', attrs={'id':'ctl00_cph1_divSymbols'})
        rows = d.find_all('tr')
        for row in rows:
            try:
                ticker = row.find('td').text.strip()
                if (market == 'XHKG'):
                    ticker = ticker[-4:] + '.HK'
                if (market == 'XLON'):
                    ticker = ticker[-4:] + '.L'
                ImportTickerToDB(ticker, market)
            except Exception:
                pass 
    except Exception:
        pass 

def ImportIPOTickerToDB(ticker, market, ipo_date):
    sql = "INSERT IGNORE INTO fdata_tickers (Ticker, Market, DateAdded) VALUES (%s, %s, %s)"
    val = (ticker, market)
    mycursor.execute(sql, val, datetime.now())
    mydb.commit()

    sql = "INSERT IGNORE INTO fdata_tickers_ipo (Ticker, Market, IPO_Date) VALUES (%s, %s, %s)"
    val = (ticker, market, ipo_date)
    mycursor.execute(sql, val)
    mydb.commit()

    print(ticker + ' in market ' + market+ ' added')

def ImportIPOTicker(url, market):
    print('Start importing IPO Tickers')
    try:
        source = requests.get(url).text
        print('url is ' + url)
        soup = BeautifulSoup(source, 'lxml')
        d = soup.find('table', attrs={'class':'Table_ipotable__3Jaj4 Table_striped__v0BUc'})
        
        rows = d.find_all('tr')
        for row in rows:
            try:
                tds = row.find_all('td')
                date_time_obj = datetime.strptime(tds[0].text, '%b %d, %Y')
    
                ImportIPOTickerToDB(tds[1].text.strip(), 'XUSA', date_time_obj)
            except Exception:
                pass 
    except Exception:
        pass 

sql = "SELECT * FROM fdata_tickers"
print(sql)
print('Before adding tickers')
df_before = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
print(df_before)

for BaseURL in BaseURLs:
    for EngChar in EngChars:

        url = BaseURL[0] + EngChar + '.htm'
        ImportTicker(url, BaseURL[1])
        
# ImportTicker(HKGBaseURL, 'XHKG')

df = pd.read_excel(r'https://www.hkex.com.hk/eng/services/trading/securities/securitieslists/ListOfSecurities.xlsx',skiprows=2)

df = df.loc[df['Category'] == 'Equity']
df['Ticker'] = df['Stock Code'].apply(lambda x: '{0:0>4}'.format(x)) + '.HK'

for index, row in df.iterrows():
    try:
        ImportTickerToDB(row['Ticker'], 'XHKG')
    except Exception:
        pass     

ImportIPOTicker(US_IPO_BaseURL, 'XUSA')

sql = "SELECT * FROM fdata_tickers"
print(sql)
print('After adding tickers')
df_after = GetRecentData(sql, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
print(df_after)

df_merge = df_after.merge(df_before, how='left', on='Ticker', suffixes=('', '_y'))
# print(df_merge)
df_merge = df_merge[pd.isnull(df_merge['Market_y'])]

print('New tickers added are')
print(df_merge)

tickers = df_merge['Ticker'].tolist()

for ticker in tickers:
    try:
        DownloadYahooFundamental(mydb, ticker, "sector", 'fdata_yahoo_property', None)
    except Exception:
        print("error on downloading sector for ticker " + ticker)

for ticker in tickers:
    try:
        DownloadYahooFundamental(mydb, ticker, "industry", 'fdata_yahoo_property', None)
    except Exception:
        print("error on downloading industry for ticker " + ticker)

today_date = date.today()

for ticker in tickers:
    try:
        DownloadYahooFundamental(mydb, ticker, "marketCap", 'fdata_yahoo_fundamental', today_date)
    except Exception:
        print("error on downloading marketCap for ticker " + ticker)

