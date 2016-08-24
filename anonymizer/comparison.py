# -*- coding: utf-8 -*-
"""
Recueil de méthode pour comparer deux anonymisations

Created on Wed Aug 24 18:20:24 2016

@author: aeidelman
"""

from anonymizer.anonymDF import AnonymDataFrame


def _identical_transformation(transfo1, transfo2):
    if len(transfo1) != len(transfo2):
        return False
    for k in range(len(transfo1)):
        if transfo1[k][0] != transfo2[k][0] or transfo1[k][1] != transfo2[k][1]:
            return False
    return True

def compare_ce_qui_est_comparable(anonymisation1, anonymisation2):
    ''' verifie que les deux objets peuvent être comparés '''
    assert isinstance(anonymisation1, AnonymDataFrame)
    assert isinstance(anonymisation2, AnonymDataFrame)

    assert all(anonymisation1.df == anonymisation2.df)

    if _identical_transformation(anonymisation1.transformation,
                                 anonymisation2.transformation):
        assert all(anonymisation1.anonymized_df == anonymisation2.anonymized_df)
        raise Exception("a priori, c'est la même anonymisation")


def batterie_de_test(anonymisation1, anonymisation2):

    compare_ce_qui_est_comparable(anonymisation1, anonymisation2)

    df = anonymisation1.df # = anonymisation2.df
    df1 = anonymisation1.anonymized_df
    transfo1 = anonymisation1.transformation
    df2 = anonymisation2.anonymized_df
    transfo2 = anonymisation2.transformation

    if len(df) != len(df1) or len(df) != len(df2):
        print('le nombre de lignes de la table initiale est ', len(df))
        print(len(df1), 'lignes ont été supprimées dans la première anonymisation')
        print(len(df2), 'lignes ont été supprimées dans la seconde anonymisation')
    
    
    print((df1 == df2).sum())

