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
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm


from nutrition.models import NutritionPlan
from nutrition.models import Meal
from nutrition.models import MealItem

from exercises.views import load_language

logger = logging.getLogger('workout_manager.custom')


class PlanForm(ModelForm):
    class Meta:
        model = NutritionPlan
        exclude=('user', 'language', )

@login_required
def overview(request):
    template_data = {}
    template_data.update(csrf(request))
    template_data['active_tab'] = 'nutrition'
    
    plans  = NutritionPlan.objects.filter(user = request.user)
    template_data['plans'] = plans
    
    return render_to_response('nutrition_overview.html',
                              template_data,
                              context_instance=RequestContext(request))

@login_required
def add(request):
    """Add a new nutrition plan and redirect to its page
    """
    
    plan = NutritionPlan()
    plan.user = request.user
    plan.language = load_language()
    plan.save()
    
    return HttpResponseRedirect('/nutrition/%s/view/' % plan.id)


@login_required
def view(request, id):
    """Show the nutrition plan with the given ID
    """
    template_data = {}
    template_data['active_tab'] = 'nutrition'
    
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    template_data['plan'] = plan
    
    # Sum the nutrional info
    nutritional_info = {'energy': 0,
                        'protein': 0,
                        'carbohydrates': 0}
    for meal in plan.meal_set.select_related():
        for item in meal.mealitem_set.select_related():
            if item.ingredient and item.amount_gramm:
                nutritional_info['energy'] += item.ingredient.energy * item.amount_gramm / 100
                nutritional_info['protein'] += item.ingredient.protein  * item.amount_gramm / 100
                nutritional_info['carbohydrates'] += item.ingredient.carbohydrates  * item.amount_gramm / 100
    template_data['nutritonal_data'] = nutritional_info
    
    
    return render_to_response('view_nutrition_plan.html', 
                              template_data,
                              context_instance=RequestContext(request))

@login_required
def edit_plan(request, id):
    """Edits a nutrition plan
    """
    template_data = {}
    template_data['active_tab'] = 'nutrition'
    
    # Load the plan
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    template_data['plan'] = plan
    
    # Process request
    if request.method == 'POST':
        form = PlanForm(request.POST, instance=plan)
        
        # If the data is valid, save and redirect
        if form.is_valid():
            plan = form.save(commit=False)
            #plan.language = load_language()
            plan.save()
            
            return HttpResponseRedirect('/nutrition/%s/view/' % id)
    else:
        form = PlanForm(instance=plan)
    template_data['form'] = form
    
    
    return render_to_response('edit_plan.html', 
                              template_data,
                              context_instance=RequestContext(request))



# ************************
# Meal functions
# ************************

class MealForm(ModelForm):
    class Meta:
        model = Meal
        exclude=('plan',)

class MealItemForm(ModelForm):
    class Meta:
        model = MealItem
        exclude=('meal', 'order')

@login_required
def edit_meal(request, id, meal_id):
    """Form to add a meal to a plan
    """
    template_data = {}
    template_data['active_tab'] = 'nutrition'
    
    # Load the plan
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    template_data['plan'] = plan
    
    # Load the meal
    meal = get_object_or_404(Meal, pk=meal_id)
    template_data['meal'] = meal
    
    if meal.plan != plan:
        return HttpResponseForbidden()
    
    
    # Process request
    if request.method == 'POST':
        meal_form = MealForm(request.POST, instance=meal)
        
        # If the data is valid, save and redirect
        if meal_form.is_valid():
            meal_item = meal_form.save(commit=False)
            meal_item.order = 1
            meal_item.save()
            
            return HttpResponseRedirect('/nutrition/%s/view/' % id)
    else:
        meal_form = MealForm(instance=meal)
    template_data['form'] = meal_form
    
    
    return render_to_response('edit_meal.html', 
                              template_data,
                              context_instance=RequestContext(request))
    


@login_required
def add_meal(request, id, meal_id=None):
    """Form to add a meal to a plan
    """
    template_data = {}
    template_data['active_tab'] = 'nutrition'
    
    # Load the plan
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    template_data['plan'] = plan
    
    meal = Meal()
    meal.plan = plan
    meal.order = 1
    meal.save()
    
    return HttpResponseRedirect('/nutrition/%s/view/' % plan.id)

@login_required
def delete_meal(request, id):
    """Deletes the meal with the given ID
    """
    
    # Load the meal
    meal = get_object_or_404(Meal, pk=id)
    plan = meal.plan
    
    # Only delete if the user is the owner
    if plan.user == request.user:
        meal.delete()
        return HttpResponseRedirect('/nutrition/%s/view/' % plan.id)
    else:
        return HttpResponseForbidden()



# ************************
# Meal ingredient functions
# ************************

@login_required
def delete_meal_item(request, item_id):
    """Deletes the meal ingredient with the given ID
    """
    
    # Load the item
    item = get_object_or_404(MealItem, pk=item_id)
    plan = item.meal.plan
    
    # Only delete if the user is the owner
    if plan.user == request.user:
        item.delete()
        return HttpResponseRedirect('/nutrition/%s/view/' % plan.id)
    else:
        return HttpResponseForbidden()

@login_required
def edit_meal_item(request, id, meal_id, item_id=None):
    """Form to add a meal to a plan
    """
    template_data = {}
    template_data['active_tab'] = 'nutrition'
    
    # Load the plan
    plan = get_object_or_404(NutritionPlan, pk=id, user=request.user)
    template_data['plan'] = plan
    
    # Load the meal
    meal = get_object_or_404(Meal, pk=meal_id)
    template_data['meal'] = meal
    
    if meal.plan != plan:
        return HttpResponseForbidden()
    
    
    # Load the meal item
    if not item_id or item_id == 'None':
        meal_item = MealItem()
    else:
        meal_item = get_object_or_404(MealItem, pk=item_id)

    template_data['meal_item'] = meal_item
    
    
    
    # Process request
    if request.method == 'POST':
        meal_form = MealItemForm(request.POST, instance=meal_item)
        
        # If the data is valid, save and redirect
        if meal_form.is_valid():
            meal_item = meal_form.save(commit=False)
            meal_item.meal = meal
            meal_item.order = 1
            meal_item.save()
            
            return HttpResponseRedirect('/nutrition/%s/view/' % id)
    else:
        meal_form = MealItemForm(instance=meal_item)
    template_data['form'] = meal_form
    
    return render_to_response('edit_meal_item.html', 
                              template_data,
                              context_instance=RequestContext(request))