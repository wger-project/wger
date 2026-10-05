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
import os
import tempfile
from unittest import mock

# Django
from django.contrib.auth.models import User
from django.db import OperationalError
from django.test import (
    SimpleTestCase,
    TestCase,
)

# Third Party
from invoke import (
    Config,
    Context,
)

# wger
from wger import tasks
from wger.tasks import WgerConfig


class WgerConfigTestCase(SimpleTestCase):
    """
    Test the invoke configuration used by the CLI
    """

    def test_user_config_file_is_ignored(self):
        with tempfile.TemporaryDirectory() as home:
            with open(os.path.join(home, '.invoke.yaml'), 'w') as config_file:
                config_file.write('run:\n  echo: true\n')

            with mock.patch.dict(os.environ, {'HOME': home}):
                # Sanity check, invoke's own config does read the file
                self.assertTrue(Config().run.echo)

                self.assertFalse(WgerConfig().run.echo)


class BootstrapTestCase(TestCase):
    """
    Test that bootstrapping never touches the data of an existing installation
    """

    fixtures = (
        'gym',
        'gym_config',
        'groups',
        'languages',
    )

    def setUp(self):
        self.context = Context()

    @mock.patch('wger.tasks.load_admin_fixture')
    @mock.patch('wger.tasks.load_fixtures')
    @mock.patch('wger.tasks.migrate_db')
    @mock.patch('wger.tasks.setup_django_environment')
    def test_existing_installation_is_left_alone(self, setup, migrate, fixtures, admin_fixture):
        User.objects.create_user('admin', password='secret')

        tasks.bootstrap(self.context, process_static=False)

        migrate.assert_not_called()
        fixtures.assert_not_called()
        admin_fixture.assert_not_called()
        self.assertTrue(User.objects.get(username='admin').check_password('secret'))

    @mock.patch('wger.tasks.load_admin_fixture')
    @mock.patch('wger.tasks.load_fixtures')
    @mock.patch('wger.tasks.migrate_db')
    @mock.patch('wger.tasks.setup_django_environment')
    def test_unreachable_database_is_an_error(self, setup, migrate, fixtures, admin):
        User.objects.create_user('admin', password='secret')

        with mock.patch(
            'django.db.connection.ensure_connection',
            side_effect=OperationalError('connection refused'),
        ):
            with self.assertRaises(OperationalError):
                tasks.bootstrap(self.context, process_static=False)

        migrate.assert_not_called()
        fixtures.assert_not_called()
        admin.assert_not_called()
        self.assertTrue(User.objects.get(username='admin').check_password('secret'))

    @mock.patch('wger.tasks.load_admin_fixture')
    @mock.patch('wger.tasks.load_fixtures')
    @mock.patch('wger.tasks.migrate_db')
    @mock.patch('wger.tasks.setup_django_environment')
    def test_empty_database_is_initialised(self, setup, migrate, fixtures, admin_fixture):
        tasks.bootstrap(self.context, process_static=False)

        migrate.assert_called_once()
        fixtures.assert_called_once()
        admin_fixture.assert_called_once()

    def test_ensure_admin_user_creates_missing_admin(self):
        tasks.ensure_admin_user()

        self.assertTrue(User.objects.get(username='admin').check_password('adminadmin'))

    def test_ensure_admin_user_keeps_existing_password(self):
        User.objects.create_user('admin', password='secret')

        tasks.ensure_admin_user()

        self.assertTrue(User.objects.get(username='admin').check_password('secret'))
