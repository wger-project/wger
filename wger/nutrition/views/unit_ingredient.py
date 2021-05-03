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
from django.forms import (
    ModelChoiceField,
    ModelForm
)
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    UpdateView
)

# wger
from wger.nutrition.models import (
    Ingredient,
    IngredientWeightUnit,
    WeightUnit
)
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin
)
from wger.utils.language import load_language


logger = logging.getLogger(__name__)


# ************************
# Weight units to ingredient functions
# ************************


class WeightUnitIngredientCreateView(WgerFormMixin,
                                     LoginRequiredMixin,
                                     PermissionRequiredMixin,
                                     CreateView):
    """
    Generic view to add a new weight unit to ingredient entry
    """

    model = IngredientWeightUnit
    title = gettext_lazy('Add a new weight unit')
    permission_required = 'nutrition.add_ingredientweightunit'

    def get_success_url(self):
        return reverse('nutrition:ingredient:view', kwargs={'id': self.kwargs['ingredient_pk']})

    def form_valid(self, form):
        ingredient = get_object_or_404(Ingredient, pk=self.kwargs['ingredient_pk'])
        form.instance.ingredient = ingredient
        return super(WeightUnitIngredientCreateView, self).form_valid(form)

    def get_form_class(self):
        """
        The form can only show units in the user's language
        """

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
    """
    Generic view to update an weight unit to ingredient entry
    """

    model = IngredientWeightUnit
    title = gettext_lazy('Edit a weight unit to ingredient connection')
    permission_required = 'nutrition.add_ingredientweightunit'

    def get_success_url(self):
        return reverse('nutrition:ingredient:view', kwargs={'id': self.object.ingredient.id})

    def get_form_class(self):
        """
        The form can only show units in the user's language
        """

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
    """
    Generic view to delete a weight unit to ingredient entry
    """

    model = IngredientWeightUnit
    fields = ('unit', 'gram', 'amount')
    title = gettext_lazy('Delete?')
    permission_required = 'nutrition.add_ingredientweightunit'

    def get_success_url(self):
        return reverse('nutrition:ingredient:view', kwargs={'id': self.object.ingredient.id})
