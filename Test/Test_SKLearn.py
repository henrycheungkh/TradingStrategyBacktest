# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 21:59:27 2021

@author: Henry Cheung
"""

# https://www.youtube.com/watch?v=7eh4d6sabA0

import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

music_data = pd.read_csv('music.csv')

# print(music_data)

X = music_data.drop(columns=['genre'])
y = music_data['genre']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = DecisionTreeClassifier()
model.fit(X_train, y_train)
predictions = model.predict(X_test)

score = accuracy_score(y_test, predictions)

print(score)

# print(predictions)

