# coding: utf-8

#!/usr/bin/env python


"""
A partir des fonctions du dépôt anonymizer, ce fichier va notamment vous permettre de :

1. **Importer** les données de la base équidés.
2. **Nettoyer** les variables et sélectionner celles à anonymiser
3. **Anonymiser** les données selon un procédé de K-anonymisation

The file can be downloaded here:
https://www.data.gouv.fr/fr/datasets/fichier-des-equides/
or directly :
https://www.data.gouv.fr/s/resources/fichier-des-equides/20141201-185229/Equides.csv

Le fichier de 200 Mo contient autours de 3 millions de lignes

"""

import csv
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

from anonymizer.anonymity import (get_k, get_anonymities,
                                  less_anonym_groups,
                                  all_local_aggregation)
from anonymizer.diversity import (get_l,
                                  get_diversities,
                                  diversity_distribution,
                                  less_diverse_groups
                                )
from anonymizer.transformations import (first_letters,
                                       last_letters,
                                       local_aggregation)
from anonymizer.transformations import str_drop
from anonymizer.anonymDF import AnonymDataFrame

from anonymizer.config_anonymizer import config
import os
import io


# ## I. Nettoyage de la base de données
path_data = config['PATH']['EQUIDES']
equides = pd.read_csv(path_data, sep = ";", encoding = "ISO-8859-1",
                      nrows = 50000, header=None, low_memory = False)

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

variables_supprimees = ['Date de mort', 'Destiné à la consommation humaine']
equides = equides.drop(variables_supprimees,1)

# La variable "date de naissance" doit être recodée. On choisit de ne garder que l'année.
equides['Date de naissance'] = last_letters(equides['Date de naissance'],6)

# On remplace les modalités vides ou non renseignées par des "non renseigné"
equides = equides.fillna('non renseigné')
equides = equides.applymap(lambda x: x.strip())
equides.replace('', 'non renseigné', inplace=True)



# On convertit tous les noms de races en minuscules afin de mieux pouvoir uniformiser
# et on normalise afin de n'obtenir plus qu'une modalité inconnu, anglo-arabe, weslh ou aa compl.

equides['Race'] = equides['Race'].str.lower()
liste_races = equides['Race'].unique().tolist()

for word in ['inconnu', 'anglo-arabe', 'welsh', 'aa compl.']:
    for race in liste_races :
        if word in race:
            print(word, race)
            equides['Race'] = equides['Race'].replace(race, word)

equides.replace('inconnu', 'non renseigné', inplace=True)
liste_races = equides['Race'].unique().tolist()
len(liste_races)


# ## II. Anonymisation 

# On définit les variables à anonymiser

ordre_aggregation = ['Race',
                     'Sexe',
                     'Robe',
                     'Pays de naissance',
                     'Destiné à la consommation humaine',
                     'Date de naissance']


Equides = AnonymDataFrame(equides,  ordre_aggregation, unknown='non renseigné')

def aggregation_serie(x):
        return(local_aggregation(x, 5, 'regroup_with_smallest', 'non renseigné'))
method_anonymisation = [(name, aggregation_serie) for name in ordre_aggregation[:-1]]

def aggregation_year(x):
        return(local_aggregation(x, 5, 'with_closest', 'non renseigné'))
method_anonymisation += [('Date de naissance', aggregation_year)]

Equides.local_transform(method_anonymisation, 5)

Equides.df = Equides.anonymized_df

Equides.get_k()
