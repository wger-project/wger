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

import six
import csv
import datetime
import logging

from django.contrib.auth.decorators import login_required
from django.http.response import (
    HttpResponseForbidden,
    HttpResponse
)
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

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

    # Python3: the .encode() is only needed for python 2.7. Should this requirement
    #          be dropped once, they can be removed.
    writer.writerow([_('Nr.'),
                     _('Gym').encode('utf8'),
                     _('Username').encode('utf8'),
                     _('Email').encode('utf8'),
                     _('First name').encode('utf8'),
                     _('Last name').encode('utf8'),
                     _('Gender').encode('utf8'),
                     _('Age').encode('utf8'),
                     _('ZIP code').encode('utf8'),
                     _('City').encode('utf8'),
                     _('Street').encode('utf8'),
                     _('Phone').encode('utf8')])
    for user in Gym.objects.get_members(gym_pk):
        address = user.userprofile.address
        writer.writerow([user.id,
                         gym.name.encode('utf8'),
                         user.username,
                         user.email,
                         user.first_name.encode('utf8'),
                         user.last_name.encode('utf8'),
                         user.userprofile.get_gender_display().encode('utf8'),
                         user.userprofile.age,
                         address['zip_code'],
                         address['city'].encode('utf8'),
                         address['street'].encode('utf8'),
                         address['phone'].encode('utf8')
                         ])

    # Send the data to the browser
    today = datetime.date.today()
    filename = 'User-data-gym-{gym}-{t.year}-{t.month:02d}-{t.day:02d}.csv'.format(t=today,
                                                                                   gym=gym.id)
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    response['Content-Length'] = len(response.content)
    return response
