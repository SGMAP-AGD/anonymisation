#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages
 

import anonymizer
 

setup(
 
    # le nom de votre bibliothèque, tel qu'il apparaitre sur pypi
    name='anonymizer',
 
    # la version du code
    version=anonymizer.__version__,
 

    packages=find_packages(),
 

    author="SGMAP-AGD",
 

    author_email="plbithorel@gmail.com",
 
    # Une description courte
    description="Module de k-anonymisation",
 

    long_description=open('README.md').read(),
 
    include_package_data=True,
 

    url='https://github.com/SGMAP-AGD/anonymisation',
 
    # Il est d'usage de mettre quelques metadata à propos de sa lib
    # Pour que les robots puissent facilement la classer.
    # La liste des marqueurs autorisées est longue:
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers.
    #
    # Il n'y a pas vraiment de règle pour le contenu. Chacun fait un peu
    # comme il le sent. Il y en a qui ne mettent rien.
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
 
 
    entry_points = {
        'console_scripts': [
            'local_agregation = anonymizer.anonymity:local_agregation',
            'get_k = anonymizer.anonymity:get_k',
        ],
    },
 
 
)
