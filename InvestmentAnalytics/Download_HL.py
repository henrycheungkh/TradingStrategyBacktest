# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 15:35:21 2020

@author: Henry Cheung
"""


# https://www.hl.co.uk/shares/shares-search-results/8/888-holdings-ordinary-0.5p/financial-statements-and-reports

from bs4 import BeautifulSoup
import requests
import pymysql
import pandas as pd
from datetime import datetime, date, timedelta
import mysql.connector
from decimal import Decimal
import locale
import InvestmentAnalytics.Config as Config

FinancialStatementDataNameDict ={"Revenue:":"Revenue", 
               "Operating Profit / (Loss):":"Operating Profit / Loss",
               "Revenue:":"Revenue", 
               "Net Interest:":"Net Interest", 
               "Profit Before Tax:":"Profit Before Tax", 
               "Profit after tax from continuing operations:":"Profit after tax from continuing operations", 
               "Profit after tax from discontinuing operations:":"Profit after tax from discontinuing operations", 
               "Profit for the period:":"Profit for the period", 
               "Equity holders of parent company:":"Equity holders of parent company",
               "Minority Interests / Other Equity:":"Minority Interests / Other Equity", 
               "Total Dividend Paid:":"Total Dividend Paid", 
               "Retained Profit / (Loss) for the Financial Year:":"Retained Profit / (Loss) for the Financial Year", 
               "Basic:":"EPS (Basic)", 
               "Diluted:":"EPS (Diluted)", 
               "Adjusted:":"EPS (Adjusted)", 
               "Dividend per Share:":"Dividend per Share"
               }

def DownloadHLFinancialStatementAndReportsBatch(BaseURL, Tickers, UploadToDB = True):

    # dbcon = pymysql.connect("localhost", "root", "", "finance")
    # Tickers = pd.read_sql_query("select * from fdata_tickers_altid where AltID_Type = 'HL'", dbcon)

    mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
    mycursor = mydb.cursor()

    
    for index, Ticker in Tickers.iterrows():
        print(str(datetime.now()))
        try:
            print(Ticker['Ticker'], Ticker['AltID'])
            url = BaseURL + Ticker['AltID'] + '/financial-statements-and-reports'
            print(url)
            source = requests.get(url).text
            soup = BeautifulSoup(source, 'lxml')
            
            data = []
            header = []
            table = soup.find('table', attrs={'class':'factsheet-table responsive'})
            table_body = table.find('tbody')
            
            
            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('th')
                cols = [ele.text.strip() for ele in cols]
                header.append([ele for ele in cols if ele])
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols if ele])
            
            for i in range(1, 6):
            
                try:
                    h = header[0][i]
                    dt_obj = datetime.strptime(h, '%d/%m/%Y')
                    # mydb = mysql.connector.connect(host="localhost",user="root",password="",database="finance")
                    # mycursor = mydb.cursor()
                    for j in range(2, 20):
                        try:
                            v = Decimal(data[j][i].strip("(").strip(")"))
                            if data[j][i].find("(") != -1:
                                v=-1 * v
        
                            sql = "INSERT INTO fdata_hl_fundamental (Ticker, StatementDate, Name, Value) VALUES (%s, %s, %s, %s)"
                            val = (Ticker['Ticker'], dt_obj, FinancialStatementDataNameDict[data[j][0]], v)
                            mycursor.execute(sql, val)
                            mydb.commit()
                        except Exception:
                            pass
                except Exception:
                    pass
                i = i + 1

        except Exception:
            pass


NewsKeywordExcludeList = ["Net Asset Value", "Transaction in Own Shares", "Issue of Equity", 
                          "Blocklisting Allotment of new shares", "Block listing Allotment of new shares", "Block listing - Allotment of new shares","Form 8.3",
                          "Form 8.5", "FORM 8.5", "Dividend Declaration", "Monthly Update",
                          "Gearing Announcement", "Result of AGM", "Price Monitoring Extension","Results of Court Meeting and General Meeting",
                          "Holding(s) in Company", "Total Voting Rights", "Redemption Price"]

DrillDownKeywordList = ["broker round-up", "(Sharecast News)"]
NewsFilteringKeywordList = ["broker round-up"]

PreferredNewsKeyword = ["profits rise"]

LoadingSign = ['-', "\\", '|', "/"]

def DownloadNewsBatch(BaseURL, Tickers, TickerAlias, DaysOfNews = 7, UploadToDB = False, DisplayLoadingStatus = True, ThreadID = -1):
    AccumulatedText = ""
    AccumulatedTextList = []
    TickerCount = 0
    LoadingSignCount = 0
    if UploadToDB:
        mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
        mycursor = mydb.cursor()

    for index, Ticker in Tickers.iterrows():
        # print('Ticker is')
        # print(Ticker)
        # print('TickerAlias is')
        # print(TickerAlias)
        ThisTickerAlias = TickerAlias.loc[TickerAlias['Ticker'] == Ticker['Ticker']]
        # print('ThisTickerAlias is')
        # print(ThisTickerAlias)
        try:
            if DisplayLoadingStatus:
                print("Loading " + LoadingSign[LoadingSignCount], end="\r")
            LoadingSignCount = (LoadingSignCount + 1) % 4
            TickerCount = TickerCount + 1
            if TickerCount % 25 == 0:
                print("Thread " + str(ThreadID) + " --- " + str(TickerCount) + " Tickers scanned at " + str(datetime.now()))
                
            PERatio = 0
            DivYield = 0
            RevGrowth = [0,0,0]
                
            url = BaseURL + Ticker['AltID'] + '/share-news'
            # print('url is')
            # print(url)
            source = requests.get(url).text
            soup = BeautifulSoup(source, 'lxml')
            try:
                ShareTitle = soup.find('meta', attrs={'name':'Share_Title'})['content']
                # print('ShareTitle is')
                # print(ShareTitle)
            except Exception:
                pass
            try:
                price = soup.find('span', attrs={'class':'positive change', 'data-grid':'stocks', 'data-field':'perc'}).text.strip()
            except Exception:
                try:
                    price = '-' + soup.find('span', attrs={'class':'negative change', 'data-grid':'stocks', 'data-field':'perc'}).text.strip() 
                except Exception:
                    price = '0'
            try:
                priceVal = float(price.replace('(', '').replace(')', '').replace('%', ''))
            except Exception:
                priceVal = 0.0
            table = soup.find('ul', attrs={'class':'headlines'})
            headlines = table.find_all('li')

            for hl in headlines:
                try:
                    datestring = hl.find('p', attrs={'class':'publish-date'}).text.strip()
                    dt = datetime.strptime(datestring, '%d %B %Y %H:%M')
                    delta = (date.today() - dt.date()).days
                    if delta < DaysOfNews:
                        headline = hl.find('h3', attrs={'class':'headline'}).find('a').text.strip()
                        detail = hl.find('p', attrs={'class':'article-intro'}).text.strip()
                        
                        Include = True
                        for ExcludeKeyword in NewsKeywordExcludeList:
                            if ExcludeKeyword in headline:
                                Include = False
                                break
                        if Include:
                            if (PERatio == 0) and (DivYield == 0):
                                PERatio, DivYield = DownloadBriefStatFromGlancePage(BaseURL, Ticker['AltID'])
                                RevGrowth = DownloadRevenueGrowth(BaseURL, Ticker['AltID'])
                            
                            NewsText = Ticker['Ticker'] + " ; " + Ticker['Property'] + " ; " + price + " ; " + str(dt.date()) + " ; PE: " + str(PERatio) + " ; Div: " + str(DivYield) + "% ; Rev Growth: " + str(RevGrowth) + "% ; " + headline + " ; " + detail
                            if UploadToDB:
                                DBHeadlineText = headline
                                DBNewsText = detail
                            DrillDown = False
                            for DrillDownKeyword in DrillDownKeywordList:
                                if DrillDownKeyword.upper() in headline.upper():
                                    DrillDown = True
                                if DrillDownKeyword.upper() in detail.upper():
                                    DrillDown = True
                                    
                            NewsFiltering = False
                            for NewsFilteringKeyword in NewsFilteringKeywordList:
                                if NewsFilteringKeyword.upper() in headline.upper():
                                    NewsFiltering = True
                            
                            if DrillDown:
                                DrillDownLink = hl.find('h3', attrs={'class':'headline'}).find('a')
                                DrillDownURL = DrillDownLink['rel'][1].replace("'", "").replace(",", "")
                                DrillDownsource = requests.get(DrillDownURL).text
                                DrillDownsoup = BeautifulSoup(DrillDownsource, 'lxml')
                                try:
                                    DrillDownNews = DrillDownsoup.find('div', attrs={'class':'tab-indent'}).text.strip()
                                    if NewsFiltering:
                                        # print('In NewsFiltering')
                                        SplitDone = False
                                        DrillDownNewsLines = DrillDownNews.splitlines()
                                        for index2, TickerAli in ThisTickerAlias.iterrows():
                                            # print('First For Loop')
                                            # print('HL_Target_Name is')
                                            # print(TickerAli['HL_Target_Name'])
                                            if TickerAli['HL_Target_Name'].upper() in DrillDownNews.upper():
                                                for SplitDrillDownNews in DrillDownNewsLines:
                                                    # print('Second For Loop')
                                                    if TickerAli['HL_Target_Name'].upper() + ':' in SplitDrillDownNews.upper():
                                                        DrillDownNews = SplitDrillDownNews
                                                        SplitDone = True
                                                        break
                                            if SplitDone:
                                                break
                                        # print('SplitDone is ' + str(SplitDone))
                                        if not SplitDone:
                                            # print('here')
                                            DrillDownNews = GetSplitNews(ShareTitle + ' ' + Ticker['Ticker'].split('.')[0], DrillDownNewsLines, DrillDownNews)
                                            # print('there')

                                            
                                            
                                        # if not pd.isnull(Ticker['HL_Target_Name']):
                                        #     if Ticker['HL_Target_Name'].upper() in DrillDownNews.upper():
                                        #         DrillDownNewsLines = DrillDownNews.splitlines()
                                        #         for SplitDrillDownNews in DrillDownNewsLines:
                                        #             if Ticker['HL_Target_Name'].upper() + ':' in SplitDrillDownNews.upper():
                                        #                 DrillDownNews = SplitDrillDownNews
                                        #                 break
                                                    
                                                    
                                    NewsText = Ticker['Ticker'] + " ; " + Ticker['Property'] + " ; " + price + " ; " + str(dt.date()) + " ; PE: " + str(PERatio) + " ; Div: " + str(DivYield) + "% ; Rev Growth: " + str(RevGrowth) + "% ; " + headline + " ; " + DrillDownNews
                                    if UploadToDB:
                                        DBHeadlineText = headline
                                        DBNewsText = DrillDownNews
                                except Exception:
                                    pass
                            print()
                            print(NewsText[ 0 : 200 ])
                            AccumulatedText = AccumulatedText + NewsText + "<BR>" + "<BR>"
                            AccumulatedTextList.append([NewsText, priceVal])
                            if UploadToDB:
                                # print('going to upload to DB')
                                # print('dt is')
                                # print(dt)
                                sql = "INSERT INTO fdata_news (Ticker, Datetime, Source, NewsHead, Headline, News) VALUES (%s, %s, %s, %s, %s, %s)"
                                val = (Ticker['Ticker'], dt ,'HL' , DBNewsText[ 0 : 100 ], DBHeadlineText, DBNewsText)
                                mycursor.execute(sql, val)
                                mydb.commit()
                                print('Uploaded to DB')
                except Exception:
                    pass    
        except Exception:
            pass   
    return [AccumulatedTextList, AccumulatedText]

def GetSplitNews(ShareTitle, DrillDownNewsLines, OriginalNews):
    # print('In GetSplitNews')
    ShareTitle = ShareTitle.split()
    MaxMatch = 0
    SplitNews = OriginalNews
    for News in DrillDownNewsLines:
        NewsShareTitle = News.split(':')[0].split()
        ThisMatch = 0
        for a in ShareTitle:
            for b in NewsShareTitle:
                # print('a = ' + a + ' and b = ' + b)
                if a.upper() == b.upper():
                    ThisMatch = ThisMatch + 1
        # print('This Match = ' + str(ThisMatch))
        if ThisMatch > MaxMatch:
            MaxMatch = ThisMatch
            SplitNews = News 
    return SplitNews


GlanceNameDict ={"P/E ratio":"P/E ratio"}

def DownloadGlancePage(BaseURL, Tickers, UploadToDB = True, DaysOfNews = 7):
    mydb = mysql.connector.connect(host=Config.CONFIG_MYSQL_CONNECTION_HOST,user=Config.CONFIG_MYSQL_CONNECTION_USER,password=Config.CONFIG_MYSQL_CONNECTION_PASSWORD,database=Config.CONFIG_MYSQL_CONNECTION_DATABASE)
    mycursor = mydb.cursor()
    for index, Ticker in Tickers.iterrows():
        given_date = datetime.today().date()
        first_day_of_month = given_date - timedelta(days = int(given_date.strftime("%d"))-1)

        try:
            url = BaseURL + Ticker['AltID']
            source = requests.get(url).text
            soup = BeautifulSoup(source, 'lxml')
            table = soup.find_all('div', attrs={'class':'columns large-3 medium-4 small-6'})

            for d in table:
                try:
                    print(d.find('span').text)
                    print(Decimal(d.find('strong').text.strip()))
                    sql = "INSERT INTO fdata_hl_glance (Ticker, CaptureDate, Name, Value) VALUES (%s, %s, %s, %s)"
                    val = (Ticker['Ticker'], first_day_of_month, GlanceNameDict[d.find('span').text], Decimal(d.find('strong').text.strip()))
                    print("inserted")
                    mycursor.execute(sql, val)
                    mydb.commit()
                    
                except Exception:
                    pass
                        
        except Exception:
            pass   
    pass

def DownloadBriefStatFromGlancePage(BaseURL, TickerAltID):
    try:
        url = BaseURL + TickerAltID
        source = requests.get(url).text
        soup = BeautifulSoup(source, 'lxml')
        table = soup.find_all('div', attrs={'class':'columns large-3 medium-4 small-6'})
        PERatio =  0.0

        for d in table:
            try:
                if d.find('span').text == "P/E ratio":
                    PERatio = Decimal(d.find('strong').text.strip())
                if d.find('span').text == "Dividend yield":
                    DivYield = Decimal(d.find('strong').text.strip().strip('%'))
            except Exception:
                pass
        return PERatio, DivYield
                    
    except Exception:
        return 0, 0   

def DownloadRevenueGrowth(BaseURL, TickerAltID):
    try:
        url = BaseURL + TickerAltID + '/financial-statements-and-reports'
        source = requests.get(url).text
        soup = BeautifulSoup(source, 'lxml')
        
        data = []
        header = []
        table = soup.find('table', attrs={'class':'factsheet-table responsive'})
        table_body = table.find('tbody')
        
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            if len(cols) > 0:
                if cols[0] == "Revenue:":
                    Rev1 = round(float((Decimal(cols[1].replace(',', '')) / Decimal(cols[2].replace(',', ''))) - 1)*100, 2)
                    Rev2 = round(float((Decimal(cols[1].replace(',', '')) / Decimal(cols[3].replace(',', ''))) - 1)*100, 2)
                    try:
                        Rev3 = round(float((Decimal(cols[1].replace(',', '')) / Decimal(cols[5].replace(',', ''))) - 1)*100, 2)
                    except Exception:
                        Rev3 = 0
                    RevGrowth = [Rev1, Rev2, Rev3]
                    return RevGrowth
        return [0,0,0]
                    
    except Exception:
        return [0,0,0]   
    

def GetTickersList(FurtherFilter = ''):
#    Tickers = pd.read_sql_query("select * from fdata_tickers_altid where AltID_Type = 'HL' and Ticker = 'AVON.L'", dbcon)
    # Tickers = pd.read_sql_query("select * from fdata_tickers_altid where AltID_Type = 'HL'" + FurtherFilter, dbcon)
    
    # Tickers = pd.read_sql_query("SELECT AA.*, BB.AltID AS HL_Target_Name FROM (SELECT A.*, B.Property FROM (select * from fdata_tickers_altid where AltID_Type = 'HL'" + FurtherFilter + ") A LEFT JOIN (SELECT * FROM `fdata_tickers_property` where Property_Type = 'Index') B ON A.Ticker = B.Ticker) AA LEFT JOIN (select * from fdata_tickers_altid where AltID_Type = 'HL Target') BB ON AA.Ticker = BB.Ticker", dbcon)
    # HoldingTickers = pd.read_sql_query("SELECT AA.*, BB.AltID AS HL_Target_Name FROM (SELECT A.*, B.Property FROM (select * from fdata_tickers_holding) A LEFT JOIN (SELECT * FROM `fdata_tickers_property` where Property_Type = 'Index') B ON A.Ticker = B.Ticker) AA LEFT JOIN (select * from fdata_tickers_altid where AltID_Type = 'HL Target') BB ON AA.Ticker = BB.Ticker", dbcon)
    Tickers = pd.read_sql_query("SELECT A.*, B.Property FROM (select * from fdata_tickers_altid where AltID_Type = 'HL'" + FurtherFilter + ") A LEFT JOIN (SELECT * FROM `fdata_tickers_property` where Property_Type = 'Index') B ON A.Ticker = B.Ticker", dbcon)
    HoldingTickers = pd.read_sql_query("SELECT A.*, B.Property FROM (select * from fdata_tickers_holding) A LEFT JOIN (SELECT * FROM `fdata_tickers_property` where Property_Type = 'Index') B ON A.Ticker = B.Ticker", dbcon)
    TickerAlias = pd.read_sql_query("SELECT Ticker, AltID As HL_Target_Name FROM fdata_tickers_alt_multi_id where AltID_Type = 'HL Target'", dbcon)
    
    # TickersOfHolding = Tickers.merge(HoldingTickers, left_on='Ticker', right_on='Ticker')
    # TickersOfNonHolding = Tickers.merge(HoldingTickers, indicator='i', how='outer', left_on='Ticker', right_on='Ticker').query('i == "left_only"').drop('i', 1)
    # TickersOfHolding = Tickers.merge(HoldingTickers, on=['Ticker', 'Property', 'HL_Target_Name'])
    # TickersOfNonHolding = Tickers.merge(HoldingTickers, indicator='i', how='outer', on=['Ticker', 'Property', 'HL_Target_Name']).query('i == "left_only"').drop('i', 1)
    TickersOfHolding = Tickers.merge(HoldingTickers, on=['Ticker', 'Property'])
    TickersOfNonHolding = Tickers.merge(HoldingTickers, indicator='i', how='outer', on=['Ticker', 'Property']).query('i == "left_only"').drop('i', 1)
    
    return Tickers, TickersOfHolding, TickersOfNonHolding, TickerAlias

dbcon = pymysql.connect(Config.CONFIG_MYSQL_CONNECTION_HOST, Config.CONFIG_MYSQL_CONNECTION_USER, Config.CONFIG_MYSQL_CONNECTION_PASSWORD, Config.CONFIG_MYSQL_CONNECTION_DATABASE)

