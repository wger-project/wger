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
from wger.manager.models import Day

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
        response = self.client.get(reverse('wger.manager.views.set.delete_set', kwargs={'pk': 3}))
        count_after = Set.objects.count()

        if fail:
            self.assertIn(response.status_code, (302, 403))
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


class TestSetOrderTestCase(WorkoutManagerTestCase):
    '''
    Tests that the order of the (existing) sets in a workout is preservead
    when adding new ones
    '''

    def add_set(self, set_ids):
        '''
        Helper function that adds a set to a day
        '''

        response = self.client.post(reverse('set-add', kwargs={'day_id': 5}),
                                    {'exercises': set_ids,
                                     'sets': 4})

        return response

    def get_order(self):
        '''
        Helper function that reads the order of the the sets in a day
        '''

        day = Day.objects.get(pk=5)
        order = ()

        for day_set in day.set_set.select_related():
            order += (day_set.id,)

        return order

    def test_set_order(self, logged_in=False):
        '''
        Helper function to test creating workouts
        '''

        # Add some sets and check the order
        self.user_login('test')
        orig = self.get_order()
        exercises = (1, 2, 3, 81, 84, 91, 111)

        for i in range(0, 7):
            self.add_set([exercises[i]])
            prev = self.get_order()
            orig += (i + 4,)
            self.assertEqual(orig, prev)
