# -*- coding: utf-8 *-*

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


from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.utils.helpers import smart_capitalize


class CapitalizerTestCase(WorkoutManagerTestCase):
    '''
    Tests the "intelligent" capitalizer
    '''

    def test_capitalizer(self):
        '''
        Tests different combinations of input strings
        '''
        self.assertEqual(smart_capitalize("some long words"), "Some Long Words")
        self.assertEqual(smart_capitalize("Here a short one"), "Here a Short One")
        self.assertEqual(smart_capitalize("meine gym AG"), "Meine Gym AG")
        self.assertEqual(smart_capitalize("ßpecial case"), "ßpecial Case")
        self.assertEqual(smart_capitalize("fIRST lettER only"), "FIRST LettER Only")
