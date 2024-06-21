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
from django.forms.models import modelformset_factory
from django.http import (
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import (
    reverse,
    reverse_lazy,
)
from django.utils.translation import (
    gettext as _,
    gettext_lazy,
)
from django.views.generic import (
    DeleteView,
    DetailView,
    UpdateView,
)

# wger
from wger.core.models import (
    RepetitionUnit,
    WeightUnit,
)
from wger.manager.forms import (
    HelperWorkoutSessionForm,
    WorkoutLogForm,
    WorkoutLogFormHelper,
)
from wger.manager.helpers import WorkoutCalendar
from wger.manager.models import (
    Day,
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


class WorkoutLogDetailView(DetailView, LoginRequiredMixin):
    """
    An overview of the workout's log
    """

    model = Workout
    template_name = 'workout/log.html'
    context_object_name = 'workout'
    owner_user = None

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(WorkoutLogDetailView, self).get_context_data(**kwargs)
        is_owner = self.owner_user == self.request.user

        # Prepare the entries for rendering and the D3 chart
        workout_log = {}

        for day_obj in self.object.day_set.all():
            day_id = day_obj.id
            workout_log[day_id] = {}
            for set_obj in day_obj.set_set.all():
                exercise_log = {}
                for base_obj in set_obj.exercise_bases:
                    exercise_base_id = base_obj.id
                    exercise_log[exercise_base_id] = []

                    # Filter the logs for user and exclude all units that are not weight
                    logs = base_obj.workoutlog_set.filter(
                        user=self.owner_user,
                        weight_unit__in=(1, 2),
                        repetition_unit=1,
                        workout=self.object,
                    )
                    entry_log, chart_data = process_log_entries(logs)
                    if entry_log:
                        exercise_log[base_obj.id].append(entry_log)

                    if exercise_log:
                        workout_log[day_id][exercise_base_id] = {}
                        workout_log[day_id][exercise_base_id]['log_by_date'] = entry_log
                        workout_log[day_id][exercise_base_id]['div_uuid'] = 'div-' + str(
                            uuid.uuid4()
                        )
                        workout_log[day_id][exercise_base_id]['chart_data'] = chart_data

        context['workout_log'] = workout_log
        context['owner_user'] = self.owner_user
        context['is_owner'] = is_owner

        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Check for ownership
        """

        workout = get_object_or_404(Workout, pk=kwargs['pk'])
        self.owner_user = workout.user
        is_owner = request.user == self.owner_user

        if not is_owner and not self.owner_user.userprofile.ro_access:
            return HttpResponseForbidden()

        # Dispatch normally
        return super(WorkoutLogDetailView, self).dispatch(request, *args, **kwargs)


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
