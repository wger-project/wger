# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

'''
Custom authentication middleware.

This is basically Django's AuthenticationMiddleware, but creates a new temporary
user automatically for anonymous users.
'''

import logging
import uuid
import re

from django.contrib import auth
from django.contrib.auth import authenticate
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import User
from django.contrib.auth import login as django_login

from wger.manager.demo import create_demo_workout

logger = logging.getLogger('workout_manager.custom')


SPECIAL_PATHS = ('dashboard',
                 'workout',
                 'weight',
                 'nutrition/overview',
                 'preferences',  # from /user/preferences
                 'feedback',)


def check_current_request(request):
    '''
    Simple helper function that checks whether the current request hit one
    of the 'special' paths (paths that need a logged in user).
    '''
    match = False
    for path in SPECIAL_PATHS:
        if path in request.path:
            match = True
    return match


def get_user(request):
    if not hasattr(request, '_cached_user'):
        user = auth.get_user(request)
        create_user = check_current_request(request)

        if not create_user:
            logger.debug('will NOT create a user for this request')

        # Django didn't find a user, so create one now
        if create_user and not user.is_authenticated():
            logger.debug('creating a new user now')
            username = uuid.uuid4().hex[:-2]
            password = uuid.uuid4().hex[:-2]
            email = ''

            user = User.objects.create_user(username, email, password)
            user.save()
            user_profile = user.get_profile()
            user_profile.is_temporary = True
            user_profile.save()
            user = authenticate(username=username, password=password)
            django_login(request, user)

            # Create some demo data
            # TODO: this absolutely kills performance
            #create_demo_workout(user)
        request._cached_user = user
    return request._cached_user


class WgerAuthenticationMiddleware(object):
    '''
    Small wrapper around django's own AuthenticationMiddleware. Simply creates
    a new user with a temporary flag if the user hits certain URLs that need
    a logged in user
    '''
    def process_request(self, request):
        assert hasattr(request, 'session'), "The Django authentication middleware requires "
        "session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert"
        "'django.contrib.sessions.middleware.SessionMiddleware'."

        request.user = SimpleLazyObject(lambda: get_user(request))


class RobotsExclusionMiddleware(object):
    '''
    Simple middleware that sends the "X-Robots-Tag" tag for the URLs used in
    our WgerAuthenticationMiddleware so that those pages are not indexed.
    '''
    def process_response(self, request, response):
        # Don't set it if it's already in the response
        if check_current_request(request) and response.get('X-Robots-Tag', None) is not None:
            return response
        response['X-Robots-Tag'] = 'noindex'
        return response
