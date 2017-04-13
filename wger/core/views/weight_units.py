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

from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.http import HttpResponseForbidden
from django.views.generic import (
    ListView,
    DeleteView,
    CreateView,
    UpdateView
)

from wger.utils.generic_views import (
    WgerFormMixin,
    WgerDeleteMixin
)

from wger.core.models import WeightUnit

logger = logging.getLogger(__name__)


class ListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    '''
    Overview of all available weight units
    '''
    model = WeightUnit
    permission_required = 'core.add_weightunit'
    template_name = 'weight_unit/list.html'


class AddView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    '''
    View to add a new weight unit
    '''

    model = WeightUnit
    fields = ['name']
    title = ugettext_lazy('Add')
    success_url = reverse_lazy('core:weight-unit:list')
    form_action = reverse_lazy('core:weight-unit:add')
    permission_required = 'core.add_weightunit'


class UpdateView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    '''
    View to update an existing weight unit
    '''

    model = WeightUnit
    fields = ['name']
    success_url = reverse_lazy('core:weight-unit:list')
    form_action_urlname = 'core:weight-unit:edit'
    permission_required = 'core.change_weightunit'

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Edit {0}').format(self.object)
        return context


class DeleteView(WgerDeleteMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    '''
    View to delete an existing license
    '''

    model = WeightUnit
    success_url = reverse_lazy('core:weight-unit:list')
    permission_required = 'core.delete_weightunit'
    form_action_urlname = 'core:weight-unit:delete'

    def dispatch(self, request, *args, **kwargs):
        '''
        Deleting the unit with ID 1 (repetitions) is not allowed

        This is the default and is hard coded in a couple of places
        '''
        if self.kwargs['pk'] == '1':
            return HttpResponseForbidden()

        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['title'] = _(u'Delete {0}?').format(self.object)
        return context
