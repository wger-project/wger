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
import math

from django.core.urlresolvers import reverse
from wger.exercises.models import Exercise

from wger.manager.tests.testcase import WorkoutManagerTestCase

logger = logging.getLogger('wger.custom')


class WorkoutTimerTestCase(WorkoutManagerTestCase):
    '''
    Tests the timer view (gym mode) for a workout day
    '''

    def timer(self, fail=True):
        '''
        Helper function
        '''

        # Fetch the timer page
        response = self.client.get(reverse('workout-timer', kwargs={'day_pk': 2}))

        if fail:
            self.assertEqual(response.status_code, 404)
        else:
            self.assertEqual(response.status_code, 200)

            # Check some of the steps
            step_list = response.context['step_list']

            self.assertEqual(step_list[0]['exercise'], Exercise.objects.get(pk=2))
            self.assertEqual(step_list[0]['reps'], 10)
            self.assertEqual(step_list[0]['step_nr'], 1)
            self.assertEqual(math.floor(step_list[0]['step_percent']), 14)
            self.assertEqual(step_list[0]['type'], 'exercise')
            self.assertEqual(step_list[0]['weight'], '')

            self.assertEqual(step_list[1]['step_nr'], 2)
            self.assertEqual(math.floor(step_list[1]['step_percent']), 28)
            self.assertEqual(step_list[1]['time'], 90)
            self.assertEqual(step_list[1]['type'], 'pause')

            self.assertEqual(step_list[2]['exercise'], Exercise.objects.get(pk=2))
            self.assertEqual(step_list[2]['reps'], 10)
            self.assertEqual(step_list[2]['step_nr'], 3)
            self.assertEqual(math.floor(step_list[2]['step_percent']), 42)
            self.assertEqual(step_list[2]['type'], 'exercise')
            self.assertEqual(step_list[2]['weight'], '')

            self.assertEqual(step_list[3]['step_nr'], 4)
            self.assertEqual(math.floor(step_list[3]['step_percent']), 57)
            self.assertEqual(step_list[3]['time'], 90)
            self.assertEqual(step_list[3]['type'], 'pause')

            self.assertEqual(step_list[4]['exercise'], Exercise.objects.get(pk=2))
            self.assertEqual(step_list[4]['reps'], 10)
            self.assertEqual(step_list[4]['step_nr'], 5)
            self.assertEqual(math.floor(step_list[4]['step_percent']), 71)
            self.assertEqual(step_list[4]['type'], 'exercise')
            self.assertEqual(step_list[4]['weight'], '')

    def test_timer_anonymous(self):
        '''
        Tests the timer as an anonymous user
        '''

        self.timer(fail=True)

    def test_timer_owner(self):
        '''
        Tests the timer as the owner user
        '''

        self.user_login('test')
        self.timer(fail=True)

    def test_timer_other(self):
        '''
        Tests the timer as a logged user not owning the data
        '''

        self.user_login('admin')
        self.timer(fail=False)
