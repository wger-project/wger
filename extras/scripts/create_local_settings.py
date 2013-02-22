#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

script_path = os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.join(script_path, '..', '..'))

from wger.main import create_settings

if __name__ == "__main__":
    cwd = os.getcwd()
    create_settings(os.path.join(cwd, 'settings.py'),
                    os.path.join(cwd, 'database.sqlite'))
