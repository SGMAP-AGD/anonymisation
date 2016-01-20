# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 11:37:34 2016

@author: Alexis Eidelman
"""

#TODO: import unittest

from anonymizer.anonymDF import AnonymDataFrame
from generate_tab import random_table_test_anonym

tab = random_table_test_anonym(1000, 8, 5)

test = AnonymDataFrame(tab, ['identifiant'], 'sensible')

test.get_k()
test.get_l()


