# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 12:49:27 2021

@author: Henry Cheung
"""

# from bs4 import BeautifulSoup
# import requests


# url = 'https://www.google.com/search?q=CWBR&tbm=nws'

# source = requests.get(url).text
# print('url is ' + url)
# soup = BeautifulSoup(source, 'lxml')
# print(soup)
# # hrefs = soup.find_all('a', attrs={'style':'text-decoration:none;display:block'})
# hrefs = soup.find_all('a')
# print('Hyperlinks are')
# print(hrefs)

import InvestmentAnalytics.Config as Config
import mysql.connector
import pymysql

from GoogleNews import GoogleNews
from newspaper import Article
import pandas as pd
from datetime import date, datetime, timedelta
import time

import requests
import logging
import threading

pd.set_option('display.max_columns', None)

KeyWords = ['']

mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)

def SynchroniseWebsiteThread(name, name2):
    logging.info("Thread %s: starting", name)
    SynchroniseWebsite(name)
    logging.info("Thread %s: finishing", name)

def SynchroniseWebsite(name):
    dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)
    WebsiteSynchMessageIterationCounter = 0
    print('Start synchronizing to the website')
    while True:
        Now_time = datetime.now()
        Now_string = Now_time.strftime('%Y-%m-%d')
        Now_string2 = Now_time.strftime('%Y%m%d')
        # print('Now_string2 = ' + Now_string2)
        sql = "SELECT * FROM `fdata_us_gapper_list_news` WHERE CaptureDate = '" + Now_string + "'"
        print(sql)
        GapperList = pd.read_sql_query(sql, dbcon)
        # print(GapperList)
        if len(GapperList) > 0:
        
            # URL = "https://stockfry.000webhostapp.com/gapper_update_post.php"
            URL = "https://www.vytrix.com/stockfry/gapper_news_update_post.php"
            
            PARAMS = { 'CaptureDate':Now_string2}
                
            for index, row in GapperList.iterrows():
                PARAMS['Ticker' + str(index+1)] = row['ticker']
                PARAMS['title' + str(index+1)] = row['title']
                PARAMS['media' + str(index+1)] = row['media']
                PARAMS['date_desc' + str(index+1)] = row['date']
                PARAMS['datetime' + str(index+1)] = row['datetime']
                PARAMS['news_desc' + str(index+1)] = row['news_desc']
                PARAMS['link_desc' + str(index+1)] = row['link']
            
            r = requests.post(URL, data=PARAMS)
            # print(r.status_code, r.reason)
            
            # if WebsiteSynchMessageIterationCounter == 0:
            print(str(len(GapperList)) + ' gappers news synchronised to website, with status code ' + str(r.status_code) + ' at ' + str(datetime.now()))
            # WebsiteSynchMessageIterationCounter = WebsiteSynchMessageIterationCounter + 1
            # if WebsiteSynchMessageIterationCounter >= 5:
            #     WebsiteSynchMessageIterationCounter = 0
        time.sleep(60*4)  

def UpdateGoogleNews(ticker, CaptureDate):
    # googlenews=GoogleNews(start='08/10/2021',end='08/11/2021')
    prior_day = CaptureDate - timedelta(days=1)
    # print('Capture Date is ' + str(CaptureDate.strftime("%m/%d/%Y")))
    # print('prior_day is ' + str(prior_day.strftime("%m/%d/%Y")))
    googlenews=GoogleNews(start=prior_day.strftime("%m/%d/%Y"),end=CaptureDate.strftime("%m/%d/%Y"))
    googlenews.search(ticker)
    result=googlenews.result()
    df=pd.DataFrame(result)
    # print(df)
    if len(df) > 0:
        df['ticker'] = ticker
        df['date desc order'] = 0
        df.loc[df['date'].str.contains("min"), 'date desc order'] = 3
        df.loc[df['date'].str.contains("hour"), 'date desc order'] = 2
        df.loc[df['date'].str.contains("day"), 'date desc order'] = 1
        df.sort_values(by=['date desc order', 'datetime'],  inplace=True, ascending=False)
        
        # print(df)
    
        for index, row in df.iterrows():

            try:
                sql = "INSERT INTO fdata_us_gapper_list_news (CaptureDate, ticker, title, media, date, datetime, news_desc, link) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE media = %s, date = %s, datetime = %s, news_desc = %s, link = %s"
                val = (CaptureDate, row['ticker'], row['title'], row['media'], row['date'], row['datetime'], row['desc'], row['link'], row['media'], row['date'], row['datetime'], row['desc'], row['link'])
                mycursor = mydb.cursor()
                mycursor.execute(sql, val)
                mydb.commit()
            except:
                pass
                # print('exception for input of ' + str(CaptureDate) + ', ' + str(row['ticker']), str(row['title']), str(row['media']), str(row['date']), str(row['datetime']), str(row['desc']), row['link'], row['media'], row['date'], row['datetime'], row['desc'], row['link'])
        
        print('News for ticker ' + ticker + ' uploaded')
    time.sleep(30)  
        
    # df.to_csv(r'd:\temp\google_news.csv')
    
today = date.today()
print(today)
today_string = today.strftime("%Y-%m-%d")

# UpdateGoogleNews(ticker, today)
dbcon = pymysql.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST, user=Config.CONFIG_MYSQL_CONNECTION_USER, password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD, database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
sql = "SELECT A.ticker FROM (select * from fdata_us_gapper_list WHERE CaptureDate = '" + today_string + "' ) A LEFT JOIN (SELECT DISTINCT ticker FROM fdata_us_gapper_list_news WHERE CaptureDate = '" + today_string + "') B ON A.ticker = B.ticker WHERE B.ticker is NULL ORDER BY ABS(A.CurrentPrice - A.PriorDayClose) / A.PriorDayClose DESC"
print(sql)
Tickers = pd.read_sql_query(sql, dbcon)

print(Tickers)

WebSynchronisation = "WebSynOff"
WebSynchronisation = "WebSynOn"

if WebSynchronisation == "WebSynOn":
    x = threading.Thread(target=SynchroniseWebsiteThread, args=('0', '0'), daemon=True)
    x.start()

for index, row in Tickers.iterrows():
    # print('Going to update news for ticker ' + row['ticker'])
    UpdateGoogleNews(row['ticker'], today)
    # time.sleep(20)  


# SynchroniseWebsite('0')
