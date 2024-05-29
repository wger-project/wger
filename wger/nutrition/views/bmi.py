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

# Standard Library
import json
import logging

# Django
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _

# wger
from wger.nutrition.forms import BmiForm
from wger.utils import helpers
from wger.utils.units import AbstractHeight


logger = logging.getLogger(__name__)
"""
BMI views
"""


@login_required
def view(request):
    """
    The BMI calculator detail page
    """

    context = {}
    form_data = {
        'height': request.user.userprofile.height,
        'weight': request.user.userprofile.weight,
        'use_metric': request.user.userprofile.use_metric,
    }
    context['form'] = BmiForm(initial=form_data)
    return render(request, 'bmi/form.html', context)


@login_required
def calculate(request):
    """
    Calculates the BMI
    """

    data = []

    form = BmiForm(request.POST, instance=request.user.userprofile)
    output_height = request.POST['height']

    if not request.user.userprofile.use_metric:
        request_copy = request.POST.copy()
        output_height = request_copy['height']
        request_copy['height'] = AbstractHeight(request_copy['height'], mode='inches').cm
        form = BmiForm(request_copy, instance=request.user.userprofile)

    if form.is_valid():
        form.save()

        # Create a new weight entry as needed
        request.user.userprofile.user_bodyweight(form.cleaned_data['weight'])

        bmi = request.user.userprofile.calculate_bmi()
        result = {
            'bmi': '{0:.2f}'.format(bmi),
            'weight': form.cleaned_data['weight'],
            'height': output_height,
        }
        data = json.dumps(result, cls=helpers.DecimalJsonEncoder)
        response = HttpResponse(data, 'application/json')
    else:
        help_message = {
            ('error'): _('Please make sure your height is within the appropriate range.'),
        }
        if request.user.userprofile.use_metric:
            help_message['cm_range'] = _('140 to 230')
        else:
            help_message['in_range'] = _('56 to 90')
        data = json.dumps(help_message)
        response = HttpResponse(data, 'application/json')
        response.status_code = 406
    # Return the results to the client
    return response


def chart_data(request):
    """
    Returns the data to render the BMI chart

    The individual values taken from
    * http://apps.who.int/bmi/index.jsp?introPage=intro_3.html
    * https://de.wikipedia.org/wiki/Body-Mass-Index
    """

    if request.user.userprofile.use_metric:
        data = json.dumps(
            [
                {'key': 'filler', 'height': 150, 'weight': 30},
                {'key': 'filler', 'height': 200, 'weight': 30},
                {'key': 'severe_thinness', 'height': 150, 'weight': 35.978},
                {'key': 'severe_thinness', 'height': 200, 'weight': 63.960},
                {'key': 'moderate_thinness', 'height': 150, 'weight': 38.228},
                {'key': 'moderate_thinness', 'height': 200, 'weight': 67.960},
                {'key': 'mild_thinness', 'height': 150, 'weight': 41.603},
                {'key': 'mild_thinness', 'height': 200, 'weight': 73.960},
                {'key': 'normal_range', 'height': 150, 'weight': 56.228},
                {'key': 'normal_range', 'height': 200, 'weight': 99.960},
                {'key': 'pre_obese', 'height': 150, 'weight': 67.478},
                {'key': 'pre_obese', 'height': 200, 'weight': 119.960},
                {'key': 'obese_class_1', 'height': 150, 'weight': 78.728},
                {'key': 'obese_class_1', 'height': 200, 'weight': 139.960},
                {'key': 'obese_class_2', 'height': 150, 'weight': 89.978},
                {'key': 'obese_class_2', 'height': 200, 'weight': 159.960},
                {'key': 'obese_class_3', 'height': 150, 'weight': 90},
                {'key': 'obese_class_3', 'height': 200, 'weight': 190},
            ]
        )
    else:
        data = json.dumps(
            [
                {'key': 'filler', 'height': 150, 'weight': 66.139},
                {'key': 'filler', 'height': 200, 'weight': 66.139},
                {'key': 'severe_thinness', 'height': 150, 'weight': 79.317},
                {'key': 'severe_thinness', 'height': 200, 'weight': 141.008},
                {'key': 'moderate_thinness', 'height': 150, 'weight': 84.277},
                {'key': 'moderate_thinness', 'height': 200, 'weight': 149.826},
                {'key': 'mild_thinness', 'height': 150, 'weight': 91.718},
                {'key': 'mild_thinness', 'height': 200, 'weight': 163.054},
                {'key': 'normal_range', 'height': 150, 'weight': 123.960},
                {'key': 'normal_range', 'height': 200, 'weight': 220.374},
                {'key': 'pre_obese', 'height': 150, 'weight': 148.762},
                {'key': 'pre_obese', 'height': 200, 'weight': 264.467},
                {'key': 'obese_class_1', 'height': 150, 'weight': 173.564},
                {'key': 'obese_class_1', 'height': 200, 'weight': 308.559},
                {'key': 'obese_class_2', 'height': 150, 'weight': 198.366},
                {'key': 'obese_class_2', 'height': 200, 'weight': 352.651},
                {'key': 'obese_class_3', 'height': 150, 'weight': 198.416},
                {'key': 'obese_class_3', 'height': 200, 'weight': 352.740},
            ]
        )

    # Return the results to the client
    return HttpResponse(data, 'application/json')
