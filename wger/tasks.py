# -*- coding: utf-8 -*-

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
import logging
import os
import pathlib
import sys
import tempfile

# Django
import django
from django.core.management import (
    call_command,
    execute_from_command_line
)
from django.utils.crypto import get_random_string

# Third Party
import requests
from invoke import task


logger = logging.getLogger(__name__)
FIXTURE_URL = 'https://github.com/wger-project/data/raw/master/fixtures/'


@task(help={'address': 'Address to bind to. Default: localhost',
            'port': 'Port to use. Default: 8000',
            'settings-path': 'Path to settings file (absolute path). Leave empty for '
                             'default',
            'extra-args': 'Additional arguments to pass to the builtin server. Pass as string: '
                          '"--arg1 --arg2=value". Default: none'})
def start(context, address='localhost', port=8000, browser=False, settings_path=None,
          extra_args=''):
    """
    Start the application using django's built in webserver
    """

    # Find the path to the settings and setup the django environment
    setup_django_environment(settings_path)

    argv = ["", "runserver", '--noreload']
    if extra_args != '':
        for argument in extra_args.split(' '):
            argv.append(argument)
    argv.append("{0}:{1}".format(address, port))
    execute_from_command_line(argv)


@task(help={'settings-path': 'Path to settings file (absolute path). Leave empty for '
                             'default',
            'database-path': 'Path to sqlite database (absolute path). Leave empty '
                             'for default'})
def bootstrap(context,
              settings_path=None,
              database_path=None):
    """
    Performs all steps necessary to bootstrap the application
    """

    # Create settings if necessary
    if settings_path is None:
        settings_path = get_path('settings.py')
    if not os.path.exists(settings_path):
        create_settings(context, settings_path=settings_path, database_path=database_path)

    # Find the path to the settings and setup the django environment
    setup_django_environment(settings_path)

    # Create Database if necessary
    if not database_exists():
        print('*** Database does not exist, creating one now')
        migrate_db(context, settings_path=settings_path)
        load_fixtures(context, settings_path=settings_path)
        create_or_reset_admin(context, settings_path=settings_path)

    # Download JS and CSS libraries
    context.run("yarn install")
    context.run("yarn build:css:sass")


@task(help={'settings-path': 'Path to settings file (absolute path). Leave empty for '
                             'default',
            'database-path': 'Path to sqlite database (absolute path). Leave empty '
                             'for default',
            'database-type': 'Database type to use. Supported: sqlite3, postgresql. Default: '
                             'sqlite3',
            'key-length': 'Length of the generated secret key. Default: 50'})
def create_settings(context,
                    settings_path=None,
                    database_path=None,
                    database_type='sqlite3',
                    key_length=50):
    """
    Creates a local settings file
    """
    if settings_path is None:
        settings_path = get_path('settings.py')

    settings_module = os.path.dirname(settings_path)
    print("*** Creating settings file at {0}".format(settings_module))

    if database_path is None:
        database_path = get_path('database.sqlite').as_posix()
    dbpath_value = database_path

    media_folder_path = get_path('media').as_posix()

    # Use localhost with default django port if no URL given
    url = 'http://localhost:8000'

    # Fill in the config file template
    settings_template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.tpl')
    with open(settings_template, 'r') as settings_file:
        settings_content = settings_file.read()

    if database_type == 'postgresql':
        dbengine = 'postgresql_psycopg2'
        dbname = 'wger'
        dbuser = 'wger'
        dbpassword = 'wger'
        dbhost = 'localhost'
        dbport = 5432
    elif database_type == 'sqlite3':
        dbengine = 'sqlite3'
        dbname = dbpath_value
        dbuser = ''
        dbpassword = ''
        dbhost = ''
        dbport = ''

    # Create a random SECRET_KEY to put it in the settings.
    # from django.core.management.commands.startproject
    secret_key = get_random_string(key_length, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')

    settings_content = settings_content.format(dbname=dbname,
                                               dbpath=dbpath_value,
                                               dbengine=dbengine,
                                               dbuser=dbuser,
                                               dbpassword=dbpassword,
                                               dbhost=dbhost,
                                               dbport=dbport,
                                               default_key=secret_key,
                                               siteurl=url,
                                               media_folder_path=media_folder_path)

    if not os.path.exists(settings_module):
        os.makedirs(settings_module)

    if not os.path.exists(os.path.dirname(database_path)):
        os.makedirs(os.path.dirname(database_path))

    with open(settings_path, 'w') as settings_file:
        settings_file.write(settings_content)


@task(help={'settings-path': 'Path to settings file (absolute path). Leave empty for '
                             'default'})
def create_or_reset_admin(context, settings_path=None):
    """
    Creates an admin user or resets the password for an existing one
    """

    # Find the path to the settings and setup the django environment
    setup_django_environment(settings_path)

    # can't be imported in global scope as it already requires
    # the settings module during import
    # wger
    from wger.manager.models import User
    try:
        User.objects.get(username="admin")
        print("*** Password for user admin was reset to 'adminadmin'")
    except User.DoesNotExist:
        print("*** Created default admin user")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, 'core', 'fixtures/')

    call_command("loaddata", path + "users.json")


@task(help={'settings-path': 'Path to settings file (absolute path). Leave empty for '
                             'default'})
def migrate_db(context, settings_path=None):
    """
    Run all database migrations
    """

    # Find the path to the settings and setup the django environment
    setup_django_environment(settings_path)

    call_command("migrate")


@task(help={'settings-path': 'Path to settings file (absolute path). Leave empty for '
                             'default'})
def load_fixtures(context, settings_path=None):
    """
    Loads all fixtures
    """

    # Find the path to the settings and setup the django environment
    setup_django_environment(settings_path)

    # Gym
    call_command("loaddata", "gym.json")

    # Core
    call_command("loaddata", "languages.json")
    call_command("loaddata", "groups.json")
    call_command("loaddata", "users.json")
    call_command("loaddata", "licenses.json")
    call_command("loaddata", "days_of_week.json")
    call_command("loaddata", "setting_repetition_units.json")
    call_command("loaddata", "setting_weight_units.json")

    # Config
    call_command("loaddata", "language_config.json")
    call_command("loaddata", "gym_config.json")

    # Manager

    # Exercises
    call_command("loaddata", "equipment.json")
    call_command("loaddata", "muscles.json")
    call_command("loaddata", "categories.json")
    call_command("loaddata", "exercise-base-data.json")
    call_command("loaddata", "exercises.json")

    # Gym
    call_command("loaddata", "gym.json")
    call_command("loaddata", "gym-config.json")
    call_command("loaddata", "gym-adminconfig.json")


@task(help={'settings-path': 'Path to settings file (absolute path). Leave empty for '
                             'default'})
def load_online_fixtures(context, settings_path=None):
    """
    Downloads fixtures from server and installs them (at the moment only ingredients)
    """

    # Find the path to the settings and setup the django environment
    setup_django_environment(settings_path)

    # Prepare the download
    for name in ('ingredients', 'weight_units', 'ingredient_units'):
        url = f'{FIXTURE_URL}{name}.json.zip'

        print(f'Downloading fixture data from {url}...')
        response = requests.get(url, stream=True)
        size = int(response.headers["content-length"]) / (1024 * 1024)
        print(f'-> fixture size: {size:.3} MB')

        # Save to temporary file and load the data
        f = tempfile.NamedTemporaryFile(delete=False, suffix='.json.zip')
        print(f'-> saving to temp file {f.name}')
        f.write(response.content)
        f.close()
        call_command("loaddata", f.name)
        print('-> removing temp file')
        print('')
        os.unlink(f.name)


@task
def config_location(context):
    """
    Returns the default location for the settings file and the data folder
    """
    print('Default locations:')
    print('* settings:      {0}'.format(get_path('settings.py')))
    print('* media folder:  {0}'.format(get_path('media')))
    print('* database path: {0}'.format(get_path('database.sqlite')))


#
#
# Helper functions
#
# Note: these functions were originally in wger/utils/main.py but were moved
#       here because of different import problems (the packaged pip-installed
#       packaged has a different sys path than the local one)
#

def get_path(file="settings.py") -> pathlib.Path:
    """
    Return the path of the given file relatively to the wger source folder

    Note: one parent is the step from e.g. some-checkout/wger/settings.py
    to some-checkout/wger, the second one to get to the source folder
    itself.
    """
    return (pathlib.Path(__file__).parent.parent / file).resolve()


def setup_django_environment(settings_path):
    """
    Setup the django environment
    """

    # Use default settings if the user didn't specify something else
    if settings_path is None:
        settings_path = get_path('settings.py').as_posix()
        print('*** No settings given, using {0}'.format(settings_path))

    # Find out file path and fine name of settings and setup django
    settings_file = os.path.basename(settings_path)
    settings_module_name = "".join(settings_file.split('.')[:-1])
    if '.' in settings_module_name:
        print("'.' is not an allowed character in the settings-file")
        sys.exit(1)
    settings_module_dir = os.path.dirname(settings_path)
    sys.path.append(settings_module_dir)
    os.environ[django.conf.ENVIRONMENT_VARIABLE] = '%s' % settings_module_name
    django.setup()


def database_exists():
    """Detect if the database exists"""

    # can't be imported in global scope as they already require
    # the settings module during import
    # Django
    from django.core.exceptions import ImproperlyConfigured
    from django.db import DatabaseError

    # wger
    from wger.manager.models import User

    try:
        # TODO: Use another model, the User could be deactivated
        User.objects.count()
    except DatabaseError:
        return False
    except ImproperlyConfigured:
        print("Your settings file seems broken")
        sys.exit(0)
    else:
        return True
