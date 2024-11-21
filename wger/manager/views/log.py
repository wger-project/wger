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
import logging

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy
from django.views.generic import (
    DeleteView,
    UpdateView,
)

# wger
from wger.manager.forms import WorkoutLogForm
from wger.manager.models import WorkoutLog
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin,
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
