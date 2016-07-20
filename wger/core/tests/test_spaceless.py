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

import logging

from django.template import Template, Context

from wger.core.tests.base_testcase import WorkoutManagerTestCase

logger = logging.getLogger(__name__)


class SpacelessTestCase(WorkoutManagerTestCase):
    '''
    Tests the custom spaceless template tag
    '''

    def test_spaceless(self):
        '''
        Tests the custom spaceless template tag
        '''
        t = Template('{% load wger_extras %}'
                     '{% spaceless_config %}<p>A text</p>   <p>more</p>{% endspaceless_config %}')
        context = Context()

        with self.settings(WGER_SETTINGS={'REMOVE_WHITESPACE': True}):
            self.assertEqual(t.render(context), '<p>A text</p><p>more</p>')

        with self.settings(WGER_SETTINGS={'REMOVE_WHITESPACE': False}):
            self.assertEqual(t.render(context), '<p>A text</p>   <p>more</p>')
