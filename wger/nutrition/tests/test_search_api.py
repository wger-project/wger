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
from unittest.mock import patch

# Django
from django.contrib.auth.models import User
from django.db import connection
from django.test import RequestFactory
from django.urls import reverse

# Third Party
from rest_framework import status

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase
from wger.nutrition.api.filtersets import (
    IngredientFilterSet,
    _has_literal_trigram,
)
from wger.nutrition.api.views import IngredientViewSet
from wger.nutrition.models import (
    Ingredient,
    LogItem,
    NutritionPlan,
)


class PersonalIngredientSearchTestMixin:
    def prepare_personal_search(self) -> None:
        template = Ingredient.objects.get(name='Test ingredient 1')
        self.history_ingredients = [
            Ingredient.objects.create(
                name=name,
                language=template.language,
                energy=100,
                protein=10,
                carbohydrates=10,
                fat=10,
            )
            for name in (
                'History search alpha',
                'History search beta',
                'History search beta',
                'History search gamma',
            )
        ]
        self.history_plan = NutritionPlan.objects.filter(user__username='test').first()
        other_plan = NutritionPlan.objects.filter(user__username='admin').first()
        self.own_history = {self.history_ingredients[1].pk, self.history_ingredients[3].pk}
        self.other_history = {self.history_ingredients[2].pk}
        for ingredient in (
            self.history_ingredients[1],
            self.history_ingredients[1],
            self.history_ingredients[3],
        ):
            LogItem.objects.create(plan=self.history_plan, ingredient=ingredient, amount=100)
        LogItem.objects.create(
            plan=other_plan,
            ingredient=self.history_ingredients[2],
            amount=100,
        )

    def personal_search_ids(self, **params) -> list:
        ids = None
        for endpoint in ('api-ingredient-list', 'api-ingredientinfo-list'):
            response = self.client.get(
                reverse(endpoint),
                {'name__search': 'history', 'language__code': 'en', **params},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['count'], len(self.history_ingredients))
            endpoint_ids = [result['id'] for result in response.data['results']]
            if ids is not None:
                self.assertEqual(endpoint_ids, ids)
            ids = endpoint_ids
        return ids

    def test_personal_search_prioritizes_own_history(self):
        """Matching diary ingredients come first, retaining relevance within each group."""
        self.prepare_personal_search()
        self.authenticate('test')
        baseline = self.personal_search_ids()
        expected = [pk for pk in baseline if pk in self.own_history] + [
            pk for pk in baseline if pk not in self.own_history
        ]

        self.assertNotEqual(baseline, expected)
        self.assertEqual(self.personal_search_ids(prioritize_history='true'), expected)

    def test_personal_search_is_opt_in(self):
        """Authenticated searches retain anonymous ordering unless explicitly enabled."""
        self.prepare_personal_search()
        baseline = self.personal_search_ids()
        self.authenticate('test')

        self.assertEqual(self.personal_search_ids(), baseline)
        self.assertEqual(self.personal_search_ids(prioritize_history='false'), baseline)

    def test_personal_search_isolates_users(self):
        """Switching users prioritizes only the new user's diary ingredients."""
        self.prepare_personal_search()
        baseline = self.personal_search_ids()
        self.authenticate('admin')
        expected = [pk for pk in baseline if pk in self.other_history] + [
            pk for pk in baseline if pk not in self.other_history
        ]

        self.assertNotEqual(baseline, expected)
        self.assertEqual(self.personal_search_ids(prioritize_history='true'), expected)

    def test_personal_search_ignores_anonymous_opt_in(self):
        """Anonymous requests ignore the history option and preserve ordinary results."""
        self.prepare_personal_search()

        self.assertEqual(
            self.personal_search_ids(prioritize_history='true'),
            self.personal_search_ids(),
        )

    def test_personal_search_preserves_filters(self):
        """Logged ingredients must still match both the name and language filters."""
        self.prepare_personal_search()
        template = self.history_ingredients[0]
        for name, language in (
            ('Unrelated diary ingredient', template.language),
            ('History search deutsch', Ingredient.objects.get(name='Testzutat 123').language),
        ):
            ingredient = Ingredient.objects.create(
                name=name,
                language=language,
                energy=100,
                protein=10,
                carbohydrates=10,
                fat=10,
            )
            LogItem.objects.create(plan=self.history_plan, ingredient=ingredient, amount=100)
        self.authenticate('test')

        self.assertCountEqual(
            self.personal_search_ids(prioritize_history='true'),
            [ingredient.pk for ingredient in self.history_ingredients],
        )

    def test_personal_search_paginates_without_duplicates(self):
        """Repeated diary logs and equal ingredient names do not repeat or skip results."""
        self.prepare_personal_search()
        self.authenticate('test')
        expected = self.personal_search_ids(prioritize_history='true')
        first = self.personal_search_ids(prioritize_history='true', limit=2)
        second = self.personal_search_ids(prioritize_history='true', limit=2, offset=2)

        self.assertEqual(first + second, expected)
        self.assertEqual(len(set(first + second)), len(self.history_ingredients))
        self.assertEqual(first, self.personal_search_ids(prioritize_history='true', limit=2))

    def test_personal_search_respects_explicit_ordering(self):
        """An explicit ordering parameter takes precedence over history ranking."""
        self.prepare_personal_search()
        self.authenticate('test')

        self.assertEqual(
            self.personal_search_ids(prioritize_history='true', ordering='-id'),
            sorted((ingredient.pk for ingredient in self.history_ingredients), reverse=True),
        )

    def test_personal_search_without_request_keeps_default_ordering(self):
        """Using the filterset without an authenticated request does not inspect history."""
        self.prepare_personal_search()
        filterset = IngredientViewSet.filterset_class(
            {'name__search': 'history', 'prioritize_history': 'true'},
            queryset=Ingredient.objects.all(),
        )

        self.assertNotIn(LogItem._meta.db_table, str(filterset.qs.query))

    def test_personal_search_without_search_does_not_query_history(self):
        """Enabling history without a search term does not rank the whole catalogue."""
        request = RequestFactory().get('/')
        request.user = User.objects.get(username='test')
        filterset = IngredientViewSet.filterset_class(
            {'prioritize_history': 'true'},
            queryset=Ingredient.objects.order_by(),
            request=request,
        )

        self.assertNotIn(LogItem._meta.db_table, str(filterset.qs.query))
        self.assertEqual(filterset.qs.query.order_by, ())

    def test_personal_search_ranks_in_one_query(self):
        """History ranking does not fetch diary entries or issue queries per ingredient."""
        self.prepare_personal_search()
        request = RequestFactory().get('/')
        request.user = User.objects.get(username='test')
        filterset = IngredientViewSet.filterset_class(
            {'name__search': 'history', 'prioritize_history': 'true'},
            queryset=Ingredient.objects.all(),
            request=request,
        )

        with self.assertNumQueries(1):
            ids = list(filterset.qs.values_list('pk', flat=True))

        self.assertEqual(set(ids[:2]), self.own_history)


class SearchIngredientApiTestCase(PersonalIngredientSearchTestMixin, BaseTestCase, ApiBaseTestCase):
    url = '/api/v2/ingredient/'

    def test_search_ordering_ends_in_a_unique_tiebreaker(self):
        """Names repeat, so without a unique key LIMIT returns a random subset."""
        for term in ('test', 'ab'):
            with self.subTest(term=term):
                filterset = IngredientFilterSet(
                    {'name__search': term},
                    queryset=Ingredient.objects.all(),
                )

                self.assertEqual(filterset.qs.query.order_by[-1], 'id')

    def test_basic_search_logged_out(self):
        """
        Logged-out users are also allowed to use the search
        """
        response = self.client.get(self.url + '?name__search=test&language__code=en')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertCountEqual(
            [(result['id'], result['name']) for result in response.data['results']],
            [(1, 'Test ingredient 1'), (2, 'Ingredient, test, 2, organic, raw')],
        )

    def test_basic_search_logged_in(self):
        """
        Logged-in users get the same results
        """
        self.authenticate('test')
        response = self.client.get(self.url + '?name__search=test&language__code=en')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertCountEqual(
            [(result['id'], result['name']) for result in response.data['results']],
            [(1, 'Test ingredient 1'), (2, 'Ingredient, test, 2, organic, raw')],
        )

    def test_search_language_code_en_no_results(self):
        """
        The "Testzutat" ingredient should not be found when searching in English
        """
        response = self.client.get(self.url + '?name__search=Testzutat&language__code=en')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_search_language_code_de(self):
        """
        The "Testzutat" ingredient should be only found when searching in German
        """
        response = self.client.get(self.url + '?name__search=Testzutat&language__code=de')
        result1 = response.data['results'][0]

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(result1['name'], 'Testzutat 123')
        self.assertEqual(result1['id'], 6)

    def test_search_several_language_codes(self):
        """
        Passing different language codes works correctly
        """
        response = self.client.get(self.url + '?name__search=guest&language__code=en,de')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_search_unknown_language_codes(self):
        """
        Unknown language codes are ignored
        """
        response = self.client.get(self.url + '?name__search=guest&language__code=en,de,kg')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_search_only_unknown_language_codes(self):
        """
        When all language codes are unknown the filter has no effect, not a silent English fallback
        """
        response = self.client.get(self.url + '?name__search=guest&language__code=kg')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 7)

    def test_search_all_languages(self):
        """
        Disable all language filters
        """
        response = self.client.get(self.url + '?name__search=guest')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 7)

    @patch('wger.nutrition.api.filtersets.IngredientFilterSet.search_barcode')
    def test_search_name_with_valid_barcode(self, mock_search_barcode):
        """
        Searching for an 8-14 digit number in the name field should trigger the OFF API lookup
        """
        mock_search_barcode.return_value = Ingredient.objects.none()
        self.client.get(self.url + '?name__search=1300000000000')

        args, kwargs = mock_search_barcode.call_args
        self.assertEqual(args[1], 'code')
        self.assertEqual(args[2], '1300000000000')

    @patch('wger.nutrition.api.filtersets.IngredientFilterSet.search_barcode')
    def test_search_name_with_text(self, mock_search_barcode):
        """
        Searching for a standard text string should fall back to full-text search
        """
        self.client.get(self.url + '?name__search=apples')
        mock_search_barcode.assert_not_called()

    @patch('wger.nutrition.api.filtersets.IngredientFilterSet.search_barcode')
    def test_search_name_with_short_number(self, mock_search_barcode):
        """
        Searching for a short number (<8) should fall back to full-text search
        """
        self.client.get(self.url + '?name__search=7000000')
        mock_search_barcode.assert_not_called()

    @patch('wger.nutrition.api.filtersets.IngredientFilterSet.search_barcode')
    def test_search_name_with_long_number(self, mock_search_barcode):
        """
        Searching for a long number (>14) should fall back to full-text search
        """
        self.client.get(self.url + '?name__search=150000000000000')
        mock_search_barcode.assert_not_called()

    @patch('wger.nutrition.api.filtersets.IngredientFilterSet.search_barcode')
    def test_search_name_returns_barcode(self, mock_search_barcode):
        """
        If search_barcode finds a match, it should return it
        """
        mock_search_barcode.return_value = Ingredient.objects.filter(pk=2)

        response = self.client.get(self.url + '?name__search=1300000000000')
        result1 = response.data['results'][0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(result1['name'], 'Ingredient, test, 2, organic, raw')
        self.assertEqual(result1['id'], 2)

    def test_filter_nutriscore_exact(self):
        """
        Exact match on nutriscore returns only ingredients with that grade
        """
        response = self.client.get(self.url + '?nutriscore=a')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_filter_nutriscore_in(self):
        """
        `in` lookup accepts a comma-separated list of grades
        """
        response = self.client.get(self.url + '?nutriscore__in=a,b')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 7)

    def test_filter_nutriscore_lt(self):
        """
        `lt` lookup returns ingredients with a better grade (e.g. better than C → A, B)
        """
        response = self.client.get(self.url + '?nutriscore__lt=c')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 7)

    def test_filter_nutriscore_lte(self):
        """
        `lte` lookup is inclusive (e.g. C or better → A, B, C)
        """
        response = self.client.get(self.url + '?nutriscore__lte=c')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 10)

    def test_filter_nutriscore_gt(self):
        """
        `gt` lookup returns ingredients with a worse grade (e.g. worse than C → D, E)
        """
        response = self.client.get(self.url + '?nutriscore__gt=c')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_filter_nutriscore_gte(self):
        """
        `gte` lookup is inclusive (e.g. C or worse → C, D, E)
        """
        response = self.client.get(self.url + '?nutriscore__gte=c')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6)

    def test_barcode_found_locally(self):
        """
        A barcode already in the database is returned without calling OFF
        """
        response = self.client.get(self.url + '?code=1234567890987654321')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], 1)

    @patch('wger.nutrition.api.filtersets.Ingredient.fetch_ingredient_from_off')
    def test_barcode_not_found_locally_off_succeeds(self, mock_fetch):
        """
        A barcode absent locally is fetched from OFF and the created ingredient is returned
        """
        mock_fetch.return_value = Ingredient.objects.get(pk=2)

        response = self.client.get(self.url + '?code=0000000000000')

        mock_fetch.assert_called_once_with('0000000000000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], 2)

    @patch('wger.nutrition.api.filtersets.Ingredient.fetch_ingredient_from_off')
    def test_barcode_not_found_locally_off_returns_none(self, mock_fetch):
        """
        A barcode unknown on OFF returns an empty result
        """
        mock_fetch.return_value = None

        response = self.client.get(self.url + '?code=0000000000000')

        mock_fetch.assert_called_once_with('0000000000000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)


@skipUnless(connection.vendor == 'postgresql', 'PostgreSQL ingredient search only')
class IngredientSearchRankingApiTestCase(BaseTestCase, ApiBaseTestCase):
    """Regression tests for ingredient search retrieval and ranking."""

    url = '/api/v2/ingredient/'

    corpus = (
        'Chicken',
        'Chicken, Boiled Without Salt',
        "'Nduja Chicken, Mozzarella, Slow Roast Tomato Sandwich",
        'Chickpea Salad',
        'Lunch out (placeholder)',
        'Pasta Carbonara, Bacon',
        '"Oat Milk Mocha" Oat Milk Latte Bar',
        'Milk',
        'Rice',
        'Rice Pudding',
        'Salty Liquorice',
        'Brown rice, long grain, cooked without salt',
        'Licorice',
        'Banana',
        'Banana Bread',
        'Salmon',
        'Smoked Salmon',
        'İstanbul',
        'Istanbul spice',
        'Butter',
        'Apple Buttrr Spread',
        '餅',
        '牛乳',
    )

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        for name in cls.corpus:
            Ingredient.objects.create(
                name=name,
                source_name='Test',
                language_id=2,
                energy=100,
                protein=10,
                carbohydrates=10,
                fat=10,
            )

    def search_names(self, query):
        response = self.client.get(
            self.url,
            {'name__search': query, 'language__code': 'en'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return [result['name'] for result in response.data['results']]

    def assert_ranked_before(self, names, first, second):
        self.assertIn(first, names)
        self.assertIn(second, names)
        self.assertLess(names.index(first), names.index(second))

    def test_substring_search_requires_an_indexable_trigram(self):
        self.assertFalse(_has_literal_trigram('q--'))
        self.assertTrue(_has_literal_trigram('jäätelö'))

    def test_search_finds_words_in_long_ingredient_names(self):
        cases = (
            ('chicken', 'Chicken, Boiled Without Salt'),
            ('chicken boiled', 'Chicken, Boiled Without Salt'),
            ('chicken', "'Nduja Chicken, Mozzarella, Slow Roast Tomato Sandwich"),
            ('lunch', 'Lunch out (placeholder)'),
            ('pasta', 'Pasta Carbonara, Bacon'),
            ('milk', '"Oat Milk Mocha" Oat Milk Latte Bar'),
            ('rice', 'Rice Pudding'),
            ('banana', 'Banana Bread'),
            ('salmon', 'Smoked Salmon'),
        )

        for query, expected_name in cases:
            with self.subTest(query=query, expected_name=expected_name):
                names = self.search_names(query)
                self.assertIn(expected_name, names)

    def test_search_ranks_exact_names_first(self):
        cases = ('Chicken', 'Milk', 'Rice', 'Banana', 'Salmon')

        for expected_name in cases:
            with self.subTest(expected_name=expected_name):
                names = self.search_names(expected_name.lower())
                self.assertEqual(names[:1], [expected_name])

    def test_search_ranks_leading_matches_before_later_word_matches(self):
        names = self.search_names('chicken')

        self.assertEqual(names[:1], ['Chicken'])
        self.assert_ranked_before(
            names,
            'Chicken, Boiled Without Salt',
            "'Nduja Chicken, Mozzarella, Slow Roast Tomato Sandwich",
        )

    def test_search_supports_partial_words(self):
        names = self.search_names('chick')

        self.assertIn('Chicken', names)
        self.assertIn('Chickpea Salad', names)

    def test_short_search_only_returns_exact_names(self):
        self.assertEqual(self.search_names('c'), [])
        self.assertEqual(self.search_names('ch'), [])
        self.assertEqual(self.search_names('餅'), ['餅'])
        self.assertEqual(self.search_names('牛乳'), ['牛乳'])

    def test_punctuation_only_search_returns_no_results(self):
        self.assertEqual(self.search_names('%'), [])

    def test_search_finds_a_correctly_spelled_name_from_a_typo(self):
        names = self.search_names('chickn')

        self.assertEqual(names[:1], ['Chicken'])

    def test_search_preserves_typo_matches_from_whole_name_similarity(self):
        names = self.search_names('chiken')

        self.assertEqual(names[:1], ['Chicken'])

    def test_search_ranks_whole_words_above_inside_word_matches(self):
        names = self.search_names('rice')

        self.assert_ranked_before(
            names,
            'Brown rice, long grain, cooked without salt',
            'Licorice',
        )

    def test_search_ranks_unicode_case_insensitive_exact_matches_first(self):
        names = self.search_names('istanbul')

        self.assertEqual(names[:2], ['İstanbul', 'Istanbul spice'])

    def test_search_does_not_rank_generic_substrings_above_fuzzy_matches(self):
        names = self.search_names('buttr')

        self.assert_ranked_before(names, 'Butter', 'Apple Buttrr Spread')
