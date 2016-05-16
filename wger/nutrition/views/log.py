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

import datetime
import logging

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from wger.nutrition.models import LogItem, NutritionPlan

logger = logging.getLogger(__name__)


@login_required
def overview(request, pk, date=None):
    '''
    Shows an overview of the log for the given date
    '''
    context = {}
    if not date:
        date = datetime.date.today()

    plan = get_object_or_404(NutritionPlan, pk=pk)
    context['plan'] = plan
    context['date'] = date
    context['log_values'] = plan.get_logged_values(date)
    context['nutritional_data'] = plan.get_nutritional_values()

    return render(request, 'log/overview.html', context)
