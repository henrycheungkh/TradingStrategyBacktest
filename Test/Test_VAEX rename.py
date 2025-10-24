
import vaex
import pandas as pd  
import numpy as np

def drop_duplicates(df, columns=None):
    """Return a :class:`DataFrame` object with no duplicates in the given columns.
    .. warning:: The resulting dataframe will be in memory, use with caution.
    :param columns: Column or list of column to remove duplicates by, default to all columns.
    :return: :class:`DataFrame` object with duplicates filtered away.
    """
    if columns is None:
        columns = df.get_column_names()
    if type(columns) is str:
        columns = [columns]
    return df.groupby(columns, agg={'__hidden_count': vaex.agg.count()}).drop('__hidden_count')

pandas_df = pd.DataFrame({'Name': ['Tom', 'Joseph', 'Krish', 'John'], 'Last Name': ['Johnson', 'Cameron', 'Biden', 'Washington'], 'Age': [20, 21, 19, 18]})  
print('pandas_df is')
print(pandas_df)  

print('pandas_df.columns[:1].values is')
print(pandas_df.columns[:1].values)

print('pandas_df.columns[:1].values.tolist() is')
print(pandas_df.columns[:1].values.tolist())
print()

df = vaex.from_pandas(df=pandas_df, copy_index=False)

print('df.get_column_names() is')
print(df.get_column_names())

print('df.get_column_names()[:1] is')
print(df.get_column_names()[:1])

try:
    df['New Name'] = df['Name'].astype('float64')
except:
    print('something wrong')
    df['New Name'] = df['Name'].astype('string')

# df['New Name'] = df['Name'].astype('string')

print('df with String to float is')
print(df)

# df['New Age'] = df.Age.astype('float64')
df['New Age'] = df['Age'].astype('float64')

print('df with int to float is')
print(df)

df2 = drop_duplicates(df[['Name']])
print('drop_duplicates(df[[\'Name\']]) is')
print(df2)

print()

pandas_num_only_df = pd.DataFrame({'Age1': [20, 21, 19, 18], 'Age2': [20, 21, 19, 18], 'Age3': [20, 21, 19, 18]})  
print('pandas_num_only_df.to_numpy() is')
print(pandas_num_only_df.to_numpy())  

df_num_only = vaex.from_pandas(df=pandas_num_only_df, copy_index=False)


print('df_num_only.to_dict is')
print(df_num_only.to_dict())

dictionary = df_num_only.to_dict()

# nnn = np.array([dictionary[key] for key in ('Age1', 'Age2', 'Age3')]).T
nnn = np.array([dictionary[key] for key in sorted(dictionary.keys())]).T

print('np.array(dictionary) is')
print(nnn)

minmax = df_num_only.minmax(['Age1'])
print('df_num_only.minmax([\'Age1\']) is ')
print(minmax)
print(minmax[0,0])
print(minmax[0,1])

# print('df before rename')
# print(df)  

# df.rename('Name', 'Name2')
# # df = df.rename(Name, Name2)
# print('df after rename')
# print(df)  


