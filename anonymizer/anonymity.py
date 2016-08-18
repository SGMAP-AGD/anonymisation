# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 10:55:39 2016

@author: Alexis Eidelman
"""
import numpy as np
import pandas as pd

from anonymizer.transformations import local_aggregation

def _remove_unknown(tab, groupby, unknown):
    if unknown is not None:
        cond_unknown = (tab[groupby] == unknown).any(axis=1)
        tab = tab[~cond_unknown]   
    return tab
    
def get_k(df, groupby, unknown=None):
    """
        Return the k-anonymity level of a df, grouped by the specified columns.

        :param df: The dataframe to get k from
        :param groupby: The columns to group by
        :type df: pandas.DataFrame
        :type groupby: Array
        :return: k-anonymity
        :rtype: int
    """
    df = _remove_unknown(df, groupby, unknown)
    size_group = df.groupby(groupby).size()
    if len(size_group) == 0:
        return np.Infinity
    return min(size_group)


def get_anonymities(df, groupby, unknown=None):    
    df = _remove_unknown(df, groupby, unknown)
    return df.groupby(groupby).size()


def less_anonym_groups(df, groupby, unknown=None):
    df = _remove_unknown(df, groupby, unknown)
    grp = df.groupby(groupby)
    size_group = grp.size()
    select = size_group[size_group == min(size_group)]
    results = []
    for group_index in select.index:
        results += [grp.get_group(group_index)]
    return results


def all_local_aggregation(tab, k, variables, method, unknown=''):
    '''
        retourne une table k-anonymisée par aggrégation locale
        
        tab: la table à anonymiser
        k: un entier est le k-anonymat recherché
        variables est une liste de variable de tab :
            on traitera les données dans cet ordre et 
            la première variable sera celle dont on est le plus
            prêt à sacrifier l'aggrégation
        method : voir local_aggregation
    
    Remarque: si pour un groupe donné, plusieurs modalité ont moins de k
    éléments, on les remplace toutes par "dropped", on peut ainsi avoir un
    groupe avec dropped d'une taille supérieure à k. 
    Si ensuite on a une modalité plus grande que k à l'intérieur du groupe 
    hétéroclyte avec dropped, on peut afficher cette variable
    '''
    assert(isinstance(k, int))
    assert(all([var in tab.columns for var in variables]))
    assert(all(tab[variables].dtypes == 'object'))

    if get_k(tab, variables) >= k:
        return tab

    variable_a_aggreger = variables[-1]
    if len(variables) == 1:
        new_serie = local_aggregation(tab[variable_a_aggreger],
                                      k, method, unknown)
        tab[variable_a_aggreger] = new_serie        
        return tab

    if get_k(tab, variables[:-1]) < k:
        tab = all_local_aggregation(tab, k, variables[:-1], method, unknown)
    # on a une table k-anonymisée lorsqu'elle est restreinte aux 
    # len(variables) - 1 premières variables
        
    # on applique l'aggrégation locale d'une variable par groupe
    grp = tab.groupby(variables[:-1])
    new_serie = grp[variable_a_aggreger].apply(
        lambda x: local_aggregation(x, k, method, unknown)
        )
    tab[variable_a_aggreger] = new_serie
    
    assert get_k(tab, variables, unknown) >= k

    return tab

