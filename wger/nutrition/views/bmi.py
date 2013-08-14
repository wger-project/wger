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

from django.utils.translation import ugettext as _

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
        if (not WeightEntry.objects.all().exists()
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
    '''

    data = json.dumps([
        {'key': 'Group1', 'height': 160, 'weight': 40},
        {'key': 'Group1', 'height': 200, 'weight': 65},
        {'key': 'Group2', 'height': 160, 'weight': 44},
        {'key': 'Group2', 'height': 200, 'weight': 68},
        {'key': 'Group3', 'height': 160, 'weight': 48},
        {'key': 'Group3', 'height': 200, 'weight': 72},
        {'key': 'Group4', 'height': 160, 'weight': 63},
        {'key': 'Group4', 'height': 200, 'weight': 100},
        {'key': 'Group5', 'height': 160, 'weight': 76},
        {'key': 'Group5', 'height': 200, 'weight': 120},
        {'key': 'Group6', 'height': 160, 'weight': 88},
        {'key': 'Group6', 'height': 187, 'weight': 120},
        {'key': 'Group7', 'height': 160, 'weight': 102},
        {'key': 'Group7', 'height': 175, 'weight': 120}
        ])

    # Return the results to the client
    return HttpResponse(data, 'application/json')
