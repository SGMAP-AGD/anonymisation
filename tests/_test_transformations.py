# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 15:02:50 2016

@author: Alexis Eidelman
"""

import string
import random

import numpy as np
import pandas as pd

from anonymizer.transformations import *

# define a test data frame
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

size = 1000
_num = pd.Series(np.random.rand(size))
_str = [id_generator() for x in range(size)]
__date = pd.Series(np.random.randint(1000000000, 2000000000, size))
_date = pd.to_datetime(__date, unit='s')

df = pd.DataFrame({'num': _num, 'str': _str, 'date': _date})

## test drop
df_dropped = df.copy()
df_dropped['num'] = num_drop(df['num'])
df_dropped['str'] = str_drop(df['str'])
df_dropped['date'] = date_drop(df['date'])

for col in df_dropped.columns:
    assert(df_dropped[col].nunique() == 1)


# 1 test numbers transfo


# 2 test string transfo
_str = df['str']
assert all(first_letters(_str).str.len() == 1)
assert all(first_letters(_str, k = 3).str.len() == 3)


# 3 test date transfo


