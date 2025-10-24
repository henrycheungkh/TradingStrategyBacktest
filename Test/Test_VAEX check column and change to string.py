import vaex
import pandas as pd  
import numpy as np

def new_column_by_column_merging(df, columns=None):
    if columns is None:
        columns = df.get_column_names()
    if type(columns) is str:
        df['merged_column_key'] = df[columns]
        return df

    df['merged_column_key'] = np.array(['']*len(df))
    for col in columns:
        df['merged_column_key'] = df['merged_column_key'] + '_' + df[col].astype('string')
    return df

def new_column_by_column_merging2(df, columns=None):
    if columns is None:
        columns = df.get_column_names()
    if type(columns) is str:
        df['merged_column_key'] = df[columns]
        return df

    df['merged_column_key'] = np.array(['']*len(df))
    for col in columns:
        if df[col].dtype == 'int64':
            df[col] = df[col].astype('float64')
        df['merged_column_key'] = df['merged_column_key'] + '_' + df[col].astype('string')
    return df


pandas_df = pd.DataFrame({'Name': ['Tom', 'Joseph', 'Krish', 'John'], 'Last Name': ['Johnson', 'Cameron', 'Biden', 'Washington'], 'Age': [20, 21, 19, 18], 'Weight': [60.0, 61.0, 62.0, 63.0]})  
print('pandas_df is')
print(pandas_df)  

df = vaex.from_pandas(df=pandas_df, copy_index=False)

print(df['Name'].dtype)
print(df['Age'].dtype)
print(df['Weight'].dtype)

df['New Index'] = vaex.vrange(0, len(df))

pdf = df.to_pandas_df()

print('vaex to pandas is')
print(pdf)

df1 = new_column_by_column_merging(df, ['Name', 'Age', 'Weight'])

print('new_column_by_column_merging returns')
print(df1)

df2 = new_column_by_column_merging2(df, ['Name', 'Age', 'Weight'])

print('new_column_by_column_merging2 returns')
print(df2)

df3 = df2.sort(['Age', 'Weight'])

print('after sorting is')
print(df3)






