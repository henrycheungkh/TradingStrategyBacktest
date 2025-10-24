# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 16:47:38 2023

@author: Henry Cheung
"""

import datetime
import time
import pytz
import sys
print(sys.version)
# NYTime = datetime.datetime(2023,3,28,6,0,0,tzinfo=pytz.timezone('America/New_York'))

NYTime = pytz.timezone('America/New_York').localize(datetime.datetime(2023,3,28,17,21,0))

print("NYTime is " + NYTime.strftime("%Y%m%d-%H:%M:%S %z"))

# LondonTime = pytz.timezone('Europe/London').localize(NYTime)
# LondonTime = pytz.timezone('Europe/London').localize(NYTime.astimezone(pytz.utc))


LondonTime = NYTime.astimezone(pytz.timezone('Europe/London'))

# LondonTime = NYTime.astimezone(pytz.utc)
# NYTime is 20230328-06:00:00
# LondonTime is 20230328-10:56:00

# LondonTime = NYTime.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/London'))


print("LondonTime is " + LondonTime.strftime("%Y%m%d-%H:%M:%S %z"))

timediff = 10

while (timediff > 0):
    if timediff > 120:
        time.sleep(60)
    elif timediff > 60:
        time.sleep(30)
    elif timediff > 2:
        time.sleep(1)
    now = datetime.datetime.now()
    LondonNow = pytz.timezone('Europe/London').localize(now)
    NYNow = LondonNow.astimezone(pytz.timezone('America/New_York'))
    timediff = (LondonTime - LondonNow).total_seconds()
    print('London Time:' + LondonNow.strftime("%Y%m%d-%H:%M:%S %z") + ', NY TIme: ' + NYNow.strftime("%Y%m%d-%H:%M:%S %z") + ', time diff to target time is ' + str(timediff))




