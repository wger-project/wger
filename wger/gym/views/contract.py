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

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.http.response import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.views.generic import (
    ListView,
    DeleteView,
    CreateView,
    UpdateView
)

from wger.utils.generic_views import (
    WgerFormMixin,
    WgerDeleteMixin,
    WgerPermissionMixin
)
from wger.gym.models import Contract


logger = logging.getLogger(__name__)


class AddView(WgerFormMixin, CreateView):
    '''
    View to add a new document
    '''

    model = Contract
    fields = '__all__'
    title = ugettext_lazy('Add contract')
    permission_required = 'gym.add_contract'
    member = None

    def get_success_url(self):
        '''
        Redirect back to user page
        '''
        return reverse('core:user:overview', kwargs={'pk': self.member.pk})

    def dispatch(self, request, *args, **kwargs):
        '''
        Can only add documents to users in own gym
        '''
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        user = get_object_or_404(User, pk=self.kwargs['user_pk'])
        self.member = user
        if user.userprofile.gym_id != request.user.userprofile.gym_id:
            return HttpResponseForbidden()
        return super(AddView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        '''
        Set user instances
        '''
        form.instance.member = self.member
        form.instance.user = self.request.user
        return super(AddView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(AddView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('gym:contract:add',
                                         kwargs={'user_pk': self.kwargs['user_pk']})
        return context
