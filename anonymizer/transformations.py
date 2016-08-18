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
        ''' on regroupe les années qui ne sont pas k-anonymisées avec l'année la plus proche'''
        boucle = serie.value_counts()[-1]
        while boucle < k :
            serie2 = serie.copy()
            # Lorsqu'on a une modalité 'x ou y', il faut la transformer en 
            # valeur numérique pour calculer la distance
            # => on ne va garder que la première valeur
            # mais on stocke quand même les "année ou année" pour pouvoir
            # les modifier à la fin
            valeurs_splittees = []
            for x in serie2.unique() :
                if ' ou ' in x:
                    splittage = x.split(' ou ')
                    serie2 = serie2.replace(x, splittage[0])
                    valeurs_splittees.append(splittage)

            serie2 = serie2.astype(int)
            counts = serie2.value_counts()
            counts_to_change = counts[counts < k]
            index_to_change = counts_to_change.index.tolist()
            liste_a_comparer = serie2.unique().tolist()
            modifications = []
    
            for valeur_a_remplacer in index_to_change: 
                if valeur_a_remplacer not in modifications: 
                    liste_a_comparer2 = list(liste_a_comparer) # = copy
                    liste_a_comparer2.remove(valeur_a_remplacer)
                    pour_regrouper = [str(valeur_a_remplacer)]

                    # on effectue le calcul des distances
                    # et on les stocke dans un dictionnaire 
                    d = {}
                    for i in liste_a_comparer2 :
                        d[i] = abs(i - valeur_a_remplacer)

                    # on prend le minimum des distances trouvées
                    minimum = min(d.items(), key = lambda x: x[1])[0]
                    # on vérifie pour voir si la modalité de départ
                    # est présent en l'état dans notre série
                    # ou sous forme de "année ou année" (cf 1ère étape)
                    for groupe_splitte in valeurs_splittees:
                        if pour_regrouper[0] in groupe_splitte:
                            pour_regrouper = [_name_aggregation(groupe_splitte)]

                    # on fait la même opération concernant le minimum trouvé :
                    # si on a trouvé 2005 mais que l'on a que "2005 ou 2006" 
                    # comme modalité, il faut le repérer et modifier la valeur
                    # du string du minimum en conséquence
                    for modalite in serie.unique().tolist():
                        if str(minimum) in modalite:
                            pour_regrouper.append(modalite)
                    
                    
                    #calcul de la nouvelle modalité
                    new_name = _name_aggregation(pour_regrouper)
                    serie_init = serie_init.replace(pour_regrouper, new_name)
                    modifications.append(minimum)
                    modifications.append(valeur_a_remplacer)
                    serie = serie_init[serie_init != unknown]
            boucle = serie.value_counts().min()
        return serie_init
