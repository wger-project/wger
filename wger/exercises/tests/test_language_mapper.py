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

from django.core.cache import cache

from wger.exercises.models import ExerciseLanguageMapper
from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.utils.cache import cache_mapper


class LanguageMapperTestCase(WorkoutManagerTestCase):
    '''
    Test the language mapper
    '''

    def test_language_mapper(self):
        '''
        Test the language mapper
        '''
        mapper = ExerciseLanguageMapper.objects.get(pk=1)
        self.assertEqual(mapper.get_language('en').pk, 84)
        self.assertEqual(mapper.get_language('de').pk, 1)
        self.assertRaises(KeyError, lambda: mapper.get_language('gr'))


class LanguageMapperCacheTestCase(WorkoutManagerTestCase):
    '''
    Language mapper cache test case
    '''

    def test_cache(self):
        '''
        Test that the cache is correctly generated
        '''
        mapper = ExerciseLanguageMapper.objects.get(pk=1)

        self.assertFalse(cache.get(cache_mapper.get_exercise_language_mapper(mapper)))
        mapper.get_all_languages()
        self.assertTrue(cache.get(cache_mapper.get_exercise_language_mapper(mapper)))
