# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 01:30:07 2020

@author: Henry Cheung
"""



# https://www.hl.co.uk/shares/stock-market-summary/ftse-250

from bs4 import BeautifulSoup
import requests

url_prefix = 'https://www.hl.co.uk'

source = requests.get('https://www.hl.co.uk/shares/stock-market-summary/ftse-250').text

soup = BeautifulSoup(source, 'lxml')

# print(soup.prettify())

data = []
header = []
table = soup.find('table', attrs={'class':'stockTable'})
table_body = table.find('tbody')

RowCount = 0


rows = table_body.find_all('tr')
for row in rows:
    if RowCount > 1:
        cols = row.find_all('th')
        cols = [ele.text.strip() for ele in cols]
        header.append([ele for ele in cols if ele])
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])
        cols = row.find('a')
        if RowCount == 2:
            print(cols['href'])
            source2 = requests.get(url_prefix + cols['href']).text
            soup2 = BeautifulSoup(source2, 'lxml')
            print(soup2.prettify())
    RowCount = RowCount + 1


# print(data[2][2])
# print(data)
# print(header)