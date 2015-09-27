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

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy

from django.views.generic import CreateView, UpdateView

from wger.nutrition.models import NutritionPlan, Meal
from wger.utils.generic_views import WgerFormMixin

logger = logging.getLogger(__name__)


# ************************
# Meal functions
# ************************

class MealCreateView(WgerFormMixin, CreateView):
    '''
    Generic view to add a new meal to a nutrition plan
    '''

    model = Meal
    fields = '__all__'
    title = ugettext_lazy('Add new meal')
    owner_object = {'pk': 'plan_pk', 'class': NutritionPlan}

    def form_valid(self, form):
        plan = get_object_or_404(NutritionPlan, pk=self.kwargs['plan_pk'], user=self.request.user)
        form.instance.plan = plan
        form.instance.order = 1
        return super(MealCreateView, self).form_valid(form)

    def get_success_url(self):
        return self.object.plan.get_absolute_url()

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(MealCreateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('nutrition:meal:add',
                                         kwargs={'plan_pk': self.kwargs['plan_pk']})

        return context


class MealEditView(WgerFormMixin, UpdateView):
    '''
    Generic view to update an existing meal
    '''

    model = Meal
    fields = '__all__'
    title = ugettext_lazy('Edit meal')
    form_action_urlname = 'nutrition:meal:edit'

    def get_success_url(self):
        return self.object.plan.get_absolute_url()


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
        return HttpResponseRedirect(plan.get_absolute_url())
    else:
        return HttpResponseForbidden()
