# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 10:55:39 2016

@author: Alexis Eidelman
"""


def get_k(df, groupby):
    """
        Return the k-anonymity level of a df, grouped by the specified columns.

        :param df: The dataframe to get k from
        :param groupby: The columns to group by
        :type df: pandas.DataFrame
        :type groupby: Array
        :return: k-anonymity
        :rtype: int
    """
    size_group = df.groupby(groupby).size()
    return min(size_group)