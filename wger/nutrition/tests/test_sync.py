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

# Standard Library
from decimal import Decimal
from unittest.mock import (
    MagicMock,
    patch,
)
from uuid import UUID

# Django
from django.core.management import CommandError

# Third Party
import requests

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.nutrition.models import (
    Ingredient,
    IngredientWeightUnit,
)
from wger.nutrition.sync import sync_ingredients
from wger.nutrition.tasks import (
    sync_all_ingredients_chunked_task,
    sync_ingredient_id_range_task,
)
from wger.utils.requests import wger_headers


class MockIngredientResponse:
    def __init__(self):
        self.status_code = 200
        self.content = b'1234'

    @staticmethod
    def json():
        return {
            'count': 2,
            'next': None,
            'previous': None,
            'results': [
                {
                    'id': 1,
                    'uuid': '7908c204-907f-4b1e-ad4e-f482e9769ade',
                    'code': '0013087245950',
                    'name': 'Gâteau double chocolat',
                    'created': '2020-12-20T01:00:00+01:00',
                    'last_update': '2020-12-20T01:00:00+01:00',
                    'energy': 360,
                    'protein': '5.000',
                    'carbohydrates': '45.000',
                    'carbohydrates_sugar': '27.000',
                    'fat': '18.000',
                    'fat_saturated': '4.500',
                    'fiber': '2.000',
                    'sodium': '0.356',
                    'license': 5,
                    'license_title': ' Gâteau double chocolat ',
                    'license_object_url': '',
                    'license_author': 'Open Food Facts',
                    'license_author_url': '',
                    'license_derivative_source_url': '',
                    'language': 2,
                    'is_vegan': True,
                    'is_vegetarian': True,
                    'nutriscore': 'd',
                    'weight_units': [
                        {
                            'id': 100,
                            'uuid': 'a1b2c3d4-0000-0000-0000-000000000001',
                            'name': 'Serving',
                            'gram': 85,
                        },
                        {
                            'id': 101,
                            'uuid': 'a1b2c3d4-0000-0000-0000-000000000002',
                            'name': '1 Portion (2 slices)',
                            'gram': 60,
                        },
                    ],
                },
                {
                    'id': 22634,
                    'uuid': '582f1b7f-a8bd-4951-9edd-247bc68b28f4',
                    'code': '3181238941963',
                    'name': 'Maxi Hot Dog New York Style',
                    'created': '2020-12-20T01:00:00+01:00',
                    'last_update': '2020-12-20T01:00:00+01:00',
                    'energy': 256,
                    'protein': '11.000',
                    'carbohydrates': '27.000',
                    'carbohydrates_sugar': '5.600',
                    'fat': '11.000',
                    'fat_saturated': '4.600',
                    'fiber': None,
                    'sodium': '0.820',
                    'license': 5,
                    'license_title': ' Maxi Hot Dog New York Style',
                    'license_object_url': '',
                    'license_author': 'Open Food Facts',
                    'license_author_url': '',
                    'license_derivative_source_url': '',
                    'language': 3,
                    'is_vegan': None,
                    'is_vegetarian': None,
                    'nutriscore': None,
                    'weight_units': [],
                },
            ],
        }


class TestSyncMethods(WgerTestCase):
    @patch('requests.get', return_value=MockIngredientResponse())
    def test_ingredient_sync(self, mock_request):
        # Arrange
        ingredient = Ingredient.objects.get(pk=1)

        self.assertEqual(Ingredient.objects.count(), 14)
        self.assertEqual(ingredient.name, 'Test ingredient 1')
        self.assertEqual(ingredient.energy, 176)
        self.assertAlmostEqual(ingredient.protein, Decimal(25.63), 2)
        self.assertEqual(ingredient.code, '1234567890987654321')

        # Act
        sync_ingredients(lambda x: x)
        # The last call is the cursor sync URL — the first call probes the
        # regular endpoint for `count` so the progress bar can show ETA.
        mock_request.assert_called_with(
            'https://wger.de/api/v2/ingredient-sync/?page_size=999',
            headers=wger_headers(),
        )

        # Assert
        self.assertEqual(Ingredient.objects.count(), 15)

        ingredient = Ingredient.objects.get(pk=1)
        self.assertEqual(ingredient.name, 'Gâteau double chocolat')
        self.assertEqual(ingredient.energy, 360)
        self.assertAlmostEqual(ingredient.protein, Decimal(5), 2)
        self.assertEqual(ingredient.code, '0013087245950')
        self.assertEqual(ingredient.license.pk, 5)
        self.assertEqual(ingredient.uuid, UUID('7908c204-907f-4b1e-ad4e-f482e9769ade'))
        self.assertTrue(ingredient.is_vegan)
        self.assertTrue(ingredient.is_vegetarian)
        self.assertEqual(ingredient.nutriscore, 'd')

        # Weight units synced
        units = ingredient.ingredientweightunit_set.order_by('gram')
        self.assertEqual(units.count(), 2)
        self.assertEqual(units[0].name, '1 Portion (2 slices)')
        self.assertEqual(units[0].gram, 60)
        self.assertEqual(units[1].name, 'Serving')
        self.assertEqual(units[1].gram, 85)

        new_ingredient = Ingredient.objects.get(uuid='582f1b7f-a8bd-4951-9edd-247bc68b28f4')
        self.assertEqual(new_ingredient.name, 'Maxi Hot Dog New York Style')
        self.assertEqual(new_ingredient.energy, 256)
        self.assertAlmostEqual(new_ingredient.protein, Decimal(11), 2)
        self.assertEqual(new_ingredient.code, '3181238941963')
        self.assertIsNone(new_ingredient.is_vegan)
        self.assertIsNone(new_ingredient.is_vegetarian)
        self.assertIsNone(new_ingredient.nutriscore)
        self.assertEqual(new_ingredient.ingredientweightunit_set.count(), 0)

    @patch('requests.get', return_value=MockIngredientResponse())
    def test_sync_removes_deleted_weight_units(self, mock_request):
        """Weight units that no longer exist on the remote are deleted locally"""
        # Arrange - sync once to create the weight units
        sync_ingredients(lambda x: x)
        ingredient = Ingredient.objects.get(pk=1)
        self.assertEqual(ingredient.ingredientweightunit_set.count(), 2)

        # Add a local-only unit that doesn't exist on the remote
        IngredientWeightUnit.objects.create(ingredient=ingredient, name='Local only', gram=999)
        self.assertEqual(ingredient.ingredientweightunit_set.count(), 3)

        # Act - sync again
        sync_ingredients(lambda x: x)

        # Assert - local-only unit should be removed
        self.assertEqual(ingredient.ingredientweightunit_set.count(), 2)

    @patch('requests.get')
    def test_sync_skips_ingredient_failing_sanity_checks(self, mock_request):
        """A record that fails sanity_checks() is skipped without aborting the sync."""
        response = MagicMock()
        response.json.return_value = {
            'count': 2,
            'next': None,
            'previous': None,
            'results': [
                {
                    # protein > 100 -> fails IngredientData.sanity_checks()
                    'id': 1,
                    'uuid': 'baaaaaad-0000-0000-0000-000000000001',
                    'code': 'bogus-code',
                    'name': 'Bogus ingredient',
                    'created': '2020-12-20T01:00:00+01:00',
                    'last_update': '2020-12-20T01:00:00+01:00',
                    'energy': 200,
                    'protein': '150.000',
                    'carbohydrates': '10.000',
                    'fat': '10.000',
                    'language': 2,
                    'license': 5,
                    'license_author': 'Open Food Facts',
                    'weight_units': [],
                },
                {
                    'id': 2,
                    'uuid': '582f1b7f-a8bd-4951-9edd-247bc68b28f4',
                    'code': '3181238941963',
                    'name': 'Maxi Hot Dog New York Style',
                    'created': '2020-12-20T01:00:00+01:00',
                    'last_update': '2020-12-20T01:00:00+01:00',
                    'energy': 256,
                    'protein': '11.000',
                    'carbohydrates': '27.000',
                    'fat': '11.000',
                    'language': 3,
                    'license': 5,
                    'license_author': 'Open Food Facts',
                    'weight_units': [],
                },
            ],
        }
        mock_request.return_value = response

        count_before = Ingredient.objects.count()

        # A single malformed record must not abort the whole run
        sync_ingredients(lambda x: x)

        # The valid ingredient was synced, the malformed one was skipped
        self.assertTrue(
            Ingredient.objects.filter(uuid='582f1b7f-a8bd-4951-9edd-247bc68b28f4').exists()
        )
        self.assertFalse(
            Ingredient.objects.filter(uuid='baaaaaad-0000-0000-0000-000000000001').exists()
        )
        self.assertEqual(Ingredient.objects.count(), count_before + 1)

    @patch('requests.get', return_value=MockIngredientResponse())
    def test_ingredient_sync_languages(self, mock_request):
        # Call the function with the language_codes parameter
        sync_ingredients(lambda x: x, language_codes='en')

        # Assert that the correct URL is called with the expected parameters
        expected_url = 'https://wger.de/api/v2/ingredient-sync/?language__in=2&page_size=999'
        mock_request.assert_called_with(
            expected_url,
            headers=wger_headers(),
        )

    @patch('requests.get', return_value=MockIngredientResponse())
    def test_ingredient_sync_incremental(self, mock_request):
        """Incremental sync passes `last_update__gt` to the cursor endpoint."""
        sync_ingredients(lambda x: x, last_update_gt='2026-04-20T00:00:00Z')

        expected_url = (
            'https://wger.de/api/v2/ingredient-sync/'
            '?last_update__gt=2026-04-20T00:00:00Z&page_size=999'
        )
        mock_request.assert_called_with(
            expected_url,
            headers=wger_headers(),
        )

    @patch('requests.get', return_value=MockIngredientResponse())
    def test_ingredient_sync_fetches_count_when_progress_bar_enabled(self, mock_request):
        """With show_progress_bar=True, the first call probes for the total count.

        Cursor pagination has no `count` field, so we look up the total via
        the regular OFFSET endpoint (?limit=1) before starting the cursor
        walk so the progress bar can show percentage and ETA.
        """
        sync_ingredients(lambda x: x, show_progress_bar=True)

        # First call probes the regular endpoint for count.
        first_call_args = mock_request.call_args_list[0].args
        self.assertIn('/api/v2/ingredient/', first_call_args[0])
        self.assertIn('limit=1', first_call_args[0])

        # Last call is the cursor sync URL.
        last_call_args = mock_request.call_args_list[-1].args
        self.assertIn('/api/v2/ingredient-sync/', last_call_args[0])

    @patch('requests.get', return_value=MockIngredientResponse())
    def test_ingredient_sync_skips_count_probe_without_progress_bar(self, mock_request):
        """Without progress-bar, the count probe is skipped to save a request.

        Celery range-workers run with show_progress_bar=False (the default), so
        skipping this probe avoids ~120 unnecessary `ingredient_list`-scoped
        requests per chunked sync run.
        """
        sync_ingredients(lambda x: x)

        # All calls go to the cursor endpoint; none to the regular one.
        for call in mock_request.call_args_list:
            self.assertIn('/api/v2/ingredient-sync/', call.args[0])
            self.assertNotIn('/api/v2/ingredient/?', call.args[0])

    @patch('requests.get')
    def test_ingredient_sync_continues_when_count_fetch_fails(self, mock_request):
        """A failing count fetch must not abort the sync — fallback to no-ETA bar."""
        # First call (count) raises, subsequent calls return a valid response
        # so the cursor sync can proceed.
        responses = [
            requests.exceptions.RequestException('count fetch failed'),
            MockIngredientResponse(),
        ]

        def side_effect(*args, **kwargs):
            r = responses.pop(0)
            if isinstance(r, Exception):
                raise r
            return r

        mock_request.side_effect = side_effect
        # show_progress_bar=True forces the count probe path
        sync_ingredients(lambda x: x, show_progress_bar=True)
        # Both calls were made
        self.assertGreaterEqual(mock_request.call_count, 2)

    @patch('wger.nutrition.tasks.requests.get')
    @patch('wger.nutrition.tasks.check_min_server_version')
    def test_chunked_sync_aborts_on_incompatible_remote(self, mock_check_version, mock_request):
        """The chunked orchestrator must refuse to sync against an incompatible remote.

        This protects users on outdated wger versions whose Celery beat schedule
        still calls this task directly (instead of going through the bulk wrapper).
        """
        mock_check_version.side_effect = CommandError('Remote requires version 2.5.0')

        sync_all_ingredients_chunked_task(remote_url='https://example.com')

        mock_check_version.assert_called_once_with('https://example.com')
        # No API requests must be made when the version check fails.
        mock_request.assert_not_called()

    @patch('wger.nutrition.tasks.group')
    @patch('wger.nutrition.tasks.sync_ingredient_id_range_task')
    @patch('wger.nutrition.tasks.requests.get')
    @patch('wger.nutrition.tasks.check_min_server_version')
    def test_chunked_sync_dispatches_id_range_tasks(
        self, mock_check_version, mock_request, mock_id_range_task, mock_group
    ):
        """Orchestrator splits the id space into ID_RANGE_SIZE-row chunks."""
        # wger
        from wger.nutrition.tasks import ID_RANGE_SIZE

        # Remote pretends to have ingredients up to id = 60_000 (so 3 chunks
        # at the default ID_RANGE_SIZE = 25_000).
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'count': 50_000,
            'results': [{'id': 60_000}],
        }
        mock_request.return_value = mock_response

        sync_all_ingredients_chunked_task(remote_url='https://example.com')

        # The probe URL fetches the highest-id row.
        probe_url = mock_request.call_args.args[0]
        self.assertIn('ordering=-id', probe_url)
        self.assertIn('limit=1', probe_url)

        # Three id-range tasks dispatched: [0, 25k), [25k, 50k), [50k, 75k).
        self.assertEqual(mock_id_range_task.s.call_count, 3)
        for i, call in enumerate(mock_id_range_task.s.call_args_list):
            id_gte, id_lt, remote, language_codes = call.args
            self.assertEqual(id_gte, i * ID_RANGE_SIZE)
            self.assertEqual(id_lt, (i + 1) * ID_RANGE_SIZE)
            self.assertEqual(remote, 'https://example.com')
            self.assertIsNone(language_codes)

        # The group of tasks is dispatched to celery.
        mock_group.return_value.apply_async.assert_called_once()

    @patch('wger.nutrition.tasks.requests.get')
    @patch('wger.nutrition.tasks.check_min_server_version')
    def test_chunked_sync_handles_empty_remote(self, mock_check_version, mock_request):
        """If the remote has zero ingredients, the orchestrator returns cleanly."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'count': 0, 'results': []}
        mock_request.return_value = mock_response

        # Should not raise, should not dispatch any tasks
        result = sync_all_ingredients_chunked_task(remote_url='https://example.com')
        self.assertIsNone(result)

    @patch('wger.nutrition.tasks.sync_ingredients')
    def test_id_range_task_passes_filter_params(self, mock_sync):
        """The worker task forwards id_gte/id_lt to sync_ingredients."""
        sync_ingredient_id_range_task(
            id_gte=25_000,
            id_lt=50_000,
            remote_url='https://example.com',
            language_codes='en',
        )

        mock_sync.assert_called_once()
        kwargs = mock_sync.call_args.kwargs
        self.assertEqual(kwargs['id_gte'], 25_000)
        self.assertEqual(kwargs['id_lt'], 50_000)
        self.assertEqual(kwargs['remote_url'], 'https://example.com')
        self.assertEqual(kwargs['language_codes'], 'en')


class SyncIngredientsCommandTestCase(WgerTestCase):
    """
    Tests for the `sync-ingredients` management command.

    The `@patch('wger.core.api.min_server_version.check_min_server_version')`
    decorator is mandatory: it must be active when `_get_command_module()`
    triggers loading of `wger_command.py`, so the latter's
    `from ... import check_min_server_version` binds to a Mock instead of the
    real function. (Same pattern as `test_sync_bulk.py`.)
    """

    def _get_command_module(self):
        """The hyphenated module name needs importlib."""
        # Standard Library
        import importlib

        return importlib.import_module('wger.nutrition.management.commands.sync-ingredients')

    @patch('wger.core.api.min_server_version.check_min_server_version')
    def test_since_accepts_iso_date(self, mock_version_check):
        """Plain ISO date `YYYY-MM-DD` is accepted as `--since` value."""
        # Django
        from django.core.management import call_command

        mod = self._get_command_module()
        with patch.object(mod, 'sync_ingredients') as mock_sync:
            call_command('sync-ingredients', '--since', '2026-04-01')
            mock_sync.assert_called_once()
            self.assertEqual(mock_sync.call_args.kwargs['last_update_gt'], '2026-04-01')

    @patch('wger.core.api.min_server_version.check_min_server_version')
    def test_since_accepts_iso_datetime(self, mock_version_check):
        """Full ISO-8601 datetime is accepted as `--since` value."""
        # Django
        from django.core.management import call_command

        mod = self._get_command_module()
        with patch.object(mod, 'sync_ingredients') as mock_sync:
            call_command('sync-ingredients', '--since', '2026-04-01T12:34:56Z')
            mock_sync.assert_called_once()
            self.assertEqual(mock_sync.call_args.kwargs['last_update_gt'], '2026-04-01T12:34:56Z')

    @patch('wger.core.api.min_server_version.check_min_server_version')
    def test_since_rejects_garbage(self, mock_version_check):
        """A non-parseable `--since` value must abort the command before syncing."""
        # Django
        from django.core.management import call_command

        mod = self._get_command_module()
        with patch.object(mod, 'sync_ingredients') as mock_sync:
            with self.assertRaises(CommandError) as cm:
                call_command('sync-ingredients', '--since', 'yesterday')

            self.assertIn('ISO-8601', str(cm.exception))
            mock_sync.assert_not_called()
