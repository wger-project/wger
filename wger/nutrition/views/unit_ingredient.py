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

from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.forms import ModelForm, ModelChoiceField
from django.utils.translation import ugettext_lazy

from wger.utils.language import load_language
from django.views.generic import (
    DeleteView,
    CreateView,
    UpdateView
)
from wger.nutrition.models import (
    Ingredient,
    IngredientWeightUnit,
    WeightUnit
)
from wger.utils.generic_views import (
    WgerFormMixin,
    WgerDeleteMixin
)


logger = logging.getLogger(__name__)


# ************************
# Weight units to ingredient functions
# ************************


class WeightUnitIngredientCreateView(WgerFormMixin,
                                     LoginRequiredMixin,
                                     PermissionRequiredMixin,
                                     CreateView):
    '''
    Generic view to add a new weight unit to ingredient entry
    '''

    model = IngredientWeightUnit
    title = ugettext_lazy('Add a new weight unit')
    permission_required = 'nutrition.add_ingredientweightunit'

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(WeightUnitIngredientCreateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('nutrition:unit_ingredient:add',
                                         kwargs={'ingredient_pk': self.kwargs['ingredient_pk']})
        return context

    def get_success_url(self):
        return reverse('nutrition:ingredient:view', kwargs={'id': self.kwargs['ingredient_pk']})

    def form_valid(self, form):
        ingredient = get_object_or_404(Ingredient, pk=self.kwargs['ingredient_pk'])
        form.instance.ingredient = ingredient
        return super(WeightUnitIngredientCreateView, self).form_valid(form)

    def get_form_class(self):
        '''
        The form can only show units in the user's language
        '''

        class IngredientWeightUnitForm(ModelForm):
            unit = ModelChoiceField(queryset=WeightUnit.objects.filter(language=load_language()))

            class Meta:
                model = IngredientWeightUnit
                fields = ['unit', 'gram', 'amount']

        return IngredientWeightUnitForm


class WeightUnitIngredientUpdateView(WgerFormMixin,
                                     LoginRequiredMixin,
                                     PermissionRequiredMixin,
                                     UpdateView):
    '''
    Generic view to update an weight unit to ingredient entry
    '''

    model = IngredientWeightUnit
    title = ugettext_lazy('Edit a weight unit to ingredient connection')
    form_action_urlname = 'nutrition:unit_ingredient:edit'
    permission_required = 'nutrition.add_ingredientweightunit'

    def get_success_url(self):
        return reverse('nutrition:ingredient:view', kwargs={'id': self.object.ingredient.id})

    def get_form_class(self):
        '''
        The form can only show units in the user's language
        '''

        class IngredientWeightUnitForm(ModelForm):
            unit = ModelChoiceField(queryset=WeightUnit.objects.filter(language=load_language()))

            class Meta:
                model = IngredientWeightUnit
                fields = ['unit', 'gram', 'amount']

        return IngredientWeightUnitForm


class WeightUnitIngredientDeleteView(WgerDeleteMixin,
                                     LoginRequiredMixin,
                                     PermissionRequiredMixin,
                                     DeleteView):
    '''
    Generic view to delete a weight unit to ingredient entry
    '''

    model = IngredientWeightUnit
    fields = ('unit', 'gram', 'amount')
    title = ugettext_lazy('Delete?')
    form_action_urlname = 'nutrition:unit_ingredient:delete'
    permission_required = 'nutrition.add_ingredientweightunit'

    def get_success_url(self):
        return reverse('nutrition:ingredient:view', kwargs={'id': self.object.ingredient.id})
