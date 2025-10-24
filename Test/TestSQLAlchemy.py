# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 16:20:34 2022

@author: henry
"""


# Using pymysql

# import pymysql
# dbcon = pymysql.connect(host='localhost', user='root', password='', database='finance_fdata_master')


# Using SQLAlchemy

from os import environ
from sqlalchemy import create_engine
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# uri = 'pymysql://root@localhost:3306/finance_fdata_master'
# uri = r'mysql://root@127.0.0.1:3306/finance_fdata_master'
# uri = r'mysql://root:@127.0.0.1:3306/finance_fdata_master'
# uri = r'mysql://root@localhost/finance_fdata_master'
# uri = 'mysql+pymysql://root:@localhost/finance_fdata_master'

# db_uri = environ.get(uri)
# engine = create_engine(uri, echo=True)


# sql = "UPDATE fdata_backtest_batch SET LastBestAbsSharpeRatio = %s, LastRunStartDate = StartDate, LastRunEndDate = EndDate, LastRunTimeInMinute = %s WHERE BatchGroup = %s AND BatchID = %s AND BatchSubID = %s AND StrategyName = %s"
# sql = "UPDATE fdata_backtest_batch SET LastBestAbsSharpeRatio = 0.7084736, LastRunStartDate = '2019-01-01', LastRunEndDate = '2022-08-19', LastRunTimeInMinute = 583 WHERE BatchGroup = 'Henry Routine X25' AND BatchID = 14 AND BatchSubID = 0 AND StrategyName = 'CorrelationOnSpecificTimeSectionStrategy'"
# sql = "UPDATE fdata_backtest_batch SET LastBestAbsSharpeRatio = 0.7084736, LastRunTimeInMinute = 584 WHERE BatchID = 14"

# engine.execute(sql)









# uri = 'mysql+pymysql://root:@localhost/finance_fdata_master'
# uri = 'mysql+pymysql://root:@localhost/finance_fdata_price_dayend_ib'
# uri = 'mysql+pymysql://root:@localhost/finance_fdata_price_1min_ib'
# uri = 'mysql+pymysql://root:@localhost/finance_fdata_price_1min_ib_2024'
# uri = 'mysql+pymysql://root:@localhost/finance_fdata_price_1min_ib_2023_h1'
# uri = 'mysql+pymysql://root:@localhost/finance_fdata_price_1min_ib_2023_q1'
# uri = 'mysql+pymysql://root:@localhost/finance_fdata_fut_hist'
uri = 'mysql+pymysql://root:@localhost/finance_fdata_fut_hist_10secs_2024'

engine = create_engine(uri, echo=True)

# df = pd.read_sql("SELECT * FROM finance_fdata_price_30min_ib.fdata_price_30min_ib WHERE DATE(DateTime) >= '2025-01-01'", con=engine)    
# df = pd.read_sql("SELECT MIN(DateTime), MAX(DateTime) FROM fdata_price_1min_ib", con=engine)    
df = pd.read_sql("SELECT MIN(tDateTime), MAX(tDateTime) FROM finance_fdata_fut_hist_10secs_2024.fdata_fut_hist", con=engine)    

print(df)


# sql = "INSERT INTO finance_fdata_price_1min_ib_2025.fdata_price_1min_ib SELECT * FROM finance_fdata_price_1min_ib.fdata_price_1min_ib WHERE DATE(DateTime) >= '2025-01-01'"



# sql = "DELETE FROM finance_fdata_fut_hist_10secs_2024.fdata_fut_hist where DATE(tDateTime) >= '2025-01-01'"


# engine.execute(sql)


# from datetime import datetime, date, timedelta
# from pytz import timezone


# US_time = datetime.now(timezone('America/New_York'))
# print(US_time)

# # sql = "INSERT INTO fdata_us_gapper_list (CaptureDate, ticker, Sector, Industry, PriorDayClose, CurrentPrice, 30MA_Vol, Today_Vol, MarketCap, FreeFloat, BidAskSpread, FirstCaptureDatetime, FirstCapturePrice) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE CurrentPrice = %s, 30MA_Vol = %s, Today_Vol = %s"
# # val = (US_time, self.TickerList.loc[TickerIndex, 'ticker'], self.TickerList.loc[TickerIndex, 'Sector'], self.TickerList.loc[TickerIndex, 'Industry'], self.TickerList.loc[TickerIndex, 'PriorDayClose'], self.TickerList.loc[TickerIndex, 'CurrentPrice'], MA30Vol, self.ReqIDVol[batch_id], MarketCap, FreeFloat, 0.1, US_time, self.TickerList.loc[TickerIndex, 'CurrentPrice'], self.TickerList.loc[TickerIndex, 'CurrentPrice'], MA30Vol, self.ReqIDVol[batch_id])
# # val = (US_time, "AAPL", self.TickerList.loc[TickerIndex, 'Sector'], self.TickerList.loc[TickerIndex, 'Industry'], self.TickerList.loc[TickerIndex, 'PriorDayClose'], self.TickerList.loc[TickerIndex, 'CurrentPrice'], MA30Vol, self.ReqIDVol[batch_id], MarketCap, FreeFloat, 0.1, US_time, self.TickerList.loc[TickerIndex, 'CurrentPrice'], self.TickerList.loc[TickerIndex, 'CurrentPrice'], MA30Vol, self.ReqIDVol[batch_id])

# from sqlalchemy import insert
# from sqlalchemy import MetaData, Table, Column, Integer, Float, String, Date

# meta = MetaData()

# fdata_us_gapper_list = Table(
#    'fdata_us_gapper_list', meta, 
#    Column('CaptureDate', Date, primary_key = True), 
#    Column('ticker', String, primary_key = True), 
#    Column('Sector', String), 
#    Column('Industry', String), 
#    Column('PriorDayClose', Float), 
#    Column('CurrentPrice', Float), 
#    Column('Today_Vol', Float), 
#    Column('30MA_Vol', Float), 
#    Column('MarketCap', Float), 
#    Column('FreeFloat', Float), 
#    Column('BidAskSpread', Float), 
#    Column('FirstCaptureDatetime', Date), 
#    Column('FirstCapturePrice', Float), 
# )

# # stmt = insert(fdata_us_gapper_list).values(CaptureDate=US_time, ticker="AAPL", Sector="", Industry="", PriorDayClose=0, CurrentPrice=0, Today_Vol=0, 30MA_Vol=0, MarketCap=0, FreeFloat=0, BidAskSpread=0, FirstCaptureDatetime=US_time, FirstCapturePrice=0)
# stmt = insert(fdata_us_gapper_list).values(CaptureDate=US_time, ticker="AAPL", Sector="", Industry="", PriorDayClose=0, CurrentPrice=0, Today_Vol=0, MarketCap=0, FreeFloat=0, BidAskSpread=0, FirstCaptureDatetime=US_time, FirstCapturePrice=0)

# with engine.connect() as conn:
#     result = conn.execute(stmt)
#     conn.commit()
    
# df = pd.read_sql("SELECT DateTime, COUNT(close) FROM fdata_price_dayend_ib WHERE DataType = 'ADJUSTED_LAST' AND DATE(DateTime) >= '2024-08-01' GROUP BY DateTime  ", con=engine)    

# df = pd.read_sql("SELECT MIN(DateTime), MAX(DateTime) FROM fdata_price_1min_ib", con=engine)    
# df = pd.read_sql("SELECT B.ticker, B.expiry, TIME(B.tDateTime) FROM (SELECT ticker, DATE(tDateTime) as ValueDate, max(vol) as MaxVolume FROM fdata_fut_hist WHERE ticker in ('ES', 'NQ', 'RTY', 'YM') AND DataType = 'TRADES' AND timeframe = '1 min' and tDateTime > '2023-05-15' GROUP BY ticker, timeframe, DATE(tDateTime), DataType ORDER BY ticker, DATE(tDateTime) DESC) A LEFT JOIN (SELECT * FROM fdata_fut_hist WHERE ticker in ('ES', 'NQ', 'RTY', 'YM') AND DataType = 'TRADES' AND timeframe = '1 min' and tDateTime > '2023-05-15') B ON A.ticker = B.ticker AND A.ValueDate = DATE(B.tDateTime) AND A.MaxVolume = B.vol", con=engine)    

# sql = "SELECT A.ticker FROM (SELECT ticker FROM `fdata_price_1min_ib` WHERE DATE(DateTime) = '2023-05-05' GROUP BY ticker) A WHERE A.ticker NOT IN (SELECT ticker FROM `fdata_price_1min_ib` WHERE DATE(DateTime) >= '2023-04-27' AND DATE(DateTime) <= '2023-04-28' GROUP BY ticker) B"
# sql = "SELECT A.ticker FROM (SELECT ticker FROM `fdata_price_1min_ib` WHERE DATE(DateTime) = '2023-05-01' GROUP BY ticker) A WHERE A.ticker NOT IN (SELECT ticker FROM `fdata_price_1min_ib` WHERE DATE(DateTime) >= '2023-04-27' AND DATE(DateTime) <= '2023-04-28' GROUP BY ticker)"
# df = pd.read_sql(sql, con=engine)    

# print(df)

# df = pd.read_sql("SELECT * FROM fdata_price_dayend_ib WHERE DataType = 'ADJUSTED_LAST' AND DATE(DateTime) = '2024-08-12' AND ticker not in (SELECT ticker FROM fdata_price_dayend_ib WHERE DataType = 'ADJUSTED_LAST' AND DATE(DateTime) = '2024-08-09') ORDER BY close * vol DESC ", con=engine)    

# print(df)


# df = pd.read_sql("SELECT A.*, B.ADJUSTED_LAST_close FROM (SELECT ticker,  DateTime, close as TRADES_close FROM fdata_price_dayend_ib WHERE DataType = 'TRADES' AND ticker = 'NVDA') A INNER JOIN  (SELECT ticker,  DateTime, close as ADJUSTED_LAST_close FROM fdata_price_dayend_ib WHERE DataType = 'ADJUSTED_LAST' AND ticker = 'NVDA') B ON A.ticker = B.ticker AND A.DateTime = B.DateTime", con=engine)    

# print(df)

# uri = 'mysql+pymysql://root:@localhost/finance_fdata_fut_hist_10secs_2023_h1'
# # uri = 'mysql+pymysql://root:@localhost/finance_fdata_fut_hist'
# engine = create_engine(uri, echo=True)
# df = pd.read_sql("SELECT MIN(tDateTime), MAX(tDateTime) FROM fdata_fut_hist", con=engine)    

# print(df)


# df.to_csv(r'd:\temp\MissedTicker.csv', index=False)






# import InvestmentAnalytics.Config as Config
# import InvestmentAnalytics.DBUtil as DBUtil

# from datetime import date, datetime
# import pytz

# today = date.today()
# print("Today's date:", today)

# d1 = today.strftime("%d/%m/%Y")


# StrategyExecution = pd.read_sql("SELECT * FROM strategy_execution_config",con=DBUtil.GetSQLAlchemyEngine())   
# print(StrategyExecution)

# def GetTimeInLocalTimezone(ScanningTime, ScanningTimezone):
#     ScanningTime = datetime.strptime(today.strftime("%d/%m/%Y") + ' ' + str(ScanningTime)[-8:], '%d/%m/%Y %H:%M:%S')
#     return pytz.timezone(ScanningTimezone).localize(ScanningTime).astimezone(pytz.timezone(Config.CONFIG_LOCAL_TIMEZONE))

# def isNowInTimePeriod(startTime, endTime, nowTime = datetime.now().astimezone(pytz.timezone(Config.CONFIG_LOCAL_TIMEZONE))): 
#     print('nowTime is')
#     print(nowTime)
#     if startTime < endTime: 
#         return nowTime >= startTime and nowTime <= endTime 
#     else: 
#         #Over midnight: 
#         return nowTime >= startTime or nowTime <= endTime 

# for index, row in StrategyExecution.iterrows():
#     StartScanningTime = row['StartScanningTime']
#     EndScanningTime = row['EndScanningTime']
#     ScanningTimezone = row['ScanningTimezone']
#     print(StartScanningTime)
#     print(EndScanningTime)
#     print(ScanningTimezone)
    
#     StartScanningTime = GetTimeInLocalTimezone(StartScanningTime, ScanningTimezone)
#     EndScanningTime = GetTimeInLocalTimezone(EndScanningTime, ScanningTimezone)

#     # StartScanningTime = datetime.strptime(d1 + ' ' + str(StartScanningTime)[-8:], '%d/%m/%Y %H:%M:%S')
#     # est = pytz.timezone(ScanningTimezone)
#     # # StartScanningTime = est.localize(StartScanningTime)
#     # print(Config.CONFIG_LOCAL_TIMEZONE)
#     # StartScanningTime = est.localize(StartScanningTime).astimezone(pytz.timezone(Config.CONFIG_LOCAL_TIMEZONE))
    
#     # StartScanningTime = datetime.strptime(d1 + ' ' + StartScanningTime.strftime("%H:%M:%S"), '%d/%m/%Y %H:%M:%S')
#     # StartScanningTime = StartScanningTime.astimezone(ScanningTimezone)
#     print(StartScanningTime)
#     print(EndScanningTime)
#     # print(isNowInTimePeriod(StartScanningTime, EndScanningTime, nowTime = datetime.now().astimezone(pytz.timezone(Config.CONFIG_LOCAL_TIMEZONE))))
#     print(isNowInTimePeriod(StartScanningTime, EndScanningTime))




