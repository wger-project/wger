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

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as django_login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _

# wger
from wger.core.demo import (
    create_demo_entries,
    create_temporary_user,
)


logger = logging.getLogger(__name__)


# ************************
# Misc functions
# ************************
def index(request):
    """
    Index page
    """
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('core:dashboard'))
    else:
        return HttpResponseRedirect(reverse('software:features'))


def demo_entries(request):
    """
    Creates a set of sample entries for guest users
    """
    if not settings.WGER_SETTINGS['ALLOW_GUEST_USERS']:
        return HttpResponseRedirect(reverse('software:features'))

    if (
        not request.user.is_authenticated or request.user.userprofile.is_temporary
    ) and not request.session['has_demo_data']:
        # If we reach this from a page that has no user created by the
        # middleware, do that now
        if not request.user.is_authenticated:
            user = create_temporary_user(request)
            django_login(request, user)

        # OK, continue
        create_demo_entries(request.user)
        request.session['has_demo_data'] = True
        messages.success(
            request,
            _(
                'We have created sample workout, workout schedules, weight '
                'logs, (body) weight and nutrition plan entries so you can '
                'better see what  this site can do. Feel free to edit or '
                'delete them!'
            ),
        )
    return HttpResponseRedirect(reverse('core:dashboard'))
