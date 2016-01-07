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

from django.core.urlresolvers import reverse, reverse_lazy
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

from wger.core.models import License, SettingUnit

logger = logging.getLogger(__name__)


class ListView(WgerPermissionMixin, ListView):
    '''
    Overview of all available setting units
    '''
    model = SettingUnit
    permission_required = 'core.add_settingunit'
    template_name = 'setting_unit/list.html'


class AddView(WgerFormMixin, CreateView, WgerPermissionMixin):
    '''
    View to add a new setting unit
    '''

    model = SettingUnit
    fields = ['name']
    title = ugettext_lazy('Add')
    success_url = reverse_lazy('core:setting_unit:list')
    form_action = reverse_lazy('core:setting_unit:add')
    permission_required = 'core.add_settingunit'


class UpdateView(WgerFormMixin, UpdateView, WgerPermissionMixin):
    '''
    View to update an existing setting unit
    '''

    model = SettingUnit
    fields = ['name']
    success_url = reverse_lazy('core:setting_unit:list')
    form_action_urlname = 'core:setting_unit:edit'
    permission_required = 'core.change_settingunit'

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Edit {0}').format(self.object)
        return context


class DeleteView(WgerDeleteMixin, DeleteView, WgerPermissionMixin):
    '''
    View to delete an existing license
    '''

    model = SettingUnit
    success_url = reverse_lazy('core:setting_unit:list')
    permission_required = 'core.delete_settingunit'
    form_action_urlname = 'core:setting_unit:delete'

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['title'] = _(u'Delete {0}?').format(self.object)
        return context
