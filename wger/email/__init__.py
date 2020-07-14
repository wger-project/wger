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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# wger
from wger import get_version


VERSION = get_version()
default_app_config = 'wger.email.apps.Config'


def message_from_file(fp, *args, **kws):
    """
    Dummy method. Needed because this email app clashes with python's own
    "email" package and bad things happen sometimes. See the note in tasks.py.

    https://travis-ci.org/github/wger-project/wger/jobs/708008236
    """
    return ":("
