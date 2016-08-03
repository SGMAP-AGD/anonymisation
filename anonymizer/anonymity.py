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


def get_anonymities(df, groupby):
    return df.groupby(groupby).size()


def less_anonym_groups(df, groupby):
    grp = df.groupby(groupby)
    size_group = grp.size()
    select = size_group[size_group == min(size_group)]
    results = []
    for group_index in select.index:
        results += [grp.get_group(group_index)]
    return results

def _local_aggregate_one_var(serie, k, method):
    ''' réalise l'aggregation locale sur une seule variable'''
    
    assert method in ['dropped', 'remove', 'regroup']

    counts = serie.value_counts()
    counts_to_change = counts[counts < k]
    index_to_change = counts_to_change.index.tolist()
    
    if method == 'dropped':
        if counts_to_change.sum() >= k:
            return serie.replace(index_to_change, 'dropped')
        # si elle ne marche pas, on regroupe
        method = 'regroup'
    # on repere le mode

#    si on a droppé plus de k et sur plus d'une modalité on sait que 
#    c'est bien anonymisé. sinon, il faut faire autre chose.

    if method == 'remove':
        # TODO: prendre en compte le changement de taille et la
        # récupération dans la table
        return serie[~serie.isin(index_to_change)]
    
    if method == 'regroup':
        ''' on regroupe tout avec le mode ;
        l'effectif obtenu est plus grand que k '''

        # on cherche un groupe, par construction de taille supérieure
        # à k, avec qui regrouper.
        if counts_to_change.sum() < k:
            clients_pour_regrouper = counts[counts >= k]
            if len(clients_pour_regrouper) == 0:
                raise Exception('prevoir quelque chose parce que \
                    tout le monde est dans un groupe plus petit que k')
            # on fait le choix de ne pas déteriorer la plus grande modalité
            # on prend la plus petite possible
            pour_regrouper = clients_pour_regrouper.index[-1]
            index_to_change.append(pour_regrouper)
        # le nom de la nouvelle modalité
        new_name = ' ou '.join(index_to_change)
        return serie.replace(index_to_change, new_name)



def local_aggregation(tab, k, variables, method='regroup'):
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
    
    assert get_k(tab, variables) >= k
    return tab

