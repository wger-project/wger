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
import datetime

from django.core.urlresolvers import reverse

from wger.manager.models import Schedule
from wger.manager.models import Workout

from wger.manager.tests.testcase import STATUS_CODES_FAIL
from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase

logger = logging.getLogger('workout_manager.custom')


class CreateScheduleTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a schedule
    '''

    object_class = Schedule
    url = 'schedule-add'
    pk = 5
    user_success = 'test'
    user_fail = False
    data = {'name': 'My cool schedule',
            'start_date': datetime.date.today(),
            'is_active': True,
            'is_loop': True}


class DeleteScheduleTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a schedule
    '''

    object_class = Schedule
    url = 'schedule-delete'
    pk = 1
    user_success = 'test'
    user_fail = 'admin'


class EditScheduleTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a schedule
    '''

    object_class = Schedule
    url = 'schedule-edit'
    pk = 3
    data = {'name': 'An updated name',
            'start_date': datetime.date.today(),
            'is_active': True,
            'is_loop': True}


class ScheduleTestCase(WorkoutManagerTestCase):
    '''
    Other tests
    '''

    def schedule_detail_page(self, fail=False):
        '''
        Helper function
        '''

        response = self.client.get(reverse('schedule-view', kwargs={'pk': 2}))
        if fail:
            self.assertIn(response.status_code, STATUS_CODES_FAIL)
        else:
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'This schedule is a loop')

            schedule = Schedule.objects.get(pk=2)
            schedule.is_loop = False
            schedule.save()

            response = self.client.get(reverse('schedule-view', kwargs={'pk': 2}))
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, 'This schedule is a loop')

    def test_schedule_detail_page_owner(self):
        '''
        Tests the schedule detail page as the owning user
        '''

        self.user_login()
        self.schedule_detail_page()

    def test_schedule_detail_page_other(self):
        '''
        Tests the schedule detail page as a different user
        '''

        self.user_login('test')
        self.schedule_detail_page(fail=True)

    def test_schedule_overview(self):
        '''
        Tests the schedule overview
        '''
        self.user_login()

        response = self.client.get(reverse('schedule-overview'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['schedules']), 3)
        self.assertContains(response, 'Schedule active')

        schedule = Schedule.objects.get(pk=4)
        schedule.is_active = False
        schedule.save()

        response = self.client.get(reverse('schedule-overview'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['schedules']), 3)
        self.assertNotContains(response, 'Schedule active')

    def test_schedule_active(self):
        '''
        Tests that only one schedule can be active at a time (per user)
        '''
        def get_schedules():
            schedule1 = Schedule.objects.get(pk=2)
            schedule2 = Schedule.objects.get(pk=3)
            schedule3 = Schedule.objects.get(pk=4)

            return (schedule1, schedule2, schedule3)

        self.user_login()
        (schedule1, schedule2, schedule3) = get_schedules()
        self.assertTrue(schedule3.is_active)

        schedule1.is_active = True
        schedule1.save()
        (schedule1, schedule2, schedule3) = get_schedules()
        self.assertTrue(schedule1.is_active)
        self.assertFalse(schedule2.is_active)
        self.assertFalse(schedule3.is_active)

        schedule2.is_active = True
        schedule2.save()
        (schedule1, schedule2, schedule3) = get_schedules()
        self.assertFalse(schedule1.is_active)
        self.assertTrue(schedule2.is_active)
        self.assertFalse(schedule3.is_active)
