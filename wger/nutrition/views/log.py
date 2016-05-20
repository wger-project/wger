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

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponseRedirect,
    HttpResponseForbidden
)
from django.shortcuts import (
    render,
    get_object_or_404
)

from wger.nutrition.models import NutritionPlan

logger = logging.getLogger(__name__)


def overview(request, pk):
    '''
    Shows an overview of diary entries for the given plan
    '''

    # Check read permission
    plan = get_object_or_404(NutritionPlan, pk=pk)
    user = plan.user
    is_owner = request.user == user

    if not is_owner and not user.userprofile.ro_access:
        return HttpResponseForbidden()

    context = {'plan': plan,
               'logs': plan.get_log_overview(),
               'nutritional_data': plan.get_nutritional_values()}

    return render(request, 'log/overview.html', context)


def detail(request, pk, year, month, day):
    '''
    Shows an overview of the log for the given date
    '''

    # Check read permission
    plan = get_object_or_404(NutritionPlan, pk=pk)
    user = plan.user
    is_owner = request.user == user

    if not is_owner and not user.userprofile.ro_access:
        return HttpResponseForbidden()

    try:
        date = datetime.date(year=int(year), month=int(month), day=int(day))
    except ValueError:
        date = datetime.date.today()
        return HttpResponseRedirect(reverse('nutrition:log:detail',
                                            kwargs={'pk': pk,
                                                    'year': date.year,
                                                    'month': date.month,
                                                    'day': date.day}))

    context = {'plan': plan,
               'date': date,
               'log_summary': plan.get_log_summary(date),
               'log_entries': plan.get_log_entries(date),
               'nutritional_data': plan.get_nutritional_values()}

    return render(request, 'log/detail.html', context)
