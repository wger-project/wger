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


class UnitListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
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
    fields = ('name', 'unit_type', 'multiplier')
    title = gettext_lazy('Add')
    success_url = reverse_lazy('core:repetition-unit:list')
    permission_required = 'core.add_repetitionunit'


class UnitUpdateView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    View to update an existing setting unit
    """

    model = RepetitionUnit
    fields = ('name', 'unit_type', 'multiplier')
    success_url = reverse_lazy('core:repetition-unit:list')
    permission_required = 'core.change_repetitionunit'

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super().get_context_data(**kwargs)
        context['title'] = _('Edit {0}').format(self.object)
        return context


class UnitDeleteView(WgerDeleteMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    View to delete an existing setting unit
    """

    model = RepetitionUnit
    success_url = reverse_lazy('core:repetition-unit:list')
    permission_required = 'core.delete_repetitionunit'

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super().get_context_data(**kwargs)
        context['title'] = _('Delete {0}?').format(self.object)
        return context
