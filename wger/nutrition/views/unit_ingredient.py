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

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy

from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import UpdateView

from wger.nutrition.models import Ingredient
from wger.nutrition.models import IngredientWeightUnit

from wger.workout_manager.generic_views import YamlFormMixin
from wger.workout_manager.generic_views import YamlDeleteMixin


logger = logging.getLogger('workout_manager.custom')


# ************************
# Weight units to ingredient functions
# ************************
class WeightUnitIngredientForm(ModelForm):
    class Meta:
        model = IngredientWeightUnit
        exclude = ('ingredient',)


class WeightUnitIngredientCreateView(YamlFormMixin, CreateView):
    '''
    Generic view to add a new weight unit to ingredient entry
    '''

    model = IngredientWeightUnit
    form_class = WeightUnitIngredientForm
    title = ugettext_lazy('Add a new weight unit')

     # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(WeightUnitIngredientCreateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('weight-unit-ingredient-add',
                                         kwargs={'ingredient_pk': self.kwargs['ingredient_pk']})
        return context

    def get_success_url(self):
        return reverse('wger.nutrition.views.ingredient.ingredient_view',
                       kwargs={'id': self.kwargs['ingredient_pk']})

    def form_valid(self, form):
        ingredient = get_object_or_404(Ingredient, pk=self.kwargs['ingredient_pk'])
        form.instance.ingredient = ingredient
        return super(WeightUnitIngredientCreateView, self).form_valid(form)


class WeightUnitIngredientUpdateView(YamlFormMixin, UpdateView):
    '''
    Generic view to update an weight unit to ingredient entry
    '''

    model = IngredientWeightUnit
    form_class = WeightUnitIngredientForm
    title = ugettext_lazy('Edit a weight unit to ingredient connection')
    form_action_urlname = 'weight-unit-ingredient-edit'

    def get_success_url(self):
        return reverse('wger.nutrition.views.ingredient.ingredient_view',
                       kwargs={'id': self.object.ingredient.id})


class WeightUnitIngredientDeleteView(YamlDeleteMixin, DeleteView):
    '''
    Generic view to delete a weight unit to ingredient entry
    '''

    model = IngredientWeightUnit
    title = ugettext_lazy('Delete weight unit?')
    form_action_urlname = 'weight-unit-ingredient-delete'

    def get_success_url(self):
        return reverse('wger.nutrition.views.ingredient.ingredient_view',
                       kwargs={'id': self.object.ingredient.id})
