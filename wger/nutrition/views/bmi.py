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

from wger.nutrition.forms import BmiForm


logger = logging.getLogger('wger.custom')

'''
BMI views
'''


def view(request):
    '''
    The BMI calculator detail page
    '''

    context = {}
    context['form'] = BmiForm()
    return render_to_response('bmi/form.html',
                              context,
                              context_instance=RequestContext(request))


def calculate(request):
    '''
    Calculates the BMI
    '''

    data = []

    form = BmiForm(request.POST)
    if form.is_valid():
        height = form.cleaned_data['height'] / float(100)
        result = {'bmi': '{0:.2f}'.format(float(80) / (height * height))}
        data = json.dumps(result)
    else:
        logger.debug(form.errors)

    # Return the results to the server
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
