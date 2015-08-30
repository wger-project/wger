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
import inspect
import django
import time
import webbrowser
import threading

from invoke import run, task

from django.core.management import call_command


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()


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

