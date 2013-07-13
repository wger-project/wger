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

from django.core.cache import cache
from django.contrib import auth
from django.utils.functional import SimpleLazyObject
from django.contrib.auth import login as django_login

from wger.manager.demo import create_temporary_user


logger = logging.getLogger('workout_manager.custom')


SPECIAL_PATHS = ('dashboard',
                 'workout',
                 'weight',
                 'nutrition/overview',
                 'preferences',  # from /user/preferences
                 'feedback',
                 'about',)


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

        create_user = check_current_request(request)
        user = auth.get_user(request)

        # Set the flag in the session
        if not request.session.get('has_demo_data'):
            request.session['has_demo_data'] = False

        # Django didn't find a user, so create one now
        if create_user and not user.is_authenticated():

            logger.debug('creating a new guest user now')
            user = create_temporary_user()
            django_login(request, user)

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
        if check_current_request(request) and response.get('X-Robots-Tag', None) is None:
            #logger.debug("Adding X-Robots header")
            response['X-Robots-Tag'] = 'noindex, nofollow'
            return response
        else:
            #logger.debug("Not adding X-Robots header")
            return response
