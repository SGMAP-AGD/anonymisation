#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import pandas as pd

from anonymizer.anonymity import get_k
from anonymizer.diversity import (get_l, get_diversities, diversity_distribution,
                       less_diverse_groups)

__author__ = "Alexis, Paul"

class TestAnonymisationMethods(unittest.TestCase):

    def test_get_k(self):
        iris = pd.read_csv("data/iris.csv")
        k = get_k(iris, ['Name'])
        self.assertEqual(k, 50)

    def test_get_distinct_l(self):
        iris = pd.read_csv("data/iris.csv")
        l_diversity = get_l(iris, groupby=['Name'], column='PetalLength')
        self.assertEqual(l_diversity, 9)

    def test_get_distinct_l_with_nulls(self):
        iris = pd.read_csv("data/iris.csv")
        iris = iris.append(pd.DataFrame([[1, 1, None, 1, "Iris-Test"],
                                         [1, 1, None, 1, "Iris-Test"],
                                         [1, 1, 2, 1, "Iris-Test"]],
                           columns=iris.columns.values))
        l_diversity = get_l(iris, groupby=['Name'], column='PetalLength')
        self.assertEqual(l_diversity, 3)

if __name__ == '__main__':
    unittest.main()

