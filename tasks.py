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

import inspect
import os

from invoke import task

from django.utils.crypto import get_random_string
from django.core.management import (
    call_command,
    execute_from_command_line
)

from wger.utils.main import (
    get_user_data_path,
    get_user_config_path,
    detect_listen_opts,
    setup_django_environment,
    database_exists,
    start_browser
)


@task(help={'address': 'Address to bind to. Default: localhost',
            'port': 'Port to use. Default: 8000',
            'browser': 'Whether to open the application in a browser window. Default: false',
            'settings-path': 'Path to settings file (absolute path recommended). Leave empty for default',
            'extra-args': 'Additional arguments to pass to the builtin server. Pass as string: "--arg1 --arg2=value". Default: none'})
def start_wger(address='localhost', port=8000, browser=False, settings_path=None, extra_args=''):
    '''
    Start the application using django's built in webserver
    '''
    if browser:
        start_browser("http://{0}:{1}".format(address, port))

    # Find the path to the settings and setup the django environment
    setup_django_environment(settings_path)

    argv = ["", "runserver", '--noreload']
    if extra_args != '':
        for argument in extra_args.split(' '):
            argv.append(argument)
    argv.append("{0}:{1}".format(address, port))
    execute_from_command_line(argv)


@task(help={'settings-path': 'Path to settings file (absolute path recommended). Leave empty for default',
            'database-path': 'Path to sqlite database (absolute path recommended). Leave empty for default',
            'address': 'Address to use. Default: localhost',
            'port': 'Port to use. Default: 8000',
            'browser': 'Whether to open the application in a browser window. Default: false'})
def bootstrap_wger(settings_path=None, database_path=None, address='localhost', port=8000, browser=False):
    '''
    Performs all steps necessary to bootstrap the application
    '''

    # Find url to wger
    address, port = detect_listen_opts(address, port)
    if port == 80:
        url = "http://{0}".format(address)
    else:
        url = "http://{0}:{1}".format(address, port)

    # Create settings if necessary
    if settings_path is None:
        settings_path = get_user_config_path('wger', 'settings.py')
    if not os.path.exists(settings_path):
        create_settings(settings_path=settings_path, database_path=database_path, url=url)

    # Find the path to the settings and setup the django environment
    setup_django_environment(settings_path)

    # Create Database if necessary
    if not database_exists():
        print('*** Database does not exist, creating one now')
        migrate_db(settings_path=settings_path)
        load_fixtures(settings_path=settings_path)
        create_or_reset_admin(settings_path=settings_path)

    # Download JS libraries with bower
    call_command('bower', 'install')

    # Start the webserver
    print('*** Bootstraping complete, starting application')
    start_wger(address=address, port=port, browser=browser, settings_path=settings_path)


@task(help={'settings-path': 'Path to settings file (absolute path recommended). Leave empty for default',
            'database-path': 'Path to sqlite database (absolute path recommended). Leave empty for default',
            'database-type': 'Database type to use. Supported: sqlite3, postgresql. Default: sqlite3',
            'key-length': 'Lenght of the generated secret key. Default: 50'})
def create_settings(settings_path=None, database_path=None, url=None, database_type='sqlite3', key_length=50):
    '''
    Creates a local settings file
    '''
    if settings_path is None:
        settings_path = get_user_config_path('wger', 'settings.py')

    settings_module = os.path.dirname(settings_path)
    print("*** Creating settings file at {0}".format(settings_module))

    if database_path is None:
        database_path = get_user_data_path('wger', 'database.sqlite')
    dbpath_value = repr(database_path)

    media_folder_path = repr(get_user_data_path('wger', 'media'))

    # Use localhost with default django port if no URL given
    if url is None:
        url = 'http://localhost:8000'

    # Fill in the config file template

    # os.chdir(os.path.dirname(inspect.stack()[0][1]))
    settings_template = os.path.join(os.getcwd(), 'wger', 'settings.tpl')
    with open(settings_template, 'r') as settings_file:
        settings_content = settings_file.read()
    # The environment variable is set by travis during testing
    if database_type == 'postgresql':
        dbengine = 'postgresql_psycopg2'
        dbname = "'test_wger'"
        dbuser = 'postgres'
        dbpassword = ''
        dbhost = '127.0.0.1'
        dbport = ''
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


@task(help={'settings-path': 'Path to settings file (absolute path recommended). Leave empty for default'})
def create_or_reset_admin(settings_path=None):
    '''
    Creates an admin user or resets the password for an existing one
    '''

    # Find the path to the settings and setup the django environment
    setup_django_environment(settings_path)

    # can't be imported in global scope as it already requires
    # the settings module during import
    from wger.manager.models import User
    try:
        admin = User.objects.get(username="admin")
        print("*** Password for user admin was reset to 'admin'")
    except User.DoesNotExist:
        print("*** Created default admin user")

    os.chdir(os.path.dirname(inspect.stack()[0][1]))
    current_dir = os.path.join(os.getcwd(), 'wger')
    path = os.path.join(current_dir, 'core', 'fixtures/')
    call_command("loaddata", path + "users.json")


@task(help={'settings-path': 'Path to settings file (absolute path recommended). Leave empty for default'})
def migrate_db(settings_path=None):
    '''
    Run all database migrations
    '''

    # Find the path to the settings and setup the django environment
    setup_django_environment(settings_path)

    call_command("migrate")


@task(help={'settings-path': 'Path to settings file (absolute path recommended). Leave empty for default'})
def load_fixtures(settings_path=None):
    '''
    Loads all fixtures
    '''

    # Find the path to the settings and setup the django environment
    setup_django_environment(settings_path)

    os.chdir(os.path.dirname(inspect.stack()[0][1]))
    current_dir = os.path.join(os.getcwd(), 'wger')

    # Gym
    path = os.path.join(current_dir, 'gym', 'fixtures/')
    call_command("loaddata", path + "gym.json")

    # Core
    path = os.path.join(current_dir, 'core', 'fixtures/')
    call_command("loaddata", path + "languages.json")
    call_command("loaddata", path + "groups.json")
    call_command("loaddata", path + "users.json")
    call_command("loaddata", path + "licenses.json")
    call_command("loaddata", path + "days_of_week.json")

    # Config
    path = os.path.join(current_dir, 'config', 'fixtures/')
    call_command("loaddata", path + "language_config.json")
    call_command("loaddata", path + "gym_config.json")

    # Manager
    # path = os.path.join(current_dir, 'manager', 'fixtures/')

    # Exercises
    path = os.path.join(current_dir, 'exercises', 'fixtures/')
    call_command("loaddata", path + "equipment.json")
    call_command("loaddata", path + "muscles.json")
    call_command("loaddata", path + "categories.json")
    call_command("loaddata", path + "exercises.json")

    # Nutrition
    path = os.path.join(current_dir, 'nutrition', 'fixtures/')
    call_command("loaddata", path + "ingredients.json")
    call_command("loaddata", path + "weight_units.json")
    call_command("loaddata", path + "ingredient_units.json")

    # Gym
    path = os.path.join(current_dir, 'gym', 'fixtures/')
    call_command("loaddata", path + "gym.json")
    call_command("loaddata", path + "gym-config.json")
    call_command("loaddata", path + "gym-adminconfig.json")


@task
def config_location():
    '''
    Returns the default location for the settings file and the data folder
    '''
    print('Default locations:')
    print('* settings:      {0}'.format(get_user_config_path('wger', 'settings.py')))
    print('* media folder:  {0}'.format(get_user_data_path('wger', 'media')))
    print('* database path: {0}'.format(get_user_data_path('wger', 'database.sqlite')))
