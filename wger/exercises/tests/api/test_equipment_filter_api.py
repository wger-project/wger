# This file is part of wger Workout Manager.
# Licensed under the GNU Affero General Public License, version 3 or later.

# Django
from django.urls import reverse

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase
from wger.exercises.models import Equipment, Exercise


class EquipmentFilterApiTestCase(BaseTestCase, ApiBaseTestCase):
    """Exercise equipment filters must distinguish empty relations from bodyweight."""

    endpoints = ('exercise-list', 'exerciseinfo-list')

    def setUp(self):
        super().setUp()
        # Fixtures 1-4 have translations; give each a controlled equipment setup.
        self.exercise_ids = [1, 2, 3, 4]
        for pk in self.exercise_ids:
            Exercise.objects.get(pk=pk).equipment.clear()
        self.bodyweight = Equipment.objects.create(name='none (bodyweight exercise)')
        Exercise.objects.get(pk=2).equipment.set([1])
        Exercise.objects.get(pk=3).equipment.set([1, 2])
        Exercise.objects.get(pk=4).equipment.set([self.bodyweight])

    def assert_results(self, endpoint, params, expected):
        response = self.client.get(reverse(endpoint), {'limit': 1000, **params})
        self.assertEqual(response.status_code, 200)
        ids = [item['id'] for item in response.data['results']]
        self.assertEqual(len(ids), len(set(ids)), 'Duplicate exercises in API response')
        self.assertEqual(response.data['count'], len(ids))
        self.assertEqual(set(ids) & set(self.exercise_ids), set(expected))

    def test_empty_equipment(self):
        for endpoint in self.endpoints:
            with self.subTest(endpoint=endpoint):
                self.assert_results(endpoint, {'equipment__isnull': 'true'}, [1])

    def test_nonempty_equipment_has_no_duplicates(self):
        for endpoint in self.endpoints:
            with self.subTest(endpoint=endpoint):
                self.assert_results(endpoint, {'equipment__isnull': 'false'}, [2, 3, 4])

    def test_omitted_filter_keeps_all_equipment_states(self):
        for endpoint in self.endpoints:
            with self.subTest(endpoint=endpoint):
                self.assert_results(endpoint, {}, self.exercise_ids)

    def test_empty_parameter_does_not_filter(self):
        for endpoint in self.endpoints:
            with self.subTest(endpoint=endpoint):
                self.assert_results(endpoint, {'equipment__isnull': ''}, self.exercise_ids)

    def test_bodyweight_is_not_an_empty_relation(self):
        for endpoint in self.endpoints:
            with self.subTest(endpoint=endpoint):
                self.assert_results(endpoint, {'equipment': self.bodyweight.pk}, [4])

    def test_existing_equipment_filter(self):
        for endpoint in self.endpoints:
            with self.subTest(endpoint=endpoint):
                self.assert_results(endpoint, {'equipment': 1}, [2, 3])

    def test_empty_equipment_combines_with_category(self):
        for endpoint in self.endpoints:
            with self.subTest(endpoint=endpoint):
                self.assert_results(endpoint, {'equipment__isnull': 'true', 'category': 3}, [])

    def test_exercise_endpoint_still_requires_translation(self):
        exercise = Exercise.objects.create(category_id=2)
        response = self.client.get(
            reverse('exercise-list'), {'equipment__isnull': 'true', 'limit': 1000}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(exercise.pk, [item['id'] for item in response.data['results']])

    def test_empty_muscle_relations(self):
        for field in ('muscles', 'muscles_secondary'):
            getattr(Exercise.objects.get(pk=1), field).clear()
            for pk in (2, 3, 4):
                getattr(Exercise.objects.get(pk=pk), field).set([1, 2])
            for endpoint in self.endpoints:
                with self.subTest(field=field, endpoint=endpoint):
                    self.assert_results(endpoint, {f'{field}__isnull': 'true'}, [1])

    def test_nonempty_muscle_relations_have_no_duplicates(self):
        for field in ('muscles', 'muscles_secondary'):
            getattr(Exercise.objects.get(pk=1), field).clear()
            for pk in (2, 3, 4):
                getattr(Exercise.objects.get(pk=pk), field).set([1, 2])
            for endpoint in self.endpoints:
                with self.subTest(field=field, endpoint=endpoint):
                    self.assert_results(endpoint, {f'{field}__isnull': 'false'}, [2, 3, 4])

    def test_equipment_and_muscle_filters_combine(self):
        for field in ('muscles', 'muscles_secondary'):
            getattr(Exercise.objects.get(pk=2), field).clear()
            for pk in (1, 3, 4):
                getattr(Exercise.objects.get(pk=pk), field).set([1, 2])
            for endpoint in self.endpoints:
                with self.subTest(field=field, endpoint=endpoint):
                    self.assert_results(
                        endpoint,
                        {'equipment__isnull': 'false', f'{field}__isnull': 'true'},
                        [2],
                    )
