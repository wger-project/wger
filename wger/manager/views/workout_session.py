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

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
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
    CreateView,
    DeleteView,
    UpdateView,
)

# wger
from wger.manager.forms import WorkoutSessionForm
from wger.manager.models import (
    Workout,
    WorkoutLog,
    WorkoutSession,
)
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin,
)


logger = logging.getLogger(__name__)
"""
Workout session
"""


class WorkoutSessionUpdateView(WgerFormMixin, LoginRequiredMixin, UpdateView):
    """
    Generic view to edit an existing workout session entry
    """

    model = WorkoutSession
    form_class = WorkoutSessionForm

    def get_context_data(self, **kwargs):
        context = super(WorkoutSessionUpdateView, self).get_context_data(**kwargs)
        context['title'] = _('Edit workout impression for {0}').format(self.object.date)

        return context

    def get_success_url(self):
        return reverse('manager:workout:calendar')


class WorkoutSessionAddView(WgerFormMixin, LoginRequiredMixin, CreateView):
    """
    Generic view to add a new workout session entry
    """

    model = WorkoutSession
    form_class = WorkoutSessionForm

    def get_date(self):
        """
        Returns a date object from the URL parameters or None if no date
        could be created
        """
        try:
            date = datetime.date(
                int(self.kwargs['year']),
                int(self.kwargs['month']),
                int(self.kwargs['day']),
            )
        except ValueError:
            date = None

        return date

    def dispatch(self, request, *args, **kwargs):
        """
        Check for ownership
        """
        workout = Workout.objects.get(pk=kwargs['workout_pk'])
        if workout.get_owner_object().user != request.user:
            return HttpResponseForbidden()

        if not self.get_date():
            return HttpResponseBadRequest('You need to use a valid date')

        return super(WorkoutSessionAddView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WorkoutSessionAddView, self).get_context_data(**kwargs)
        context['title'] = _('New workout impression for the {0}'.format(self.get_date()))
        return context

    def get_success_url(self):
        return reverse('manager:workout:calendar')

    def form_valid(self, form):
        """
        Set the workout and the user
        """

        workout = Workout.objects.get(pk=self.kwargs['workout_pk'])
        form.instance.workout = workout
        form.instance.user = self.request.user
        form.instance.date = self.get_date()
        return super(WorkoutSessionAddView, self).form_valid(form)


class WorkoutSessionDeleteView(WgerDeleteMixin, LoginRequiredMixin, DeleteView):
    """
    Generic view to delete a workout routine
    """

    model = WorkoutSession
    success_url = reverse_lazy('manager:workout:overview')
    messages = gettext_lazy('Successfully deleted')

    def form_valid(self, form):
        """
        Delete the workout session and, if wished, all associated weight logs as well
        """
        if self.kwargs.get('logs') == 'logs':
            WorkoutLog.objects.filter(user=self.request.user, date=self.get_object().date).delete()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        logs = '' if not self.kwargs.get('logs') else self.kwargs['logs']
        context = super(WorkoutSessionDeleteView, self).get_context_data(**kwargs)
        context['title'] = _('Delete {0}?').format(self.object)
        if logs == 'logs':
            self.delete_message_extra = _('This will delete all weight logs for this day as well.')
        return context
