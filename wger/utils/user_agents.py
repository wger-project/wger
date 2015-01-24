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

import logging

logger = logging.getLogger(__name__)


def is_amazon_webview(user_agent):
    '''
    Check if the client is an Amazon WebView.

    See the amazon developer page for specific user agents:
    https://developer.amazon.com/sdk/webapps/faq.html#distribution

    :param user_agent A string with the user agent to check
    :return boolean
    '''
    if 'amazonwebapp' in user_agent.lower():
        return True
    else:
        return False


def check_request_amazon(request):
    '''

    :param request:
    :return: boolean
    '''
    if request.META.get('HTTP_USER_AGENT'):
        return is_amazon_webview(request.META.get('HTTP_USER_AGENT'))
    else:
        return False


def is_android_webview(user_agent):
    '''
    Check if the client is an Android WebView.

    :param user_agent A string with the user agent to check
    :return boolean
    '''
    if 'wgerandroidwebapp' in user_agent.lower():
        return True
    else:
        return False


def check_request_android(request):
    '''

    :param request:
    :return: boolean
    '''
    if request.META.get('HTTP_USER_AGENT'):
        return is_android_webview(request.META.get('HTTP_USER_AGENT'))
    else:
        return False
