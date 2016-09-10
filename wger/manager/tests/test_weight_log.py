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
import logging

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse, reverse_lazy

from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WorkoutManagerDeleteTestCase
from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.exercises.models import Exercise
from wger.manager.models import Workout
from wger.manager.models import WorkoutLog
from wger.manager.models import WorkoutSession
from wger.utils.cache import cache_mapper

logger = logging.getLogger(__name__)


class WorkoutLogShareButtonTestCase(WorkoutManagerTestCase):
    '''
    Test that the share button is correctly displayed and hidden
    '''

    def test_share_button(self):
        url = reverse('manager:log:log', kwargs={'pk': 1})

        response = self.client.get(url)
        self.assertFalse(response.context['show_shariff'])

        self.user_login('admin')
        response = self.client.get(url)
        self.assertTrue(response.context['show_shariff'])

        self.user_login('test')
        response = self.client.get(url)
        self.assertFalse(response.context['show_shariff'])


class WeightLogAccessTestCase(WorkoutManagerTestCase):
    '''
    Test accessing the weight log page
    '''

    def test_access_shared(self):
        '''
        Test accessing the URL of a shared weight log
        '''
        url = reverse('manager:log:log', kwargs={'pk': 1})

        self.user_login('admin')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.user_login('test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.user_logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_access_not_shared(self):
        '''
        Test accessing the URL of a private weight log
        '''
        url = reverse('manager:log:log', kwargs={'pk': 3})

        self.user_login('admin')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.user_login('test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.user_logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


class CalendarShareButtonTestCase(WorkoutManagerTestCase):
    '''
    Test that the share button is correctly displayed and hidden
    '''

    def test_share_button(self):
        url = reverse('manager:workout:calendar', kwargs={'username': 'admin'})

        response = self.client.get(url)
        self.assertFalse(response.context['show_shariff'])

        self.user_login('admin')
        response = self.client.get(url)
        self.assertTrue(response.context['show_shariff'])

        self.user_login('test')
        response = self.client.get(url)
        self.assertFalse(response.context['show_shariff'])


class CalendarAccessTestCase(WorkoutManagerTestCase):
    '''
    Test accessing the calendar page
    '''

    def test_access_shared(self):
        '''
        Test accessing the URL of a shared calendar page
        '''
        url = reverse('manager:workout:calendar', kwargs={'username': 'admin'})

        self.user_login('admin')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.user_login('test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.user_logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_access_not_shared(self):
        '''
        Test accessing the URL of a unshared calendar page
        '''
        url = reverse('manager:workout:calendar', kwargs={'username': 'test'})

        self.user_login('admin')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        self.user_login('test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.user_logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class WeightLogOverviewAddTestCase(WorkoutManagerTestCase):
    '''
    Tests the weight log functionality
    '''

    def add_weight_log(self, fail=True):
        '''
        Helper function to test adding weight log entries
        '''

        # Fetch the overview page
        response = self.client.get(reverse('manager:log:log', kwargs={'pk': 1}))

        # All access OK, since user 1 has ro_access = True
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['active_tab'], 'workout')
        self.assertEqual(response.context['workout'].id, 1)

        # Open the log entry page
        response = self.client.get(reverse('manager:day:log', kwargs={'pk': 1}))
        if fail:
            self.assertIn(response.status_code, (302, 403))
        else:
            self.assertEqual(response.status_code, 200)

        # Add new log entries
        count_before = WorkoutLog.objects.count()
        response = self.client.post(reverse('manager:day:log', kwargs={'pk': 1}),
                                    {'date': '2012-01-01',
                                     'notes': 'My cool impression',
                                     'impression': '3',
                                     'time_start': datetime.time(10, 0),
                                     'time_end': datetime.time(12, 0),
                                     'form-0-reps': 10,
                                     'form-0-repetition_unit': 1,
                                     'form-0-weight': 10,
                                     'form-0-weight_unit': 1,
                                     'form-1-reps': 10,
                                     'form-1-repetition_unit': 1,
                                     'form-1-weight': 10,
                                     'form-1-weight_unit': 1,
                                     'form-TOTAL_FORMS': 3,
                                     'form-INITIAL_FORMS': 0,
                                     'form-MAX-NUM_FORMS': 3
                                     })
        count_after = WorkoutLog.objects.count()

        # Logged out users get a 302 redirect to login page
        # Users not owning the workout, a 403, forbidden
        if fail:
            self.assertIn(response.status_code, (302, 403))
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
        Test the wgerGetWorkoutSession method
        '''

        user1 = User.objects.get(pk=1)
        user2 = User.objects.get(pk=2)
        workout1 = Workout.objects.get(pk=2)
        workout2 = Workout.objects.get(pk=2)

        WorkoutLog.objects.all().delete()
        l = WorkoutLog()
        l.user = user1
        l.date = datetime.date(2014, 1, 5)
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
        session1.date = datetime.date(2014, 1, 5)
        session1.save()

        session2 = WorkoutSession()
        session2.user = user1
        session2.workout = workout1
        session2.notes = 'Something else here'
        session2.impression = '1'
        session2.date = datetime.date(2014, 1, 1)
        session2.save()

        session3 = WorkoutSession()
        session3.user = user2
        session3.workout = workout2
        session3.notes = 'The notes here'
        session3.impression = '2'
        session3.date = datetime.date(2014, 1, 5)
        session3.save()

        self.assertEqual(l.get_workout_session(), session1)


class WeightLogDeleteTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a WorkoutLog
    '''

    object_class = WorkoutLog
    url = reverse_lazy('manager:log:delete', kwargs={'pk': 1})
    pk = 1


class WeightLogEntryEditTestCase(WorkoutManagerTestCase):
    '''
    Tests editing individual weight log entries
    '''

    def edit_log_entry(self, fail=True):
        '''
        Helper function to test edit log entries
        '''

        response = self.client.get(reverse('manager:log:edit', kwargs={'pk': 1}))
        if fail:
            self.assertTrue(response.status_code in (302, 403))

        else:
            self.assertEqual(response.status_code, 200)

        date_before = WorkoutLog.objects.get(pk=1).date
        response = self.client.post(reverse('manager:log:edit', kwargs={'pk': 1}),
                                    {'date': '2012-01-01',
                                     'reps': 10,
                                     'repetition_unit': 2,
                                     'weight_unit': 3,
                                     'weight': 10,
                                     'exercise': 1
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


class WorkoutLogCacheTestCase(WorkoutManagerTestCase):
    '''
    Workout log cache test case
    '''

    def test_calendar(self):
        '''
        Test the log cache is correctly generated on visit
        '''
        log_hash = hash((1, 2012, 10))
        self.user_login('admin')
        self.assertFalse(cache.get(cache_mapper.get_workout_log_list(log_hash)))

        self.client.get(reverse('manager:workout:calendar', kwargs={'year': 2012, 'month': 10}))
        self.assertTrue(cache.get(cache_mapper.get_workout_log_list(log_hash)))

    def test_calendar_day(self):
        '''
        Test the log cache on the calendar day view is correctly generated on visit
        '''
        log_hash = hash((1, 2012, 10, 1))
        self.user_login('admin')
        self.assertFalse(cache.get(cache_mapper.get_workout_log_list(log_hash)))

        self.client.get(reverse('manager:workout:calendar-day', kwargs={'username': 'admin',
                                                                        'year': 2012,
                                                                        'month': 10,
                                                                        'day': 1}))
        self.assertTrue(cache.get(cache_mapper.get_workout_log_list(log_hash)))

    def test_calendar_anonymous(self):
        '''
        Test the log cache is correctly generated on visit by anonymous users
        '''
        log_hash = hash((1, 2012, 10))
        self.user_logout()
        self.assertFalse(cache.get(cache_mapper.get_workout_log_list(log_hash)))

        self.client.get(reverse('manager:workout:calendar', kwargs={'username': 'admin',
                                                                    'year': 2012,
                                                                    'month': 10}))
        self.assertTrue(cache.get(cache_mapper.get_workout_log_list(log_hash)))

    def test_calendar_day_anonymous(self):
        '''
        Test the log cache is correctly generated on visit by anonymous users
        '''
        log_hash = hash((1, 2012, 10, 1))
        self.user_logout()
        self.assertFalse(cache.get(cache_mapper.get_workout_log_list(log_hash)))

        self.client.get(reverse('manager:workout:calendar-day', kwargs={'username': 'admin',
                                                                        'year': 2012,
                                                                        'month': 10,
                                                                        'day': 1}))
        self.assertTrue(cache.get(cache_mapper.get_workout_log_list(log_hash)))

    def test_cache_update_log(self):
        '''
        Test that the caches are cleared when saving a log
        '''
        log_hash = hash((1, 2012, 10))
        log_hash_day = hash((1, 2012, 10, 1))
        self.user_login('admin')
        self.client.get(reverse('manager:workout:calendar', kwargs={'year': 2012, 'month': 10}))
        self.client.get(reverse('manager:workout:calendar-day', kwargs={'username': 'admin',
                                                                        'year': 2012,
                                                                        'month': 10,
                                                                        'day': 1}))

        log = WorkoutLog.objects.get(pk=1)
        log.weight = 35
        log.save()

        self.assertFalse(cache.get(cache_mapper.get_workout_log_list(log_hash)))
        self.assertFalse(cache.get(cache_mapper.get_workout_log_list(log_hash_day)))

    def test_cache_update_log_2(self):
        '''
        Test that the caches are only cleared for a the log's month
        '''
        log_hash = hash((1, 2012, 10))
        log_hash_day = hash((1, 2012, 10, 1))
        self.user_login('admin')
        self.client.get(reverse('manager:workout:calendar', kwargs={'year': 2012, 'month': 10}))
        self.client.get(reverse('manager:workout:calendar-day', kwargs={'username': 'admin',
                                                                        'year': 2012,
                                                                        'month': 10,
                                                                        'day': 1}))

        log = WorkoutLog.objects.get(pk=3)
        log.weight = 35
        log.save()

        self.assertTrue(cache.get(cache_mapper.get_workout_log_list(log_hash)))
        self.assertTrue(cache.get(cache_mapper.get_workout_log_list(log_hash_day)))

    def test_cache_delete_log(self):
        '''
        Test that the caches are cleared when deleting a log
        '''
        log_hash = hash((1, 2012, 10))
        log_hash_day = hash((1, 2012, 10, 1))
        self.user_login('admin')
        self.client.get(reverse('manager:workout:calendar', kwargs={'year': 2012, 'month': 10}))
        self.client.get(reverse('manager:workout:calendar-day', kwargs={'username': 'admin',
                                                                        'year': 2012,
                                                                        'month': 10,
                                                                        'day': 1}))

        log = WorkoutLog.objects.get(pk=1)
        log.delete()

        self.assertFalse(cache.get(cache_mapper.get_workout_log_list(log_hash)))
        self.assertFalse(cache.get(cache_mapper.get_workout_log_list(log_hash_day)))

    def test_cache_delete_log_2(self):
        '''
        Test that the caches are only cleared for a the log's month
        '''
        log_hash = hash((1, 2012, 10))
        log_hash_day = hash((1, 2012, 10, 1))
        self.user_login('admin')
        self.client.get(reverse('manager:workout:calendar', kwargs={'year': 2012, 'month': 10}))
        self.client.get(reverse('manager:workout:calendar-day', kwargs={'username': 'admin',
                                                                        'year': 2012,
                                                                        'month': 10,
                                                                        'day': 1}))

        log = WorkoutLog.objects.get(pk=3)
        log.delete()

        self.assertTrue(cache.get(cache_mapper.get_workout_log_list(log_hash)))
        self.assertTrue(cache.get(cache_mapper.get_workout_log_list(log_hash_day)))


class WorkoutLogApiTestCase(api_base_test.ApiBaseResourceTestCase):
    '''
    Tests the workout log overview resource
    '''
    pk = 5
    resource = WorkoutLog
    private_resource = True
    data = {"exercise": 1,
            "workout": 3,
            "reps": 3,
            "repetition_unit": 1,
            "weight_unit": 2,
            "weight": 2,
            "date": datetime.date.today()}
