#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup script for wger Workout manager

    :copyright: 2011, 2012 by OpenSlides team, see AUTHORS.
    :license: GNU GPL, see LICENSE for more details.
"""

# Third Party
from setuptools import (
    find_packages,
    setup
)

# wger
from wger import get_version


with open('README.rst') as readme:
    long_description = readme.read()

with open('requirements.txt') as requirements_production:
    install_requires = requirements_production.readlines()

setup(
    name='wger',
    description='FLOSS workout, fitness and weight manager/tracker written with Django',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    version=get_version(),
    url='https://github.com/wger-project',
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    # Copy-pasting here the requirement since the git+git:// syntax is not
    # supported here. After the release, django-user-agent will be removed
    # and this can be replaced again with: install_requires=install_requires,
    install_requires=[
            "wheel",
            "bleach>=3.1,<3.2",
            "django-bootstrap-breadcrumbs==0.9.1",
            "django-bower==5.2.0",
            "django-formtools>=2.0,<3.0",
            "django-recaptcha==2.0.6",
            "Django>=3.0,<3.1",
            "django_compressor>=2.4,<2.5",
            "django_extensions>=2.1",
            "django-sortedm2m>=3.0,<3.1",
            "django-storages>=1.7",
            "easy-thumbnails>=2.7,<2.8",
            "icalendar==4.0.3",
            "invoke==0.17",
            "pillow>=6.2,<6.3",
            "python-mimeparse",
            "reportlab==3.5.21",
            "matplotlib>=3.1",
            "requests",
            "setuptools>=18.5",
            "sphinx",

            "django-cors-headers>=3.0",
            "django-filter==2.1.0",
            "django-tastypie>=0.14,<.0.15",
            "djangorestframework>=3.11,<3.12",
            "django-user_agents"
        ],
    entry_points={
        'console_scripts': [
            'wger = wger.__main__:main',
        ],
    },
)
