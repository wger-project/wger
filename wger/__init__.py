#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    :copyright: 2011, 2012 by OpenSlides team, see AUTHORS.
    :license: GNU GPL, see LICENSE for more details.
"""

VERSION = (1, 8, 0, 'alpha', 3)
RELEASE = False


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

    main_parts = 2 if version[2] == 0 else 3
    main = '.'.join(str(x) for x in version[:main_parts])

    if version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'rc'}
        sub = mapping[version[3]] + str(version[4])
    else:
        sub = ''
    if not release:
        sub += '-dev'

    return main + sub
