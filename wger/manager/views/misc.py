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


from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _


from django.contrib.auth.decorators import login_required


from wger.manager.models import DaysOfWeek
from wger.manager.models import TrainingSchedule

from wger.nutrition.models import NutritionPlan

from wger.weight.models import WeightEntry


logger = logging.getLogger('workout_manager.custom')


# ************************
# Misc functions
# ************************
def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        return HttpResponseRedirect(reverse('software:features'))


@login_required
def dashboard(request):
    '''
    Show the index page, in our case, the last workout and nutritional plan
    and the current weight
    '''

    template_data = {}

    # Load the last workout, if one exists
    try:
        current_workout = TrainingSchedule.objects.filter(user=request.user).latest('creation_date')
    except ObjectDoesNotExist:
        current_workout = False
    template_data['current_workout'] = current_workout

    # Load the last nutritional plan, if one exists
    try:
        plan = NutritionPlan.objects.filter(user=request.user).latest('creation_date')
    except ObjectDoesNotExist:
        plan = False
    template_data['plan'] = plan

    # Load the last logged weight entry, if one exists
    try:
        weight = WeightEntry.objects.filter(user=request.user).latest('creation_date')
    except ObjectDoesNotExist:
        weight = False
    template_data['weight'] = weight

    if current_workout:
        # Format a bit the days so it doesn't have to be done in the template
        week_day_result = []
        for week in DaysOfWeek.objects.all():
            day_has_workout = False
            for day in current_workout.day_set.select_related():
                for day_of_week in day.day.select_related():
                    if day_of_week.id == week.id:
                        day_has_workout = True
                        week_day_result.append((_(week.day_of_week), day.description, True))
                        break

            if not day_has_workout:
                week_day_result.append((_(week.day_of_week), _('Rest day'), False))

        template_data['weekdays'] = week_day_result

    if plan:

        # Load the nutritional info
        template_data['nutritional_info'] = plan.get_nutritional_values()

    return render_to_response('index.html',
                              template_data,
                              context_instance=RequestContext(request))
