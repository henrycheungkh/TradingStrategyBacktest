# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 14:01:47 2020

@author: Henry Cheung
"""

import InvestmentAnalytics.Download_HL as dhl

import Config

t = dhl.GetTickersList()[0]

print('--- Download Financial Statement And Reports ---')
dhl.DownloadHLFinancialStatementAndReportsBatch(Config.CONFIG_HL_BASE_URL, t)
print('--- Download Glance Page ---')
dhl.DownloadGlancePage(Config.CONFIG_HL_BASE_URL, t)