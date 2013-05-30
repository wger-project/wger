# -*- coding: utf-8 -*-

# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

from wger.config.models import LanguageConfig

from wger.manager.tests.testcase import WorkoutManagerEditTestCase


class EditLanguageConfigTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a language config
    '''

    object_class = LanguageConfig
    url = 'config:languageconfig-edit'
    pk = 1
    data = {'show': False}
