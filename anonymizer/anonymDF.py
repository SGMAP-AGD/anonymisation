# -*- coding: utf-8 -*-
"""
Created on Sun Nov 01 19:28:44 2015

@author: Alexis
"""

import pandas as pd

from anonymizer.anonymity import (get_k, get_anonymities, less_anonym_groups,
    local_aggregation)
from anonymizer.diversity import (get_l, get_diversities, diversity_distribution,
                       less_diverse_groups)


class AnonymDataFrame(object):

    def __init__(self, df, var_identifiantes, var_sensibles=None,
                 unknown=None):
        assert isinstance(df, pd.DataFrame)
        self.df = df

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

    def list_valeurs_identifiantes(self):
        for var in self.identifiant:
            print(self.df[var].unique())

    def get_k(self):
        return get_k(self.df, self.identifiant, self.unknown)

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
        return local_aggregation(self.df, k, self.identifiant, method=method)

    def transform(self, transformation):
        ''' return a new AnonymDataFrame with
            transformation is a dict where:
                keys are columns of self.df
                values are transformations to operate on var
        '''
        assert isinstance(transformation, dict)
        assert all([x in self.df.columns for x in transformation])
        df = self.df.copy()
        for colname, transfo in transformation.items():
            df[colname] = transfo(self.df[colname])
        return AnonymDataFrame(df, self.identifiant, self.sensible)

