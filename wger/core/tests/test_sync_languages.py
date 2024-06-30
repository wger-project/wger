
import os
import json
from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from unittest.mock import patch

# wger
from wger.core.models import Language
from wger.core.tests.base_testcase import (
    WgerAccessTestCase,
    WgerAddTestCase,
    WgerDeleteTestCase,
    WgerEditTestCase,
    WgerTestCase,
    BaseTestCase
)
from wger.core.tests.test_language import (
    CreateLanguageTestCase,
    DeleteLanguageTestCase,
)


mock_json_data = [
            {"model": "core.language", "pk": 1, "fields": {"short_name": "de", "full_name": "Deutsch", "full_name_en": "German"}},
            {"model": "core.language", "pk": 2, "fields": {"short_name": "en", "full_name": "English", "full_name_en": "English"}},
        ]


class LanguageSyncResetTestCase(WgerTestCase):
    """
    Test the representation of a model
    """
    def setUp(self):
        # Create a temporary file with mock JSON data
        self.mock_json_data = [
            {"model": "core.language", "pk": 1, "fields": {"short_name": "de", "full_name": "Deutsch", "full_name_en": "German"}},
            {"model": "core.language", "pk": 2, "fields": {"short_name": "en", "full_name": "English", "full_name_en": "English"}},
        ]

        for lang in self.mock_json_data:
            language, created = Language.objects.update_or_create(
                short_name=lang["fields"]["short_name"],
                defaults={'full_name': lang["fields"]["full_name"], 'full_name_en': lang["fields"]["full_name_en"]},
            )
        call_command('loaddata', 'languages.json')
        self.temp_json_file = "temp_languages.json"
        with open(self.temp_json_file, "w") as f:
            json.dump(self.mock_json_data, f)

    def tearDown(self):
        # Remove the temporary file
        os.remove(self.temp_json_file)

    def test_command_functionality(self):
        """
        Test that the representation of an object is correct
        """
        self.assertEqual(f'{Language.objects.get(pk=1)}', 'Deutsch (de)')
        Language.objects.filter(id=1).delete()

        self.assertRaises(Language.DoesNotExist, lambda: Language.objects.get(pk=1))

        call_command('sync_core_languages')

        self.assertEqual(f'{Language.objects.get(pk=1)}', 'Deutsch (de)')
