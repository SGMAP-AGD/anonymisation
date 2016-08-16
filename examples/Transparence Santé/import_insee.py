import pandas as pd

# Nouvelle fonction pour expand la base insee, afin de pouvoir l'intégrer ensuite à la base transparence

# Prend en arguments :
# - les données INSEE sous forme de dataframe, groupées par département
# - annuaire de correspondances entre les professions INSEE et les professions Transparence Santé

def expand_insee (df_groupby_dept, annuaire, avantages) :
    effectif_sante_dept = df_groupby_dept.sum()
    départements = effectif_sante_dept.index.tolist()
    pro = effectif_sante_dept.columns.tolist()
    expand_insee = pd.DataFrame()
    ligne = []

    for départmt in départements :
        for profession in pro :
            if annuaire[profession][0] == 'benef_specialite_code' :
                ligne = ['non renseigné',
                         '[PRS]', 'Médecin', '[FR]', '[DR]', annuaire[profession][1], '[RPPS]',
                         'non renseigné', 'non renseigné', 'non renseigné', départmt, 'non renseigné',
                         'non renseigné']

            elif annuaire[profession][0] == 'qualite' :
                ligne = ['non renseigné', 
                         '[PRS]', annuaire[profession][1], '[FR]', 'non renseigné', 'non renseigné', 'non renseigné',
                         'non renseigné', 'non renseigné', 'non renseigné', départmt, 'non renseigné',
                         'non renseigné']

            nombre_total = effectif_sante_dept.loc[départmt, profession]
            nombre_déjà_présent = len(avantages[(avantages['benef_dept']==départmt)&(avantages[annuaire[profession][0]]==annuaire[profession][1])])
            nombre_ajoutés = nombre_total - nombre_déjà_présent

            expand_insee = pd.concat([expand_insee, pd.DataFrame(nombre_ajoutés*[ligne])])

    return(expand_insee)


# Fonction pour calculer le nombre de modifications apportées
# Arguments :
# - Result : dataframe, anonymisée
# - Base : dataframe brute, intput de l'anonymisation
# - insee = 'oui' ou insee = 'non' : la base inclut les données INSEE (oui) ou pas (non)
def nbre_modif (result, base, insee = 'non'):
    if insee == 'oui' :
        nombre_modifications = (result[result['ligne_type']=='[A]'] != base[base['ligne_type']=='[A]']).sum().sum()
    else :
        nombre_modifications = (result != base).sum().sum()
    return(nombre_modifications)
