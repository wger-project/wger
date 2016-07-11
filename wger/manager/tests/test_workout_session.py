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

import datetime

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse, reverse_lazy

from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WorkoutManagerAddTestCase
from wger.core.tests.base_testcase import WorkoutManagerEditTestCase
from wger.core.tests.base_testcase import WorkoutManagerTestCase, WorkoutManagerDeleteTestCase
from wger.manager.models import Workout, WorkoutSession, WorkoutLog
from wger.utils.cache import cache_mapper


'''
Tests for workout sessions
'''


class AddWorkoutSessionTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a workout session
    '''

    object_class = WorkoutSession
    url = reverse_lazy('manager:session:add', kwargs={'workout_pk': 1,
                                                      'year': datetime.date.today().year,
                                                      'month': datetime.date.today().month,
                                                      'day': datetime.date.today().day})
    data = {
        'user': 1,
        'workout': 1,
        'date': datetime.date.today(),
        'notes': 'Some interesting and deep insights',
        'impression': '3',
        'time_start': datetime.time(10, 0),
        'time_end': datetime.time(13, 0)
    }


class EditWorkoutSessionTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a workout session
    '''

    object_class = WorkoutSession
    url = 'manager:session:edit'
    pk = 3
    data = {
        'user': 1,
        'workout': 2,
        'date': datetime.date(2014, 1, 30),
        'notes': 'My new insights',
        'impression': '3',
        'time_start': datetime.time(10, 0),
        'time_end': datetime.time(13, 0)
    }


class WorkoutSessionModelTestCase(WorkoutManagerTestCase):
    '''
    Tests other functionality from the model
    '''

    def test_unicode(self):
        '''
        Test the unicode representation
        '''

        session = WorkoutSession()
        session.workout = Workout.objects.get(pk=1)
        session.date = datetime.date.today()
        self.assertEqual('{0}'.format(session),
                         u'{0} - {1}'.format(Workout.objects.get(pk=1), datetime.date.today()))


class DeleteTestWorkoutTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a Workout
    '''

    object_class = WorkoutSession
    url = 'manager:session:delete'
    pk = 3


class WorkoutSessionDeleteLogsTestCase(WorkoutManagerTestCase):
    '''
    Tests that deleting a session can also delete all weight logs
    '''

    def test_delete_logs(self):
        self.user_login('admin')

        session = WorkoutSession.objects.get(pk=1)
        count_before = WorkoutLog.objects.filter(user__username=session.user.username,
                                                 date=session.date).count()
        self.assertEqual(count_before, 1)

        response = self.client.post(reverse('manager:session:delete',
                                            kwargs={'pk': 1, 'logs': 'logs'}))
        self.assertEqual(response.status_code, 302)
        count_after = WorkoutLog.objects.filter(user__username=session.user.username,
                                                date=session.date).count()
        self.assertEqual(count_after, 0)


class WorkoutSessionTestCase(WorkoutManagerTestCase):
    '''
    Tests other workout session methods
    '''

    def test_model_validation(self):
        '''
        Tests the custom clean() method
        '''
        self.user_login('admin')

        # Values OK
        session = WorkoutSession()
        session.workout = Workout.objects.get(pk=2)
        session.user = User.objects.get(pk=1)
        session.date = datetime.date.today()
        session.time_start = datetime.time(12, 0)
        session.time_end = datetime.time(13, 0)
        session.impression = '3'
        session.notes = 'Some notes here'
        self.assertFalse(session.full_clean())

        # No start or end times, also OK
        session.time_start = None
        session.time_end = None
        self.assertFalse(session.full_clean())

        # Start time but not end time
        session.time_start = datetime.time(17, 0)
        session.time_end = None
        self.assertRaises(ValidationError, session.full_clean)

        # No start time but end time
        session.time_start = None
        session.time_end = datetime.time(17, 0)
        self.assertRaises(ValidationError, session.full_clean)

        # Start time after end time
        session.time_start = datetime.time(17, 0)
        session.time_end = datetime.time(13, 0)
        self.assertRaises(ValidationError, session.full_clean)


class WorkoutLogCacheTestCase(WorkoutManagerTestCase):
    '''
    Workout log cache test case
    '''

    def test_cache_update_session(self):
        '''
        Test that the caches are cleared when updating a workout session
        '''
        log_hash = hash((1, 2012, 10))
        self.user_login('admin')
        self.client.get(reverse('manager:workout:calendar', kwargs={'year': 2012, 'month': 10}))

        session = WorkoutSession.objects.get(pk=1)
        session.notes = 'Lorem ipsum'
        session.save()

        self.assertFalse(cache.get(cache_mapper.get_workout_log_list(log_hash)))

    def test_cache_update_session_2(self):
        '''
        Test that the caches are only cleared for a the session's month
        '''
        log_hash = hash((1, 2012, 10))
        self.user_login('admin')
        self.client.get(reverse('manager:workout:calendar', kwargs={'year': 2012, 'month': 10}))

        # Session is from 2014
        session = WorkoutSession.objects.get(pk=2)
        session.notes = 'Lorem ipsum'
        session.save()

        self.assertTrue(cache.get(cache_mapper.get_workout_log_list(log_hash)))

    def test_cache_delete_session(self):
        '''
        Test that the caches are cleared when deleting a workout session
        '''
        log_hash = hash((1, 2012, 10))
        self.user_login('admin')
        self.client.get(reverse('manager:workout:calendar', kwargs={'year': 2012, 'month': 10}))

        session = WorkoutSession.objects.get(pk=1)
        session.delete()

        self.assertFalse(cache.get(cache_mapper.get_workout_log_list(log_hash)))

    def test_cache_delete_session_2(self):
        '''
        Test that the caches are only cleared for a the session's month
        '''
        log_hash = hash((1, 2012, 10))
        self.user_login('admin')
        self.client.get(reverse('manager:workout:calendar', kwargs={'year': 2012, 'month': 10}))

        session = WorkoutSession.objects.get(pk=2)
        session.delete()

        self.assertTrue(cache.get(cache_mapper.get_workout_log_list(log_hash)))


class WorkoutSessionApiTestCase(api_base_test.ApiBaseResourceTestCase):
    '''
    Tests the workout overview resource
    '''
    pk = 4
    resource = WorkoutSession
    private_resource = True
    data = {'workout': 3,
            'date': datetime.date(2014, 1, 30),
            'notes': 'My new insights',
            'impression': '3',
            'time_start': datetime.time(10, 0),
            'time_end': datetime.time(13, 0)}
