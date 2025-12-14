# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 10:59:30 2023

@author: Henry Cheung
"""
import pandas as pd
import InvestmentAnalytics.Config as Config
import InvestmentAnalytics.DBUtil as DBUtil
from sqlalchemy.sql import text
import xml.etree.ElementTree as ET


from ib_insync import IB, Stock
import nest_asyncio
nest_asyncio.apply()


IB_API_hostname = Config.CONFIG_IB_CONNECTION_HOST
IB_API_port = Config.CONFIG_IB_CONNECTION_PORT
IB_API_clientId = Config.CONFIG_IB_CONNECTION_DEFAULT_CLIENT_ID 

print('In DownloadUSStockDividendFromIB.py')
print('IB_API_hostname = ' + IB_API_hostname)
print('IB_API_port = ')
print(IB_API_port)
print('IB_API_clientId = ')
print(IB_API_clientId)
time.sleep(10)


def fetch_dividend_data(ib, ticker):
    contract = Stock(ticker, exchange='SMART', currency='USD')
    details = ib.reqFundamentalData(contract, 'ReportsFinSummary')
    
    # Here, I'm just returning the raw XML data. You might want to parse it for relevant details.
    return details

if __name__ == "__main__":
    
    sql = "select distinct ticker from fdata_price_dayend_ib"

    print(sql)
    Tickers = pd.read_sql(sql,con=DBUtil.GetSQLAlchemyEngine(DatabaseName=Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_DAYEND_IB))
    print(Tickers)
    
    TickersTotalCount = len(Tickers)
    TickersCount = 1

    # Create an IB instance and connect
    ib = IB()
#     ib.connect('127.0.0.1', 7496, clientId=1)  # 7497 is the default port for TWS paper trading
    ib.connect(IB_API_hostname, IB_API_port, clientId=IB_API_clientId)  # 7497 is the default port for TWS paper trading
    
    for index, row in Tickers.iterrows():
        # print('Download for ' + row['ticker'] + ' (' + str(TickersCount) + '/' + str(TickersTotalCount) + ')')
        # ticker = 'AAPL'
        
        # if row['ticker'] == 'AAA':
        if True:
            print('Try to download for ' + row['ticker'] + ' (' + str(TickersCount) + '/' + str(TickersTotalCount) + ')')
            data = fetch_dividend_data(ib, row['ticker'])
            if len(data) > 0:
                # print(len(data))
                # print(data)  # This will print XML data. You'll need to parse this to extract dividend information.
                root = ET.fromstring(data)
                for element in root:
                    # print(element.tag, element.attrib, element.text)
                #     # if element.tag in ('DividendPerShares', 'TotalRevenues', 'Dividends', 'EPSs'):
                #     # if element.tag in ('DividendPerShares', 'Dividends'):
                    if element.tag in ('Dividends'):
                        for values in element:
                            sql = "INSERT IGNORE INTO fdata_finsummary_dividend (ticker, type, exDate, recordDate, payDate, declarationDate, value) values ('" + row['ticker'] + "', '" + values.attrib['type'] + "', '" + values.attrib['exDate'] + "', '" + values.attrib['recordDate'] + "', '" + values.attrib['payDate'] + "', '" + values.attrib['declarationDate'] + "', " + values.text + ")"
                #             print(element.tag, values.attrib['asofDate'], values.attrib['reportType'], values.attrib['period'], values.text) 
    
                            # print(sql)
                            statement = text(sql)
                            # line = { "timeframe": BarSize}
                            engine = DBUtil.GetSQLAlchemyEngine(DatabaseName=Config.CONFIG_MYSQL_CONNECTION_DATABASE_PRICE_DAYEND_IB)
                            # engine.execute(statement)
                            with engine.connect() as conn:
                                # result = conn.execute(statement)
                                conn.execute(statement)
 #                               conn.commit()
                                conn.close()
                            
                            # print('sql executed')
                
        TickersCount = TickersCount + 1

    ib.disconnect()
