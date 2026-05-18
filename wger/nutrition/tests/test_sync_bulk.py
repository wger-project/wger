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
import gzip
import importlib
import json
import shutil
import tempfile
from decimal import Decimal
from io import StringIO
from pathlib import Path
from unittest.mock import (
    MagicMock,
    patch,
)

# Django
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.nutrition.consts import SyncMode
from wger.nutrition.models import Ingredient
from wger.nutrition.sync import (
    _open_jsonl,
    download_ingredient_dump,
    export_ingredient_dump,
    sync_ingredients_from_dump,
)


SAMPLE_INGREDIENTS = [
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
        'license_title': 'Gâteau double chocolat',
        'license_object_url': '',
        'license_author': 'Open Food Facts',
        'license_author_url': '',
        'license_derivative_source_url': '',
        'language': 2,
        'weight_units': [
            {
                'id': 100,
                'uuid': 'a1b2c3d4-0000-0000-0000-000000000001',
                'name': 'Serving',
                'gram': 85,
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
        'license_title': 'Maxi Hot Dog New York Style',
        'license_object_url': '',
        'license_author': 'Open Food Facts',
        'license_author_url': '',
        'license_derivative_source_url': '',
        'language': 3,
        'weight_units': [],
    },
]


def _write_dump(path, ingredients, use_gzip=True):
    """Helper to write a JSONL dump file."""

    if use_gzip:
        with gzip.open(path, 'wt', encoding='utf-8') as f:
            for item in ingredients:
                f.write(json.dumps(item) + '\n')

    else:
        with open(path, 'w', encoding='utf-8') as f:
            for item in ingredients:
                f.write(json.dumps(item) + '\n')


class TestOpenJsonl(SimpleTestCase):
    """Test the _open_jsonl helper that handles both gzip and plain files."""

    def test_opens_gzip_file(self):
        with tempfile.NamedTemporaryFile(suffix='.jsonl.gz', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            _write_dump(tmp_path, SAMPLE_INGREDIENTS, use_gzip=True)
            with _open_jsonl(tmp_path) as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual(json.loads(lines[0])['name'], 'Gâteau double chocolat')
        finally:
            Path(tmp_path).unlink()

    def test_opens_plain_file(self):
        with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False, mode='w') as tmp:
            tmp_path = tmp.name

        try:
            _write_dump(tmp_path, SAMPLE_INGREDIENTS, use_gzip=False)
            with _open_jsonl(tmp_path) as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual(json.loads(lines[1])['name'], 'Maxi Hot Dog New York Style')
        finally:
            Path(tmp_path).unlink()


class TestExportIngredientDump(WgerTestCase):
    """Test exporting ingredients to a JSONL dump via default_storage."""

    def setUp(self):
        super().setUp()
        self.tmp_media = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_media, ignore_errors=True)
        super().tearDown()

    def _export(self):
        with self.settings(MEDIA_ROOT=self.tmp_media):
            return export_ingredient_dump(lambda x: x)

    def test_export_creates_file(self):
        """Test that export creates a valid gzipped JSONL file."""
        with self.settings(MEDIA_ROOT=self.tmp_media):
            saved_name = self._export()

            self.assertTrue(default_storage.exists(saved_name))

            # Read back and verify content
            with default_storage.open(saved_name, 'rb') as f:
                raw = f.read()

        lines = gzip.decompress(raw).decode('utf-8').strip().split('\n')

        # The test fixtures have 14 ingredients
        self.assertEqual(len(lines), 14)

        # Verify each line is valid JSON with expected fields
        for line in lines:
            data = json.loads(line)
            self.assertIn('uuid', data)
            self.assertIn('name', data)
            self.assertIn('energy', data)
            self.assertIn('protein', data)
            self.assertIn('language', data)

    def test_export_returns_storage_path(self):
        """Test that export returns the storage path."""
        saved_name = self._export()

        self.assertIn('ingredients', saved_name)
        self.assertTrue(saved_name.endswith('.jsonl.gz'))

    def test_export_overwrites_existing(self):
        """Test that a second export replaces the first."""
        saved_name_1 = self._export()
        saved_name_2 = self._export()

        self.assertEqual(saved_name_1, saved_name_2)

        with self.settings(MEDIA_ROOT=self.tmp_media):
            self.assertTrue(default_storage.exists(saved_name_2))


class TestSyncIngredientsFromDump(WgerTestCase):
    """Test importing ingredients from a JSONL dump file."""

    def _create_dump_file(self, ingredients=None, use_gzip=True):
        """Create a temporary dump file and return its path."""
        suffix = '.jsonl.gz' if use_gzip else '.jsonl'
        tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        tmp.close()
        _write_dump(tmp.name, ingredients or SAMPLE_INGREDIENTS, use_gzip=use_gzip)
        return tmp.name

    def test_update_mode_updates_existing(self):
        """Test that UPDATE mode updates existing ingredients by UUID."""
        file_path = self._create_dump_file()

        try:
            # Ingredient with this UUID already exists in fixtures
            ingredient = Ingredient.objects.get(uuid='7908c204-907f-4b1e-ad4e-f482e9769ade')
            self.assertEqual(ingredient.name, 'Test ingredient 1')

            count = sync_ingredients_from_dump(lambda x: x, file_path)

            ingredient.refresh_from_db()
            self.assertEqual(ingredient.name, 'Gâteau double chocolat')
            self.assertEqual(ingredient.energy, 360)
            self.assertAlmostEqual(ingredient.protein, Decimal(5), 2)
            self.assertEqual(count, 2)

            # Weight units synced
            units = ingredient.ingredientweightunit_set.all()
            self.assertEqual(units.count(), 1)
            self.assertEqual(units[0].name, 'Serving')
            self.assertEqual(units[0].gram, 85)
        finally:
            Path(file_path).unlink()

    def test_update_mode_creates_new(self):
        """Test that UPDATE mode creates new ingredients for unknown UUIDs."""
        file_path = self._create_dump_file()

        try:
            self.assertEqual(Ingredient.objects.count(), 14)

            sync_ingredients_from_dump(lambda x: x, file_path)

            self.assertEqual(Ingredient.objects.count(), 15)
            new_ingredient = Ingredient.objects.get(
                uuid='582f1b7f-a8bd-4951-9edd-247bc68b28f4',
            )
            self.assertEqual(new_ingredient.name, 'Maxi Hot Dog New York Style')
            self.assertEqual(new_ingredient.energy, 256)
        finally:
            Path(file_path).unlink()

    def test_insert_mode(self):
        """Test that INSERT mode bulk-creates ingredients."""
        file_path = self._create_dump_file()

        try:
            # Delete the ingredient that would conflict
            Ingredient.objects.filter(
                uuid='7908c204-907f-4b1e-ad4e-f482e9769ade',
            ).delete()

            initial_count = Ingredient.objects.count()
            count = sync_ingredients_from_dump(
                lambda x: x,
                file_path,
                mode=SyncMode.INSERT,
            )

            self.assertEqual(count, 2)
            self.assertEqual(Ingredient.objects.count(), initial_count + 2)
        finally:
            Path(file_path).unlink()

    def test_handles_plain_jsonl(self):
        """Test that import works with plain (non-gzipped) JSONL files."""
        file_path = self._create_dump_file(use_gzip=False)

        try:
            count = sync_ingredients_from_dump(lambda x: x, file_path)
            self.assertEqual(count, 2)
        finally:
            Path(file_path).unlink()

    def test_handles_invalid_json(self):
        """Test that invalid JSON lines are skipped."""
        tmp = tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False, mode='w')
        tmp.write('not valid json\n')
        tmp.write(json.dumps(SAMPLE_INGREDIENTS[1]) + '\n')
        tmp.close()

        try:
            count = sync_ingredients_from_dump(lambda x: x, tmp.name)
            self.assertEqual(count, 1)
        finally:
            Path(tmp.name).unlink()

    def test_handles_missing_uuid(self):
        """Test that entries without UUID are skipped."""
        bad_entry = {**SAMPLE_INGREDIENTS[0]}
        del bad_entry['uuid']

        tmp = tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False, mode='w')
        tmp.write(json.dumps(bad_entry) + '\n')
        tmp.write(json.dumps(SAMPLE_INGREDIENTS[1]) + '\n')
        tmp.close()

        try:
            count = sync_ingredients_from_dump(lambda x: x, tmp.name)
            self.assertEqual(count, 1)
        finally:
            Path(tmp.name).unlink()

    def test_returns_error_count(self):
        """Test that the function correctly tracks errors."""
        tmp = tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False, mode='w')
        tmp.write('bad json\n')
        tmp.write(json.dumps({'no_uuid': True}) + '\n')
        tmp.write(json.dumps(SAMPLE_INGREDIENTS[1]) + '\n')
        tmp.close()

        try:
            # We can't directly get the error count from return value,
            # but we can verify only valid entries are processed
            count = sync_ingredients_from_dump(lambda x: x, tmp.name)
            self.assertEqual(count, 1)
        finally:
            Path(tmp.name).unlink()

    def test_skips_ingredient_failing_sanity_checks(self):
        """An entry that fails sanity_checks() is skipped and the import continues."""
        bad_entry = {**SAMPLE_INGREDIENTS[0]}
        bad_entry['uuid'] = 'baaaaaad-0000-0000-0000-000000000001'
        bad_entry['protein'] = '150.000'  # > 100 -> fails sanity_checks()

        tmp = tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False, mode='w')
        tmp.write(json.dumps(bad_entry) + '\n')
        tmp.write(json.dumps(SAMPLE_INGREDIENTS[1]) + '\n')
        tmp.close()

        try:
            count = sync_ingredients_from_dump(lambda x: x, tmp.name)

            # Only the valid entry was imported; the malformed one was skipped
            self.assertEqual(count, 1)
            self.assertFalse(
                Ingredient.objects.filter(uuid='baaaaaad-0000-0000-0000-000000000001').exists()
            )
            self.assertTrue(
                Ingredient.objects.filter(uuid='582f1b7f-a8bd-4951-9edd-247bc68b28f4').exists()
            )
        finally:
            Path(tmp.name).unlink()


class TestDownloadIngredientDump(WgerTestCase):
    """Test downloading the ingredient dump from a remote server."""

    def _mock_response(self, status_code=200, content=b'fake gzip content'):
        mock = MagicMock()
        mock.status_code = status_code
        mock.headers = {'content-length': str(len(content))}
        mock.raw.stream.return_value = [content]
        return mock

    @patch('wger.nutrition.sync.requests.get')
    def test_download_success(self, mock_get: MagicMock):
        mock_get.return_value = self._mock_response()

        with tempfile.TemporaryDirectory() as folder:
            path = download_ingredient_dump(lambda x: x, folder=folder)

            self.assertTrue(path.exists())
            self.assertEqual(path.name, 'ingredients.jsonl.gz')

    @patch('wger.nutrition.sync.requests.get')
    def test_download_404_raises_file_not_found(self, mock_get: MagicMock):
        mock_get.return_value = self._mock_response(status_code=404)

        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(FileNotFoundError) as ctx:
                download_ingredient_dump(lambda x: x, folder=folder)

            self.assertIn('not found', str(ctx.exception).lower())
            self.assertIn('export-ingredients', str(ctx.exception))

    @patch('wger.nutrition.sync.requests.get')
    def test_download_server_error_raises(self, mock_get: MagicMock):
        mock_get.return_value = self._mock_response(status_code=500)

        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(Exception):
                download_ingredient_dump(lambda x: x, folder=folder)

    @patch('wger.nutrition.sync.requests.get')
    def test_download_skips_existing_file(self, mock_get: MagicMock):
        """Test that an already-downloaded file is reused."""
        with tempfile.TemporaryDirectory() as folder:
            file_path = Path(folder) / 'ingredients.jsonl.gz'
            file_path.write_text('existing')

            path = download_ingredient_dump(lambda x: x, folder=folder)

            self.assertEqual(path, file_path)
            mock_get.assert_not_called()

    @patch('wger.nutrition.sync.requests.get')
    def test_download_disables_content_decoding(self, mock_get: MagicMock):
        """Test that raw response decoding is disabled to preserve gzip."""
        mock_response = self._mock_response()
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as folder:
            download_ingredient_dump(lambda x: x, folder=folder)

        self.assertFalse(mock_response.raw.decode_content)


class TestBulkSyncManagementCommands(WgerTestCase):
    """Test the management commands for bulk export and import."""

    def test_export_ingredients_command(self):
        """Test the export-ingredients management command."""
        with tempfile.TemporaryDirectory() as tmp_media:
            with self.settings(MEDIA_ROOT=tmp_media):
                out = StringIO()
                call_command('export-ingredients', stdout=out)

                output = out.getvalue()
                self.assertIn('Exporting', output)
                self.assertIn('done!', output)

    def _get_command_module(self):
        """Get the sync-ingredients-bulk command module (hyphenated name needs importlib)."""
        return importlib.import_module('wger.nutrition.management.commands.sync-ingredients-bulk')

    @patch('wger.core.api.min_server_version.check_min_server_version')
    def test_bulk_sync_command_calls_functions(self, mock_version_check: MagicMock):
        """Test that the sync-ingredients-bulk command calls the right functions."""
        mod = self._get_command_module()

        with (
            patch.object(
                mod,
                'download_ingredient_dump',
                return_value=Path('/tmp/fake.jsonl.gz'),
            ) as mock_download,
            patch.object(mod, 'sync_ingredients_from_dump') as mock_sync,
        ):
            out = StringIO()
            call_command(
                'sync-ingredients-bulk',
                '--remote-url',
                'https://example.com',
                stdout=out,
            )

            mock_download.assert_called_once()
            mock_sync.assert_called_once()

    @patch('wger.core.api.min_server_version.check_min_server_version')
    def test_bulk_sync_command_handles_404(self, mock_version_check: MagicMock):
        """Test that the command shows a helpful error when dump is not found."""
        mod = self._get_command_module()

        with patch.object(
            mod,
            'download_ingredient_dump',
            side_effect=FileNotFoundError('Bulk ingredient dump not found'),
        ):
            out = StringIO()
            with self.assertRaises(CommandError):
                call_command(
                    'sync-ingredients-bulk',
                    '--remote-url',
                    'https://example.com',
                    stdout=out,
                )
