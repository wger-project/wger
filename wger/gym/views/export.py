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
import csv
import datetime
import logging

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import (
    Group,
    Permission,
    User
)
from django.core.urlresolvers import reverse, reverse_lazy
from django.http.response import (
    HttpResponseForbidden,
    HttpResponse,
    HttpResponseRedirect
)
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.views.generic import (
    ListView,
    DeleteView,
    CreateView,
    UpdateView
)

from wger.gym.forms import GymUserAddForm, GymUserPermisssionForm
from wger.gym.helpers import get_user_last_activity, is_any_gym_admin
from wger.gym.models import (
    Gym,
    GymAdminConfig,
    GymUserConfig
)
from wger.config.models import GymConfig as GlobalGymConfig
from wger.utils.generic_views import (
    WgerFormMixin,
    WgerDeleteMixin,
    WgerPermissionMixin
)
from wger.utils.helpers import password_generator


logger = logging.getLogger(__name__)


@login_required
def users(request, gym_pk):
    '''
    Exports all users in selected gym
    '''
    gym = get_object_or_404(Gym, pk=gym_pk)

    if not request.user.has_perm('gym.manage_gyms') \
            and not request.user.has_perm('gym.manage_gym'):
        return HttpResponseForbidden()

    if request.user.has_perm('gym.manage_gym') \
            and request.user.userprofile.gym != gym:
        return HttpResponseForbidden()

    # Crease CSV 'file'
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response, delimiter='\t', quoting=csv.QUOTE_ALL)
    writer.writerow([_('Nr.'),
                     _('Username'),
                     _('First name'),
                     _('Last name'),
                     _('Gym')])
    for userprofile in gym.userprofile_set.all():
        user = userprofile.user
        writer.writerow([user.id,
                         user.username,
                         user.first_name,
                         user.last_name,
                         gym.name])

    # Send the data to the browser
    today = datetime.date.today()
    filename = 'User-data-gym-{gym}-{t.year}-{t.month:02d}-{t.day:02d}.csv'.format(t=today,
                                                                                  gym=gym.id)
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    response['Content-Length'] = len(response.content)
    return response
