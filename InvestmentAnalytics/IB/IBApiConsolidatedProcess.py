# -*- coding: utf-8 -*-
"""
Created on Sun May 16 00:46:02 2021

@author: Henry Cheung
"""
# import InvestmentAnalytics.Config as Config
# from InvestmentAnalytics.DBUtil import AppendDBExportScript

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
# from ibapi.contract import *
# from ibapi.common import *
# import pandas as pd
# import numpy as np
# import time
# from datetime import date, datetime, timedelta
# import math
# import csv
# from pytz import timezone
# import pymysql
# import mysql.connector


class IBapiProcess(EWrapper, EClient):
    def __init__(self):
        pass
        
    def RunProcess(self):
        pass
    
    def InitiateProcess(self):
        pass
    
class IBapiDataReader(IBapiProcess):
    def __init__(self, RequestID_Range):
        super().__init__()
        self.RequestID_Range = RequestID_Range
        
    def InitiateProcess(self):
        pass

    def clearCache(self):
        self.DownloadComplete = False
        self.DownloadError = False