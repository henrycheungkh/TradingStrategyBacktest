# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 23:05:50 2020

@author: Henry Cheung
"""


# https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hsio201120.htm
# https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hhio201120.htm

# https://www.hkstockradar.com/optionhsigoi0.htm
# https://www.hkstockradar.com/optionhsigoi1.htm
# https://www.hkstockradar.com/optionhhigoi0.htm
# https://www.hkstockradar.com/optionhhigoi1.htm

from bs4 import BeautifulSoup
import requests
import pymysql
import pandas as pd
from datetime import datetime, date, timedelta
import mysql.connector
from decimal import Decimal
import locale
import Config

ContractMonth = {'NOV-20':202011, 'DEC-20':202012, 'JAN-21':202101, 'FEB-21':202102, 'MAR-21':202103}

ContractList = {'HSI':'https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hsio', 'HHI':'https://www.hkex.com.hk/eng/stat/dmstat/dayrpt/hhio'}

today = date.today()
# print(today.strftime("%y%m%d"))
BackdateCount = 30

mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
mycursor = mydb.cursor()


for i in range(0, BackdateCount+1):
    try:
        valuedate = today + timedelta(days=-i)
        print(valuedate.strftime("%y%m%d"))
        for contract in ContractList:
            try:
                source = requests.get(ContractList[contract] + valuedate.strftime("%y%m%d") + '.htm').text
                soup = BeautifulSoup(source, 'lxml')
                # table = soup.find('a', attrs={'name':'month1'})
                lines = soup.text.splitlines()
                for l in lines:
                    cells = l.split()
                    try:
                        if cells[0] in ContractMonth:
                            if cells[20].strip() != '0':
                                sql = "INSERT INTO fdata_hkex_indexoptionstat (ValueDate, Ticker, ContractMonth, Strike, CallPut, PrevDayAfterHourOpeningPrice, PrevDayAfterHourDailyHigh, PrevDayAfterHourDailyLow, PrevDayAfterHourClosePrice, PrevDayAfterHourVolume, OpeningPrice, DailyHigh, DailyLow, OQPClose, OQPChange, IV, Volume, CombinedContractHigh, CombinedContractLow, CombinedVolume, OpenInterest, ChangeInOI) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                                val = (valuedate, contract, ContractMonth[cells[0]],  cells[1],  cells[2],  cells[3],  cells[4],  cells[5],  cells[6],  cells[7],  cells[9],  cells[10],  cells[11],  cells[12],  cells[13],  cells[14],  cells[15],  cells[17],  cells[18],  cells[19],  cells[20],  cells[21])
                                # print("inserted")
                                mycursor.execute(sql, val)
                                mydb.commit()
                                print('*' + cells[0] + ";" + cells[1]  + ";" + cells[2]+ ";" + cells[3]  + ";" + cells[4]+ ";" + cells[5]  + ";" + cells[6]+ ";" + cells[7]  + ";" +  cells[9]  + ";" + cells[10]+ ";" + cells[11]  + ";" + cells[12]+ ";" + cells[13]  + ";" + cells[14]+ ";" + cells[15]  + ";" + cells[17]+ ";" + cells[18]  + ";" + cells[19]+ ";" + cells[20]+ ";" + cells[21])
                            else:
                                print(cells[0] + ";" + cells[1]  + ";" + cells[2]+ ";" + cells[3]  + ";" + cells[4]+ ";" + cells[5]  + ";" + cells[6]+ ";" + cells[7]  + ";" +  cells[9]  + ";" + cells[10]+ ";" + cells[11]  + ";" + cells[12]+ ";" + cells[13]  + ";" + cells[14]+ ";" + cells[15]  + ";" + cells[17]+ ";" + cells[18]  + ";" + cells[19]+ ";" + cells[20]+ ";" + cells[21])
                    except Exception:
                            pass   
            except Exception:
                    pass   
    except Exception:
        pass   



