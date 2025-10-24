# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 14:01:47 2020

@author: Henry Cheung
"""

import InvestmentAnalytics.Download_HL

import Config

Download_HL.DownloadHLFinancialStatementAndReportsBatch(Config.CONFIG_HL_BASE_URL, Download_HL.GetTickersList()[0])