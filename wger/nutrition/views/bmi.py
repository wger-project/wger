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
           or (datetime.date.today() - WeightEntry.objects.all().latest().creation_date
               > datetime.timedelta(1))):
            entry = WeightEntry()
            entry.weight = form.cleaned_data['weight']
            entry.user = request.user
            entry.creation_date = datetime.date.today()
            entry.save()

        # Update the last entry
        else:
            entry = WeightEntry.objects.all().latest()
            entry.weight = form.cleaned_data['weight']
            entry.save()

        bmi = request.user.userprofile.calculate_bmi()
        result = {'bmi': '{0:.2f}'.format(bmi)}
        data = json.dumps(result)

    # Return the results to the client
    return HttpResponse(data, 'application/json')
