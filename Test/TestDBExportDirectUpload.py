# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 09:41:13 2021

@author: Henry Cheung
"""

import InvestmentAnalytics.Config as Config

from InvestmentAnalytics.DBUtil import AppendDBExportScript, DBExportDirectUpload

DBExportDirectUpload(r'D:\Shared\TAHistoricalData\FuturesHistoricalDataBackup\20211019_10 secs_ES_3 D\UploadScript.sql', 'fdata_fut_hist', DatabaseName = Config.CONFIG_MYSQL_CONNECTION_DATABASE_FUT_HIST)


