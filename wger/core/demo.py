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
import uuid

# Django
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.management import call_command
from django.http import HttpRequest


logger = logging.getLogger(__name__)


def create_temporary_user(request: HttpRequest):
    """
    Creates a temporary user
    """
    username = uuid.uuid4().hex[:-2]
    password = uuid.uuid4().hex[:-2]
    email = ''

    user = User.objects.create_user(username, email, password)
    user.save()
    user_profile = user.userprofile
    user_profile.is_temporary = True
    user_profile.age = 25
    user_profile.height = 175
    user_profile.save()
    user = authenticate(request=request, username=username, password=password)
    return user


def create_demo_entries(user):
    """
    Creates some demo data for temporary users
    """
    call_command(
        'dummy-generator-routines',
        '--routines=4',
        f'--user-id={user.id}',
    )
    call_command(
        'dummy-generator-workout-diary',
        f'--user-id={user.id}',
    )
    call_command(
        'dummy-generator-body-weight',
        '--nr-entries=40',
        f'--user-id={user.id}',
    )
    call_command(
        'dummy-generator-nutrition',
        '--plans=5',
        f'--user-id={user.id}',
    )
    call_command(
        'dummy-generator-measurement-categories',
        '--nr-categories=4',
        f'--user-id={user.id}',
    )
    call_command(
        'dummy-generator-measurements',
        '--nr-measurements=10',
        f'--user-id={user.id}',
    )
