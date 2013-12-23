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

from wger.exercises.models import Exercise
from wger.manager.models import Workout
from wger.manager.models import DaysOfWeek
from wger.manager.models import Day
from wger.manager.models import Set
from wger.manager.models import Setting

from wger.manager.tests.testcase import WorkoutManagerTestCase


class WorkoutCanonicalFormTestCase(WorkoutManagerTestCase):
    '''
    Tests the canonical form for a workout
    '''
    maxDiff = None

    def test_canonical_form(self):
        '''
        Tests the canonical form for a workout
        '''

        workout = Workout.objects.get(pk=1)
        setting_1 = Setting.objects.get(pk=1)
        setting_2 = Setting.objects.get(pk=2)
        canonical_form = [{'days_of_week': {'day_list': [DaysOfWeek.objects.get(pk=2)],
                                            'text': u'Tuesday'},
                          'obj': Day.objects.get(pk=1),
                          'set_list': [{'exercise_list': [{'obj': Exercise.objects.get(pk=1),
                                                           'setting_list': [8, 8],
                                                           'setting_obj_list': [setting_1],
                                                           'setting_text': u'2 \xd7 8'}],
                                        'is_superset': False,
                                        'obj': Set.objects.get(pk=1)}]},
                          {'days_of_week': {'day_list': [DaysOfWeek.objects.get(pk=4)],
                                            'text': u'Thursday'},
                           'obj': Day.objects.get(pk=2),
                           'set_list': [{'exercise_list': [{'obj': Exercise.objects.get(pk=2),
                                                           'setting_list': [10, 10, 10, 10],
                                                           'setting_obj_list': [setting_2],
                                                           'setting_text': u'4 \xd7 10'}],
                                        'is_superset': False,
                                        'obj': Set.objects.get(pk=2)}]},
                          {'days_of_week': {'day_list': [DaysOfWeek.objects.get(pk=5)],
                                            'text': u'Friday'},
                           'obj': Day.objects.get(pk=4),
                           'set_list': []}]

        self.assertEqual(workout.canonical_representation, canonical_form)

    def test_canonical_form_day(self):
        '''
        Tests the canonical form for a day
        '''

        day = Day.objects.get(pk=5)
        canonical_form = [{'exercise_list': [{'obj': Exercise.objects.get(pk=2),
                                              'setting_list': [10, 10, 10, 10],
                                              'setting_obj_list': [Setting.objects.get(pk=3)],
                                              'setting_text': u'4 \xd7 10'}],
                          'is_superset': False,
                          'obj': Set.objects.get(pk=3)}]

        self.assertEqual(day.canonical_representation, canonical_form)
