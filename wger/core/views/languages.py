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
    DetailView,
    ListView,
    UpdateView,
)

# wger
from wger.core.models import Language
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin,
)


logger = logging.getLogger(__name__)


class LanguageListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Show an overview of all languages
    """

    model = Language
    template_name = 'language/overview.html'
    context_object_name = 'language_list'
    permission_required = 'core.change_language'


class LanguageDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Language
    template_name = 'language/view.html'
    context_object_name = 'view_language'
    permission_required = 'core.change_language'


class LanguageCreateView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Generic view to add a new language
    """

    model = Language
    fields = ['short_name', 'full_name', 'full_name_en']
    title = gettext_lazy('Add')
    permission_required = 'core.add_language'


class LanguageDeleteView(WgerDeleteMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Generic view to delete an existing language
    """

    model = Language
    success_url = reverse_lazy('core:language:overview')
    messages = gettext_lazy('Successfully deleted')
    permission_required = 'core.delete_language'

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(LanguageDeleteView, self).get_context_data(**kwargs)
        context['title'] = _('Delete {0}?').format(self.object.full_name)
        return context


class LanguageEditView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Generic view to update an existing language
    """

    model = Language
    fields = ['short_name', 'full_name', 'full_name_en']
    permission_required = 'core.change_language'

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(LanguageEditView, self).get_context_data(**kwargs)
        context['title'] = _('Edit {0}').format(self.object.full_name)
        return context
