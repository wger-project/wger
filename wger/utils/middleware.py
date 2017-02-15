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

'''
Custom middleware
'''

import logging

from django.conf import settings
from django.contrib import auth
from django.utils.functional import SimpleLazyObject
from django.contrib.auth import login as django_login

from wger.core.demo import create_temporary_user


logger = logging.getLogger(__name__)


SPECIAL_PATHS = ('dashboard',)


def check_current_request(request):
    '''
    Simple helper function that checks whether the current request hit one
    of the 'special' paths (paths that need a logged in user).
    '''

    # Don't create guest users for requests that are accessing the site
    # through the REST API
    if 'api' in request.path:
        return False

    # Other paths
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
        if settings.WGER_SETTINGS['ALLOW_GUEST_USERS'] and \
                request.method == 'GET' and \
                create_user and not user.is_authenticated():

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
            response['X-Robots-Tag'] = 'noindex, nofollow'
        return response


class JavascriptAJAXRedirectionMiddleware(object):
    '''
    Middleware that sends helper headers when working with AJAX.

    This is used for AJAX forms due to limitations of javascript. The way it
    was done before was to load the whole redirected page, then read from a DIV
    in the page and redirect to that URL. This now just sends a header when the
    form was called via the JS function wgerFormModalDialog() and no errors are
    present.
    '''

    def process_response(self, request, response):

        if request.META.get('HTTP_X_WGER_NO_MESSAGES') and b'has-error' not in response.content:

            logger.debug('Sending X-wger-redirect')
            response['X-wger-redirect'] = request.path
            response.content = request.path
        return response
