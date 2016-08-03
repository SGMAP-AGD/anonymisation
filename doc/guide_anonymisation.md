# Guide pratique de l'anonymisation

L'anonymisation est un processus mis en oeuvre lors de certains traitements de données personnelles. Il vise, dans un jeu de donné publié, à empêcher de:

* Distinguer un individu.
* Lier des informations relatives à un individu.
* Inférer des informations concernant un individu.

L'anonymisation ne se limite pas à la suppression des champs identifiants d'un jeu de données, comme le nom ou l'adresse d'un individu. D'autres variables, qualifiées de réidentifiantes, peuvent être utilisées pour identifier un individu au sein d'un jeu de données. Il est donc nécessaire de mettre en oeuvre des techniques plus avancées d'anonymisation, comme la généralisation.

## Classement des variables

Une des première étapes du processus d'anonymisation consiste à classer les variables en 3 catégories:

* Variables identifiantes
* Variables quasi-identifiantes: 
* Variables sensibles

## Variables identifiantes

Les variables identifiantes sont obfusquées ou tout simplement retirées lors de l'anonymisation.
On parle alors de pseudonymisation une fois cette étape passée. Le jeu de données n'est à ce stade pas encore anonymis.

### Obfuscation

Parfois, certaines variables identifiantes ne doivent pas être retirées du jeu de données anonymisé. C'est par exemple le cas lorsque le jeu données servira à analyser des parcours utilisateur et qu'un identifiant individuel apparaitra plusieurs fois dans le jeu de données anonymisé. Il convient alors d'obfusquer cet identifiant pour ne pas le dévoiler tout en préservant son caractère particulier.

La méthode retenue dans ce cas est celle du hachage des champs concernés. Les champs concernés doivent être hachés en utilisant un algorithme issu de la famille SHA-2 ou SHA-3 http://csrc.nist.gov/publications/fips/fips180-4/fips-180-4.pdf, les plus robustes à l'heure actuelle. Ces fonctions sont disponibles dans toutes les blibliothèques cryptographiques des langages de programmation.

R: digest
Python: hashlib
SAS
Java


## Anonymisation par généralisation

Lors d'une anonymisation par aggrégation, les variables sont modifiées de telle sorte à rendre la ré-identification impossible. Ces modifications peuvent prendre plusieurs formes. On peut appliquer un changement d'échelle, en passant, par exemple, d'un code communal (75001) à un code départemental (75). On peut aussi fusionner plusieurs modalités, soit de façon générale (sur toute la base), soit de manière locale (seules les modalités des lignes qui posent problème seront modifiées). Exemple : deux lignes qui prennent comme code postal "75001" et "75014" prennent comme nouvelle modalité "75001 ou 75014".

## K-anonymat

## L-Diversité

## Mesurer la perte d'informations

ARTICLE 29 DATA PROTECTION WORKING PARTY
http://ec.europa.eu/justice/data-protection/article-29/documentation/opinion-recommendation/files/2014/wp216_en.pdf
