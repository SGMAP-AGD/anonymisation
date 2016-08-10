# coding: utf-8

#!/usr/bin/env python


"""
A partir des fonctions du dépôt anonymizer, ce fichier va notamment vous permettre de :

1. **Importer** les données de la base équidés.
2. **Nettoyer** les variables et sélectionner celles à anonymiser
3. **Anonymiser** les données selon un procédé de K-anonymisation

"""

import csv
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

from anonymizer.import_insee import (expand_insee,
                                     nbre_modif)

from anonymizer.anonymity import (get_k, get_anonymities,
                                  less_anonym_groups,
                                  local_aggregation,
                                  _local_aggregate_one_var)
from anonymizer.diversity import (get_l,
                                  get_diversities,
                                  diversity_distribution,
                                  less_diverse_groups
                                )
from anonymizer.transformations import (first_letters,
                                       last_letters)
from anonymizer.transformations import str_drop
from anonymizer.anonymDF import AnonymDataFrame


# ## I. Nettoyage de la base de données

chemin = "/home/pierre-louis/Téléchargements/Equides.csv"
equides = pd.read_csv(chemin, sep = ";", encoding = "ISO-8859-1", nrows = 50000, header=None, low_memory = False)


nom_de_colonnes = ['Race',
                   'Sexe',
                   'Robe',
                   'Date de naissance',
                   'Pays de naissance',
                   'Nom',
                   'Destiné à la consommation humaine',
                   'Date de mort']
equides.columns = nom_de_colonnes


# On supprime la date de mort puisque cela nous fournirait un indice sur l'âge du cheval,
# qu'il faudrait veiller à anonymiser.

variables_supprimees = ['Date de mort']
equides = equides.drop(variables_supprimees,1)


# La variable "date de naissance" doit être recodée. On choisit de ne garder que l'année.
equides['Date de naissance'] = last_letters(equides['Date de naissance'],6)

# On remplace les modalités vides ou non renseignées par des "non renseigné"
equides = equides.fillna('non renseigné')
equides = equides.applymap(lambda x: x.strip())
equides.replace('', 'non renseigné', inplace=True)



liste_races = equides['Race'].unique().tolist()

# On convertit tous les noms de races en minuscules afin de mieux pouvoir uniformiser
# et on normalise afin de n'obtenir plus qu'une modalité inconnu, anglo-arabe, weslh ou aa compl.

equides['Race'] = equides['Race'].str.lower()


a_remplacer = []
for i in liste_races :
    if 'inconnu' in i :
        a_remplacer.append(i)
equides['Race'] = equides['Race'].replace(a_remplacer, 'inconnu')

a_remplacer = []
for i in liste_races :
    if 'anglo-arabe' in i :
        a_remplacer.append(i)
equides['Race'] = equides['Race'].replace(a_remplacer, 'anglo-arabe')

a_remplacer = []
for i in liste_races :
    if 'welsh' in i :
        a_remplacer.append(i)
equides['Race'] = equides['Race'].replace(a_remplacer, 'welsh')

a_remplacer = []
for i in liste_races :
    if 'aa compl.' in i :
        a_remplacer.append(i)
equides['Race'] = equides['Race'].replace(a_remplacer, 'aa compl.')


# ## II. Anonymisation 

# On définit les variables à anonymiser

var = ['Race',
       'Sexe',
       'Robe',
       'Pays de naissance',
       'Destiné à la consommation humaine',
       'Date de naissance']


# Pour les cinq premières variables, on anonymise selon la méthode "groupped"

k = 5
kanonym_equides = local_aggregation(equides.copy(), k, var[:-1])


# Pour la date de naissance, on anonymise selon la méthode "year"

kanonym_equides = local_aggregation(kanonym_equides, k, [var[-1]], method = "year")


# ## III. Résultats

# La base est 5-anonymisée

kanonym_equides