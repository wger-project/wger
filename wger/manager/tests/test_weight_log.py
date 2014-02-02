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
import datetime
from django.contrib.auth.models import User

from django.core.urlresolvers import reverse, reverse_lazy

from wger.exercises.models import Exercise
from wger.manager.models import WorkoutLog
from wger.manager.models import Workout
from wger.manager.models import WorkoutSession

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase
from wger.manager.tests.testcase import ApiBaseResourceTestCase

logger = logging.getLogger('wger.custom')


class WeightLogOverviewAddTestCase(WorkoutManagerTestCase):
    '''
    Tests the weight log functionality
    '''

    def add_weight_log(self, fail=True):
        '''
        Helper function to test adding weight log entries
        '''

        # Fetch the overview page
        response = self.client.get(reverse('workout-log', kwargs={'pk': 1}))

        if fail:
            # Logged out users get a 302 redirect to login page
            # Users not owning the workout, a 403, forbidden
            self.assertTrue(response.status_code in (302, 403))
        else:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['active_tab'], 'workout')
            self.assertEqual(response.context['workout'].id, 1)

        # Open the log entry page
        response = self.client.get(reverse('day-log', kwargs={'pk': 1}))
        if fail:
            self.assertTrue(response.status_code in (302, 403))
        else:
            self.assertEqual(response.status_code, 200)

        # Add new log entries
        count_before = WorkoutLog.objects.count()
        response = self.client.post(reverse('day-log', kwargs={'pk': 1}),
                                    {'date': '2012-01-01',
                                     'notes': 'My cool impression',
                                     'impression': '3',
                                     'time_start': datetime.time(10, 0),
                                     'time_end': datetime.time(12, 0),
                                     'form-0-reps': 10,
                                     'form-0-weight': 10,
                                     'form-TOTAL_FORMS': 3,
                                     'form-INITIAL_FORMS': 0,
                                     'form-MAX-NUM_FORMS': 3
                                     })

        count_after = WorkoutLog.objects.count()

        # Logged out users get a 302 redirect to login page
        # Users not owning the workout, a 403, forbidden
        if fail:
            self.assertTrue(response.status_code in (302, 403))
            self.assertEqual(count_before, count_after)
        else:
            self.assertEqual(response.status_code, 302)
            self.assertGreater(count_after, count_before)

    def test_add_weight_log_anonymous(self):
        '''
        Tests adding weight log entries as an anonymous user
        '''

        self.add_weight_log(fail=True)

    def test_add_weight_log_owner(self):
        '''
        Tests adding weight log entries as the owner user
        '''

        self.user_login('admin')
        self.add_weight_log(fail=False)

    def test_add_weight_log_other(self):
        '''
        Tests adding weight log entries as a logged user not owning the data
        '''

        self.user_login('test')
        self.add_weight_log(fail=True)


class WeightlogTestCase(WorkoutManagerTestCase):
    '''
    Tests other model methods
    '''

    def test_get_workout_session(self):
        '''
        Test the get_workout_session method
        '''

        user1 = User.objects.get(pk=1)
        user2 = User.objects.get(pk=2)
        workout1 = Workout.objects.get(pk=2)
        workout2 = Workout.objects.get(pk=2)

        WorkoutLog.objects.all().delete()
        l = WorkoutLog()
        l.user = user1
        l.date = datetime.date(2014, 01, 05)
        l.exercise = Exercise.objects.get(pk=1)
        l.workout = workout1
        l.weight = 10
        l.reps = 10
        l.save()

        session1 = WorkoutSession()
        session1.user = user1
        session1.workout = workout1
        session1.notes = 'Something here'
        session1.impression = '3'
        session1.date = datetime.date(2014, 01, 05)
        session1.save()

        session2 = WorkoutSession()
        session2.user = user1
        session2.workout = workout1
        session2.notes = 'Something else here'
        session2.impression = '1'
        session2.date = datetime.date(2014, 01, 01)
        session2.save()

        session3 = WorkoutSession()
        session3.user = user2
        session3.workout = workout2
        session3.notes = 'The notes here'
        session3.impression = '2'
        session3.date = datetime.date(2014, 01, 05)
        session3.save()

        self.assertEqual(l.get_workout_session(), session1)


class WeightLogAddTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a WorkoutLog
    '''

    object_class = WorkoutLog
    url = reverse_lazy('workout-log-add', kwargs={'workout_pk': 1})
    pk = 6
    data = {'reps': 10,
            'weight': 120.5,
            'date': datetime.date.today(),
            'exercise': 1}


class WeightLogEntryEditTestCase(WorkoutManagerTestCase):
    '''
    Tests editing individual weight log entries
    '''

    def edit_log_entry(self, fail=True):
        '''
        Helper function to test edit log entries
        '''

        response = self.client.get(reverse('workout-log-edit', kwargs={'pk': 1}))
        if fail:
            self.assertTrue(response.status_code in (302, 403))

        else:
            self.assertEqual(response.status_code, 200)

        date_before = WorkoutLog.objects.get(pk=1).date
        response = self.client.post(reverse('workout-log-edit', kwargs={'pk': 1}),
                                    {'date': '2012-01-01',
                                     'reps': 10,
                                     'weight': 10,
                                     })

        date_after = WorkoutLog.objects.get(pk=1).date

        if fail:
            # Logged out users get a 302 redirect to login page
            # Users not owning the workout, a 403, forbidden
            self.assertTrue(response.status_code in (302, 403))
            self.assertEqual(date_before, date_after)

        else:
            self.assertEqual(response.status_code, 302)
            self.assertEqual(date_after, datetime.date(2012, 1, 1))

    def test_edit_log_entry_anonymous(self):
        '''
        Tests editing a weight log entries as an anonymous user
        '''

        self.edit_log_entry(fail=True)

    def test_edit_log_entry_owner(self):
        '''
        Tests editing a weight log entries as the owner user
        '''

        self.user_login('admin')
        self.edit_log_entry(fail=False)

    def test_edit_log_entry_other(self):
        '''
        Tests editing a weight log entries as a logged user not owning the data
        '''

        self.user_login('test')
        self.edit_log_entry(fail=True)


class WorkoutLogApiTestCase(ApiBaseResourceTestCase):
    '''
    Tests the workout log overview resource
    '''
    resource = 'workoutlog'
    resource_updatable = False


class WorkoutLogDetailApiTestCase(ApiBaseResourceTestCase):
    '''
    Tests accessing a specific workoutlog
    '''
    resource = 'workoutlog/5'
