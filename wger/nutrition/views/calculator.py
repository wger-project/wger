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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

import logging
import json

from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response

from wger.nutrition.forms import BmrForm
from wger.nutrition.forms import PhysicalActivitiesForm
from wger.nutrition.forms import DailyCaloriesForm


logger = logging.getLogger('wger.custom')

'''
Protein calculator views
'''


def view(request):
    '''
    The basal metabolic rate detail page
    '''

    form_data = {'age': request.user.userprofile.age,
                 'height': request.user.userprofile.height,
                 'gender': request.user.userprofile.gender,
                 'weight': request.user.userprofile.weight}

    context = {}
    context['form'] = BmrForm(initial=form_data)
    context['select_lists'] = 'gender'
    context['form_activities'] = PhysicalActivitiesForm(instance=request.user.userprofile)
    context['select_lists_activities'] = ('work_intensity',
                                          'sport_intensity',
                                          'freetime_intensity')
    context['form_calories'] = DailyCaloriesForm(instance=request.user.userprofile)

    return render_to_response('rate/form.html',
                              context,
                              context_instance=RequestContext(request))


def calculate_bmr(request):
    '''
    Calculates the basal metabolic rate.

    Currently only the Mifflin-St.Jeor-Formel is supported
    '''

    data = []

    form = BmrForm(data=request.POST, instance=request.user.userprofile)
    if form.is_valid():
        form.save()

        # Create a new weight entry as needed
        request.user.userprofile.user_bodyweight(form.cleaned_data['weight'])

        bmr = request.user.userprofile.calculate_basal_metabolic_rate()
        result = {'bmr': '{0:.0f}'.format(bmr)}
        data = json.dumps(result)
    else:
        logger.debug(form.errors)

    # Return the results to the client
    return HttpResponse(data, 'application/json')


def calculate_activities(request):
    '''
    Calculates the calories needed by additional physical activities
    '''

    data = []

    form = PhysicalActivitiesForm(data=request.POST, instance=request.user.userprofile)
    if form.is_valid():
        form.save()

        # Calculate the activities factor and the total calories
        factor = request.user.userprofile.calculate_activities()
        total = request.user.userprofile.calculate_basal_metabolic_rate() * factor
        result = {'activities': '{0:.0f}'.format(total),
                  'factor': '{0:.2f}'.format(factor)}
        data = json.dumps(result)

    else:
        logger.debug(form.errors)

    # Return the results to the client
    return HttpResponse(data, 'application/json')


def update_total(request):
    '''
    Calculates the total calories

    TODO: this really should be moved to an API so we can just update this
          setting in the user profile
    '''

    data = []

    form = DailyCaloriesForm(data=request.POST, instance=request.user.userprofile)
    if form.is_valid():
        form.save()

        # Save the total calories
        request.user.userprofile.calories = form.cleaned_data['calories']
        request.user.userprofile.save()
    else:
        logger.debug(form.errors)

    # Return the results to the client
    return HttpResponse(data, 'application/json')
