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

from django.utils.translation import ugettext as _

from wger.nutrition.forms import BmrForm
from wger.nutrition.forms import PhysicalActivitiesForm
from wger.nutrition.forms import DailyCaloriesForm
from wger.manager.models import UserProfile


logger = logging.getLogger('wger.custom')

'''
Protein calculator views
'''


def view(request):
    '''
    The basal metabolic rate detail page
    '''

    context = {}
    context['form'] = BmrForm()
    context['select_lists'] = 'gender'
    context['form_activities'] = PhysicalActivitiesForm()
    context['select_lists_activities'] = ('work_intensity',
                                          'sport_intensity',
                                          'freetime_intensity')
    context['form_calories'] = DailyCaloriesForm()

    return render_to_response('rate/form.html',
                              context,
                              context_instance=RequestContext(request))


def calculate(request):
    '''
    Calculates the basal metabolic rate.

    Currently only the Mifflin-St.Jeor-Formel is supported
    '''

    data = []

    form = BmrForm(request.POST)
    if form.is_valid():
        if form.cleaned_data['gender'] == UserProfile.GENDER_MALE:
            factor = 5
        else:
            factor = -161
        rate = ((10 * form.cleaned_data['weight'])  # in kg
                + (6.25 * form.cleaned_data['height'])  # in cm
                - (5 * form.cleaned_data['age'])  # in years
                + factor
                )
        result = {'bmr': '{0:.0f}'.format(rate)}
        data = json.dumps(result)
        #logger.debug(data)
    #else:
    #    logger.debug(form.errors)

    # Return the results to the server
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def calculate_activities(request):
    '''
    Calculates the calories needed by additional physical activities
    '''

    data = []

    form = PhysicalActivitiesForm(request.POST)
    if form.is_valid():

        # Sleep
        sleep = form.cleaned_data['sleep_hours'] * 1.9

        # Work
        if form.cleaned_data['work_hours'] == UserProfile.INTENSITY_LOW:
            work_factor = 1.5
        elif form.cleaned_data['work_hours'] == UserProfile.INTENSITY_MEDIUM:
            work_factor = 2
        else:
            work_factor = 4
        work = form.cleaned_data['work_hours'] * work_factor

        # Sport
        if form.cleaned_data['sport_hours'] == UserProfile.INTENSITY_LOW:
            sport_factor = 3
        elif form.cleaned_data['sport_hours'] == UserProfile.INTENSITY_MEDIUM:
            sport_factor = 7
        else:
            sport_factor = 12
        sport = form.cleaned_data['sport_hours'] * sport_factor

        # Free time
        if form.cleaned_data['freetime_hours'] == UserProfile.INTENSITY_LOW:
            freetime_factor = 2
        elif form.cleaned_data['freetime_hours'] == UserProfile.INTENSITY_MEDIUM:
            freetime_factor = 4
        else:
            freetime_factor = 6
        freetime = form.cleaned_data['freetime_hours'] * freetime_factor

        total = (sleep + work + sport + freetime) / 24.0
        result = {'activities': '{0:.2f}'.format(total)}
        data = json.dumps(result)
        logger.debug(data)
    else:
        logger.debug(form.errors)

    # Return the results to the server
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
