# -*- coding: utf-8 -*-

"""

Created on Wed Apr  3 23:56:24 2019

 

@author: hc39138

"""

#from VCDataHubLib.AdvanceDataFrame import AdvanceDataFrame
from AdvanceDataFrame import AdvanceDataFrame
from datetime import datetime
import pandas as pd
pd.set_option('display.max_columns', 50)

df1 = AdvanceDataFrame({'lkey': ['foo', 'bar', 'baz', 'foo'],
                     'value': [1, 2, 3, 5]})

df2 = pd.DataFrame({'rkey': ['foo', 'bar', 'baz', 'foo'],
                     'value': [5, 6, 7, 8]})

print ("Result of typical merge")
print(df1.merge(df2, left_on='lkey', right_on='rkey'))
print('Result of merge with left query is lkey == "foo"')
print(df1.merge(df2, left_on='lkey', right_on='rkey', left_query='lkey == "foo"'))
print('Result of merge with right query is value == 5')
print(df1.merge(df2, left_on='lkey', right_on='rkey', right_query='value == 5'))
print('Result of merge with result query is value_y > 5')
print(df1.merge(df2, left_on='lkey', right_on='rkey', result_query='value_y > 5'))
 

#-------------------------


RiskInOriginalBucket = AdvanceDataFrame({"Desk" : ["Exotics","Exotics","Exotics","Exotics","Exotics","Exotics","Exotics","Exotics","Hybrids","Hybrids","Hybrids","Hybrids","Hybrids","Hybrids","Hybrids","Hybrids"],
                            "Underlying" : [".STOXX50E",".STOXX50E",".STOXX50E",".STOXX50E",".SPX",".SPX",".SPX",".SPX",".STOXX50E",".STOXX50E",".STOXX50E",".STOXX50E",".SPX",".SPX",".SPX",".SPX"],
                            "Tenor" : [datetime.strptime('Jun 1 2020', '%b %d %Y'),datetime.strptime('Jun 1 2022', '%b %d %Y'),datetime.strptime('Jun 1 2024', '%b %d %Y'),datetime.strptime('Jun 1 2026', '%b %d %Y'),datetime.strptime('Jun 1 2020', '%b %d %Y'),datetime.strptime('Jun 1 2022', '%b %d %Y'),datetime.strptime('Jun 1 2024', '%b %d %Y'),datetime.strptime('Jun 1 2026', '%b %d %Y'),datetime.strptime('Jun 1 2020', '%b %d %Y'),datetime.strptime('Jun 1 2022', '%b %d %Y'),datetime.strptime('Jun 1 2024', '%b %d %Y'),datetime.strptime('Jun 1 2026', '%b %d %Y'),datetime.strptime('Jun 1 2020', '%b %d %Y'),datetime.strptime('Jun 1 2022', '%b %d %Y'),datetime.strptime('Jun 1 2024', '%b %d %Y'),datetime.strptime('Jun 1 2026', '%b %d %Y')],
                            "Strike" : [0.8,0.9,1.1,1.2,0.8,0.9,1.1,1.2,0.8,0.9,1.1,1.2,0.8,0.9,1.1,1.2],
                            "Risk" : [12000,14000,13000,15000,12500,14500,13500,15500,12300,14300,13300,15300,12700,14700,13700,15700] })

print(RiskInOriginalBucket)

RiskInOriginalBucket.to_excel(r'd:\temp\RiskInOriginalBucket.xlsx',merge_cells=False)

NewTenor = pd.DataFrame({"Underlying" : [".STOXX50E",".STOXX50E",".STOXX50E",".SPX",".SPX",".SPX"],
                         "Tenor" : [datetime.strptime('Jun 1 2021', '%b %d %Y'),datetime.strptime('Jun 1 2023', '%b %d %Y'),datetime.strptime('Jun 1 2025', '%b %d %Y'),datetime.strptime('Aug 1 2021', '%b %d %Y'),datetime.strptime('Aug 1 2023', '%b %d %Y'),datetime.strptime('Aug 1 2025', '%b %d %Y')]})

NewStrike = pd.DataFrame({"Underlying" : [".STOXX50E",".STOXX50E",".STOXX50E",".SPX",".SPX",".SPX"],
                          "Strike" : [0.85,0.95,1.15,0.83,0.93,1.13]})

NewStrike2 = pd.DataFrame({ "Strike" : [0.85,0.95,1.15]})

TenorReBucketedRisk = RiskInOriginalBucket.ReBucket("Risk",NewTenor,"Tenor")
print('Risk after rebucketing by tenor:')
print(TenorReBucketedRisk)
TenorReBucketedRisk.to_excel(r'd:\temp\TenorReBucketedRisk.xlsx',merge_cells=False)

StrikeReBucketedRisk = RiskInOriginalBucket.ReBucket("Risk",NewStrike,"Strike")
print('Risk after rebucketing by strike:')
print(StrikeReBucketedRisk)
StrikeReBucketedRisk.to_excel(r'd:\temp\StrikeReBucketedRisk.xlsx',merge_cells=False)

Strike2ReBucketedRisk = RiskInOriginalBucket.ReBucket("Risk",NewStrike2)
print('Risk after rebucketing by strike set 2:')
print(Strike2ReBucketedRisk)
Strike2ReBucketedRisk.to_excel(r'd:\temp\Strike2ReBucketedRisk.xlsx',merge_cells=False)

TenorStrikeReBucketedRisk = RiskInOriginalBucket.ReBucket("Risk",NewTenor,"Tenor").ReBucket("Risk",NewStrike,"Strike")
print('Risk after rebucketing by tenor and strike:')
print(TenorStrikeReBucketedRisk)
TenorStrikeReBucketedRisk.to_excel(r'd:\temp\TenorStrikeReBucketedRisk.xlsx',merge_cells=False)

TenorRangeReBucketedRisk = RiskInOriginalBucket.ReBucket("Risk",NewTenor,"Tenor","Range")
print('Risk after rebucketing by tenor range:')
print(TenorRangeReBucketedRisk)
TenorRangeReBucketedRisk.to_excel(r'd:\temp\TenorRangeReBucketedRisk.xlsx',merge_cells=False)

#-----------------------


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

CorrelationAfterInterpolation.to_excel(r'd:\temp\CorrelationAfterInterpolation.xlsx',merge_cells=False)
 