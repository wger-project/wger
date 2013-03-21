# -*- coding: utf-8 -*-

# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
import logging

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy


from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import ListView

from wger.nutrition.models import WeightUnit

from wger.manager.utils import load_language

from wger.workout_manager.generic_views import YamlFormMixin
from wger.workout_manager.generic_views import YamlDeleteMixin


logger = logging.getLogger('workout_manager.custom')
# ************************
# Weight units functions
# ************************


class WeightUnitListView(ListView):
    '''
    Generic view to list all weight units
    '''

    model = WeightUnit
    template_name = 'units/list.html'
    context_object_name = 'unit_list'

    def get_queryset(self):
        '''
        Only show ingredient units in the current user's language
        '''
        return WeightUnit.objects.filter(language=load_language())


class WeightUnitForm(ModelForm):
    class Meta:
        model = WeightUnit
        exclude = ('language',)


class WeightUnitCreateView(YamlFormMixin, CreateView):
    '''
    Generic view to add a new weight unit for ingredients
    '''

    model = WeightUnit
    form_class = WeightUnitForm
    title = ugettext_lazy('Add new weight unit')
    form_action = reverse_lazy('weight-unit-add')

    def get_success_url(self):
        return reverse('weight-unit-list')

    def form_valid(self, form):
        form.instance.language = load_language()
        return super(WeightUnitCreateView, self).form_valid(form)


class WeightUnitDeleteView(YamlDeleteMixin, DeleteView):
    '''
    Generic view to delete a weight unit
    '''

    model = WeightUnit
    success_url = reverse_lazy('weight-unit-list')
    title = ugettext_lazy('Delete weight unit?')
    form_action_urlname = 'weight-unit-delete'


class WeightUnitUpdateView(YamlFormMixin, UpdateView):
    '''
    Generic view to update an weight unit
    '''

    model = WeightUnit
    form_class = WeightUnitForm
    title = ugettext_lazy('Edit a weight unit')
    form_action_urlname = 'weight-unit-edit'

    def get_success_url(self):
        return reverse('weight-unit-list')
