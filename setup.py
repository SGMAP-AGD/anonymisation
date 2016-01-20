#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import anonymizer

setup(
    name="anonymizer",
    version="0.1",
    author="AGD Team",
    description="Tools to anonimize a dataset",
    long_description=open('README.md').read(),
    packages=find_packages(),
    url="https://github.com/SGMAP-AGD/anonymisatio",
    install_requires=[
                      'pandas',
                      ]
)
