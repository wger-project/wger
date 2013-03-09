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
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy

from django.views.generic import CreateView
from django.views.generic import UpdateView

from wger.nutrition.models import NutritionPlan
from wger.nutrition.models import Meal
from wger.nutrition.models import MealItem

from wger.workout_manager.generic_views import YamlFormMixin


logger = logging.getLogger('workout_manager.custom')


# ************************
# Meal functions
# ************************

class MealForm(ModelForm):
    class Meta:
        model = Meal
        exclude = ('plan', 'order')


class MealItemForm(ModelForm):
    class Meta:
        model = MealItem
        exclude = ('meal', 'order')


class MealCreateView(YamlFormMixin, CreateView):
    '''
    Generic view to add a new meal to a nutrition plan
    '''

    model = Meal
    form_class = MealForm
    title = ugettext_lazy('Add new meal')
    owner_object = {'pk': 'plan_pk', 'class': NutritionPlan}

    def form_valid(self, form):
        plan = get_object_or_404(NutritionPlan, pk=self.kwargs['plan_pk'], user=self.request.user)
        form.instance.plan = plan
        form.instance.order = 1
        return super(MealCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('wger.nutrition.views.plan.view', kwargs={'id': self.object.plan.id})

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(MealCreateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('meal-add',
                                         kwargs={'plan_pk': self.kwargs['plan_pk']})

        return context


class MealEditView(YamlFormMixin, UpdateView):
    '''
    Generic view to update an existing meal
    '''

    model = Meal
    form_class = MealForm
    title = ugettext_lazy('Edit meal')
    form_action_urlname = 'meal-edit'

    def get_success_url(self):
        return reverse('wger.nutrition.views.plan.view', kwargs={'id': self.object.plan.id})


@login_required
def delete_meal(request, id):
    '''
    Deletes the meal with the given ID
    '''

    # Load the meal
    meal = get_object_or_404(Meal, pk=id)
    plan = meal.plan

    # Only delete if the user is the owner
    if plan.user == request.user:
        meal.delete()
        return HttpResponseRedirect(reverse('wger.nutrition.views.plan.view',
                                            kwargs={'id': plan.id}))
    else:
        return HttpResponseForbidden()
