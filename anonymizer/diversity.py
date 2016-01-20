# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 10:55:46 2016

@author: Alexis Eidelman, Paul
"""


def _l_diversity(x):
    """
        A simple implementation of l-diversity counting na as distinct values

        Aggarwal, Charu C.; Yu, Philip S. (2008):
        "A General Survey of Privacy"
        http://charuaggarwal.net/generalsurvey.pdf
        Springer. ISBN 978-0-387-70991-8
    """
    nb_distinct_without_na = x.nunique(dropna=True)
    nb_of_na = sum(x.isnull())
    return nb_distinct_without_na + nb_of_na


def get_diversities(df, groupby, column):
    """
        Return the diversities levels of a column in a dataframe.

        This implementation takes Nan values as distinct modalities.

        You should replace all invalid, unknown and false rows by
        the numpy nan type before using this function.

        :param df: A pandas dataframe
        :param column: The sensible data column
        :param groupby: The columns to group by
        :type df: pandas.core.frame.DataFrame
        :type column: str
        :type groupby: list
        :return: diversities for each group
        :rtype: pandas.core.frame.DataFrame

        :Example:

        >>> iris = pd.read_csv("tests/iris.csv")
        >>> diversities = anonymization.get_diversities(iris,
                                                       groupby=['Name'],
                                                       column='PetalLength')
    """
    grp = df.groupby(groupby)
    res = grp[column].agg({'l_diversity' : _l_diversity })
    return res


def get_l(df, groupby, column):
    """
        Return the l-diversity value as an integer.

        Calls the get_diversities and extract the minimum l-diversity level.

        :param df: The dataframe to get l from
        :param column: The sensible data column
        :param groupby: The columns to group by
        :type df: pandas.core.frame.DataFrame
        :type column: str
        :type groupby: list
        :return: l-diversity
        :rtype: int


    """
    return min(get_diversities(df, groupby, column)['l_diversity'])


def diversity_distribution(df, groupby, column):
    """
        Return the l-diversity distribution of a dataframe.
    """
    diversity = get_diversities(df, groupby, column)['l_diversity']
    return diversity.value_counts().sort_index()


def less_diverse_groups(df, groupby, column):
    """
        Return the less diverse groups.
    """
    grp = df.groupby(groupby)
    res = grp[column].agg({'l_diversity' : _l_diversity })
    diversity = res['l_diversity']
    select = diversity[diversity == min(diversity)]
    results = []
    for group_index in select.index:
        results += [grp.get_group(group_index)]
    return results
