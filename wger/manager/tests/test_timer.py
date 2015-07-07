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
import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.exercises.models import Exercise
from wger.manager.models import WorkoutSession
from wger.manager.models import Workout

logger = logging.getLogger(__name__)


class WorkoutTimerTestCase(WorkoutManagerTestCase):
    '''
    Tests the timer view (gym mode) for a workout day
    '''

    def test_timer_no_weight(self):
        '''
        Test the timer page when there are no saved weights
        '''

        # Fetch the timer page
        self.user_login('test')
        response = self.client.get(reverse('manager:workout:timer', kwargs={'day_pk': 5}))
        self.assertEqual(response.status_code, 200)

        # Check some of the steps
        step_list = response.context['step_list']
        step_list.reverse()

        current_step = step_list.pop()
        self.assertEqual(current_step['weight'], '')

    def timer(self, fail=True, pause_active=True, pause_seconds=90):
        '''
        Helper function
        '''

        # Fetch the timer page
        response = self.client.get(reverse('manager:workout:timer', kwargs={'day_pk': 2}))

        if fail:
            self.assertIn(response.status_code, (302, 404))
        else:
            self.assertEqual(response.status_code, 200)

            # Check some of the steps
            step_list = response.context['step_list']
            step_list.reverse()
            list_length = len(step_list)

            current_step = step_list.pop()
            self.assertEqual(current_step['exercise'], Exercise.objects.get(pk=2))
            self.assertEqual(current_step['reps'], 10)
            self.assertEqual(current_step['step_nr'], list_length - len(step_list))
            self.assertEqual(math.floor(current_step['step_percent']),
                             math.floor(current_step['step_nr'] * (100.0 / list_length)))
            self.assertEqual(current_step['type'], 'exercise')
            self.assertEqual(current_step['weight'], Decimal(15))

            if pause_active:
                current_step = step_list.pop()
                self.assertEqual(current_step['step_nr'], list_length - len(step_list))
                self.assertEqual(math.floor(current_step['step_percent']),
                                 math.floor(current_step['step_nr'] * (100.0 / list_length)))
                self.assertEqual(current_step['time'], pause_seconds)
                self.assertEqual(current_step['type'], 'pause')

            current_step = step_list.pop()
            self.assertEqual(current_step['exercise'], Exercise.objects.get(pk=2))
            self.assertEqual(current_step['reps'], 10)
            self.assertEqual(current_step['step_nr'], list_length - len(step_list))
            self.assertEqual(math.floor(current_step['step_percent']),
                             math.floor(current_step['step_nr'] * (100.0 / list_length)))
            self.assertEqual(current_step['type'], 'exercise')
            self.assertEqual(current_step['weight'], Decimal(15))

            if pause_active:
                current_step = step_list.pop()
                self.assertEqual(current_step['step_nr'], list_length - len(step_list))
                self.assertEqual(math.floor(current_step['step_percent']),
                                 math.floor(current_step['step_nr'] * (100.0 / list_length)))
                self.assertEqual(current_step['time'], pause_seconds)
                self.assertEqual(current_step['type'], 'pause')

            current_step = step_list.pop()
            self.assertEqual(current_step['exercise'], Exercise.objects.get(pk=2))
            self.assertEqual(current_step['reps'], 10)
            self.assertEqual(current_step['step_nr'], list_length - len(step_list))
            self.assertEqual(math.floor(current_step['step_percent']),
                             math.floor(current_step['step_nr'] * (100.0 / list_length)))
            self.assertEqual(current_step['type'], 'exercise')
            self.assertEqual(current_step['weight'], Decimal(15))

    def test_timer_anonymous(self):
        '''
        Tests the timer as an anonymous user
        '''

        self.timer(fail=True)

    def test_timer_owner(self):
        '''
        Tests the timer as the owner user
        '''
        self.user_login('admin')
        self.timer(fail=False)

    def test_timer_owner_custom_pause(self):
        '''
        Tests the timer as the owner, use custom time
        '''
        self.user_login('admin')
        user = User.objects.get(username='admin')
        user.userprofile.timer_pause = 120
        user.userprofile.save()
        self.timer(fail=False, pause_seconds=120)

    def test_timer_owner_no_pause(self):
        '''
        Tests the timer as the owner, deactivate timer
        '''
        self.user_login('admin')
        user = User.objects.get(username='admin')
        user.userprofile.timer_active = False
        user.userprofile.save()
        self.timer(fail=False, pause_active=False)

    def test_timer_other(self):
        '''
        Tests the timer as a logged user not owning the data
        '''

        self.user_login('test')
        self.timer(fail=True)


class WorkoutTimerWorkoutSessionTestCase(WorkoutManagerTestCase):
    '''
    Other tests
    '''

    def test_workout_session(self):
        '''
        Tests that the correct urls and forms for workout session is passed
        '''
        WorkoutSession.objects.all().delete()
        self.user_login('test')

        today = datetime.date.today()
        response = self.client.get(reverse('manager:workout:timer', kwargs={'day_pk': 5}))
        self.assertEqual(response.context['form_action'],
                         reverse('manager:session:add', kwargs={'workout_pk': 3,
                                                                'year': today.year,
                                                                'month': today.month,
                                                                'day': today.day}))

        session = WorkoutSession()
        session.user = User.objects.get(username='test')
        session.workout = Workout.objects.get(pk=2)
        session.date = datetime.date.today()
        session.notes = 'Something here'
        session.impression = '2'
        session.time_start = datetime.time(11, 00)
        session.time_end = datetime.time(13, 00)
        session.save()

        response = self.client.get(reverse('manager:workout:timer', kwargs={'day_pk': 5}))
        self.assertEqual(response.context['form_action'],
                         reverse('manager:session:edit', kwargs={'pk': session.pk}))
