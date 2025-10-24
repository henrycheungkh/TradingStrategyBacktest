# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 08:24:51 2021

@author: Henry Cheung
"""


import scipy.stats
import math

sample_mean = 56.2
sample_stdev = 130.72392
sample_size = 110

t_score = sample_mean / (sample_stdev / math.sqrt(sample_size))
p_value_from_t_score = scipy.stats.t.sf(abs(t_score), df=sample_size - 1)

z_score = sample_mean / sample_stdev
p_value_from_z_score = scipy.stats.norm.sf(abs(z_score))

print('t score is ' + str(t_score) + ' and p value from t score is ' + str(p_value_from_t_score))
print('z score is ' + str(z_score) + ' and p value from z score is ' + str(p_value_from_z_score))
