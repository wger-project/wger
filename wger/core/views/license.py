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
from wger.core.models import License
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin,
)


logger = logging.getLogger(__name__)


class LicenseListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Overview of all available licenses
    """

    model = License
    permission_required = 'core.add_license'
    template_name = 'license/list.html'


class LicenseAddView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    View to add a new license
    """

    model = License
    fields = ['full_name', 'short_name', 'url']
    success_url = reverse_lazy('core:license:list')
    title = gettext_lazy('Add')
    permission_required = 'core.add_license'


class LicenseUpdateView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    View to update an existing license
    """

    model = License
    fields = ['full_name', 'short_name', 'url']
    success_url = reverse_lazy('core:license:list')
    permission_required = 'core.change_license'

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(LicenseUpdateView, self).get_context_data(**kwargs)
        context['title'] = _('Edit {0}').format(self.object)
        return context


class LicenseDeleteView(WgerDeleteMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    View to delete an existing license
    """

    model = License
    success_url = reverse_lazy('core:license:list')
    permission_required = 'core.delete_license'

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(LicenseDeleteView, self).get_context_data(**kwargs)
        context['title'] = _('Delete {0}?').format(self.object)
        return context
