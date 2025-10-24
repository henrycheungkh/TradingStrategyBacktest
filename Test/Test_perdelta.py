# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 01:45:27 2021

@author: Henry Cheung
"""


# from datetime import date, datetime, timedelta

# def perdelta(start, end, delta):
#     curr = start
#     while curr < end:
#         yield curr
#         curr += delta
        
# # data = list(perdelta(date(2011, 10, 10), date(2011, 10, 11), timedelta(minutes=1)))

# data = []
# for result in perdelta(date(2011, 10, 10), date(2011, 10, 11), timedelta(minutes=1)):
#     data.append(result)

# print(data)


from datetime import date, datetime, timedelta

def datetime_range(start, end, delta):
    current = start
    if not isinstance(delta, timedelta):
        delta = timedelta(**delta)
    while current < end:
        yield current
        current += delta

def datetime_range_list(start, end, delta):
    print(start)
    print(end)
    return list(datetime_range(start, end, delta))
start = datetime(2021,3,1)
end = datetime(2021,10,2)
start = date(2021,3,1)
end = date(2021,10,2)
start = datetime.combine(start, datetime.min.time())
end = datetime.combine(end, datetime.min.time())

data = datetime_range_list(start, end, {'minutes':1})
print(data[0])

#this unlocks the following interface:
# for dt in datetime_range(start, end, {'days': 2, 'hours':12}):
# for dt in datetime_range(start, end, {'hours':2}):
# for dt in datetime_range(start, end, {'minutes':1}):
#     print (dt)