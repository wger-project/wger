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

from wger.nutrition.forms import UnitChooserForm
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
from wger.workout_manager import helpers
from wger.workout_manager.generic_views import YamlFormMixin
from wger.workout_manager.generic_views import YamlDeleteMixin
from wger.workout_manager.constants import PAGINATION_OBJECTS_PER_PAGE

logger = logging.getLogger('workout_manager.custom')


# ************************
# Ingredient functions
# ************************
class IngredientListView(ListView):
    '''
    Show an overview of all ingredients
    '''
    model = Ingredient
    template_name = 'ingredient/overview.html'
    context_object_name = 'ingredients_list'
    paginate_by = PAGINATION_OBJECTS_PER_PAGE

    def get_queryset(self):
        '''
        Filter the ingredients the user will see by its language

        (the user can also want to see ingredients in English, in addition to his
        native language, see load_ingredient_languages)
        '''
        languages = load_ingredient_languages(self.request)
        return Ingredient.objects.filter(language__in=languages)


def view(request, id, slug=None):
    template_data = {}

    ingredient = get_object_or_404(Ingredient, pk=id)
    template_data['ingredient'] = ingredient
    template_data['form'] = UnitChooserForm(data={'ingredient_id': ingredient.id,
                                                  'amount': 100,
                                                  'unit': None})

    return render_to_response('ingredient/view.html',
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
    success_url = reverse_lazy('ingredient-list')
    messages = ugettext_lazy('Ingredient successfully deleted')

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(IngredientDeleteView, self).get_context_data(**kwargs)

        context['title'] = _('Delete %s?') % self.object.name
        context['form_action'] = reverse('ingredient-delete', kwargs={'pk': self.object.id})

        return context


class IngredientEditView(YamlFormMixin, UpdateView):
    '''
    Generic view to update an existing ingredient
    '''

    model = Ingredient
    form_class = IngredientForm
    title = ugettext_lazy('Add a new ingredient')
    form_action_urlname = 'ingredient-edit'
    messages = ugettext_lazy('Ingredient successfully updated')


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


def search(request):
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
        return render_to_response('ingredient/search.html',
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
        result.append({'id': unit.id,
                       'name': unit.unit.name,
                       'amount': unit.amount,
                       'name_model': unicode(unit)})

    return HttpResponse(json.dumps(result, cls=helpers.DecimalJsonEncoder),
                        'application/json')


def ajax_get_ingredient_values(request, pk):
    '''
    Calculates the nutritional values for the given amount and exercise
    '''

    result = {'energy': 0,
              'protein': 0,
              'carbohydrates': 0,
              'carbohydrates_sugar': 0,
              'fat': 0,
              'fat_saturated': 0,
              'fibres': 0,
              'sodium': 0,
              'errors': []}
    ingredient = get_object_or_404(Ingredient, pk=pk)

    if request.method == 'POST':
        form = UnitChooserForm(request.POST)

        if form.is_valid():

            # Create a temporary MealItem object
            if form.cleaned_data['unit']:
                unit_id = form.cleaned_data['unit'].id
            else:
                unit_id = None

            item = MealItem()
            item.ingredient = ingredient
            item.weight_unit_id = unit_id
            item.amount = form.cleaned_data['amount']

            result = item.get_nutritional_values()
        else:
            result['errors'] = form.errors

    return HttpResponse(json.dumps(result, cls=helpers.DecimalJsonEncoder),
                        'application/json')
