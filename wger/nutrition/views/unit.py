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
    PermissionRequiredMixin
)
from django.urls import (
    reverse,
    reverse_lazy
)
from django.utils.translation import (
    gettext as _,
    gettext_lazy
)
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView
)

# wger
from wger.nutrition.models import WeightUnit
from wger.utils.constants import PAGINATION_OBJECTS_PER_PAGE
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin
)
from wger.utils.language import load_language


logger = logging.getLogger(__name__)
# ************************
# Weight units functions
# ************************


class WeightUnitListView(PermissionRequiredMixin, ListView):
    """
    Generic view to list all weight units
    """

    model = WeightUnit
    template_name = 'units/list.html'
    context_object_name = 'unit_list'
    paginate_by = PAGINATION_OBJECTS_PER_PAGE
    permission_required = 'nutrition.add_ingredientweightunit'

    def get_queryset(self):
        """
        Only show ingredient units in the current user's language
        """
        return WeightUnit.objects.filter(language=load_language())


class WeightUnitCreateView(WgerFormMixin,
                           LoginRequiredMixin,
                           PermissionRequiredMixin,
                           CreateView):
    """
    Generic view to add a new weight unit for ingredients
    """

    model = WeightUnit
    fields = ['name']
    title = gettext_lazy('Add new weight unit')
    permission_required = 'nutrition.add_ingredientweightunit'

    def get_success_url(self):
        return reverse('nutrition:weight_unit:list')

    def form_valid(self, form):
        form.instance.language = load_language()
        return super(WeightUnitCreateView, self).form_valid(form)


class WeightUnitDeleteView(WgerDeleteMixin,
                           LoginRequiredMixin,
                           PermissionRequiredMixin,
                           DeleteView):
    """
    Generic view to delete a weight unit
    """

    model = WeightUnit
    fields = ['name']
    success_url = reverse_lazy('nutrition:weight_unit:list')
    permission_required = 'nutrition.delete_ingredientweightunit'
    messages = gettext_lazy('Successfully deleted')

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(WeightUnitDeleteView, self).get_context_data(**kwargs)
        context['title'] = _('Delete {0}?').format(self.object)
        return context


class WeightUnitUpdateView(WgerFormMixin,
                           LoginRequiredMixin,
                           PermissionRequiredMixin,
                           UpdateView):
    """
    Generic view to update an weight unit
    """

    model = WeightUnit
    fields = ['name']
    permission_required = 'nutrition.change_ingredientweightunit'

    def get_success_url(self):
        return reverse('nutrition:weight_unit:list')

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(WeightUnitUpdateView, self).get_context_data(**kwargs)
        context['title'] = _('Edit {0}').format(self.object)
        return context
