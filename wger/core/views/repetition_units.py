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
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
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
from wger.core.models import RepetitionUnit
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin,
)


logger = logging.getLogger(__name__)


class ListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Overview of all available setting units
    """

    model = RepetitionUnit
    permission_required = 'core.add_repetitionunit'
    template_name = 'repetition_unit/list.html'


class AddView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    View to add a new setting unit
    """

    model = RepetitionUnit
    fields = ['name']
    title = gettext_lazy('Add')
    success_url = reverse_lazy('core:repetition-unit:list')
    permission_required = 'core.add_repetitionunit'


class UpdateView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    View to update an existing setting unit
    """

    model = RepetitionUnit
    fields = ['name']
    success_url = reverse_lazy('core:repetition-unit:list')
    permission_required = 'core.change_repetitionunit'

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['title'] = _('Edit {0}').format(self.object)
        return context


class DeleteView(WgerDeleteMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    View to delete an existing setting unit
    """

    model = RepetitionUnit
    success_url = reverse_lazy('core:repetition-unit:list')
    permission_required = 'core.delete_repetitionunit'

    def dispatch(self, request, *args, **kwargs):
        """
        Deleting the unit with ID 1 (repetitions) is not allowed

        This is the default and is hard coded in a couple of places
        """
        if self.kwargs['pk'] == '1':
            return HttpResponseForbidden()

        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['title'] = _('Delete {0}?').format(self.object)
        return context
