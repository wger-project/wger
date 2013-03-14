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
import json

from django import forms
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy


from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import ListView


from wger.nutrition.models import NutritionPlan
from wger.nutrition.models import Meal
from wger.nutrition.models import MealItem
from wger.nutrition.models import Ingredient
from wger.nutrition.models import WeightUnit
from wger.nutrition.models import IngredientWeightUnit
from wger.nutrition.models import MEALITEM_WEIGHT_GRAM
from wger.nutrition.models import MEALITEM_WEIGHT_UNIT

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4, cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table
from reportlab.lib import colors

from wger.manager.utils import load_language
from wger.manager.utils import load_ingredient_languages

from wger.workout_manager import get_version
from wger.workout_manager.generic_views import YamlFormMixin
from wger.workout_manager.generic_views import YamlDeleteMixin
from wger.workout_manager import helpers

logger = logging.getLogger('workout_manager.custom')


# ************************
# Meal ingredient functions
# ************************
class MealItemForm(forms.ModelForm):
    weight_unit = forms.ModelChoiceField(queryset=IngredientWeightUnit.objects.none(),
                                         empty_label="g",
                                         required=False)

    class Meta:
        model = MealItem
        exclude = ('meal', 'order', )

    def __init__(self, *args, **kwargs):
        super(MealItemForm, self).__init__(*args, **kwargs)
        try:
            ingredient_id = args[0]['ingredient']
        except IndexError:
            ingredient_id = None

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

    template_data['meal_item'] = meal_item

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
        #else:
        #    logger.debug(meal_form.errors)

    else:
        meal_form = MealItemForm(instance=meal_item)
    template_data['form'] = meal_form

    return render_to_response('edit_meal_item.html',
                              template_data,
                              context_instance=RequestContext(request))


# ************************
# Ingredient functions
# ************************
def ingredient_overview(request):
    '''
    Show an overview of all ingredients
    '''

    template_data = {}

    # Filter the ingredients the user will see by its language
    # (the user can also want to see ingredients in English, see load_ingredient_languages)
    languages = load_ingredient_languages(request)

    # Load the ingredients and paginate it
    ingredients_list = Ingredient.objects.filter(language__in=languages)

    pagination = helpers.pagination(ingredients_list, request.GET.get('page'))
    template_data['page_range'] = pagination['page_range']
    template_data['ingredients'] = pagination['page']

    return render_to_response('ingredient_overview.html',
                              template_data,
                              context_instance=RequestContext(request))


def ingredient_view(request, id, slug=None):
    template_data = {}

    ingredient = get_object_or_404(Ingredient, pk=id)
    template_data['ingredient'] = ingredient

    return render_to_response('view_ingredient.html',
                              template_data,
                              context_instance=RequestContext(request))


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        exclude = ('language',)


class IngredientDeleteView(YamlDeleteMixin, DeleteView):
    '''
    Generic view to delete an existing ingredient
    '''

    model = Ingredient
    template_name = 'delete.html'
    success_url = reverse_lazy('wger.nutrition.views.ingredient.ingredient_overview')

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(IngredientDeleteView, self).get_context_data(**kwargs)

        context['title'] = _('Delete %s?') % self.object.name
        context['form_action'] = reverse('ingredient-delete', kwargs={'pk': self.kwargs['pk']})

        return context


class IngredientEditView(YamlFormMixin, UpdateView):
    '''
    Generic view to update an existing ingredient
    '''

    model = Ingredient
    form_class = IngredientForm
    title = ugettext_lazy('Add a new ingredient')
    form_action_urlname = 'ingredient-edit'


class IngredientCreateView(YamlFormMixin, CreateView):
    '''
    Generic view to add a new ingredient
    '''

    model = Ingredient
    form_class = IngredientForm
    title = ugettext_lazy('Add a new ingredient')
    form_action = reverse_lazy('ingredient-add')

    def form_valid(self, form):
        form.instance.language = load_language()
        return super(IngredientCreateView, self).form_valid(form)


def ingredient_search(request):
    '''
    Search for an exercise, return the result as a JSON list or as HTML page, depending on how
    the function was invoked
    '''

    # Filter the ingredients the user will see by its language
    # (the user can also want to see ingredients in English, see load_ingredient_languages)
    languages = load_ingredient_languages(request)

    # Perform the search
    q = request.GET.get('term', '')
    ingredients = Ingredient.objects.filter(name__icontains=q, language__in=languages)

    # AJAX-request, this comes from the autocompleter. Create a list and send it back as JSON
    if request.is_ajax():

        results = []
        for ingredient in ingredients:
            ingredient_json = {}
            ingredient_json['id'] = ingredient.id
            ingredient_json['name'] = ingredient.name
            ingredient_json['value'] = ingredient.name
            results.append(ingredient_json)
        data = json.dumps(results)

        # Return the results to the server
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)

    # Usual search (perhaps JS disabled), present the results as normal HTML page
    else:
        template_data = {}
        template_data.update(csrf(request))
        template_data['ingredients'] = ingredients
        template_data['search_term'] = q
        return render_to_response('ingredient_search.html',
                                  template_data,
                                  context_instance=RequestContext(request))


@login_required
def ajax_get_ingredient_units(request, pk):
    '''
    Fetches the available ingredient units
    '''

    units = IngredientWeightUnit.objects.filter(ingredient_id=pk)
    result = []
    for unit in units:
        result.append({'id': unit.id, 'name': unit.unit.name, 'amount': unit.amount})

    return HttpResponse(json.dumps(result, cls=helpers.DecimalJsonEncoder),
                        'application/json')
