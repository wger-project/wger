#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup script for wger Workout manager

    :copyright: 2011, 2012 by OpenSlides team, see AUTHORS.
    :license: GNU GPL, see LICENSE for more details.
"""

# for python 2.5 support
from __future__ import with_statement

from setuptools import setup
from setuptools import find_packages
from wger import get_version


with open('README.rst') as readme:
    long_description = readme.read()

setup(
    name='wger',
    description='Workout and exercise manager',
    long_description=long_description,
    version=get_version(),
    url='http://wger.de',
    author='Roland Geider',
    author_email='roland@wger.de',
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
        'Programming Language :: Python',
    ],
    setup_requires=[
        'versiontools >= 1.6',
    ],
    install_requires=[
        'django >= 1.5.3',
        'reportlab',
        'django-browserid == 0.9',
        'django-recaptcha',
        'django_mobile',
        'django-discover-runner',
        'pep8',
        'bleach',
        'south < 2.0',
        'django-tastypie',
        'python-mimeparse'
    ],
    entry_points={
        'console_scripts': [
            'wger = wger.main:main',
        ],
    },
)
