# -*- coding: utf-8 -*-
"""
Created on Wed Oct 20 10:23:44 2021

@author: Henry Cheung
"""


import os
import pandas as pd
from binance.client import Client
api_key = os.environ.get('binance_api')
api_secret = os.environ.get('binance_secret')
client = Client(api_key, api_secret)

# valid intervals - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
interval = '1m'
# get timestamp of earliest date data is available
timestamp = client._get_earliest_valid_timestamp('BTCUSDT', interval)
print(timestamp)

AnalysisStartTime = datetime.now()
print('Download started at ' + str(AnalysisStartTime))


# request historical candle (or klines) data
bars = client.get_historical_klines('BTCUSDT', interval, timestamp, limit=1000)

for line in bars:
    del line[6:]
btc_df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close', 'vol'])
btc_df['datetime'] = pd.to_datetime(btc_df['date'], unit='ms')
# btc_df.set_index('date', inplace=True)
print(len(btc_df))
print(btc_df)





# print(client.get_account())

# # get latest price from Binance API
# btc_price = client.get_symbol_ticker(symbol="BTCUSDT")
# # print full output (dictionary)
# print(btc_price)
