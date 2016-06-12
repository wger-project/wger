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


import sys
import time
import logging
import threading
import webbrowser
import os
import ctypes
import socket
from invoke import task

import django
from django.utils.crypto import get_random_string
from django.core.management import (
    call_command,
    execute_from_command_line
)

logger = logging.getLogger(__name__)


@task(help={'address': 'Address to bind to. Default: localhost',
            'port': 'Port to use. Default: 8000',
            'browser': 'Whether to open the application in a browser window. Default: false',
            'settings-path': 'Path to settings file (absolute path recommended). Leave empty for default',
            'extra-args': 'Additional arguments to pass to the builtin server. Pass as string: "--arg1 --arg2=value". Default: none'})
def start_wger(context, address='localhost', port=8000, browser=False, settings_path=None, extra_args=''):
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
            'browser': 'Whether to open the application in a browser window. Default: false',
            'start-server': 'Whether to start the development server. Default: true'})
def bootstrap_wger(context,
                   settings_path=None,
                   database_path=None,
                   address='localhost',
                   port=8000,
                   browser=False,
                   start_server=True):
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
        create_settings(context, settings_path=settings_path, database_path=database_path, url=url)

    # Find the path to the settings and setup the django environment
    setup_django_environment(settings_path)

    # Create Database if necessary
    if not database_exists():
        print('*** Database does not exist, creating one now')
        migrate_db(context, settings_path=settings_path)
        load_fixtures(context, settings_path=settings_path)
        create_or_reset_admin(context, settings_path=settings_path)

    # Download JS libraries with bower
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wger'))
    context.run('npm install bower')
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    call_command('bower', 'install')

    # Start the webserver
    if start_server:
        print('*** Bootstraping complete, starting application')
        start_wger(address=address, port=port, browser=browser, settings_path=settings_path)


@task(help={'settings-path': 'Path to settings file (absolute path recommended). Leave empty for default',
            'database-path': 'Path to sqlite database (absolute path recommended). Leave empty for default',
            'database-type': 'Database type to use. Supported: sqlite3, postgresql. Default: sqlite3',
            'key-length': 'Lenght of the generated secret key. Default: 50'})
def create_settings(context, settings_path=None, database_path=None, url=None, database_type='sqlite3', key_length=50):
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
    settings_template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wger', 'settings.tpl')
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
def create_or_reset_admin(context, settings_path=None):
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

    # os.chdir(os.path.dirname(inspect.stack()[0][1]))
    # current_dir = os.path.join(os.getcwd(), 'wger')
    current_dir = os.path.dirname(os.path.abspath(__file__))

    path = os.path.join(current_dir, 'wger', 'core', 'fixtures/')
    call_command("loaddata", path + "users.json")


@task(help={'settings-path': 'Path to settings file (absolute path recommended). Leave empty for default'})
def migrate_db(context, settings_path=None):
    '''
    Run all database migrations
    '''

    # Find the path to the settings and setup the django environment
    setup_django_environment(settings_path)

    call_command("migrate")


@task(help={'settings-path': 'Path to settings file (absolute path recommended). Leave empty for default'})
def load_fixtures(context, settings_path=None):
    '''
    Loads all fixtures
    '''

    # Find the path to the settings and setup the django environment
    setup_django_environment(settings_path)


    # os.chdir(os.path.dirname(inspect.stack()[0][1]))
    # current_dir = os.path.join(os.getcwd(), 'wger')
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Gym
    path = os.path.join(current_dir, 'wger', 'gym', 'fixtures/')
    call_command("loaddata", path + "gym.json")

    # Core
    path = os.path.join(current_dir, 'wger', 'core', 'fixtures/')
    call_command("loaddata", path + "languages.json")
    call_command("loaddata", path + "groups.json")
    call_command("loaddata", path + "users.json")
    call_command("loaddata", path + "licenses.json")
    call_command("loaddata", path + "days_of_week.json")
    call_command("loaddata", path + "setting_repetition_units.json")
    call_command("loaddata", path + "setting_weight_units.json")

    # Config
    path = os.path.join(current_dir, 'wger', 'config', 'fixtures/')
    call_command("loaddata", path + "language_config.json")
    call_command("loaddata", path + "gym_config.json")

    # Manager
    # path = os.path.join(current_dir, 'manager', 'fixtures/')

    # Exercises
    path = os.path.join(current_dir, 'wger', 'exercises', 'fixtures/')
    call_command("loaddata", path + "equipment.json")
    call_command("loaddata", path + "muscles.json")
    call_command("loaddata", path + "categories.json")
    call_command("loaddata", path + "exercises.json")

    # Nutrition
    path = os.path.join(current_dir, 'wger', 'nutrition', 'fixtures/')
    call_command("loaddata", path + "ingredients.json")
    call_command("loaddata", path + "weight_units.json")
    call_command("loaddata", path + "ingredient_units.json")

    # Gym
    path = os.path.join(current_dir, 'wger', 'gym', 'fixtures/')
    call_command("loaddata", path + "gym.json")
    call_command("loaddata", path + "gym-config.json")
    call_command("loaddata", path + "gym-adminconfig.json")


@task
def config_location(context):
    '''
    Returns the default location for the settings file and the data folder
    '''
    print('Default locations:')
    print('* settings:      {0}'.format(get_user_config_path('wger', 'settings.py')))
    print('* media folder:  {0}'.format(get_user_data_path('wger', 'media')))
    print('* database path: {0}'.format(get_user_data_path('wger', 'database.sqlite')))


#
#
# Helper functions
#
# Note: these functions were originally in wger/utils/main.py but were moved
#       here because of different import problems (the packaged pip-installed
#       packaged has a different sys path than the local one)
#


def get_user_data_path(*args):
    if sys.platform == "win32":
        return win32_get_app_data_path(*args)

    data_home = os.environ.get(
        'XDG_DATA_HOME', os.path.join(
            os.path.expanduser('~'), '.local', 'share'))

    return os.path.join(data_home, *args)


def get_user_config_path(*args):
    if sys.platform == "win32":
        return win32_get_app_data_path(*args)

    config_home = os.environ.get(
        'XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))

    return os.path.join(config_home, *args)


def win32_get_app_data_path(*args):
    shell32 = ctypes.WinDLL("shell32.dll")
    SHGetFolderPath = shell32.SHGetFolderPathW
    SHGetFolderPath.argtypes = (
        ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32,
        ctypes.c_wchar_p)
    SHGetFolderPath.restype = ctypes.c_uint32

    CSIDL_LOCAL_APPDATA = 0x001c
    MAX_PATH = 260

    buf = ctypes.create_unicode_buffer(MAX_PATH)
    res = SHGetFolderPath(0, CSIDL_LOCAL_APPDATA, 0, 0, buf)
    if res != 0:
        raise Exception("Could not deterime APPDATA path")

    return os.path.join(buf.value, *args)


def detect_listen_opts(address, port):
    if address is None:
        try:
            address = socket.gethostbyname(socket.gethostname())
        except socket.error:
            address = "127.0.0.1"

    if port is None:
        # test if we can use port 80
        s = socket.socket()
        port = 80
        try:
            s.bind((address, port))
            s.listen(-1)
        except socket.error:
            port = 8000
        finally:
            s.close()

    return address, port


def setup_django_environment(settings_path):
    '''
    Setup the django environment
    '''

    # Use default settings if the user didn't specify something else
    if settings_path is None:
        settings_path = get_user_config_path('wger', 'settings.py')
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
    from django.db import DatabaseError
    from django.core.exceptions import ImproperlyConfigured
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


def start_browser(url):
    '''
    Start the web browser with the given URL
    '''
    browser = webbrowser.get()

    def function():
        time.sleep(1)
        browser.open(url)

    thread = threading.Thread(target=function)
    thread.start()
