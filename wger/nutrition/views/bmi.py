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

import datetime
import logging
import json

from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response

from wger.nutrition.forms import BmiForm
from wger.weight.models import WeightEntry
from wger.utils import helpers

logger = logging.getLogger('wger.custom')

'''
BMI views
'''


def view(request):
    '''
    The BMI calculator detail page
    '''

    context = {}
    form_data = {'height': request.user.userprofile.height,
                 'weight': request.user.userprofile.weight}
    context['form'] = BmiForm(initial=form_data)
    return render_to_response('bmi/form.html',
                              context,
                              context_instance=RequestContext(request))


def calculate(request):
    '''
    Calculates the BMI
    '''

    data = []

    form = BmiForm(request.POST, instance=request.user.userprofile)
    if form.is_valid():
        form.save()

        # Create a new weight entry as needed
        if (not WeightEntry.objects.filter(user=request.user).exists()
           or (datetime.date.today()
               - WeightEntry.objects.filter(user=request.user).latest().creation_date
               > datetime.timedelta(1))):
            entry = WeightEntry()
            entry.weight = form.cleaned_data['weight']
            entry.user = request.user
            entry.creation_date = datetime.date.today()
            entry.save()

        # Update the last entry
        else:
            entry = WeightEntry.objects.filter(user=request.user).latest()
            entry.weight = form.cleaned_data['weight']
            entry.save()

        bmi = request.user.userprofile.calculate_bmi()
        result = {'bmi': '{0:.2f}'.format(bmi),
                  'weight': form.cleaned_data['weight'],
                  'height': request.user.userprofile.height}
        data = json.dumps(result, cls=helpers.DecimalJsonEncoder)

    # Return the results to the client
    return HttpResponse(data, 'application/json')


def chart_data(request):
    '''
    Returns the data to render the BMI chart

    The individual values taken from
    * http://apps.who.int/bmi/index.jsp?introPage=intro_3.html
    * https://de.wikipedia.org/wiki/Body-Mass-Index
    '''

    data = json.dumps([
        {'key': 'filler', 'height': 150, 'weight': 36},
        {'key': 'filler', 'height': 200, 'weight': 64},

        {'key': 'severe_thinness', 'height': 150, 'weight': 36},
        {'key': 'severe_thinness', 'height': 200, 'weight': 64},

        {'key': 'moderate_thinness', 'height': 150, 'weight': 36.25},
        {'key': 'moderate_thinness', 'height': 200, 'weight': 64},

        {'key': 'mild_thinness', 'height': 150, 'weight': 41.625},
        {'key': 'mild_thinness', 'height': 200, 'weight': 74},

        {'key': 'normal_range', 'height': 150, 'weight': 56.025},
        {'key': 'normal_range', 'height': 200, 'weight': 99.6},

        {'key': 'pre_obese', 'height': 150, 'weight': 67.275},
        {'key': 'pre_obese', 'height': 200, 'weight': 119.6},

        {'key': 'obese_class_1', 'height': 150, 'weight': 78.525},
        {'key': 'obese_class_1', 'height': 200, 'weight': 139.6},

        {'key': 'obese_class_2', 'height': 150, 'weight': 89.775},
        {'key': 'obese_class_2', 'height': 200, 'weight': 159},

        {'key': 'obese_class_3', 'height': 150, 'weight': 190},
        {'key': 'obese_class_3', 'height': 200, 'weight': 190}
        ])

    # Return the results to the client
    return HttpResponse(data, 'application/json')
