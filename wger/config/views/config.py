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

# Third Party
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.utils.translation import ugettext_lazy
from django.views.generic import UpdateView

# wger
from wger.config.models import UserCanCreate
from wger.config.forms import UserCreateItemPermForm
from wger.utils.generic_views import (
    WgerFormMixin,
    WgerMultiplePermissionRequiredMixin
)


logger = logging.getLogger(__name__)


class UserItemPermView(WgerFormMixin,
                       LoginRequiredMixin,
                       WgerMultiplePermissionRequiredMixin,
                       UpdateView):

    model = UserCanCreate
    title = ugettext_lazy('Permission to create new items')
    form_class = UserCreateItemPermForm
    permission_required = ('gym.manage_gym', 'gym.manage_gyms')

    def dispatch(self, request, *args, **kwargs):
        '''
        Check permissions

        - Managers can edit permissions for members of their own gym
        - General managers can edit permissions for every member
        '''
        user = request.user
        if not user.is_authenticated():
            return HttpResponseForbidden()

        if user.has_perm('gym.manage_gym') \
            and not user.has_perm('gym.manage_gyms') \
                and user.userprofile.gym != self.get_object().userprofile.gym:
            return HttpResponseForbidden()

        return super(UserItemPermView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('core:user:overview', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super(UserItemPermView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('core:user:create-item-perm',
                                         kwargs={'pk': self.object.id})
        return context
