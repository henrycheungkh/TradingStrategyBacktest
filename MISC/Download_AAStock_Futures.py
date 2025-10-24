# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 22:15:35 2020

@author: Henry Cheung
"""

# http://www.aastocks.com/tc/stocks/market/bmpfutures.aspx?future=200000

from bs4 import BeautifulSoup
import requests
import mysql.connector
from decimal import Decimal
import locale
from datetime import datetime
import Config
import pytz
import time

locale.setlocale(locale.LC_ALL, 'USA')

FuturesList = [["200000", "HSI", "FUT"],
               ["200001", "HSI", "FUT"],
               ["200200", "HHI", "FUT"],
               ["200201", "HHI", "FUT"],
               ["242500", "HSTECH", "FUT"],
               ["242501", "HSTECH", "FUT"]]

PrevCapturedTick = {"200000":[0,-1], "200001":[0,-1], "200200":[0,-1], "200201":[0,-1], "242500":[0,-1], "242501":[0,-1] }


def DownloadFuturesPriceTick(Futures, UploadToDB = True):

    source = requests.get('http://www.aastocks.com/tc/stocks/market/bmpfutures.aspx?future=' + Futures[0]).text
    soup = BeautifulSoup(source, 'lxml')
    # print(soup.prettify())
    
    tag = soup.find('div', class_='font26 bold cls ff-arial')
    price = Decimal(locale.atoi(str(tag.text).strip().strip(",")))
    if not UploadToDB:
        print("Futures Price is " + str(price))
    
    tag = soup.find_all('div', class_='font18 txt_c bold cls ff-arial')
    cum_vol = Decimal(locale.atoi(str(tag[2].text).strip().strip(",")))
    if not UploadToDB:
        print("Volume is " + str(cum_vol))

    tag = soup.find_all('div', class_='float_r cls')
    if not UploadToDB:
        print("Expiry is " + tag[4].text[0:4] + tag[4].text[5:7])
        print("Gross Open Interest is " + tag[2].text)
        print("Net Open Interest is " + tag[3].text)
        # print(tag)
    expiry = int(tag[4].text[0:4] + tag[4].text[5:7])
    GrossOpenInterest =  int(locale.atoi(str(tag[2].text).strip().strip(",")))
    NetOpenInterest =  int(locale.atoi(str(tag[3].text).strip().strip(",")))
    MarketOpenText = str(tag[1].text)
    # print(MarketOpenText)
    if MarketOpenText == 'N/A':
        MarketDayOpen = 0
    else:
        MarketDayOpen = int(locale.atoi(MarketOpenText.strip().strip(",")))
    if not UploadToDB:
        print("Market Open = " + str(MarketOpen))

    tag = soup.find('span', class_='float_r cls')
    if tag.text == 'N/A':
        DayRangeLow = 0
        DayRangeHigh = 0
    else:
        DayRangeText = tag.text.split(' - ')
        DayRangeLow = int(locale.atoi(DayRangeText[0].strip().strip(",")))
        DayRangeHigh = int(locale.atoi(DayRangeText[1].strip().strip(",")))
    
    if UploadToDB and MarketDayOpen != 0 and PrevCapturedTick[Futures[0]][1] != -1 and ((PrevCapturedTick[Futures[0]][0] != price) or (PrevCapturedTick[Futures[0]][1] != cum_vol)):
        mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
        mycursor = mydb.cursor()
        sql = "INSERT INTO fdata_fut_tick (Ticker, InstrumentType, Expiry, tDateTime, price, cum_vol,GrossOpenInterest,NetOpenInterest, MarketDayOpen, DayRangeLow, DayRangeHigh, src) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        # val = (Futures[1], Futures[2], Futures[3], datetime.now(tz=None), price, cum_vol, "AAStock")
        val = (Futures[1], Futures[2], expiry, datetime.now(tz=None), price, cum_vol, GrossOpenInterest, NetOpenInterest, MarketDayOpen, DayRangeLow, DayRangeHigh, "AAStock")
        mycursor.execute(sql, val)
        mydb.commit()
        print("*" + Futures[1]+", "+Futures[2]+", " + str(expiry) + ", " + str(price) + ", " + str(cum_vol)+ ", " + str(GrossOpenInterest)+ ", " + str(NetOpenInterest)+ ", " + str(MarketDayOpen)+ ", " + str(DayRangeLow)+ ", " + str(DayRangeHigh))
    else:
        print(Futures[1]+", "+Futures[2]+", " + str(expiry) + ", " + str(price) + ", " + str(cum_vol)+ ", " + str(GrossOpenInterest)+ ", " + str(NetOpenInterest)+ ", " + str(MarketDayOpen)+ ", " + str(DayRangeLow)+ ", " + str(DayRangeHigh))
    PrevCapturedTick[Futures[0]][0] = price
    PrevCapturedTick[Futures[0]][1] = cum_vol
    

while True:
    for f in FuturesList:
        try:
            tz = pytz.timezone('Hongkong')
            HK_now = int(datetime.now(tz).strftime("%H%M"))
            # print(HK_now)
            if (HK_now < 330) or (HK_now > 830):
                DownloadFuturesPriceTick(f)
            else:
                print(HK_now, ' - out of trading hour')
                if HK_now < 800:
                    print('wait for half an hour')
                    time.sleep(30*60)
                if HK_now < 815:
                    print('wait for 15 mins')
                    time.sleep(15*60)
        except Exception:
            pass

# DownloadFuturesPriceTick(FuturesList[0], False)