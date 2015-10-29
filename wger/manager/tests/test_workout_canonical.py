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

from decimal import Decimal

from django.core.cache import cache

from wger.core.models import DaysOfWeek
from wger.exercises.models import Exercise
from wger.manager.models import Workout
from wger.manager.models import Day
from wger.manager.models import Set
from wger.manager.models import Setting

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.utils.cache import cache_mapper


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
        self.assertEqual(workout.canonical_representation['muscles'], {'back': [2], 'front': [1]})
        self.assertEqual(workout.canonical_representation['obj'], workout)

        canonical_form = {'days_of_week': {'day_list': [DaysOfWeek.objects.get(pk=2)],
                                           'text': u'Tuesday'},
                          'muscles': {'back': [2], 'front': [1]},
                          'obj': Day.objects.get(pk=1),
                          'set_list': [{'exercise_list': [{'obj': Exercise.objects.get(pk=1),
                                                           'comment_list': [u'test 123'],
                                                           'has_weight': False,
                                                           'setting_list': [u'8', u'8'],
                                                           'reps_list': [8, 8],
                                                           'weight_list': [None, None],
                                                           'setting_obj_list': [setting_1],
                                                           'setting_text': u'2 \xd7 8'}],
                                        'is_superset': False,
                                        'has_settings': True,
                                        'muscles': {'back': [2], 'front': [1]},
                                        'obj': Set.objects.get(pk=1)}]}
        self.assertEqual(workout.canonical_representation['day_list'][0], canonical_form)

        canonical_form = {'days_of_week': {'day_list': [DaysOfWeek.objects.get(pk=4)],
                                           'text': u'Thursday'},
                          'obj': Day.objects.get(pk=2),
                          'muscles': {'back': [2], 'front': []},
                          'set_list': [{'exercise_list': [{'obj': Exercise.objects.get(pk=2),
                                                           'comment_list': [u'Foobar'],
                                                           'has_weight': True,
                                                           'reps_list': [10, 10, 10, 10],
                                                           'setting_list': [u'10 (15kg)',
                                                                            u'10 (15kg)',
                                                                            u'10 (15kg)',
                                                                            u'10 (15kg)'],
                                                           'weight_list': [Decimal(15)] * 4,
                                                           'setting_obj_list': [setting_2],
                                                           'setting_text': u'4 \xd7 10 (15kg)'}],
                                        'is_superset': False,
                                        'has_settings': True,
                                        'muscles': {'back': [2], 'front': []},
                                        'obj': Set.objects.get(pk=2)}]}
        self.assertEqual(workout.canonical_representation['day_list'][1], canonical_form)

        canonical_form = {'days_of_week': {'day_list': [DaysOfWeek.objects.get(pk=5)],
                                           'text': u'Friday'},
                          'obj': Day.objects.get(pk=4),
                          'muscles': {'back': [], 'front': []},
                          'set_list': []}
        self.assertEqual(workout.canonical_representation['day_list'][2], canonical_form)

    def test_canonical_form_day(self):
        '''
        Tests the canonical form for a day
        '''

        day = Day.objects.get(pk=5)
        weekday1 = DaysOfWeek.objects.get(pk=3)
        weekday2 = DaysOfWeek.objects.get(pk=5)
        self.assertEqual(day.canonical_representation['days_of_week'],
                         {'day_list': [weekday1, weekday2], 'text': u'Wednesday, Friday'})
        self.assertEqual(day.canonical_representation['muscles'], {'back': [2], 'front': []})
        self.assertEqual(day.canonical_representation['obj'], day)

        canonical_form = [{'exercise_list': [{'obj': Exercise.objects.get(pk=2),
                                              'comment_list': [u'Foobar'],
                                              'reps_list': [10, 10, 10, 10],
                                              'has_weight': False,
                                              'setting_list': [u'10', u'10', u'10', u'10'],
                                              'weight_list': [None, None, None, None],
                                              'setting_obj_list': [Setting.objects.get(pk=3)],
                                              'setting_text': u'4 \xd7 10'}],
                           'is_superset': False,
                           'has_settings': True,
                           'muscles': {'back': [2], 'front': []},
                           'obj': Set.objects.get(pk=3)}]

        self.assertEqual(day.canonical_representation['set_list'], canonical_form)


class WorkoutCacheTestCase(WorkoutManagerTestCase):
    '''
    Test case for the workout canonical representation
    '''

    def test_canonical_form_cache(self):
        '''
        Tests that the workout cache of the canonical form is correctly generated
        '''
        self.assertFalse(cache.get(cache_mapper.get_workout_canonical(1)))

        workout = Workout.objects.get(pk=1)
        workout.canonical_representation
        self.assertTrue(cache.get(cache_mapper.get_workout_canonical(1)))

    def test_canonical_form_cache_save(self):
        '''
        Tests the workout cache when saving
        '''
        workout = Workout.objects.get(pk=1)
        workout.canonical_representation
        self.assertTrue(cache.get(cache_mapper.get_workout_canonical(1)))

        workout.save()
        self.assertFalse(cache.get(cache_mapper.get_workout_canonical(1)))

    def test_canonical_form_cache_delete(self):
        '''
        Tests the workout cache when deleting
        '''
        workout = Workout.objects.get(pk=1)
        workout.canonical_representation
        self.assertTrue(cache.get(cache_mapper.get_workout_canonical(1)))

        workout.delete()
        self.assertFalse(cache.get(cache_mapper.get_workout_canonical(1)))
