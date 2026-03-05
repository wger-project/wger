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
import sys
import tempfile

# Django
import django
from django.core.management import (
    call_command,
    color_style,
    execute_from_command_line,
)

# Third Party
import requests
from invoke import (
    Collection,
    Program,
    task,
)
from tqdm import tqdm


logger = logging.getLogger(__name__)
FIXTURE_URL = 'https://github.com/wger-project/data/raw/master/fixtures/'

style = color_style()


@task(
    help={
        'address': 'Address to bind to. Default: localhost',
        'port': 'Port to use. Default: 8000',
        'settings-path': 'Path to settings file (absolute path). Leave empty for default',
        'extra-args': 'Additional arguments to pass to the builtin server. Pass as string: '
        '"--arg1 --arg2=value". Default: none',
    }
)
def start(context, address='localhost', port=8000, settings_path=None, extra_args=''):
    """
    Start the application using django's built in webserver
    """
    setup_django_environment(settings_path)

    argv = ['', 'runserver', '--noreload']
    if extra_args != '':
        for argument in extra_args.split(' '):
            argv.append(argument)
    argv.append(f'{address}:{port}')
    execute_from_command_line(argv)


@task(
    help={
        'settings-path': 'Path to settings file. Leave empty for default (settings.main)',
        'process-static': 'Whether to process static files (install npm packages and process css). Default: True',
    }
)
def bootstrap(context, settings_path=None, process_static=True):
    """
    Performs all steps necessary to bootstrap the application
    """
    setup_django_environment(settings_path)

    # Create Database if necessary
    if not database_exists():
        print('*** Database does not exist, creating one now')
        migrate_db(context, settings_path=settings_path)
        load_fixtures(context, settings_path=settings_path)
        create_or_reset_admin(context, settings_path=settings_path)

    # Download JS and CSS libraries
    if process_static:
        context.run('npm install')
        context.run('npm run build:css:sass')


@task(help={'settings-path': 'Path to settings file (absolute path). Leave empty for default'})
def create_or_reset_admin(context, settings_path: str = None):
    """
    Creates an admin user or resets the password for an existing one
    """
    setup_django_environment(settings_path)

    # can't be imported in global scope as it already requires
    # the settings module during import
    # Django
    from django.contrib.auth.models import User

    try:
        User.objects.get(username='admin')
        print("*** Password for user admin was reset to 'adminadmin'")
    except User.DoesNotExist:
        print('*** Created default admin user')

    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, 'core', 'fixtures/')

    call_command('loaddata', path + 'users.json')


@task(help={'settings-path': 'Path to settings file. Leave empty for default (settings.main)'})
def migrate_db(context, settings_path=None):
    """
    Run all database migrations
    """
    setup_django_environment(settings_path)

    call_command('migrate')


@task(help={'settings-path': 'Path to settings file. Leave empty for default (settings.main)'})
def load_fixtures(context, settings_path: str = None):
    """
    Loads all fixtures
    """
    setup_django_environment(settings_path)

    # Gym
    call_command('loaddata', 'gym.json')

    # Core
    call_command('loaddata', 'languages.json')
    call_command('loaddata', 'groups.json')
    call_command('loaddata', 'users.json')
    call_command('loaddata', 'licenses.json')
    call_command('loaddata', 'setting_repetition_units.json')
    call_command('loaddata', 'setting_weight_units.json')

    # Config
    call_command('loaddata', 'gym_config.json')

    # Manager

    # Exercises
    call_command('loaddata', 'equipment.json')
    call_command('loaddata', 'muscles.json')
    call_command('loaddata', 'categories.json')
    call_command('loaddata', 'exercise-base-data.json')
    call_command('loaddata', 'translations.json')

    # Gym
    call_command('loaddata', 'gym.json')
    call_command('loaddata', 'gym-config.json')
    call_command('loaddata', 'gym-adminconfig.json')


@task(help={'settings-path': 'Path to settings file. Leave empty for default (settings.main)'})
def load_online_fixtures(context, settings_path: str = None):
    """
    Downloads fixtures from server and installs them (at the moment only ingredients)
    """
    setup_django_environment(settings_path)

    # Prepare the download
    for name in ('ingredients', 'weight_units', 'ingredient_units'):
        url = f'{FIXTURE_URL}{name}.json.zip'

        print(f'Downloading fixture data from {url}...')
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        size = int(response.headers['content-length']) / (1024 * 1024)
        print(f'-> fixture size: {size:.3} MB')

        # Save to temporary file and load the data
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json.zip') as f:
            print(f'-> saving to temp file {f.name}')
            with tqdm(total=total_size, unit='B', unit_scale=True, desc='Downloading') as pbar:
                for data in response.iter_content(chunk_size=1024):
                    f.write(data)
                    pbar.update(len(data))
        f.close()
        print('Loading downloaded data, this may take a while...')
        call_command('loaddata', f.name, '--verbosity=3')
        print('-> removing temp file')
        print('')
        os.unlink(f.name)


#
#
# Helper functions
#
def setup_django_environment(settings_path: str = None):
    """
    Setup the django environment
    """
    if settings_path is not None:
        print(f'*** Using settings from argument: {settings_path}')
        os.environ['DJANGO_SETTINGS_MODULE'] = settings_path
    elif os.environ.get('DJANGO_SETTINGS_MODULE') is not None:
        print(f'*** Using settings from env: {os.environ.get("DJANGO_SETTINGS_MODULE")}')
    else:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings.main'
        print('*** No settings given, using settings.main')

    # Check if we are in the wger source folder
    if not os.path.isfile('manage.py'):
        print(style.ERROR('Error: please run this script from the wger checkout folder'))
        sys.exit(1)

    django.setup()


def database_exists():
    """Detect if the database exists"""

    # can't be imported in global scope as they already require
    # the settings module during import
    # Django
    from django.contrib.auth.models import User
    from django.core.exceptions import ImproperlyConfigured
    from django.db import DatabaseError

    try:
        User.objects.count()
    except DatabaseError:
        return False
    except ImproperlyConfigured as e:
        print(style.ERROR('Your settings file seems broken: '), e)
        sys.exit(0)
    else:
        return True


def make_program():
    ns = Collection(
        bootstrap,
        create_or_reset_admin,
        migrate_db,
        load_fixtures,
        load_online_fixtures,
    )
    return Program(namespace=ns)
    # program.run()
