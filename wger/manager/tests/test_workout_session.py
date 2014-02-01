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

from django.core.urlresolvers import reverse, reverse_lazy

from wger.manager.models import Workout, WorkoutSession

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import ApiBaseResourceTestCase

'''
Tests for workout sessions
'''


class AddWorkoutSessionTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a workout session
    '''

    object_class = WorkoutSession
    url = reverse_lazy('workout-session-add', kwargs={'workout_pk': 1})
    pk = 4
    data = {
        'user': 1,
        'workout': 1,
        'date': datetime.date.today(),
        'notes': 'Some interesting and deep insights',
        'impression': '3',
        'time_start': datetime.time(10, 0),
        'time_end': datetime.time(13, 0)
    }
    #user_success = 'test'
    #user_fail = 'admin'


class EditWorkoutSessionTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a workout session
    '''

    object_class = WorkoutSession
    url = 'workout-session-edit'
    pk = 3
    #user_success = 'test'
    #user_fail = 'admin'
    data = {
        'user': 1,
        'workout': 2,
        'date': datetime.date.today(),
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
        self.assertEqual(session.__unicode__(),
                         u'{0} - {1}'.format(Workout.objects.get(pk=1), datetime.date.today()))


class WorkoutSessionApiTestCase(ApiBaseResourceTestCase):
    '''
    Tests the workout overview resource
    '''
    resource = 'workoutsession'
    resource_updatable = False


class WorkoutSessionDetailApiTestCase(ApiBaseResourceTestCase):
    '''
    Tests accessing a specific workout
    '''
    resource = 'workoutsession/1'
    user_fail = 'test'
    user = 'admin'
