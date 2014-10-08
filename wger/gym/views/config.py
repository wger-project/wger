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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponseForbidden, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.views.generic import ListView
from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import UpdateView

from wger.core.forms import GymUserAddForm
from wger.core.helpers import get_user_last_activity
from wger.gym.models import Gym, GymConfig
from wger.utils.generic_views import WgerFormMixin
from wger.utils.generic_views import WgerDeleteMixin
from wger.utils.generic_views import WgerPermissionMixin
from wger.utils.helpers import password_generator


logger = logging.getLogger('wger.custom')


class GymConfigUpdateView(WgerFormMixin, UpdateView):
    '''
    View to update an existing gym configuration
    '''

    model = GymConfig
    permission_required = 'gym.change_gymconfig'

    def dispatch(self, request, *args, **kwargs):
        '''
        Only managers for this gym can add new members
        '''
        if request.user.has_perm('gym.change_gymconfig'):
            gym_id = request.user.userprofile.gym_id
            if gym_id != int(self.kwargs['pk']):
                return HttpResponseForbidden()
        return super(GymConfigUpdateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        '''
        Return to the gym user overview
        '''
        return reverse('gym:gym:user-list', kwargs={'pk': self.object.gym.pk})

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(GymConfigUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('gym:config:edit', kwargs={'pk': self.object.id})
        context['title'] = _(u'Edit {0}').format(self.object)
        return context
