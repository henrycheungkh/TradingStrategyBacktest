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

from GoogleNews import GoogleNews
from newspaper import Article
import pandas as pd
from datetime import date, datetime, timedelta


pd.set_option('display.max_columns', None)

KeyWords = ['']

ticker = 'AGFY'

mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)

def UpdateGoogleNews(ticker, CaptureDate):
    # googlenews=GoogleNews(start='08/10/2021',end='08/11/2021')
    prior_day = CaptureDate - timedelta(days=1)
    print('Capture Date is ' + str(CaptureDate.strftime("%m/%d/%Y")))
    print('prior_day is ' + str(prior_day.strftime("%m/%d/%Y")))
    googlenews=GoogleNews(start=prior_day.strftime("%m/%d/%Y"),end=CaptureDate.strftime("%m/%d/%Y"))
    googlenews.search(ticker)
    result=googlenews.result()
    df=pd.DataFrame(result)
    # print(df)
    df['ticker'] = ticker
    df['date desc order'] = 0
    df.loc[df['date'].str.contains("min"), 'date desc order'] = 3
    df.loc[df['date'].str.contains("hour"), 'date desc order'] = 2
    df.loc[df['date'].str.contains("day"), 'date desc order'] = 1
    df.sort_values(by=['date desc order', 'datetime'],  inplace=True, ascending=False)
    
    # print(df)

    for index, row in df.iterrows():
    
        sql = "INSERT INTO fdata_us_gapper_list_news (CaptureDate, ticker, title, media, date, datetime, news_desc, link) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE media = %s, date = %s, datetime = %s, news_desc = %s, link = %s"
        val = (CaptureDate, row['ticker'], row['title'], row['media'], row['date'], row['datetime'], row['desc'], row['link'], row['media'], row['date'], row['datetime'], row['desc'], row['link'])
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        mydb.commit()
    
    print('News for ticker ' + ticker + ' uploaded')
        
    # df.to_csv(r'd:\temp\google_news.csv')
    
today = date.today()
print(today)
    
UpdateGoogleNews(ticker, today)

