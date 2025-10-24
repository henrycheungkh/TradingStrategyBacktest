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

# BaseURL = 'https://stockanalysis.com/ipos/2021-list/'
BaseURL = 'https://stockanalysis.com/ipos/2021/'

BaseURLs = [['http://eoddata.com/stocklist/NASDAQ/', 'XUSA', 'Nasdaq']
            , ['http://eoddata.com/stocklist/NYSE/', 'XUSA', 'NYSE']
            , ['http://eoddata.com/stocklist/AMEX/', 'XUSA', 'AMEX']
            , ['http://eoddata.com/stocklist/LSE/', 'XLON', 'LSE']]
EngChars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

HKGBaseURL = 'http://eoddata.com/stocklist/HKEX.htm'

mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
mycursor = mydb.cursor()


def ImportTickerToDB(ticker, market, ipo_date):
    # mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
    # mycursor = mydb.cursor()
    sql = "INSERT IGNORE INTO fdata_tickers (Ticker, Market) VALUES (%s, %s)"
    val = (ticker, market)
    mycursor.execute(sql, val)
    mydb.commit()

    sql = "INSERT IGNORE INTO fdata_tickers_ipo (Ticker, Market, IPO_Date) VALUES (%s, %s, %s)"
    val = (ticker, market, ipo_date)
    mycursor.execute(sql, val)
    mydb.commit()

    print(ticker + ' in market ' + market+ ' added')
   

def ImportTicker(url, market):
    print('Start importing Tickers')
    # url = BaseURL[0] + EngChar + '.htm'
    try:
        
        source = requests.get(url).text
        print('url is ' + url)
        soup = BeautifulSoup(source, 'lxml')
        # d = soup.find('table', attrs={'class':'maintable tablesort'})
        d = soup.find('table', attrs={'class':'Table_ipotable__3Jaj4 Table_striped__v0BUc'})
        # print('after soup.find')
    
    # rows = []
    # # for child in soup.find_all('table')[4].children:
    # for child in d.children:
    #     row = []
    #     for td in child:
    #         try:
    #             row.append(td.text.replace('\n', ''))
    #         except:
    #             continue
    #     if len(row) > 0:
    #         rows.append(row)

    # df = pd.DataFrame(rows[1:], columns=rows[0])   
    
    # print(df)
        
        
        rows = d.find_all('tr')
        # print('after find all tr')
        for row in rows:
            try:
                
                
                # print(row)
                tds = row.find_all('td')
                # print(tds[0].text)
                date_time_obj = datetime.strptime(tds[0].text, '%b %d, %Y')
                # print(date_time_obj)
                # print(tds[0].text)
                # print(tds[1].text)
           
            
        #         # ticker = row.find('td').text.strip()
        #         # if (market == 'XHKG'):
        #         #     ticker = ticker[-4:] + '.HK'
        #         # if (market == 'XLON'):
        #         #     ticker = ticker[-4:] + '.L'
    
        #         # print(ticker + ' in market ' + market)
    
                ImportTickerToDB(tds[1].text.strip(), 'XUSA', date_time_obj)
    
        #         # mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
        #         # mycursor = mydb.cursor()
        #         # sql = "INSERT INTO fdata_tickers (Ticker, Market) VALUES (%s, %s)"
        #         # val = (ticker, market)
        #         # mycursor.execute(sql, val)
        #         # mydb.commit()
    
        #         # print(ticker + ' in market ' + market+ ' added')
        
        
        
            except Exception:
                pass 

    except Exception:
        pass 

ImportTicker(BaseURL, 'XUSA')

# for BaseURL in BaseURLs:
#     for EngChar in EngChars:

#         url = BaseURL[0] + EngChar + '.htm'
#         ImportTicker(url, BaseURL[1])
        
# ImportTicker(HKGBaseURL, 'XHKG')

# df = pd.read_excel(r'https://www.hkex.com.hk/eng/services/trading/securities/securitieslists/ListOfSecurities.xlsx',skiprows=2)

# df = df.loc[df['Category'] == 'Equity']
# df['Ticker'] = df['Stock Code'].apply(lambda x: '{0:0>4}'.format(x)) + '.HK'

# for index, row in df.iterrows():
#     try:
#         ImportTickerToDB(row['Ticker'], 'XHKG')
#     # print(row['c1'], row['c2'])
#     except Exception:
#         pass     

