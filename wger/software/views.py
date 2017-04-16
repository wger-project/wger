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

import logging

from django.conf import settings

from django.shortcuts import render

logger = logging.getLogger(__name__)


def features(request):
    '''
    Render the features page
    '''

    context = {'allow_registration': settings.WGER_SETTINGS['ALLOW_REGISTRATION'],
               'allow_guest_users': settings.WGER_SETTINGS['ALLOW_GUEST_USERS']}
    return render(request, 'features.html', context)
