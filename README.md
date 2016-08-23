# anonymisation

Le répertoire anonymisation fournit une méthode, des outils et des références sur l'anonymisation des données à caractère personnel.

## Objectifs et usages  

Ce projet  a pour objectif : 
+ D'introduire l'utilisateur et le producteur de données aux enjeux de l'anonymisation, d'un point de vue juridique, scientifique et technique.
+ De construire un espace collaboratif autour de ce thème.
+ De proposer une méthode robuste et testée de k-anonymisation de données.  

## Contenu  

Plus précisément, cet espace est constitué :  
* D'un [wiki](https://github.com/SGMAP-AGD/anonymisation/wiki) qui détaille la démarche, les outils](https://github.com/SGMAP-AGD/anonymisation/wiki/Les-outils et [l'exemple de Transparence Santé](https://github.com/SGMAP-AGD/anonymisation/wiki/Transparence-Sant%C3%A9).
* Du code qui formalise le traitement de k-anonymisation.
* De deux exemples d'application à Transparence Santé et à Equides.


## Données à télécharger

Les données exploitées pour tester notre algorithme peuvent être téléchargées aux endroits suivants : 
* [Transparence Santé](https://www.data.gouv.fr/fr/datasets/transparence-sante-1/) (data.gouv.fr)
* [Données INSEE pour l'enrichissement des données](http://www.insee.fr/fr/themes/detail.asp?reg_id=99&ref_id=equip-serv-medical-para) (INSEE)
* [Fichier des équidés](https://www.data.gouv.fr/fr/datasets/fichier-des-equides/) (data.gouv.fr)

## Installation

  pip install anonymizer  
  
Pour l'application des exemples, pensez à bien renseigner vos répertoires de travail dans chacun des fichiers config-anonymizer.ini respectifs. Des exemples (config_anonymizer.ini.exemple) sont donnés.

## Qui sommes-nous ?
Ce projet est développé par [l'équipe de l'Administrateur Général des Données (AGD)](http://agd.data.gouv.fr/), en collaboration avec toutes les bonnes volontés et les producteurs de données à caractère personnel. [Le forum d'Etalab](https://forum.etalab.gouv.fr/) est aussi ouvert à toute question, remarque ou suggestion. [Une consultation](https://forum.etalab.gouv.fr/search?q=anonymisation) sur les logiciels d'anonymisation y a notamment été initiée.
