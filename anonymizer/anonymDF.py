# -*- coding: utf-8 -*-
"""
Created on Sun Nov 01 19:28:44 2015

@author: Alexis
"""

import pandas as pd

from anonymizer.anonymity import (get_k, get_anonymities, less_anonym_groups,
    all_local_aggregation)
from anonymizer.diversity import (get_l, get_diversities, diversity_distribution,
                       less_diverse_groups)


class AnonymDataFrame(object):

    def __init__(self, df, var_identifiantes, var_sensibles=None,
                 unknown=None):
        assert isinstance(df, pd.DataFrame)
        self.df = df
        self.transformation = None
        self.anonymized_df = None

        columns = df.columns
        for var in [var_identifiantes]:
            assert isinstance(var, list)
        if not all([x in columns for x in var_identifiantes]):
            not_in_columns = [x for x in var_identifiantes if x not in columns]
            raise Exception(not_in_columns, ' not in df.columns')

        if var_sensibles is not None:
            assert isinstance(var_sensibles, str)
            assert var_sensibles in columns
            assert var_sensibles not in var_identifiantes

        self.identifiant = var_identifiantes
        self.sensible = var_sensibles
        self.unknown = unknown

    def copy(self):
        copy = AnonymDataFrame(self.df,
                               self.identifiant,
                               self.sensible,
                               self.unknown
                               )
        copy.anonymized_df = self.anonymized_df
        copy.transformation = self.transformation
        return copy

    def list_valeurs_identifiantes(self):
        for var in self.identifiant:
            print(self.df[var].unique())

    def get_k(self):
        return get_k(self.df, self.identifiant, self.unknown)

    def  get_final_k(self):
        return get_k(self.anonymized_df, self.identifiant, self.unknown)

    def get_anonymities(self, force_unknown=None):
        if force_unknown is None:
            force_unknown = self.unknown
        return get_anonymities(self.df, self.identifiant, force_unknown)

    def less_anonym_groups(self, force_unknown=None):
        if force_unknown is None:
            force_unknown = self.unknown
        return less_anonym_groups(self.df, self.identifiant, force_unknown)

    def get_l(self):
        return get_l(self.df, self.identifiant, self.sensible)

    def get_diversities(self):
        return get_diversities(self.df, self.identifiant, self.sensible)

    def diversity_distribution(self):
        return diversity_distribution(self.df, self.identifiant, self.sensible)

    def less_diverse_groups(self):
        return less_diverse_groups(self.df, self.identifiant, self.sensible)

    def local_aggregation(self, k, method='regroup'):
        return all_local_aggregation(self.df, k, self.identifiant, method=method)

    def transform(self, transformation):
        '''
         return a new AnonymDataFrame with a transformed self.df
         df is modified by application of transformation
        - transformation can be
            - a list of tuple with:
                - first element is the name the column
                - second element is the transformation
            Note: it has no effect here but transformation are applied
            in the self.variables order or in the order of list when
            transformation is a list
        '''
        self.transformation = transformation
        assert isinstance(transformation, list)
        assert all([len(x) == 2 for x in transformation])
        assert all([x[0] in self.df.columns for x in transformation])
        anonymized_df = self.df.copy()
        for colname, transfo in transformation:
            anonymized_df[colname] = transfo(anonymized_df[colname])
        
        self.anonymized_df = anonymized_df
        return self.copy()

    def local_transform(self, transformation, k, force_unknown=None):
        '''
         return a new AnonymDataFrame with a transformed self.df
         df is modified by application of transformation

        The main difference with transformation is that here
        tranformation are applied by each group only if needed.

        - transformation: can be
            - a list of tuple with:
                - first element is the name the column
                - second element is the transformation
            - no dict here as order counts

        - k: un entier est le k-anonymat recherché

        Note: it does have effect here but transformation are applied
        in the self.variables order or in the order of list when
        transformation is a list

        '''

        if force_unknown is None:
            force_unknown = self.unknown
        self.transformation = transformation
        assert isinstance(transformation, list)
        assert all([len(x) == 2 for x in transformation])
        assert all([x[0] in self.df.columns for x in transformation])
        variables = [x[0] for x in transformation]
        derniere_transfo = transformation[-1]
        anonymized_df = self.df.copy()

        if get_k(anonymized_df, variables, force_unknown) >= k:
            self.anonymized_df = anonymized_df
            return self.copy()

        if len(transformation) == 1:
            colname = transformation[0][0]
            transfo = transformation[0][1]
            anonymized_df[colname] = transfo(anonymized_df[colname])
            self.anonymized_df = anonymized_df
            return self.copy()

        if get_k(anonymized_df, variables[:-1], force_unknown) < k:
            anonymized_df = self.local_transform(transformation[:-1], k).anonymized_df
        # on a une table k-anonymisée lorsqu'elle est restreinte aux
        # len(variables) - 1 premières variables

        # on applique l'aggrégation locale d'une variable par groupe
        grp = anonymized_df.groupby(variables[:-1])
        fonction = derniere_transfo[1]
        variable = derniere_transfo[0]
        anonymized_df[variable] = grp[variable].apply(fonction)
        #assert get_k(anonymized_df, variables, force_unknown) >= k

        self.anonymized_df = anonymized_df
        return self.copy()
