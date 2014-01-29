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
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext as _

from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.views.generic import ListView

from wger.exercises.models import Equipment

from wger.utils.generic_views import WgerFormMixin
from wger.utils.generic_views import WgerDeleteMixin
from wger.utils.generic_views import WgerPermissionMixin
from wger.utils.constants import PAGINATION_OBJECTS_PER_PAGE


logger = logging.getLogger('wger.custom')

'''
Exercise equipment
'''


class EquipmentListView(WgerPermissionMixin, ListView):
    '''
    Generic view to list all equipments
    '''

    model = Equipment
    template_name = 'equipment/list.html'
    context_object_name = 'equipment_list'
    paginate_by = PAGINATION_OBJECTS_PER_PAGE
    permission_required = 'exercises.change_equipment'


class EquipmentEditView(WgerFormMixin, UpdateView, WgerPermissionMixin):
    '''
    Generic view to update an existing equipment item
    '''

    model = Equipment
    title = ugettext_lazy('Edit equipment')
    permission_required = 'exercises.change_equipment'
    success_url = reverse_lazy('equipment-list')

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(EquipmentEditView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('equipment-edit',
                                         kwargs={'pk': self.object.id})

        return context


class EquipmentAddView(WgerFormMixin, CreateView, WgerPermissionMixin):
    '''
    Generic view to add a new equipment item
    '''

    model = Equipment
    title = ugettext_lazy('Add equipment')
    permission_required = 'exercises.add_equipment'
    success_url = reverse_lazy('equipment-list')

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(EquipmentAddView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('equipment-add')

        return context


class EquipmentDeleteView(WgerDeleteMixin, DeleteView, WgerPermissionMixin):
    '''
    Generic view to delete an existing exercise image
    '''

    model = Equipment
    messages = ugettext_lazy('Successfully deleted')
    permission_required = 'exercises.delete_equipment'
    success_url = reverse_lazy('equipment-list')

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        pk = self.kwargs['pk']
        context = super(EquipmentDeleteView, self).get_context_data(**kwargs)

        context['title'] = _('Delete equipment?')
        context['form_action'] = reverse('equipment-delete',
                                         kwargs={'pk': pk})

        return context


class EquipmentOverviewView(WgerPermissionMixin, ListView):
    '''
    Overview with all exercises, group by equipment
    '''

    model = Equipment
    template_name = 'equipment/overview.html'
    context_object_name = 'equipment_list'
