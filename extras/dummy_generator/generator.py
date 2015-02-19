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
import csv
import uuid
import random
import django
import argparse

from django.db import IntegrityError
from django.utils.text import slugify

sys.path.insert(0, os.path.join('..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

# Must happen after calling django.setup()
from django.contrib.auth.models import User
from wger.gym.models import GymUserConfig

parser = argparse.ArgumentParser(description='Data generator. Please consult the documentaiton')
parser.add_argument("model",
                    help="The kind of entries you want to generate",
                    choices=['users', 'workout', 'gyms', 'logs', 'exercises'])

args = parser.parse_args()


if args.model == 'users':
    print("** Generating users")

    first_names = []
    last_names = []

    with open(os.path.join('csv', 'first_names_germany.csv')) as name_file:
        name_reader = csv.reader(name_file)
        for row in name_reader:
            first_names.append(row)

    with open(os.path.join('csv', 'last_names_german.csv')) as name_file:
        name_reader = csv.reader(name_file)
        for row in name_reader:
            last_names.append(row[0])

    for i in range(1, 101):
        uid = uuid.uuid4()
        name_data = random.choice(first_names)
        name = name_data[0]
        gender = name_data[1]
        surname = random.choice(last_names)

        username = slugify('{0}, {1} {2}'.format(name,
                                                 surname[0],
                                                 str(uid).split('-')[1]))
        email = '{0}@example.com'.format(username)
        password = username

        try:
            user = User.objects.create_user(username,
                                            email,
                                            password)
            user.first_name = name
            user.last_name = surname
            user.save()

        # Even with the uuid part, usernames are not guaranteed to be unique,
        # in this case, just ignore and continue
        except IntegrityError as e:
            continue

        user.userprofile.gym_id = 1
        user.userprofile.gender = '1' if gender == 'm' else 2
        user.userprofile.save()

        config = GymUserConfig()
        config.gym_id = 1
        config.user = user
        config.save()

        # print('Name: {0}, {1}'.format(name, surname))
        # print('Username: {0}'.format(username))
        # print('Email: {0}'.format(email))
        # print('')

    pass