# -*- coding: utf-8 -*-

# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Standard Library
import os
import sys

# Third Party
from invoke import run


"""
This simple wrapper script is used as a console entry point in the packaged
version of the application. It simply redirects all arguments to the invoke
command, which does all the work.
"""

invoke_cmd = 'invoke '


def main():
    # Change the working directory so that invoke can find the tasks file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    args = sys.argv[1:]
    if len(args):
        run(invoke_cmd + ' '.join(args), pty=True)
    else:
        run(invoke_cmd + '--list')


if __name__ == '__main__':
    main()
