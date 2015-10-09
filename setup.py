#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup script for wger Workout manager

    :copyright: 2011, 2012 by OpenSlides team, see AUTHORS.
    :license: GNU GPL, see LICENSE for more details.
"""

from setuptools import (
    setup,
    find_packages
)
from wger import get_version


with open('README.rst') as readme:
    long_description = readme.read()

with open('requirements.txt') as requirements_production:
    install_requires = requirements_production.readlines()

setup(
    name='wger',
    description='FLOSS workout, fitness and weight manager/tracker written with Django',
    long_description=long_description,
    version=get_version(),
    url='https://wger.de',
    author='Roland Geider',
    author_email='roland@geider.net',
    license='AGPL3+',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    classifiers=[
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Other Audience',
        'Framework :: Django',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'wger = wger.__main__:main',
        ],
    },
)
