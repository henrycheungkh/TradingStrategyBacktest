# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 00:09:01 2020

@author: Henry Cheung
"""


from yahoofinancials import YahooFinancials

import yfinance as yf


arkk = yf.Ticker("ARKK")
# print(arkk.info['legalType'])

sbux = yf.Ticker("AAPL")
tlry = yf.Ticker("TLRY")


print(sbux.info)
print(sbux.info)
print(sbux.info['marketCap'])
print(sbux.info['sector'])
print(tlry.info['sector'])
print(sbux.info['industry'])
print(tlry.info['industry'])

# ticker = ['AAPL', 'MSFT']
# yahoo_financials = YahooFinancials(ticker)

# balance_sheet_data_qt = yahoo_financials.get_financial_stmts('quarterly', 'balance')
# # print(balance_sheet_data_qt)
# income_statement_data_qt = yahoo_financials.get_financial_stmts('quarterly', 'income')
# # print(income_statement_data_qt)
# all_statement_data_qt =  yahoo_financials.get_financial_stmts('quarterly', ['income', 'cash', 'balance'])
# earnings_data = yahoo_financials.get_stock_earnings_data()
# net_income = yahoo_financials.get_net_income()

# income_statement_data = yahoo_financials.get_financial_stmts('annual', 'income')
# print(income_statement_data)




msft = yf.Ticker("TSLA")
# msft = yf.Ticker(["MSFT", "AAPL"])

print(vars(msft))

# get stock info
msft.info

# get historical market data
hist = msft.history(period="max")

# show actions (dividends, splits)
msft.actions

# show dividends
msft.dividends

# show splits
msft.splits

# show financials
msft.financials
msft.quarterly_financials

# show major holders
msft.major_holders

# print(msft.major_holders)

# show institutional holders
msft.institutional_holders

# print(msft.institutional_holders)

# msft.mutual_fund_holders


# show balance sheet
msft.balance_sheet
msft.quarterly_balance_sheet

# show cashflow
msft.cashflow
msft.quarterly_cashflow

# show earnings
msft.earnings
msft.quarterly_earnings

# show sustainability
msft.sustainability

# show analysts recommendations
msft.recommendations

# show next event (earnings, etc)
msft.calendar

# show ISIN code - *experimental*
# ISIN = International Securities Identification Number
msft.isin

# show options expirations
msft.options

# get option chain for specific expiration
# opt = msft.option_chain('YYYY-MM-DD')
# data available via: opt.calls, opt.puts