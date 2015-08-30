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

import os
import sys
import time
import django
import base64
import inspect
import threading
import webbrowser

from invoke import run, task

from django.core.management import call_command
from wger.utils.main import (
    get_user_data_path,
    get_user_config_path,
    detect_listen_opts,
    setup_django_environment
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()


@task
def bootstrap_app(settings=None, address='localhost', port=8000, no_browser=False, upgrade_db=False, reset_admin=False):
    '''
    Performs all steps necessary to bootstrap the application
    '''

    # Find the path to the settings
    settings_path = settings
    # if settings_path is None:
    #     settings_path = get_user_config_path('wger', 'settings.py')

    # Override URL if no browser should be started
    addr, port = detect_listen_opts(address, port)
    if no_browser:
        url = None
    else:
        # Find url to wger
        if port == 80:
            url = "http://{0}".format(addr)
        else:
            url = "http://{0}:{1}".format(addr, port)

    # print(settings_path)
    # print(port)
    # print(url)
    # sys.exit()


    # Create settings if necessary
    if not os.path.exists(settings_path):
        create_settings(settings_path, url=url)

    # Set the django environment to the settings
    setup_django_environment(settings_path)

    # Create Database if necessary
    if not database_exists() or upgrade_db:
        migrate_db()
        create_or_reset_admin()

    # Only run the south migrations
    elif upgrade_db:
        migrate_db()

    # Reset Admin
    elif reset_admin:
        create_or_reset_admin()

    # Start wger
    # if opts.no_reload:
    #     extra_args = ['--noreload']
    # else:
    #     extra_args = []
    #
    # start_wger(addr, port, start_browser_url=url, extra_args=extra_args)


@task
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



@task
def create_settings(settings_path=None, database_path=None, url=None, database_type='sqlite3', key_length=30):
    if settings_path is None:
        settings_path = get_user_config_path('wger', 'settings.py')
    settings_module = os.path.dirname(settings_path)
    print("* Creating settings file at {0}".format(settings_module))

    if database_path is None:
        database_path = get_user_data_path('wger', 'database.sqlite')
    dbpath_value = repr(database_path)

    media_folder_path = get_user_data_path('wger', 'media')
    print("Please edit your settings file and enter the values for the reCaptcha keys ")
    print("You can leave this empty, but won't be able to register new users")

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

    settings_content = settings_content.format(dbname=dbname,
                                               dbpath=dbpath_value,
                                               dbengine=dbengine,
                                               dbuser=dbuser,
                                               dbpassword=dbpassword,
                                               dbhost=dbhost,
                                               dbport=dbport,
                                               default_key=base64.b64encode(os.urandom(key_length)),
                                               siteurl=url,
                                               media_folder_path=media_folder_path)

    if not os.path.exists(settings_module):
        os.makedirs(settings_module)

    if not os.path.exists(os.path.dirname(database_path)):
        os.makedirs(os.path.dirname(database_path))

    with open(settings_path, 'w') as settings_file:
        settings_file.write(settings_content)


@task
def create_or_reset_admin():
    # can't be imported in global scope as it already requires
    # the settings module during import
    from wger.manager.models import User
    try:
        admin = User.objects.get(username="admin")
        print("Password for user admin was reset to 'admin'")
    except User.DoesNotExist:
        print("Created default admin user")

    os.chdir(os.path.dirname(inspect.stack()[0][1]))
    current_dir = os.path.join(os.getcwd(), 'wger')
    path = os.path.join(current_dir, 'core', 'fixtures/')
    call_command("loaddata", path + "users.json")


@task
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


@task
def migrate_db():
    '''
    Run all database migrations
    '''
    call_command("migrate")

    '''
    call_command(["migrate", "core"])
    call_command(["migrate", "gym"])
    call_command(["migrate", "config"])
    call_command(["migrate", "manager"])
    call_command(["migrate", "exercises"])
    call_command(["migrate", "nutrition"])
    call_command(["migrate", "weight"])

    # Other apps
    call_command(["migrate", "easy_thumbnails"])
    call_command(["migrate", "tastypie"])
    '''


@task
def load_fixtures():
    '''
    Loads all fixtures
    '''
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

