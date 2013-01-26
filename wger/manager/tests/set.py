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

import logging

from django.core.urlresolvers import reverse

from wger.manager.models import Set

from wger.manager.tests.testcase import WorkoutManagerTestCase

logger = logging.getLogger('workout_manager.custom')


class SetDeleteTestCase(WorkoutManagerTestCase):
    '''
    Tests deleting a set from a workout
    '''

    def delete_set(self, fail=True):
        '''
        Helper function to test deleting a set from a workout
        '''

        # Fetch the overview page
        count_before = Set.objects.count()
        response = self.client.get(reverse('wger.manager.views.delete_set', kwargs={'id': 3,
                                           'day_id': 5,
                                           'set_id': 3}))
        count_after = Set.objects.count()

        if fail:
            self.assertTrue(response.status_code in (302, 403))
            self.assertEqual(count_before, count_after)
        else:
            self.assertEqual(response.status_code, 302)
            self.assertEqual(count_before - 1, count_after)
            self.assertRaises(Set.DoesNotExist, Set.objects.get, pk=3)

    def test_delete_set_anonymous(self):
        '''
        Tests deleting a set from a workout as an anonymous user
        '''

        self.delete_set(fail=True)

    def test_delete_set_owner(self):
        '''
        Tests deleting a set from a workout as the owner user
        '''

        self.user_login('admin')
        self.delete_set(fail=True)

    def test_delete_set_other(self):
        '''
        Tests deleting a set from a workout as a logged user not owning the data
        '''

        self.user_login('test')
        self.delete_set(fail=False)
