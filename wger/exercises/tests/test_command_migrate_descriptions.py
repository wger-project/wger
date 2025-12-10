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
from io import StringIO

# Django
from django.core.management import call_command

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models import Translation


class TestMigrateDescriptionsCommand(WgerTestCase):
    """
    Tests the migrate descriptions command
    """

    def setUp(self):
        super().setUp()
        self.translation = Translation.objects.get(pk=1)

        self.raw_html = (
            '<p>This is <b>bold</b> and <i>italic</i>.</p><ul><li>Item 1</li><li>Item 2</li></ul>'
        )

        # Set to Legacy State (no markdown).
        Translation.objects.filter(pk=1).update(description=self.raw_html, description_source=None)
        self.translation.refresh_from_db()

    def test_migration_command(self):
        """
        Test that the command converts HTML to Markdown correctly for various tags.
        """

        out = StringIO()
        call_command('migrate_descriptions_to_markdown', stdout=out)

        self.translation.refresh_from_db()

        src = self.translation.description_source
        self.assertIsNotNone(src)
        self.assertTrue('**bold**' in src or '__bold__' in src)  # Markdownify config dependant
        self.assertTrue('*italic*' in src or '_italic_' in src)
        self.assertIn('* Item 1', src)
        self.assertIn('* Item 2', src)

        desc = self.translation.description
        self.assertIn('<strong>bold</strong>', desc)
        self.assertIn('<em>italic</em>', desc)
        self.assertIn('<ul>', desc)
        self.assertIn('<li>Item 1</li>', desc)
        self.assertIn('<p>', desc)

    def test_dry_run(self):
        """
        Test that dry-run does not alter the database.
        """

        out = StringIO()
        call_command('migrate_descriptions_to_markdown', '--dry-run', stdout=out)

        self.translation.refresh_from_db()

        self.assertIsNone(self.translation.description_source)
        self.assertIn('[Dry Run]', out.getvalue())
        self.assertEqual(self.translation.description, self.raw_html)
