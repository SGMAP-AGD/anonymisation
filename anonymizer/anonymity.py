# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 10:55:39 2016

@author: Alexis Eidelman
"""
import numpy as np

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


def _name_aggregation(list_of_values):
    list_of_values.sort()
    return ' ou '.join(list_of_values)


def _local_aggregate_one_var(serie_init, k, method, unknown=''):
    ''' 
        réalise l'aggregation locale sur une seule variable
        
    '''
    
    assert method in ['dropped', 'remove', 'regroup', 'year']

    serie_without_null = serie_init[serie_init != unknown]
    serie = serie_without_null
    counts = serie.value_counts()
    counts_to_change = counts[counts < k]
    index_to_change = counts_to_change.index.tolist()
    
    if method == 'dropped':
        if counts_to_change.sum() >= k:
            return serie_init.replace(index_to_change, unknown)
        # si elle ne marche pas, on regroupe
        method = 'regroup'
    # on repere le mode

#    si on a droppé plus de k et sur plus d'une modalité on sait que 
#    c'est bien anonymisé. sinon, il faut faire autre chose.

    if method == 'remove':
        # TODO: prendre en compte le changement de taille et la
        # récupération dans la table
        return serie_init[~serie_init.isin(index_to_change)]
    
    if method == 'regroup':
        ''' on regroupe tout avec le mode ;
        l'effectif obtenu est plus grand que k '''

        # on cherche un groupe, par construction de taille supérieure
        # à k, avec qui regrouper.
        if counts_to_change.sum() < k:
            clients_pour_regrouper = counts[counts >= k]
            if len(clients_pour_regrouper) != 0:
                pour_regrouper = clients_pour_regrouper.index[-1]
                index_to_change.append(pour_regrouper)
            else :
                pour_regrouper = counts_to_change.index[-1]
                index_to_change.append(pour_regrouper)
            # on fait le choix de ne pas déteriorer la plus grande modalité
            # on prend la plus petite possible
            
        # le nom de la nouvelle modalité
        new_name = _name_aggregation(index_to_change)
        return serie_init.replace(index_to_change, new_name)

    if method == 'year':
        ''' on regroupe les années qui ne sont pas k-anonymisées avec l'année la plus proche'''
        boucle = serie.value_counts()[-1]
        while boucle < k :
            serie2 = serie.copy()            
            valeur_non_renseignee = 9999
            assert (sum(serie2 == str(valeur_non_renseignee)) == 0, 'La valeur 9999 est déjà prise')
            serie2.replace('non renseigné', valeur_non_renseignee, inplace = True)
              
            # Lorsqu'on a une modalité 'x ou y', il faut la transformer en 
            # valeur numérique pour calculer la distance
            # => on ne va garder que la première valeur
            # mais on stocke quand même les "année ou année" pour pouvoir
            # les modifier à la fin
            serie2 = serie2.astype(str)
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
            boucle = serie.value_counts().min()
        return serie_init


def local_aggregation(tab, k, variables, method='regroup', 
                      unknown=''):
    '''
        retourne une table k-anonymisée par aggrégation locale
        
        tab: la table à anonymiser
        k: un entier est le k-anonymat recherché
        variables est une liste de variable de tab :
            on traitera les données dans cet ordre et 
            la première variable sera celle dont on est le plus
            prêt à sacrifier l'aggrégation
        method : voir _local_aggregate_one_var
    
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
        new_serie = _local_aggregate_one_var(tab[variable_a_aggreger],
                                             k, method)
        tab[variable_a_aggreger] = new_serie        
        return tab

    if get_k(tab, variables[:-1]) < k:
        tab = local_aggregation(tab, k, variables[:-1])
    # on a une table k-anonymisée lorsqu'elle est restreinte aux 
    # len(variables) - 1 premières variables
        
    # on applique l'aggrégation locale d'une variable par groupe
    grp = tab.groupby(variables[:-1])
    new_serie = grp[variable_a_aggreger].apply(
        lambda x: _local_aggregate_one_var(x, k, method)
        )
    tab[variable_a_aggreger] = new_serie
    
    assert get_k(tab, variables, unknown) >= k

    return tab

