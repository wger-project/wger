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
from django.contrib.auth.models import User

from wger.manager.models import Schedule
from wger.manager.models import ScheduleStep
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


class ScheduleAjaxTestCase(WorkoutManagerTestCase):
    '''
    Tests the AJAX reordering call for steps
    '''

    def test_schedule_api_owner_1(self):
        '''
        Tests the AJAX reordering as the owner user. All IDs exist and are owned
        '''
        self.user_login()
        response = self.client.get(reverse('schedule-edit-api', kwargs={'pk': 2}),
                                   {'do': 'set_order', 'order': 'step-3,step-1,step-2'})
        self.assertEqual(response.status_code, 200)

        schedule = Schedule.objects.get(pk=2)
        steps = schedule.schedulestep_set.all()
        self.assertEqual(steps[0].id, 3)
        self.assertEqual(steps[1].id, 1)
        self.assertEqual(steps[2].id, 2)

    def test_schedule_api_owner_2(self):
        '''
        Tests the AJAX reordering as the owner user. All IDs exist and are owned
        '''

        self.user_login()
        response = self.client.get(reverse('schedule-edit-api', kwargs={'pk': 2}),
                                   {'do': 'set_order', 'order': 'step-3,step-2,step-1'})
        self.assertEqual(response.status_code, 200)

        schedule = Schedule.objects.get(pk=2)
        steps = schedule.schedulestep_set.all()
        self.assertEqual(steps[0].id, 3)
        self.assertEqual(steps[1].id, 2)
        self.assertEqual(steps[2].id, 1)

    def test_schedule_api_owner_3(self):
        '''
        Tests the AJAX reordering as the owner user, wrong step in the order list
        '''
        self.user_login()
        response = self.client.get(reverse('schedule-edit-api', kwargs={'pk': 2}),
                                   {'do': 'set_order', 'order': 'step-3,step-1,step-2,step-44'})
        self.assertEqual(response.status_code, 200)

        schedule = Schedule.objects.get(pk=2)
        steps = schedule.schedulestep_set.all()
        self.assertEqual(steps[0].id, 3)
        self.assertEqual(steps[1].id, 1)
        self.assertEqual(steps[2].id, 2)

    def test_schedule_api_owner_4(self):
        '''
        Tests the AJAX reordering as the owner user, wrong step in the order list
        '''
        self.user_login()
        response = self.client.get(reverse('schedule-edit-api', kwargs={'pk': 2}),
                                   {'do': 'set_order', 'order': 'foo,bar-47,step-2,step-1,step-3'})
        self.assertEqual(response.status_code, 200)

        schedule = Schedule.objects.get(pk=2)
        steps = schedule.schedulestep_set.all()
        self.assertEqual(steps[0].id, 2)
        self.assertEqual(steps[1].id, 1)
        self.assertEqual(steps[2].id, 3)

    def test_schedule_api_owner_5(self):
        '''
        Tests the AJAX reordering as the owner user, wrong step in the order list
        '''
        self.user_login()
        response = self.client.get(reverse('schedule-edit-api', kwargs={'pk': 2}),
                                   {'do': 'set_order', 'order': 'blahrg'})
        self.assertEqual(response.status_code, 200)

        schedule = Schedule.objects.get(pk=2)
        steps = schedule.schedulestep_set.all()
        self.assertEqual(steps[0].id, 1)
        self.assertEqual(steps[1].id, 2)
        self.assertEqual(steps[2].id, 3)

    def test_schedule_api_other_1(self):
        '''
        Tests the AJAX reordering as a different user
        '''
        self.user_login('test')
        response = self.client.get(reverse('schedule-edit-api', kwargs={'pk': 2}),
                                   {'do': 'set_order', 'order': 'step-3,step-1,step-2'})
        self.assertIn(response.status_code, STATUS_CODES_FAIL)

    def test_schedule_api_other_2(self):
        '''
        Tests the AJAX reordering as a different user, steps belong to a different schedule
        '''
        self.user_login('test')
        response = self.client.get(reverse('schedule-edit-api', kwargs={'pk': 1}),
                                   {'do': 'set_order', 'order': 'step-3,step-1,step-2'})
        self.assertEqual(response.status_code, 200)

        # No change in order
        schedule = Schedule.objects.get(pk=2)
        steps = schedule.schedulestep_set.all()
        self.assertEqual(steps[0].id, 1)
        self.assertEqual(steps[1].id, 2)
        self.assertEqual(steps[2].id, 3)


class ScheduleModelTestCase(WorkoutManagerTestCase):
    '''
    Tests the model methods
    '''

    def delete_objects(self, user):
        '''
        Helper function
        '''

        Workout.objects.filter(user=user).delete()
        Schedule.objects.filter(user=user).delete()

    def create_schedule(self, user, start_date=datetime.date.today(), is_loop=False):
        '''
        Helper function
        '''

        schedule = Schedule()
        schedule.user = user
        schedule.name = 'temp'
        schedule.is_active = True
        schedule.start_date = start_date
        schedule.is_loop = is_loop
        schedule.save()
        return schedule

    def create_workout(self, user):
        '''
        Helper function
        '''

        workout = Workout()
        workout.user = user
        workout.save()
        return workout

    def test_get_workout_steps_test_1(self):
        '''
        Test with no workouts and no schedule steps
        '''
        self.user_login('test')
        user = User.objects.get(pk=2)
        self.delete_objects(user)

        schedule = self.create_schedule(user)
        self.assertFalse(schedule.get_current_scheduled_workout())

    def test_get_workout_steps_test_2(self):
        '''
        Test with one schedule step
        '''
        self.user_login('test')
        user = User.objects.get(pk=2)
        self.delete_objects(user)

        schedule = self.create_schedule(user)
        workout = self.create_workout(user)
        step = ScheduleStep()
        step.schedule = schedule
        step.workout = workout
        step.duration = 3
        step.save()
        self.assertEqual(schedule.get_current_scheduled_workout().workout, workout)

    def test_get_workout_steps_test_3(self):
        '''
        Test with 3 steps
        '''
        self.user_login('test')
        user = User.objects.get(pk=2)
        self.delete_objects(user)

        start_date = datetime.date.today() - datetime.timedelta(weeks=4)
        schedule = self.create_schedule(user, start_date=start_date)
        workout = self.create_workout(user)
        step = ScheduleStep()
        step.schedule = schedule
        step.workout = workout
        step.duration = 3
        step.order = 1
        step.save()

        workout2 = self.create_workout(user)
        step2 = ScheduleStep()
        step2.schedule = schedule
        step2.workout = workout2
        step2.duration = 1
        step2.order = 2
        step2.save()

        workout3 = self.create_workout(user)
        step3 = ScheduleStep()
        step3.schedule = schedule
        step3.workout = workout3
        step3.duration = 2
        step3.order = 3
        step3.save()
        self.assertEqual(schedule.get_current_scheduled_workout().workout, workout2)

    def test_get_workout_steps_test_4(self):
        '''
        Test with 3 steps. Start is too far in the past, schedule ist not a loop
        '''
        self.user_login('test')
        user = User.objects.get(pk=2)
        self.delete_objects(user)

        start_date = datetime.date.today() - datetime.timedelta(weeks=7)
        schedule = self.create_schedule(user, start_date=start_date)
        workout = self.create_workout(user)
        step = ScheduleStep()
        step.schedule = schedule
        step.workout = workout
        step.duration = 3
        step.order = 1
        step.save()

        workout2 = self.create_workout(user)
        step2 = ScheduleStep()
        step2.schedule = schedule
        step2.workout = workout2
        step2.duration = 1
        step2.order = 2
        step2.save()

        workout3 = self.create_workout(user)
        step3 = ScheduleStep()
        step3.schedule = schedule
        step3.workout = workout3
        step3.duration = 2
        step3.order = 3
        step3.save()
        self.assertFalse(schedule.get_current_scheduled_workout())

    def test_get_workout_steps_test_5(self):
        '''
        Test with 3 steps. Start is too far in the past but schedule is a loop
        '''
        self.user_login('test')
        user = User.objects.get(pk=2)
        self.delete_objects(user)

        start_date = datetime.date.today() - datetime.timedelta(weeks=7)
        schedule = self.create_schedule(user, start_date=start_date, is_loop=True)
        workout = self.create_workout(user)
        step = ScheduleStep()
        step.schedule = schedule
        step.workout = workout
        step.duration = 3
        step.order = 1
        step.save()

        workout2 = self.create_workout(user)
        step2 = ScheduleStep()
        step2.schedule = schedule
        step2.workout = workout2
        step2.duration = 1
        step2.order = 2
        step2.save()

        workout3 = self.create_workout(user)
        step3 = ScheduleStep()
        step3.schedule = schedule
        step3.workout = workout3
        step3.duration = 2
        step3.order = 3
        step3.save()
        self.assertTrue(schedule.get_current_scheduled_workout().workout, workout)
