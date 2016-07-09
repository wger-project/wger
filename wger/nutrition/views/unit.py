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
from django.utils.translation import ugettext_lazy, ugettext as _
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin

from django.views.generic import (
    DeleteView,
    CreateView,
    UpdateView,
    ListView
)

from wger.nutrition.models import WeightUnit
from wger.utils.constants import PAGINATION_OBJECTS_PER_PAGE
from wger.utils.language import load_language
from wger.utils.generic_views import (
    WgerFormMixin,
    WgerDeleteMixin
)

logger = logging.getLogger(__name__)
# ************************
# Weight units functions
# ************************


class WeightUnitListView(PermissionRequiredMixin, ListView):
    '''
    Generic view to list all weight units
    '''

    model = WeightUnit
    template_name = 'units/list.html'
    context_object_name = 'unit_list'
    paginate_by = PAGINATION_OBJECTS_PER_PAGE
    permission_required = 'nutrition.add_ingredientweightunit'

    def get_queryset(self):
        '''
        Only show ingredient units in the current user's language
        '''
        return WeightUnit.objects.filter(language=load_language())


class WeightUnitCreateView(WgerFormMixin,
                           LoginRequiredMixin,
                           PermissionRequiredMixin,
                           CreateView):
    '''
    Generic view to add a new weight unit for ingredients
    '''

    model = WeightUnit
    fields = ['name']
    title = ugettext_lazy('Add new weight unit')
    form_action = reverse_lazy('nutrition:weight_unit:add')
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
    '''
    Generic view to delete a weight unit
    '''

    model = WeightUnit
    fields = ['name']
    success_url = reverse_lazy('nutrition:weight_unit:list')
    form_action_urlname = 'nutrition:weight_unit:delete'
    permission_required = 'nutrition.delete_ingredientweightunit'
    messages = ugettext_lazy('Successfully deleted')

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(WeightUnitDeleteView, self).get_context_data(**kwargs)
        context['title'] = _(u'Delete {0}?').format(self.object)
        return context


class WeightUnitUpdateView(WgerFormMixin,
                           LoginRequiredMixin,
                           PermissionRequiredMixin,
                           UpdateView):
    '''
    Generic view to update an weight unit
    '''

    model = WeightUnit
    fields = ['name']
    form_action_urlname = 'nutrition:weight_unit:edit'
    permission_required = 'nutrition.change_ingredientweightunit'

    def get_success_url(self):
        return reverse('nutrition:weight_unit:list')

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(WeightUnitUpdateView, self).get_context_data(**kwargs)
        context['title'] = _(u'Edit {0}').format(self.object)
        return context
