# -*- coding: utf-8 -*-

"""
Created on Wed Apr  3 23:52:45 2019

@author: hc39138

Remark:
    For Rebucketing and Interpolation, avoid using column names in input dataframe with suffices of '_y', '_Left' or '_Right' as the column name suffices are used in the calculation

"""

import pandas as pd
import numpy as np
from datetime import datetime

class AdvanceDataFrame(pd.DataFrame):
   
    def get_ohlc(self, Symbol_Columns, Price_Column, Resample_Frequency):
        pass
    
    def single_dimension_interpolate(self, ValueInOriginalPillars, OriginalPillarColumnName, OriginalPillarValueColumnName, LeftExtrapolationMethod='flat', RightExtrapolationMethod='flat', AdjacentPillarSuffix=('_Left','_Right')):
        
        df = self.AttachAdjacentPillarAndPillarValue(ValueInOriginalPillars, OriginalPillarValueColumnName,OriginalPillarColumnName,AdjacentPillarSuffix=AdjacentPillarSuffix)
        ValueInOriginalPillars = ValueInOriginalPillars.rename(index=str, columns={OriginalPillarColumnName:OriginalPillarColumnName+AdjacentPillarSuffix[0], OriginalPillarValueColumnName:OriginalPillarValueColumnName+AdjacentPillarSuffix[0]})
        df = df.AttachAdjacentPillarAndPillarValue(ValueInOriginalPillars, OriginalPillarValueColumnName+AdjacentPillarSuffix[0],OriginalPillarColumnName+AdjacentPillarSuffix[0],False,AdjacentPillarSuffix=AdjacentPillarSuffix)
        ValueInOriginalPillars = ValueInOriginalPillars.rename(index=str, columns={OriginalPillarColumnName+AdjacentPillarSuffix[0]:OriginalPillarColumnName+AdjacentPillarSuffix[1], OriginalPillarValueColumnName+AdjacentPillarSuffix[0]:OriginalPillarValueColumnName+AdjacentPillarSuffix[1]})
        df = df.AttachAdjacentPillarAndPillarValue(ValueInOriginalPillars, OriginalPillarValueColumnName+AdjacentPillarSuffix[1],OriginalPillarColumnName+AdjacentPillarSuffix[1],False,AdjacentPillarSuffix=AdjacentPillarSuffix)
        
        df[OriginalPillarValueColumnName] = np.nan
        
        df.loc[(df[OriginalPillarColumnName+AdjacentPillarSuffix[1]] > df[OriginalPillarColumnName+AdjacentPillarSuffix[0]]), OriginalPillarValueColumnName] = df[OriginalPillarValueColumnName+AdjacentPillarSuffix[0]] + (df[OriginalPillarValueColumnName+AdjacentPillarSuffix[1]] - df[OriginalPillarValueColumnName+AdjacentPillarSuffix[0]]) * (df[OriginalPillarColumnName] - df[OriginalPillarColumnName+AdjacentPillarSuffix[0]])/(df[OriginalPillarColumnName+AdjacentPillarSuffix[1]] - df[OriginalPillarColumnName+AdjacentPillarSuffix[0]])
        df.loc[(df[OriginalPillarColumnName+AdjacentPillarSuffix[1]] == df[OriginalPillarColumnName+AdjacentPillarSuffix[0]]), OriginalPillarValueColumnName] = df[OriginalPillarValueColumnName+AdjacentPillarSuffix[0]]
        
        for extrap in [[LeftExtrapolationMethod,AdjacentPillarSuffix[0],AdjacentPillarSuffix[1]],[RightExtrapolationMethod,AdjacentPillarSuffix[1],AdjacentPillarSuffix[0]]]:
            if extrap[0] == 'flat':
                df.loc[pd.isnull(df[OriginalPillarColumnName+extrap[1]]),OriginalPillarValueColumnName] = df[OriginalPillarValueColumnName+extrap[2]]
            # if extrap[0] == 'straight':
            #     df.loc[pd.isnull(df[OriginalPillarColumnName+extrap[1]]),OriginalPillarValueColumnName] = df[OriginalPillarValueColumnName+extrap[2]] + (df[OriginalPillarValueColumnName+extrap[2]+extrap[2]] - df[OriginalPillarValueColumnName+extrap[2]]) * (df[OriginalPillarColumnName] - df[OriginalPillarColumnName+extrap[2]]) / (df[OriginalPillarColumnName+extrap[2]+extrap[2]] - df[OriginalPillarColumnName+extrap[2]])
            
        df = df.drop(columns=[OriginalPillarColumnName + AdjacentPillarSuffix[0],OriginalPillarColumnName + AdjacentPillarSuffix[1],OriginalPillarColumnName + AdjacentPillarSuffix[0]+AdjacentPillarSuffix[0],OriginalPillarColumnName + AdjacentPillarSuffix[0]+AdjacentPillarSuffix[1],OriginalPillarColumnName + AdjacentPillarSuffix[1]+AdjacentPillarSuffix[0],OriginalPillarColumnName + AdjacentPillarSuffix[1]+AdjacentPillarSuffix[1],
                              OriginalPillarValueColumnName + AdjacentPillarSuffix[0],OriginalPillarValueColumnName + AdjacentPillarSuffix[1],OriginalPillarValueColumnName + AdjacentPillarSuffix[0]+AdjacentPillarSuffix[0],OriginalPillarValueColumnName + AdjacentPillarSuffix[0]+AdjacentPillarSuffix[1],OriginalPillarValueColumnName + AdjacentPillarSuffix[1]+AdjacentPillarSuffix[0],OriginalPillarValueColumnName + AdjacentPillarSuffix[1]+AdjacentPillarSuffix[1]])
        df.__class__ = AdvanceDataFrame
        return df
    
    def AttachAdjacentPillarAndPillarValue(self,ValueInOriginalPillars, OriginalPillarValueColumnName,OriginalPillarColumnName=None,SamePillarAsLeftAdjacentAllowed=True,SamePillarAsRightAdjacentAllowed=True, AdjacentPillarSuffix=('_Left','_Right')):
        IdentifierColumnNames = list(ValueInOriginalPillars.columns.values)
        IdentifierColumnNames.remove(OriginalPillarValueColumnName)
        IdentifierColumnNames.append(OriginalPillarColumnName)
        IdentifierColumnNames.remove(OriginalPillarColumnName)
        WithAdjacentPillarAttached = self.AttachAdjacentPillar(ValueInOriginalPillars[IdentifierColumnNames],OriginalPillarColumnName,SamePillarAsLeftAdjacentAllowed,SamePillarAsRightAdjacentAllowed,AdjacentPillarSuffix=AdjacentPillarSuffix)
        df = WithAdjacentPillarAttached[0]
        FullIdentifierColumnNames = list(df.columns.values)
        FullIdentifierColumnNames.remove(WithAdjacentPillarAttached[2])
        FullIdentifierColumnNames.remove(WithAdjacentPillarAttached[1])
        df = self.merge(df, how='left', left_on=FullIdentifierColumnNames, right_on=FullIdentifierColumnNames, suffixes=('', '_y'))
        LeftIdentifierColumnNames = IdentifierColumnNames[:]
        LeftIdentifierColumnNames.remove(OriginalPillarColumnName)
        LeftIdentifierColumnNames.append(OriginalPillarColumnName + AdjacentPillarSuffix[0])
        df = df.merge(ValueInOriginalPillars.rename(index=str, columns={OriginalPillarValueColumnName:OriginalPillarValueColumnName+AdjacentPillarSuffix[0]}), how='left', left_on=LeftIdentifierColumnNames, right_on=IdentifierColumnNames, suffixes=('', '_y')).drop(columns=[OriginalPillarColumnName + '_y'])
        LeftIdentifierColumnNames.remove(OriginalPillarColumnName + AdjacentPillarSuffix[0])
        LeftIdentifierColumnNames.append(OriginalPillarColumnName + AdjacentPillarSuffix[1])
        df = df.merge(ValueInOriginalPillars.rename(index=str, columns={OriginalPillarValueColumnName:OriginalPillarValueColumnName+AdjacentPillarSuffix[1]}), how='left', left_on=LeftIdentifierColumnNames, right_on=IdentifierColumnNames, suffixes=('', '_y')).drop(columns=[OriginalPillarColumnName + '_y'])
        df.__class__ = AdvanceDataFrame
        
        return df

    def AttachAdjacentPillar(self,NewBucketPillars,BucketPillarColumnName=None,SamePillarAsLeftAdjacentAllowed=True,SamePillarAsRightAdjacentAllowed=True, AdjacentPillarSuffix=('_Left','_Right')):
        df = self.copy()
        NewBucketPillars = NewBucketPillars.drop_duplicates()
        IdentifierUsed = list(NewBucketPillars.columns.values)
        df = df[IdentifierUsed].drop_duplicates()
        IdentifierUsed.remove(BucketPillarColumnName)
        DummyIndexUsed = len(IdentifierUsed) == 0
        if DummyIndexUsed:
            DummyIndex = self.GetNonOverlappingNewColumnName('DummyIndex')
            IdentifierUsed.append(DummyIndex)
            df[IdentifierUsed[0]] = 1
            NewBucketPillars[IdentifierUsed[0]] = 1
        BucketLeftColumnName = self.GetNonOverlappingNewColumnName(BucketPillarColumnName + AdjacentPillarSuffix[0])
        BucketRightColumnName = self.GetNonOverlappingNewColumnName(BucketPillarColumnName + AdjacentPillarSuffix[1])
        df[BucketLeftColumnName] = np.nan
        df[BucketRightColumnName] = np.nan

        df = df.merge(NewBucketPillars, how='left', left_on = IdentifierUsed, right_on = IdentifierUsed, suffixes=('', '_y'))
        
        if SamePillarAsLeftAdjacentAllowed:
            df.loc[df[BucketPillarColumnName ] >= df[BucketPillarColumnName + '_y'], BucketLeftColumnName] = df[BucketPillarColumnName + '_y']
        else:
            df.loc[df[BucketPillarColumnName ] > df[BucketPillarColumnName + '_y'], BucketLeftColumnName] = df[BucketPillarColumnName + '_y']
        if SamePillarAsRightAdjacentAllowed:
            df.loc[df[BucketPillarColumnName ] <= df[BucketPillarColumnName + '_y'], BucketRightColumnName] = df[BucketPillarColumnName + '_y']
        else:
            df.loc[df[BucketPillarColumnName ] < df[BucketPillarColumnName + '_y'], BucketRightColumnName] = df[BucketPillarColumnName + '_y']

        if df[BucketPillarColumnName].dtype == 'datetime64[ns]':
            df[BucketLeftColumnName] = pd.to_datetime(df[BucketLeftColumnName])
            df[BucketRightColumnName] = pd.to_datetime(df[BucketRightColumnName])
        df = df.drop(columns=[BucketPillarColumnName + '_y'])
        IdentifierUsed.append(BucketPillarColumnName)
        df_ptable = df.pivot_table(index=IdentifierUsed, values=[BucketLeftColumnName, BucketRightColumnName], aggfunc={BucketLeftColumnName: max,
                              BucketRightColumnName: min})
        df_ptable = df_ptable.reset_index()
        if DummyIndexUsed:
            df_ptable = df_ptable.drop(columns=['DummyIndex'])
        return [df_ptable, BucketLeftColumnName, BucketRightColumnName]

    def GetNonOverlappingNewColumnName(self, ColumnName):
        if not ColumnName in self:
            return ColumnName
        else:
            i = 1
            while (ColumnName + str(i)) in self:
                i = i + 1
            return (ColumnName + str(i))
    
    def ReBucket(self,ReBucketedColumnName,NewBucketPillars,BucketPillarColumnName=None,Method='Proportional',RangeBoundary=None, AdjacentPillarSuffix=('_Left','_Right')):
        if BucketPillarColumnName is None:
            BucketPillarColumnName = NewBucketPillars.columns.values[-1]
        if RangeBoundary == None:
            if NewBucketPillars[BucketPillarColumnName].dtype == 'datetime64[ns]':
                RangeBoundary=(datetime.strptime('Jan 1 1800', '%b %d %Y'),datetime.strptime('Jan 1 2200', '%b %d %Y'))
            else:
                RangeBoundary=(0,99999999)

        if Method == 'Range':
            IdentifierUsed = list(NewBucketPillars.columns.values)
            IdentifierUsed.remove(BucketPillarColumnName)
            df1 = NewBucketPillars[IdentifierUsed].drop_duplicates()
            df2 = df1.copy()
            df1[BucketPillarColumnName] = RangeBoundary[0]
            df2[BucketPillarColumnName] = RangeBoundary[1]
            NewBucketPillars = pd.concat([NewBucketPillars,df1,df2])
            NewBucketsMapping = self.AttachAdjacentPillar(NewBucketPillars,BucketPillarColumnName,SamePillarAsLeftAdjacentAllowed=True,SamePillarAsRightAdjacentAllowed=False,AdjacentPillarSuffix=AdjacentPillarSuffix)
        else:
            NewBucketsMapping = self.AttachAdjacentPillar(NewBucketPillars,BucketPillarColumnName,AdjacentPillarSuffix=AdjacentPillarSuffix)

        df = self.merge(NewBucketsMapping[0], how='left', left_on=list(NewBucketPillars.columns.values), right_on=list(NewBucketPillars.columns.values))

        if Method == 'Range':
            df = df.reset_index()
            df.__class__ = AdvanceDataFrame
            return df
     
        df[ReBucketedColumnName+AdjacentPillarSuffix[0]] = 0
        df[ReBucketedColumnName+AdjacentPillarSuffix[1]] = 0

        if df[BucketPillarColumnName].dtype == 'datetime64[ns]':
            df[ReBucketedColumnName+AdjacentPillarSuffix[0]] = df[ReBucketedColumnName] * (df[BucketPillarColumnName+AdjacentPillarSuffix[1]] - df[BucketPillarColumnName]).dt.days / (df[BucketPillarColumnName+AdjacentPillarSuffix[1]] - df[BucketPillarColumnName+AdjacentPillarSuffix[0]]).dt.days
            df[ReBucketedColumnName+AdjacentPillarSuffix[1]] = df[ReBucketedColumnName] * (df[BucketPillarColumnName] - df[BucketPillarColumnName+AdjacentPillarSuffix[0]]).dt.days / (df[BucketPillarColumnName+AdjacentPillarSuffix[1]] - df[BucketPillarColumnName+AdjacentPillarSuffix[0]]).dt.days
        else:
            df[ReBucketedColumnName+AdjacentPillarSuffix[0]] = df[ReBucketedColumnName] * (df[BucketPillarColumnName+AdjacentPillarSuffix[1]] - df[BucketPillarColumnName]) / (df[BucketPillarColumnName+AdjacentPillarSuffix[1]] - df[BucketPillarColumnName+AdjacentPillarSuffix[0]])
            df[ReBucketedColumnName+AdjacentPillarSuffix[1]] = df[ReBucketedColumnName] * (df[BucketPillarColumnName] - df[BucketPillarColumnName+AdjacentPillarSuffix[0]]) / (df[BucketPillarColumnName+AdjacentPillarSuffix[1]] - df[BucketPillarColumnName+AdjacentPillarSuffix[0]])

        df.loc[pd.isnull(df[BucketPillarColumnName+AdjacentPillarSuffix[0]]), ReBucketedColumnName+AdjacentPillarSuffix[1]] = df[ReBucketedColumnName]
        df.loc[pd.isnull(df[BucketPillarColumnName+AdjacentPillarSuffix[1]]), ReBucketedColumnName+AdjacentPillarSuffix[0]] = df[ReBucketedColumnName]
        df.loc[df[BucketPillarColumnName+AdjacentPillarSuffix[0]] == df[BucketPillarColumnName+AdjacentPillarSuffix[1]], ReBucketedColumnName+AdjacentPillarSuffix[0]] = df[ReBucketedColumnName]
        df.loc[df[BucketPillarColumnName+AdjacentPillarSuffix[0]] == df[BucketPillarColumnName+AdjacentPillarSuffix[1]], ReBucketedColumnName+AdjacentPillarSuffix[1]] = 0

        df_left = df.copy().drop(columns=[BucketPillarColumnName,ReBucketedColumnName,BucketPillarColumnName+AdjacentPillarSuffix[1],ReBucketedColumnName+AdjacentPillarSuffix[1]])
        df_left = df_left.rename(index=str, columns={ReBucketedColumnName+AdjacentPillarSuffix[0]:ReBucketedColumnName, BucketPillarColumnName+AdjacentPillarSuffix[0]:BucketPillarColumnName})
        df_right = df.copy().drop(columns=[BucketPillarColumnName,ReBucketedColumnName,BucketPillarColumnName+AdjacentPillarSuffix[0],ReBucketedColumnName+AdjacentPillarSuffix[0]])
        df_right = df_right.rename(index=str, columns={ReBucketedColumnName+AdjacentPillarSuffix[1]:ReBucketedColumnName, BucketPillarColumnName+AdjacentPillarSuffix[1]:BucketPillarColumnName})

        df = pd.concat([df_left,df_right],sort=False)
        df = df[pd.notnull(df[ReBucketedColumnName])]

        DataLabelUsed = list(df.columns.values)
        DataLabelUsed.remove(ReBucketedColumnName)

        df = df.pivot_table(values=ReBucketedColumnName, index=DataLabelUsed, aggfunc=np.sum).reset_index()
        df.__class__ = AdvanceDataFrame
        return df

    @staticmethod
    def GetColumnNonNullValues(df, column_labels):
        df = df[column_labels]
        for c in column_labels:
            df = df[pd.notnull(df[c])]
        return df

    def merge(self, right, how='inner', on=None, left_on=None, right_on=None, left_index=False, right_index=False, sort=False, suffixes=('_x', '_y'), copy=True, indicator=False, validate=None, left_query=None, right_query=None, result_query=None):
        if left_query is None:
            left_df = self
        else:
            left_df = self.query(left_query)
        if right_query is None:
            right_df = right
        else:
            right_df = right.query(right_query)

        df = pd.DataFrame.merge(left_df,right_df, how, on, left_on, right_on, left_index, right_index, sort, suffixes, copy, indicator, validate)
        if result_query is not None:
            df = df.query(result_query)
        df.__class__ = AdvanceDataFrame
        return df

    def drop(self, labels=None, axis=0, index=None, columns=None, level=None, inplace=False, errors='raise'):
        df = self.copy()
        df.__class__ = pd.DataFrame
        df = df.drop(labels, axis, index, columns, level, inplace, errors)
        df.__class__ = AdvanceDataFrame
        return df
        

    @staticmethod
    def InitFromDataframe(dataframeobject):
        df = dataframeobject.copy()
        df.__class__ = AdvanceDataFrame
        return df