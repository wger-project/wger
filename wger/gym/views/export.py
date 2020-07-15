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
import csv
import datetime
import logging

# Django
from django.contrib.auth.decorators import login_required
from django.http.response import (
    HttpResponse,
    HttpResponseForbidden
)
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

# wger
from wger.gym.models import Gym


logger = logging.getLogger(__name__)


@login_required
def users(request, gym_pk):
    '''
    Exports all members in selected gym
    '''
    gym = get_object_or_404(Gym, pk=gym_pk)

    if not request.user.has_perm('gym.manage_gyms') \
            and not request.user.has_perm('gym.manage_gym'):
        return HttpResponseForbidden()

    if request.user.has_perm('gym.manage_gym') \
            and request.user.userprofile.gym != gym:
        return HttpResponseForbidden()

    # Create CSV 'file'
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response, delimiter='\t', quoting=csv.QUOTE_ALL)

    writer.writerow([_('Nr.'),
                     _('Gym'),
                     _('Username'),
                     _('Email'),
                     _('First name'),
                     _('Last name'),
                     _('Gender'),
                     _('Age'),
                     _('ZIP code'),
                     _('City'),
                     _('Street'),
                     _('Phone')])
    for user in Gym.objects.get_members(gym_pk):
        address = user.userprofile.address
        writer.writerow([user.id,
                         gym.name,
                         user.username,
                         user.email,
                         user.first_name,
                         user.last_name,
                         user.userprofile.get_gender_display(),
                         user.userprofile.age,
                         address['zip_code'],
                         address['city'],
                         address['street'],
                         address['phone']
                         ])

    # Send the data to the browser
    today = datetime.date.today()
    filename = 'User-data-gym-{gym}-{t.year}-{t.month:02d}-{t.day:02d}.csv'.format(t=today,
                                                                                   gym=gym.id)
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    response['Content-Length'] = len(response.content)
    return response
