#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
A partir des fonctions du dépôt anonymizer, ce fichier va notamment vous permettre de :

1. **Importer** les données de la base Transparence Santé.
2. **Nettoyer** les variables et sélectionner celles à anonymiser
3. **Anonymiser** les données selon un procédé de K-anonymisation
4. **Compléter** avec les données INSEE afin d'en mesurer la plus-value.
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
from anonymizer.transformations import (first_letters)
from anonymizer.transformations import str_drop
from anonymizer.anonymDF import AnonymDataFrame


# ## I. Nettoyage de la base de données

# Importation des 50 000 premières lignes

chemin = "C:/Users/Pierre-Louis/declaration_avantage_2016_06_06_04_00.csv"

nbre_lignes = 50000
avantages = pd.read_csv(chemin, sep = ";", nrows = nbre_lignes, low_memory = False)


# === transformatiosn préalables ===

# * On transforme les CP en indicateurs régionaux
avantages['benef_dept'] = first_letters(avantages['benef_codepostal'],2)
avantages['benef_etablissement_dept'] = first_letters(avantages['benef_etablissement_codepostal'],2)

# * On supprime les CP peu orthodoxes
erreur_CP = ['0', '', 'IN']
avantages.loc[avantages['benef_dept'].isin(erreur_CP), 'benef_dept'] = np.nan
erreur_pays = ['[RE]','[GP]']
avantages.loc[avantages['benef_pays_code'].isin(erreur_pays), 'benef_pays_code'] = '[FR]'

# * On homogénéise les valeurs manquantes ou tierces par la mention "non-renseigné"
avantages = avantages.fillna('non renseigné')
to_replace = ['[AUTRE]', '']
avantages.replace(to_replace, 'non renseigné', inplace=True)


# * On supprime d'abord les variables identifiantes afin de ne garder que les variables quasi-identifiantes

variables_supprimees = ['avant_convention_lie', # nom de code de la convention
                        'identifiant_type', # on garde seulement la valeur
                        'benef_qualification', # champ libre qu'on ne garde pas
                        'benef_speicalite_libelle', #
                        'ligne_rectification',
                        'denomination_sociale',
                        'benef_titre_libelle',
                        'pays',
                        'benef_prenom', # identifiant
                        'benef_nom', # identifiant
                        'benef_adresse1', # identifiant
                        'benef_adresse2', # identifiant
                        'benef_adresse3',# identifiant
                        'benef_adresse4',# identifiant
                        'benef_identifiant_valeur',# identifiant
                        'benef_ville',# identifiant
                        'benef_etablissement_ville',# identifiant
                        'categorie',
                        'benef_qualite_code',
                        'benef_codepostal',
                        'benef_etablissement_codepostal']

avantages = avantages.drop(variables_supprimees,1)


# * On transforme la valeur des conventions/avantages en leur équivalent décile (uniformisation)

avantages['avant_montant_ttc'] = avantages['avant_montant_ttc'].astype(float)
avantages['montant_décile'] = pd.qcut(avantages.avant_montant_ttc,10)

# * On transforme la date (signature des avantages) en année/mois (le jour est trop identifiant)

annee = []
mois = []

for row in pd.to_datetime(avantages['avant_date_signature'], infer_datetime_format=True):
    annee.append(row.year)
    mois.append(row.month)
avantages['mois'] = mois
avantages['année'] = annee
avantages['avant_nature'] = avantages['avant_nature'].str.lower()



# On crée une colonne "avantages ou conventions" (par la suite, cela nous permettra de différencier les données originales des données INSEE)
avantages['av_ou_conv'] = 'oui'


# On définit ici les variables traitées pour l'anonymisation

var = ['benef_categorie_code',
       'qualite', 'benef_titre_code',
       'benef_specialite_code',
       'benef_dept',
       'benef_identifiant_type_code']


# ## II. Traitement des données brutes (sans INSEE)

# On k-anonymise dès maintenant la base brute.
# On définit ici k = 5

copy = avantages.copy
k = 5
avantages_kanonym = local_aggregation(avantages.copy(), k, var, method='regroup')

modalites_modifiees = [(avantages_kanonym != avantages).sum().sum()] # Nombre de lignes modifiées
modalites_intactes = [len(avantages[avantages['av_ou_conv']=='oui']) - modalites_modifiees[0]] # Nombre de lignes intactes


# ## II. Chargement des données INSEE

# construction d'un dictionnaire reliant les professions (INSEE) aux professions (Transparence Santé)

annuaire = {'Médecin omnipraticien' : ['benef_specialite_code', '[SM54]'],
 'Spécialiste en cardiologie' : ['benef_specialite_code', '[SM04]'],
 'Spécialiste en dermatologie vénéréologie' : ['benef_specialite_code', '[SM15]'],
 'Spécialiste en gynécologie médicale' : ['benef_specialite_code', '[SM19]'],
 'Spécialiste en gynécologie obstétrique' : ['benef_specialite_code', '[SM20]'],
 'Spécialiste en gastro-entérologie hépatologie' : ['benef_specialite_code', '[SM24]'],
 'Spécialiste en psychiatrie' : ['benef_specialite_code', '[SM42]'],
 'Spécialiste en ophtalmologie' : ['benef_specialite_code', '[SM38]'],
 'Spécialiste en oto-rhino-laryngologie' : ['benef_specialite_code', '[SM39]'],
 'Spécialiste en pédiatrie' : ['benef_specialite_code', '[SM40]'],
 'Spécialiste en pneumologie' : ['benef_specialite_code', '[SM41]'],
 'Spécialiste en radiodiagnostic et imagerie médicale' : ['benef_specialite_code', '[SM44]'],
 'Spécialiste en stomatologie' : ['benef_specialite_code', '[SM50]'],
 'Chirurgien dentiste' : ['qualite', 'Chirurgien-dentiste'],
 'Sage-femme' : ['qualite', 'Sage-femme'],
 'Infirmier' : ['qualite', 'Infirmier'],
 'Masseur kinésithérapeute' : ['qualite', 'Masseur-kinésithérapeute'],
 'Orthophoniste' : ['qualite', 'Orthophoniste'],
 'Orthoptiste' : ['qualite', 'Orthoptiste'],
 'Pédicure-podologue' : ['qualite', 'Pédicure-podologue'],
 'Audio prothésiste' : ['qualite', 'Audio prothésiste'],
 'Ergothérapeute' : ['qualite', 'Ergothérapeute'],
 'Psychomotricien' : ['qualite', 'Psychomotricien']}


# On charge les données INSEE

# On charge les données INSEE

chemin_insee = '/home/pierre-louis/Téléchargements/Python/insee_sante.csv'

insee_init = pd.read_csv(chemin_insee, sep=";", encoding = "ISO-8859-1", low_memory=False)
insee_init.columns.astype(str)

insee_init['Département'] = insee_init['Département'].astype(str)
insee_init['Région 2016'] = insee_init['Région 2016'].astype(str)

insee_init['Département'] = first_letters(insee_init['Département'],2)

# On fusionne les départements d'Outre-mer dans une seule catégorie (trop identifiant, sinon)  

outremer = ['1','2','3','4','6']
insee_init.loc[insee_init['Région 2016'].isin(outremer), 'Région 2016'] = 1

list_région = insee_init['Région 2016'].unique().tolist()

insee = insee_init.copy()

var_écartées = ['Région', 'Région 2016', 'CODGEO', 'Libellé commune ou ARM']
insee = insee.drop(var_écartées,1)


# === On rajoute à la base originale les données INSEE ===

# avantages_total est donc constituée de la base Transparence Santé, complétée par les données INSEE

g = insee.groupby('Département')

expand_insee = expand_insee(g, annuaire, avantages)

expand_insee.columns = avantages.columns.tolist()
avantages_total = pd.concat([avantages, expand_insee]).reset_index()




# === On anonymise (données enrichies) ===


result_insee = local_aggregation(avantages_total.copy(), k, var, method = 'regroup')
nombre_de_modifications = nbre_modif(result_insee, avantages_total, 'oui')

modalites_modifiees.append(nombre_de_modifications)
modalites_intactes.append(len(avantages_total[avantages_total['av_ou_conv']=='oui'])-modalites_modifiees[1])


## IV. Comparaison

# === Représentation graphique des différences entre les deux méthodes ===  


# On mesure :  

#1. Le nombre de **lignes différentes** avant et après l'opération  
#2. Le nombre de **lignes inchangées**  après l'opération  
#3. On stocke ces valeurs dans modalites_modifiees et modalites_intactes  

n_groups = 2 # data to plot


fig, ax = plt.subplots() # create plot # éventuellement mentionner la taille du graphique : figsize=(15, 6)

index = np.arange(n_groups)
bar_width = 0.35
opacity = 1

rects1 = plt.bar(index, modalites_modifiees, bar_width,
                 alpha=opacity,
                 color='b',
                 label='Modalités modifiées')


rects2 = plt.bar(index + bar_width, modalites_intactes , bar_width,
                 alpha=opacity,
                 color='y',
                 label='Modalités non modifiées')

plt.ylim(0, 40000)
ax.axhline(y = modalites_modifiees[0])
ax.axhline(y = modalites_intactes[0])

plt.xlabel('Région')
plt.ylabel('Modalités modifiées')
plt.title('Nombre de modalités')
plt.xticks(index + bar_width, 'bla')
plt.legend()

plt.tight_layout()
plt.show()


# === On va maintenant comparer par variables le taux de remplacement ===

(avantages_kanonym[var[0]] != avantages[var[0]]).sum()

modif_par_var_1 = []
for variable in var :
    modif_par_var_1.append((avantages_kanonym[variable] != avantages[variable]).sum())

modif_par_var_2 = []
for variable in var :
    modif_par_var_2.append((result_insee[variable][result_insee['av_ou_conv']=='oui'] != avantages_total[variable][avantages_total['av_ou_conv']=='oui']).sum())


n_groups = len(var) # data to plot

fig, ax = plt.subplots(figsize=(15, 6)) # create plot


index = np.arange(n_groups)
bar_width = 0.35
opacity = 1

rects1 = plt.bar(index, modif_par_var_1, bar_width,
                 alpha=opacity,
                 color='b',
                 label='Séries brutes')


rects2 = plt.bar(index + bar_width, modif_par_var_2 , bar_width,
                 alpha=opacity,
                 color='y',
                 label='Séries avec données INSEE')

plt.ylim(0, 18000) #ax.axhline(y = modalites_modifiees[0]) #ax.axhline(y = taille_données_transparence[0])


plt.xlabel('Variable anonymisée')
plt.ylabel('Nombre de valeurs modifiées')
plt.title('Modification de valeurs')
plt.xticks(index + bar_width, var)
plt.legend()

plt.tight_layout()
plt.show()

