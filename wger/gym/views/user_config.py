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

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.utils.translation import ugettext as _
from django.views.generic import UpdateView

from wger.gym.models import GymUserConfig
from wger.utils.generic_views import WgerFormMixin


logger = logging.getLogger(__name__)


class ConfigUpdateView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    '''
    View to update an existing user gym configuration
    '''

    model = GymUserConfig
    fields = '__all__'
    permission_required = 'gym.change_gymuserconfig'

    def dispatch(self, request, *args, **kwargs):
        '''
        Only managers for this gym can edit the user settings
        '''

        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        config = self.get_object()
        gym_id = request.user.userprofile.gym_id
        if gym_id != config.gym.pk:
            return HttpResponseForbidden()
        return super(ConfigUpdateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        '''
        Return to the gym user overview
        '''
        return reverse('gym:gym:user-list', kwargs={'pk': self.object.gym.pk})

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(ConfigUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('gym:user_config:edit', kwargs={'pk': self.object.id})
        context['title'] = _('Configuration')
        return context
