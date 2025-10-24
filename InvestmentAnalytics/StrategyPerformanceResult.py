# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 00:20:03 2021

@author: Henry Cheung
"""


class StrategyPerformanceResult:
    def __init__(self, TransactionRecord = None, TransactionFee = None):
        self.TransactionRecord = TransactionRecord
        self.TransactionFee = TransactionFee
        