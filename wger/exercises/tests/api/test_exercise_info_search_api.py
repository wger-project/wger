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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
from unittest import skipUnless

# Django
from django.db import connection
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase
from wger.exercises.models import (
    Exercise,
    ExerciseCategory,
    Translation,
)


class ExerciseInfoFilterApiTestCase(BaseTestCase, ApiBaseTestCase):
    url = '/api/v2/exerciseinfo/'

    def _results(self, response):
        if isinstance(response.data, dict) and 'results' in response.data:
            return response.data['results']
        return response.data

    def _has_translation_name(self, item, expected_name: str) -> bool:
        for t in item.get('translations', []):
            if t.get('name') == expected_name:
                return True
        return False

    def test_basic_search_logged_out(self):
        """
        Logged-out users can search via name__search and language__code
        """
        response = self.client.get(
            reverse('exerciseinfo-list'),
            {'name__search': 'exercise', 'language__code': 'en'},
        )
        results = self._results(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 4)
        ids = {item['id'] for item in results}
        self.assertIn(1, ids)
        item1 = next(item for item in results if item['id'] == 1)
        self.assertTrue(self._has_translation_name(item1, 'An exercise'))

    def test_basic_search_logged_in(self):
        """
        Logged-in users get the same results
        """
        self.authenticate('test')
        response = self.client.get(
            reverse('exerciseinfo-list'),
            {'name__search': 'exercise', 'language__code': 'en'},
        )
        results = self._results(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 4)
        ids = {item['id'] for item in results}
        self.assertIn(1, ids)
        item1 = next(item for item in results if item['id'] == 1)
        self.assertTrue(self._has_translation_name(item1, 'An exercise'))

    def test_search_language_code_en_no_results(self):
        """
        A DE-only exercise name should not be found when searching in English
        """
        response = self.client.get(
            reverse('exerciseinfo-list'),
            {'name__search': 'Weitere', 'language__code': 'en'},
        )
        results = self._results(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 0)

    def test_search_language_code_de(self):
        """
        A DE-only exercise should be found when searching in German
        """
        response = self.client.get(
            reverse('exerciseinfo-list'),
            {'name__search': 'Weitere', 'language__code': 'de'},
        )
        results = self._results(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], 4)

    def test_search_several_language_codes(self):
        """
        Passing different language codes works correctly
        """
        response = self.client.get(
            reverse('exerciseinfo-list'),
            {'name__search': 'demo', 'language__code': 'en,de'},
        )
        results = self._results(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 4)

    def test_search_unknown_language_codes(self):
        """
        Unknown language codes are ignored
        """
        response = self.client.get(
            reverse('exerciseinfo-list'),
            {'name__search': 'demo', 'language__code': 'en,de,zz'},
        )
        results = self._results(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 4)

    def test_search_all_languages(self):
        """
        Disable all language filters when language__code is omitted
        """
        response = self.client.get(
            reverse('exerciseinfo-list'),
            {'name__search': 'demo'},
        )
        results = self._results(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 4)

    def test_search_matches_alias(self):
        """
        Alias terms should also match
        """
        response = self.client.get(
            reverse('exerciseinfo-list'),
            {'name__search': 'different', 'language__code': 'en'},
        )
        results = self._results(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results), 1)


@skipUnless(connection.vendor == 'postgresql', 'PostgreSQL exercise search only')
class ExerciseInfoSearchRankingApiTestCase(BaseTestCase, ApiBaseTestCase):
    """Retrieval and ranking of the exercise name search"""

    corpus = (
        'Curl',
        'Leg Curl',
        'Curl With Kettlebell',
        'Alternating Biceps Curls With Dumbbell',
        'Barbell Reverse Wrist Curl',
        'Rowing Machine',
        'Bent Over Rowing',
        'Butterfly Narrow Grip',
        'Bench Press',
        'Decline Bench Press Barbell',
    )

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        category = ExerciseCategory.objects.first()
        for name in cls.corpus:
            exercise = Exercise.objects.create(
                category=category,
                license_id=2,
                license_author='test',
            )
            Translation.objects.create(
                exercise=exercise,
                language_id=2,
                name=name,
                description='A description for the search test corpus.',
            )

    def search_names(self, query, **params):
        response = self.client.get(
            reverse('exerciseinfo-list'),
            {'name__search': query, 'language__code': 'en', **params},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        names = []
        for item in response.data['results']:
            names += [
                translation['name']
                for translation in item['translations']
                if translation['name'] in self.corpus
            ]
        return names

    def assert_ranked_before(self, names, first, second):
        self.assertIn(first, names)
        self.assertIn(second, names)
        self.assertLess(names.index(first), names.index(second))

    def test_search_finds_words_in_long_exercise_names(self):
        names = self.search_names('curl')

        for expected_name in (
            'Alternating Biceps Curls With Dumbbell',
            'Barbell Reverse Wrist Curl',
            'Leg Curl',
        ):
            with self.subTest(expected_name=expected_name):
                self.assertIn(expected_name, names)

    def test_search_ranks_exact_names_first(self):
        self.assertEqual(self.search_names('curl')[:1], ['Curl'])
        self.assertEqual(self.search_names('bench press')[:1], ['Bench Press'])

    def test_search_ranks_shorter_names_before_longer_ones(self):
        names = self.search_names('curl')

        self.assert_ranked_before(names, 'Leg Curl', 'Alternating Biceps Curls With Dumbbell')

    def test_search_matches_word_beginnings(self):
        names = self.search_names('row')

        self.assertIn('Rowing Machine', names)
        self.assertIn('Bent Over Rowing', names)

    def test_search_ignores_matches_inside_a_word(self):
        self.assertNotIn('Butterfly Narrow Grip', self.search_names('row'))

    def test_search_finds_a_correctly_spelled_name_from_a_typo(self):
        self.assertIn('Bench Press', self.search_names('bech press'))

    def test_search_keeps_an_explicitly_requested_ordering(self):
        names = self.search_names('curl', ordering='-id')

        self.assertEqual(names[:1], ['Barbell Reverse Wrist Curl'])
