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

# Standard Library
import datetime
import logging
import uuid

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import reverse
from django.utils.translation import gettext_lazy
from django.views.generic import (
    DeleteView,
    DetailView,
    UpdateView,
)

# wger
from wger.manager.forms import WorkoutLogForm
from wger.manager.helpers import WorkoutCalendar
from wger.manager.models import (
    Schedule,
    Workout,
    WorkoutLog,
    WorkoutSession,
)
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin,
)
from wger.utils.helpers import check_access
from wger.weight.helpers import (
    group_log_entries,
    process_log_entries,
)


logger = logging.getLogger(__name__)


# ************************
# Log functions
# ************************
class WorkoutLogUpdateView(WgerFormMixin, UpdateView, LoginRequiredMixin):
    """
    Generic view to edit an existing workout log weight entry
    """

    model = WorkoutLog
    form_class = WorkoutLogForm

    def get_success_url(self):
        return reverse('manager:workout:view', kwargs={'pk': self.object.workout_id})


class WorkoutLogDeleteView(WgerDeleteMixin, DeleteView, LoginRequiredMixin):
    """
    Delete a workout log
    """

    model = WorkoutLog
    title = gettext_lazy('Delete workout log')

    def get_success_url(self):
        return reverse('manager:workout:view', kwargs={'pk': self.object.workout_id})


def add(request, pk):
    """
    Add a new workout log
    """

    context = {}

    return render(request, 'log/add.html', context)


def calendar(request, username=None, year=None, month=None):
    """
    Show a calendar with all the workout logs
    """
    context = {}
    is_owner, user = check_access(request.user, username)
    year = int(year) if year else datetime.date.today().year
    month = int(month) if month else datetime.date.today().month

    (current_workout, schedule) = Schedule.objects.get_current_workout(user)
    grouped_log_entries = group_log_entries(user, year, month)

    context['calendar'] = WorkoutCalendar(grouped_log_entries).formatmonth(year, month)
    context['logs'] = grouped_log_entries
    context['current_year'] = year
    context['current_month'] = month
    context['current_workout'] = current_workout
    context['owner_user'] = user
    context['is_owner'] = is_owner
    context['impressions'] = WorkoutSession.IMPRESSION
    context['month_list'] = WorkoutLog.objects.filter(user=user).dates('date', 'month')
    return render(request, 'calendar/month.html', context)


def day(request, username, year, month, day):
    """
    Show the logs for a single day
    """
    context = {}
    is_owner, user = check_access(request.user, username)

    try:
        date = datetime.date(int(year), int(month), int(day))
    except ValueError as e:
        logger.error(f'Error on date: {e}')
        return HttpResponseForbidden()
    context['logs'] = group_log_entries(user, date.year, date.month, date.day)
    context['date'] = date
    context['owner_user'] = user
    context['is_owner'] = is_owner

    return render(request, 'calendar/day.html', context)
