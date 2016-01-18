#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import pandas as pd

from agd_tools import anonymization

__author__ = "Paul"


class TestAnonymisationMethods(unittest.TestCase):

    def test_get_k(self):
        iris = pd.read_csv("tests/iris.csv")
        k = anonymization.get_k(iris, ['Name'])
        self.assertEqual(k, 50)

    def test_get_distinct_l(self):
        iris = pd.read_csv("tests/iris.csv")
        l_diversity = anonymization.get_distinct_l(iris,
                                                   groupby=['Name'],
                                                   column='PetalLength')
        self.assertEqual(l_diversity, 9)

    def test_get_distinct_l_with_nulls(self):
        iris = pd.read_csv("tests/iris.csv")
        iris = iris.append(pd.DataFrame([[1, 1, None, 1, "Iris-Test"],
                                         [1, 1, None, 1, "Iris-Test"],
                                         [1, 1, 2, 1, "Iris-Test"]],
                           columns=iris.columns.values))
        l_diversity = anonymization.get_distinct_l(iris,
                                                   groupby=['Name'],
                                                   column='PetalLength')
        self.assertEqual(l_diversity, 3)

if __name__ == '__main__':
    unittest.main()
