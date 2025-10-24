# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 22:56:59 2021

@author: Henry Cheung
"""
from AdvanceDataFrame import AdvanceDataFrame
from datetime import datetime
import pandas as pd
pd.set_option('display.max_columns', 50)

TotemConsensusDerivedParameter = AdvanceDataFrame({ 
"Underlying1" : [".STOXX50E",".STOXX50E",".SPX",".SPX",".SPX",".SPX",".STOXX50E",".STOXX50E"],
"Underlying2" : ["EURSFIX10Y=","EURSFIX10Y=","USDSFIX10Y=","USDSFIX10Y=","EURSFIX10Y=","EURSFIX10Y=","USDSFIX10Y=","USDSFIX10Y="],
"Tenor" : [2, 5,2, 5,2, 5,2, 5],
"Correlation" : [0.2,0.25,0.19,0.28,0.32,0.21,0.24,0.29] })

NewTenorRequiringInterpolatedCorrelation = AdvanceDataFrame({
"Desk" : ["Exotics","Exotics","Exotics","Exotics","Exotics",
"Exotics","Exotics","Exotics","Exotics","Exotics",
"Exotics","Exotics","Exotics","Exotics","Exotics",
"Exotics","Exotics","Exotics","Exotics","Exotics",
"Hybrids","Hybrids","Hybrids","Hybrids","Hybrids",
"Hybrids","Hybrids","Hybrids","Hybrids","Hybrids",
"Hybrids","Hybrids","Hybrids","Hybrids","Hybrids",
"Hybrids","Hybrids","Hybrids","Hybrids","Hybrids"],
"Underlying1" : [".STOXX50E",".STOXX50E",".STOXX50E",".STOXX50E",".STOXX50E",
".SPX",".SPX",".SPX",".SPX",".SPX",
".SPX",".SPX",".SPX",".SPX",".SPX",
".STOXX50E",".STOXX50E",".STOXX50E",".STOXX50E",".STOXX50E",
".STOXX50E",".STOXX50E",".STOXX50E",".STOXX50E",".STOXX50E",
".SPX",".SPX",".SPX",".SPX",".SPX",
".SPX",".SPX",".SPX",".SPX",".SPX",
".STOXX50E",".STOXX50E",".STOXX50E",".STOXX50E",".STOXX50E"],
"Underlying2" : ["EURSFIX10Y=","EURSFIX10Y=","EURSFIX10Y=","EURSFIX10Y=","EURSFIX10Y=",
"USDSFIX10Y=","USDSFIX10Y=","USDSFIX10Y=","USDSFIX10Y=","USDSFIX10Y=",
"EURSFIX10Y=","EURSFIX10Y=","EURSFIX10Y=","EURSFIX10Y=","EURSFIX10Y=",
"USDSFIX10Y=","USDSFIX10Y=","USDSFIX10Y=","USDSFIX10Y=","USDSFIX10Y=",
"EURSFIX10Y=","EURSFIX10Y=","EURSFIX10Y=","EURSFIX10Y=","EURSFIX10Y=",
"USDSFIX10Y=","USDSFIX10Y=","USDSFIX10Y=","USDSFIX10Y=","USDSFIX10Y=",
"EURSFIX10Y=","EURSFIX10Y=","EURSFIX10Y=","EURSFIX10Y=","EURSFIX10Y=",
"USDSFIX10Y=","USDSFIX10Y=","USDSFIX10Y=","USDSFIX10Y=","USDSFIX10Y="],
"Tenor" : [1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,1,2,3,4,5]
        })

CorrelationAfterInterpolation = NewTenorRequiringInterpolatedCorrelation.single_dimension_interpolate(TotemConsensusDerivedParameter,"Tenor", "Correlation")

print('Correlation After Interpolation:')
print(CorrelationAfterInterpolation)
