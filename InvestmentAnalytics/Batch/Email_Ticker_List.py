# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 02:33:37 2020

@author: Henry Cheung
"""
from InvestmentAnalytics.EmailModule import SendEmail
from datetime import date, datetime, timedelta

# from os import environ
# from sqlalchemy import create_engine

# import InvestmentAnalytics.Config as Config



now = datetime.now()
string = now.strftime('%Y%m%d')


# print(Message)
SendEmail(['henry.cheungkh@gmail.com','kirklaush@yahoo.com'], 'Gapper Scanning Ticker List - ' + date.today().strftime("%B %d, %Y"), "" , files=[r'G:\temp\TickerListForGapperScanning' + string + '.zip'])

