# -*- coding: utf-8 -*-
"""
Created on Tue May  4 09:49:44 2021

@author: Henry Cheung
"""


s = "+0.87 (+0.23%)"
# print(s)
# s = s.split('(')[1]
# print(s)
# s = s.replace('%','').replace(')','')
# print(s)
# s = float(s)
s = float(s.split('(')[1].replace('%','').replace(')',''))
print(s)