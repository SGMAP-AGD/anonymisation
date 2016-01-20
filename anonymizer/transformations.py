# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 14:40:36 2016

@author: Alexis Eidelman


List of transformation to aggregate a column
There is four parts in that file.
    1 - deals with numeral values
    2 - deals with string values
    3 - deals with date values
    4 - deals with special function, not always aggregating
"""

import pandas as pd

### 1 - numbers
def num_drop(x):
    return x.mean()

### 2 - string
def str_drop(x):
    return 'dropped'

def first_letters(x, k=1):
    return x.str[:k]

### 3 - date
def date_drop(x):
    return x.min()

def period_by_hours(x, separation):
    ''' aggrege le x par intervale d'heure.
        Le calcul pourrait être simple si on interdisait
        le chevauchement de jour.
    '''
    print(separation)
    assert isinstance(separation, list)
    assert all([sep < 24 for sep in separation])
    separation.sort()

    if 0 in separation:
        separation.append(24)
        hour_categ = pd.cut(x.dt.hour, separation, right=False)
        date_categ = x.dt.date
        return date_categ.astype(str) + ' ' + hour_categ.astype(str)
    else:
        hour = x.dt.hour
        hour_categ = pd.cut(hour, separation, right=False).astype(str)
        night_categ = '[' + str(separation[-1]) + ', ' + str(separation[0]) + ')'
        hour_categ[(hour < separation[0]) & (hour >= separation[-1])] = night_categ
        date_categ = x.dt.date
        date_categ[x.dt.hour < separation[1]] -= pd.DateOffset(1)
        return date_categ.astype(str) + ' ' + hour_categ


### 4 - special

