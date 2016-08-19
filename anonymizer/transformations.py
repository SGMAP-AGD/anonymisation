# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 14:40:36 2016

@author: Alexis Eidelman


List of transformation to aggregate a column
There is four parts in that file.
    1 - deals with numeral values
    2 - deals with string values
    3 - deals with date values
    4 - deals with special function, not always aggregating
"""

import numpy as np
import pandas as pd

### 1 - numbers
def num_drop(x):
    return x.mean()

### 2 - string
def str_drop(x):
    return 'dropped'

def first_letters(x, k=1):
    return x.str[:k]

def last_letters(x, k=1):
    return x.str[k:]

### 3 - date
def date_drop(x):
    return x.min()

def period_by_hours(x, separation):
    ''' aggrege le x par intervale d'heure.
        Le calcul pourrait être simple si on interdisait
        le chevauchement de jour.
    '''
    print(separation)
    assert isinstance(separation, list)
    assert all([sep < 24 for sep in separation])
    separation.sort()

    if 0 in separation:
        separation.append(24)
        hour_categ = pd.cut(x.dt.hour, separation, right=False)
        date_categ = x.dt.date
        return date_categ.astype(str) + ' ' + hour_categ.astype(str)
    else:
        hour = x.dt.hour
        hour_categ = pd.cut(hour, separation, right=False).astype(str)
        night_categ = '[' + str(separation[-1]) + ', ' + str(separation[0]) + ')'
        hour_categ[(hour < separation[0]) | (hour >= separation[-1])] = night_categ
        assert hour_categ.nunique(dropna=False) == len(separation)
        date_categ = x.dt.date.astype(str)
        # décalage d'un jour pour les premières heures
        decale = x.dt.date[x.dt.hour < separation[1]] + pd.DateOffset(days=-1)
        date_categ[x.dt.hour < separation[1]] = decale.astype(str)
        assert all(date_categ.str.len() == 10)
        return date_categ + ' ' + hour_categ


### 4 - special

def _name_aggregation(list_of_values):
    list_of_values.sort()
    return ' ou '.join(list_of_values)


def local_aggregation(serie_init, k, method, unknown=''):
    '''
        réalise l'aggregation locale sur une seule variable

    '''
    assert serie_init.dtype == 'object'
    assert method in ['into_unknown', 'remove',
                      'regroup_with_smallest',
                      'regroup_with_biggest',
                      'with_closest']

    serie_without_null = serie_init[serie_init != unknown]
    serie = serie_without_null
    counts = serie.value_counts()
    counts_to_change = counts[counts < k]
    index_to_change = counts_to_change.index.tolist()

    # si pas de groupe inférieur à k, on a fini
    if len(index_to_change) == 0:
        return serie_init

    if len(serie) < k:
        return pd.Series(unknown, index=serie_init.index)

    if method == 'into_unknown':
        # si on a que deux valeurs alors le non renseigné devient
        # facile à retrouver : c'est l'autre valeur
        #    si remplace k et sur plus d'une modalité on sait que
        #    c'est bien anonymisé. sinon, il faut faire autre chose.
        if counts_to_change.sum() >= k  or serie_init.nunique() > 2:
            return serie_init.replace(index_to_change, unknown)
        else:
            return pd.Series(unknown, index=serie_init.index)

    if method == 'remove':
        return serie_init[~serie_init.isin(index_to_change)]

    if 'regroup' in method:
        # on regroupe en priorité les petits groupes entre eux
        # si ça ne suffit pas on va chercher un autre groupe
        # on cherche donc un groupe, par construction de taille supérieure
        # à k, avec qui regrouper.
        if counts_to_change.sum() >= k:
            pass # rien à faire

        if counts_to_change.sum() < k:
            clients_pour_regrouper = counts[counts >= k]
            if len(clients_pour_regrouper) == 0:
                # ne doit pas se produire parce que ça veut dire
                # qu'on a moins de k petit et pas de gros, ça veut
                # dire qu'on a moins de k lignes
                raise Exception('Ca ne doit pas arriver')
            # on cherche un groupe, par construction de taille supérieure
            # à k, avec qui regrouper.
            # on recommander plutôt de ne pas déteriorer la plus grande modalité
            # et de prendre la plus petite possible
            if method == 'regroup_with_smallest':
                pour_regrouper = clients_pour_regrouper.index[-1]
            if method == 'regroup_with_biggest':
                pour_regrouper = clients_pour_regrouper.index[0]

            index_to_change.append(pour_regrouper)

        # le nom de la nouvelle modalité
        new_name = _name_aggregation(index_to_change)
        return serie_init.replace(index_to_change, new_name)

    if method == 'with_closest':
        # on regroupe les nombres qui ne sont pas k-anonymisés avec
        # la valeur la plus proche
        df = pd.DataFrame(counts)
        df.columns = ['count']
        df['name'] = df.index

        def _to_float(str_expression):
            if ' ou ' in str_expression:
                splittage = str_expression.split(' ou ')
                barycentre = np.mean([float(k) for k in splittage])
                return barycentre
            else:
                return float(str_expression)

        df['value'] = df['name'].apply(_to_float)

        modifications = []
        while df['count'].min() < k:
            valeur_a_remplacer = df.iloc[-1,:]
            distance = (df['value'] - valeur_a_remplacer['value'])**2
            idxmin = distance[distance > 0].idxmin()

            pour_regrouper = [valeur_a_remplacer['name'], idxmin]

            #calcul de la nouvelle modalité
            new_name = _name_aggregation(pour_regrouper)
            new_count = df.loc[pour_regrouper]['count'].sum()
            # introduit un biais quand on agregre deux valeurs
            # puis une troisième, on tire vers la troisième
            new_value = df.loc[pour_regrouper]['value'].mean()
            df.loc[new_name] = [new_count, new_name, new_value]
            df.drop(pour_regrouper, inplace=True)
            df.sort_values('count', ascending=False,
                           inplace=True)

            modifications.append((pour_regrouper, new_name))

        for modification in modifications:
            serie_init.replace(modification[0], modification[1], inplace=True)
        return serie_init
