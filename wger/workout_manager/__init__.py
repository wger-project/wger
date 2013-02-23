#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    :copyright: 2011, 2012 by OpenSlides team, see AUTHORS.
    :license: GNU GPL, see LICENSE for more details.
"""

VERSION = (1, 2, 0, 'alpha', 1)
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


def hg_version():
    import socket
    import os
    from os.path import realpath, join, dirname
    try:
        from mercurial import ui as hgui
        from mercurial.localrepo import localrepository
        from mercurial.node import short as shorthex
        from mercurial.error import RepoError
        nomercurial = False
    except ImportError:
        return 'unknown'

    os.environ['HGRCPATH'] = ''
    conts = realpath(join(dirname(__file__)))
    try:
        ui = hgui.ui()
        repository = localrepository(ui, join(conts, '..'))
        ctx = repository['.']
        if ctx.tags() and ctx.tags() != ['tip']:
            version = ' '.join(ctx.tags())
        else:
            version = '%(num)s:%(id)s' % {
                'num': ctx.rev(), 'id': shorthex(ctx.node())
            }
    except TypeError:
        version = 'unknown'
    except RepoError:
        return 0

    # This value defines the timeout for sockets in seconds.  Per default python
    # sockets do never timeout and as such we have blocking workers.
    # Socket timeouts are set globally within the whole application.
    # The value *must* be a floating point value.
    socket.setdefaulttimeout(10.0)

    return version
