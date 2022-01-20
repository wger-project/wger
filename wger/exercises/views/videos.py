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
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
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
from wger.exercises.forms import (
    ExerciseImageForm,
    ExerciseVideoForm,
)
from wger.exercises.models import (
    Exercise,
    ExerciseVideo,
)
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin,
)


logger = logging.getLogger(__name__)
"""
Exercise videos
"""


class ExerciseVideoEditView(
    WgerFormMixin,
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView,
):
    """
    Generic view to update an existing exercise video
    """

    model = ExerciseVideo
    title = gettext_lazy('Edit')
    permission_required = 'exercises.change_exercisevideo'
    form_class = ExerciseVideoForm

    def get_success_url(self):
        return reverse('exercise:exercise:view', kwargs={'id': self.object.exercise_base.id})

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(ExerciseVideoEditView, self).get_context_data(**kwargs)
        context['enctype'] = 'multipart/form-data'
        return context


class ExerciseVideoAddView(
    WgerFormMixin,
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView,
):
    """
    Generic view to add a new exercise video
    """

    model = ExerciseVideo
    title = gettext_lazy('Add new video')
    permission_required = 'exercises.add_exercisevideo'
    form_class = ExerciseVideoForm

    def form_valid(self, form):
        """Set the exercise base and the author"""
        exercise = get_object_or_404(Exercise, pk=self.kwargs['exercise_pk'])
        form.instance.exercise_base = exercise.exercise_base
        return super(ExerciseVideoAddView, self).form_valid(form)

    def get_success_url(self):
        return reverse('exercise:exercise:view', kwargs={'id': self.kwargs['exercise_pk']})

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(ExerciseVideoAddView, self).get_context_data(**kwargs)
        context['enctype'] = 'multipart/form-data'
        return context


class ExerciseVideoDeleteView(
    WgerDeleteMixin,
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DeleteView,
):
    """
    Generic view to delete an existing exercise image
    """

    model = ExerciseVideo
    fields = ('video', 'is_main')
    messages = gettext_lazy('Successfully deleted')
    permission_required = 'exercises.delete_exercisevideo'

    def get_success_url(self):
        """
        Return to exercise image
        """
        return reverse('exercise:exercise:view', kwargs={'id': self.kwargs['exercise_pk']})

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(ExerciseVideoDeleteView, self).get_context_data(**kwargs)

        context['title'] = _('Delete?')
        return context
