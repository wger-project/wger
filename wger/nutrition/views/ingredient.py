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

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core import mail
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.core.cache import cache
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import ListView

from wger.nutrition.forms import UnitChooserForm
from wger.nutrition.models import MealItem
from wger.nutrition.models import Ingredient
from wger.nutrition.models import IngredientWeightUnit

from wger.utils import helpers
from wger.utils.generic_views import YamlFormMixin
from wger.utils.generic_views import YamlDeleteMixin
from wger.utils.constants import PAGINATION_OBJECTS_PER_PAGE
from wger.utils.language import load_language
from wger.utils.language import load_ingredient_languages
from wger.utils.cache import cache_mapper

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
        return (Ingredient.objects.filter(language__in=languages)
                                  .filter(status__in=Ingredient.INGREDIENT_STATUS_OK)
                                  .only('id', 'name'))


def view(request, id, slug=None):
    template_data = {}

    ingredient = cache.get(cache_mapper.get_ingredient_key(int(id)))
    if not ingredient:
        ingredient = get_object_or_404(Ingredient, pk=id)
        cache.set(cache_mapper.get_ingredient_key(ingredient), ingredient)
    template_data['ingredient'] = ingredient
    template_data['form'] = UnitChooserForm(data={'ingredient_id': ingredient.id,
                                                  'amount': 100,
                                                  'unit': None})

    return render_to_response('ingredient/view.html',
                              template_data,
                              context_instance=RequestContext(request))


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
    title = ugettext_lazy('Edit ingredient')
    form_action_urlname = 'ingredient-edit'
    messages = ugettext_lazy('Ingredient successfully updated')


class IngredientCreateView(YamlFormMixin, CreateView):
    '''
    Generic view to add a new ingredient
    '''

    model = Ingredient
    title = ugettext_lazy('Add a new ingredient')
    form_action = reverse_lazy('ingredient-add')
    sidebar = 'ingredient/form.html'

    def form_valid(self, form):

        # set the submitter, if admin, set approrpiate status
        form.instance.user = self.request.user
        if self.request.user.has_perm('nutrition.add_ingredient'):
            form.instance.status = Ingredient.INGREDIENT_STATUS_ADMIN
        else:
            subject = _('New user submitted ingredient')
            message = _('''The user {0} submitted a new ingredient "{1}".'''.format(
                        self.request.user.username, form.instance.name))
            mail.mail_admins(subject,
                             message,
                             fail_silently=True)

        form.instance.language = load_language()
        return super(IngredientCreateView, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        '''
        Demo users can't submit ingredients
        '''
        if request.user.get_profile().is_temporary:
            return HttpResponseForbidden()
        return super(IngredientCreateView, self).dispatch(request, *args, **kwargs)


class PendingIngredientListView(ListView):
    '''
    List all ingredients pending review
    '''

    model = Ingredient
    template_name = 'ingredient/pending.html'
    context_object_name = 'ingredient_list'

    def get_queryset(self):
        '''
        Only show ingredients pending review
        '''
        return Ingredient.objects.filter(status=Ingredient.INGREDIENT_STATUS_PENDING)


@permission_required('nutrition.add_ingredient')
def accept(request, pk):
    '''
    Accepts a pending user submitted ingredient
    '''
    ingredient = get_object_or_404(Ingredient, pk=pk)
    ingredient.status = Ingredient.INGREDIENT_STATUS_ACCEPTED
    ingredient.save()
    ingredient.send_email(request)
    messages.success(request, _('Ingredient was sucessfully added to the general database'))

    return HttpResponseRedirect(ingredient.get_absolute_url())


@permission_required('nutrition.add_ingredient')
def decline(request, pk):
    '''
    Declines and deletes a pending user submitted ingredient
    '''
    ingredient = get_object_or_404(Ingredient, pk=pk)
    ingredient.status = Ingredient.INGREDIENT_STATUS_DECLINED
    ingredient.save()
    messages.success(request, _('Ingredient was sucessfully marked as rejected'))
    return HttpResponseRedirect(ingredient.get_absolute_url())


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
    ingredients = Ingredient.objects.filter(name__icontains=q,
                                            language__in=languages,
                                            status__in=Ingredient.INGREDIENT_STATUS_OK)

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
