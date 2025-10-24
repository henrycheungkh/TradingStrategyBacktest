# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 16:59:30 2020

@author: Henry Cheung
"""

import os 
import Config
from datetime import date, datetime, timedelta


# print(Config.CONFIG_BASE_DatafilePath)

today = date.today()
print(Config.CONFIG_BASE_DatafilePath + today.strftime("%Y%m%d"))

os.mkdir(Config.CONFIG_BASE_DatafilePath + today.strftime("%Y%m%d"))

print('done')

