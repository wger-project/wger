#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright: 2011, 2012 by OpenSlides team, see AUTHORS.
:license: GNU GPL, see LICENSE for more details.
"""

# Local
from .celery_configuration import app


MIN_APP_VERSION = (1, 7, 4, 'final', 1)

VERSION = (2, 3, 0, 'alpha', 3)
RELEASE = True


def get_version(version=None, release=None):
    """Derives a PEP386-compliant version number from VERSION."""

    if version is None:
        version = VERSION
    if release is None:
        release = RELEASE
    assert len(version) == 5
    assert version[3] in ('alpha', 'beta', 'rc', 'final')

    # Now build the two parts of the version number:
    # main = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|c}N - for alpha, beta and rc releases

    # Always use all three parts, otherwise we might get problems in the version
    # parser on the flutter side of things
    main_parts = 3
    main = '.'.join(str(x) for x in version[:main_parts])

    if version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'rc'}
        sub = mapping[version[3]] + str(version[4])
    else:
        sub = ''
    if not release:
        sub += '.dev0'

    return main + sub
