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

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from wger.nutrition.models import NutritionPlan
from wger.nutrition.models import Meal
from wger.nutrition.models import MealItem


logger = logging.getLogger('workout_manager.custom')


# ************************
# Meal ingredient functions
# ************************
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
        return HttpResponseRedirect(reverse('wger.nutrition.views.plan.view',
                                            kwargs={'id': plan.id}))
    else:
        return HttpResponseForbidden()


@login_required
def edit_meal_item(request, id, meal_id, item_id=None):
    '''
    Form to add a meal to a plan
    '''
    template_data = {}

    # Load the plan
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    template_data['plan'] = plan

    # Load the meal
    meal = get_object_or_404(Meal, pk=meal_id)
    template_data['meal'] = meal

    if meal.plan != plan:
        return HttpResponseForbidden()

    # Load the meal item
    # If the object is new, we will receice a 'None' (string) as the ID
    # from the template, so we check for it (ValueError) and for an actual
    # None (TypeError)
    try:
        int(item_id)
        meal_item = get_object_or_404(MealItem, pk=item_id)
        template_data['ingredient'] = meal_item.ingredient.id
        template_data['ingredient_searchfield'] = meal_item.ingredient.name

    except ValueError, TypeError:
        meal_item = MealItem()

    #template_data['meal_item'] = meal_item

    # Check that javascript is activated This is used to hide the drop down list with the
    # ingredients and use the autocompleter version instead. This is not only nicer but also much
    # faster as the ingredient list from USDA is many thosand entries long.
    js_active = request.GET.get('js', False)
    template_data['js_active'] = js_active

    # Process request
    if request.method == 'POST':
        meal_form = MealItemForm(request.POST, instance=meal_item)

        # Pass the ingredient ID back to the template, this is originally set by the JQuery
        # autocompleter, in case of errors (max. gramms reached), we need to set the ID manually
        # so the user can simply submit again.
        template_data['ingredient'] = request.POST.get('ingredient', '')

        template_data['ingredient_searchfield'] = request.POST.get('ingredient_searchfield', '')

        # If the data is valid, save and redirect
        if meal_form.is_valid():
            meal_item = meal_form.save(commit=False)
            meal_item.meal = meal
            meal_item.order = 1
            meal_item.save()

            return HttpResponseRedirect(reverse('wger.nutrition.views.plan.view',
                                                kwargs={'id': id}))

    else:
        meal_form = MealItemForm(instance=meal_item)
    template_data['form'] = meal_form

    return render_to_response('edit_meal_item.html',
                              template_data,
                              context_instance=RequestContext(request))
