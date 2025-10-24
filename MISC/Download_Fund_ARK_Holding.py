# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 23:05:24 2020

@author: Henry Cheung
"""


import csv
import requests
import datetime
import Config
import mysql.connector

# SELECT CP.*, PP.Shares AS PP_Shares, PP.MarketValue AS PP_MarketValue, PP.Weighting AS PP_Weighting, 
# (CP.Shares - PP.Shares) * CP.MarketValue / CP.Shares AS MarketValueAcquired FROM
# (SELECT * from fdata_fund_ark_holding where HoldingDate = '2020-12-04') CP LEFT join
# (SELECT * from fdata_fund_ark_holding where HoldingDate = '2020-12-03') PP
# ON PP.Fund = CP.Fund AND PP.Company = CP.Company AND PP.Ticker = CP.Ticker AND PP.Cusip
# WHERE CP.Shares > PP.Shares and CP.Weighting > PP.Weighting
# ORDER BY (CP.Shares - PP.Shares) * CP.MarketValue / CP.Shares DESC


CSV_URLs = ['https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_INNOVATION_ETF_ARKK_HOLDINGS.csv',
            'https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_AUTONOMOUS_TECHNOLOGY_&_ROBOTICS_ETF_ARKQ_HOLDINGS.csv',
            'https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_NEXT_GENERATION_INTERNET_ETF_ARKW_HOLDINGS.csv',
            'https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_GENOMIC_REVOLUTION_MULTISECTOR_ETF_ARKG_HOLDINGS.csv',
            'https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_FINTECH_INNOVATION_ETF_ARKF_HOLDINGS.csv']
mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
mycursor = mydb.cursor()


for CSV_URL in CSV_URLs:
    with requests.Session() as s:
        download = s.get(CSV_URL)
    
        decoded_content = download.content.decode('utf-8')
    
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        for row in my_list:
            try:
                # print(row)
                d = datetime.datetime.strptime(row[0], '%m/%d/%Y')
                # print(d)
                sql = "INSERT INTO fdata_fund_ark_holding (HoldingDate, Fund, Company, Ticker, Cusip, Shares, MarketValue, Weighting) VALUES (%s, %s, %s, %s,%s, %s, %s, %s)"
                val = (d, row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                mycursor.execute(sql, val)
                mydb.commit()
                
            except Exception:
                pass
        
        