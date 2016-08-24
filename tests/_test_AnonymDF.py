# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 11:37:34 2016

@author: Alexis Eidelman
"""

#TODO: import unittest

from anonymizer.anonymDF import AnonymDataFrame
import anonymizer.transformations as transfo
from generate_tab import random_table_test_anonym

tab = random_table_test_anonym(1000, 8, 5)

test = AnonymDataFrame(tab, ['identifiant'], 'sensible')

test.get_k()
test.get_l()


nb_cols = 4
tab = random_table_test_anonym((100, nb_cols), 8, 5)
nom_cols = ['ident_' + str(k) for k in range(nb_cols)]
tab = tab.astype(str)

test = AnonymDataFrame(tab, nom_cols, 'sensible')

test.get_k()
test.get_l()

def transfo_0(x):
    return transfo.local_aggregation(x, 5, 'with_closest', unknown='')
    
list_transfo = [('ident_0', transfo_0), ('ident_1', transfo_0),
                ('ident_2', transfo_0), ('ident_3', transfo_0)]

transfo1 = test.transform(list_transfo)
transfo2 = test.local_transform(list_transfo, 5)

