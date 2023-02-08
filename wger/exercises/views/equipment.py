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

# Django
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.urls import (
    reverse,
    reverse_lazy,
)
from django.utils.translation import (
    gettext as _,
    gettext_lazy,
)
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

# wger
from wger.exercises.models import Equipment
from wger.utils.constants import PAGINATION_OBJECTS_PER_PAGE
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin,
)


logger = logging.getLogger(__name__)
"""
Exercise equipment
"""


class EquipmentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Generic view to list all equipments
    """

    model = Equipment
    fields = ['name']
    template_name = 'equipment/admin-overview.html'
    context_object_name = 'equipment_list'
    paginate_by = PAGINATION_OBJECTS_PER_PAGE
    permission_required = 'exercises.change_equipment'


class EquipmentEditView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Generic view to update an existing equipment item
    """

    model = Equipment
    fields = ['name']
    permission_required = 'exercises.change_equipment'
    success_url = reverse_lazy('exercise:equipment:list')

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(EquipmentEditView, self).get_context_data(**kwargs)
        context['title'] = _('Edit {0}').format(self.object)
        return context


class EquipmentAddView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Generic view to add a new equipment item
    """

    model = Equipment
    fields = ['name']
    title = gettext_lazy('Add new equipment')
    permission_required = 'exercises.add_equipment'
    success_url = reverse_lazy('exercise:equipment:list')


class EquipmentDeleteView(WgerDeleteMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Generic view to delete an existing exercise image
    """

    model = Equipment
    messages = gettext_lazy('Successfully deleted')
    title = gettext_lazy('Delete equipment?')
    permission_required = 'exercises.delete_equipment'
    success_url = reverse_lazy('exercise:equipment:list')

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        pk = self.kwargs['pk']
        context = super(EquipmentDeleteView, self).get_context_data(**kwargs)

        context['title'] = _('Delete equipment?')
        context['form_action'] = reverse('exercise:equipment:delete', kwargs={'pk': pk})

        return context
