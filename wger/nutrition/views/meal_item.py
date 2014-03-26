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

from django import forms
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy

from django.views.generic import CreateView
from django.views.generic import UpdateView

from wger.nutrition.models import Meal
from wger.nutrition.models import MealItem
from wger.nutrition.models import Ingredient
from wger.nutrition.models import IngredientWeightUnit

from wger.utils.generic_views import WgerFormMixin


logger = logging.getLogger('wger.custom')


# ************************
# Meal ingredient functions
# ************************
class MealItemForm(forms.ModelForm):
    weight_unit = forms.ModelChoiceField(queryset=IngredientWeightUnit.objects.none(),
                                         empty_label="g",
                                         required=False)
    ingredient = forms.ModelChoiceField(queryset=Ingredient.objects.all(),
                                        widget=forms.HiddenInput)

    class Meta:
        model = MealItem

    def __init__(self, *args, **kwargs):
        super(MealItemForm, self).__init__(*args, **kwargs)

        # Get the ingredient_id
        ingredient_id = None

        if kwargs.get('instance'):
            ingredient_id = kwargs['instance'].ingredient_id

        if kwargs.get('data'):
            ingredient_id = kwargs['data']['ingredient']

        # Filter the available ingredients
        if ingredient_id:
            self.fields['weight_unit'].queryset = \
                IngredientWeightUnit.objects.filter(ingredient_id=ingredient_id)


@login_required
def delete_meal_item(request, item_id):
    '''
    Deletes the meal ingredient with the given ID
    '''

    # Load the item
    item = get_object_or_404(MealItem, pk=item_id)
    plan = item.meal.plan

    # Only delete if the user is the owner
    if plan.user == request.user:
        item.delete()
        return HttpResponseRedirect(reverse('nutrition-view', kwargs={'id': plan.id}))
    else:
        return HttpResponseForbidden()


class MealItemCreateView(WgerFormMixin, CreateView):
    '''
    Generic view to create a new meal item
    '''

    model = MealItem
    form_class = MealItemForm
    template_name = 'meal_item/edit.html'

    def dispatch(self, request, *args, **kwargs):
        '''
        Check that the user owns the meal
        '''
        meal = get_object_or_404(Meal, pk=kwargs['meal_id'])
        if meal.plan.user == request.user:
            self.meal = meal
            return super(MealItemCreateView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def get_success_url(self):
        return reverse('nutrition-view', kwargs={'id': self.meal.plan.id})

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(MealItemCreateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('mealitem-add', kwargs={'meal_id': self.meal.id})
        context['ingredient_searchfield'] = self.request.POST.get('ingredient_searchfield', '')
        return context

    def form_valid(self, form):
        '''
        Manually set the corresponding meal
        '''
        form.instance.meal = self.meal
        form.instance.order = 1
        return super(MealItemCreateView, self).form_valid(form)


class MealItemEditView(WgerFormMixin, UpdateView):
    '''
    Generic view to update an existing meal item
    '''

    model = MealItem
    form_class = MealItemForm
    title = ugettext_lazy('Edit meal item')
    form_action_urlname = 'mealitem-edit'
    template_name = 'meal_item/edit.html'

    def get_success_url(self):
        return reverse('nutrition-view', kwargs={'id': self.object.meal.plan.id})

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(MealItemEditView, self).get_context_data(**kwargs)
        context['ingredient_searchfield'] = self.object.ingredient.name
        return context
