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
# You should have received a copy of the GNU Affero General Public License

# Standard Library
import logging

# Django
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
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
    TemplateView,
)

# wger
from wger.exercises.models import Exercise
from wger.utils.generic_views import WgerDeleteMixin


logger = logging.getLogger(__name__)


def view(request, id, slug=None):
    """
    Detail view for an exercise translation
    """
    exercise = get_object_or_404(Exercise, pk=id)

    return HttpResponsePermanentRedirect(
        reverse(
            'exercise:exercise:view-base', kwargs={'pk': exercise.exercise_base_id, 'slug': slug}
        )
    )


class ExerciseDeleteView(
    WgerDeleteMixin,
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DeleteView,
):
    """
    Generic view to delete an existing exercise
    """

    model = Exercise
    success_url = reverse_lazy('exercise:exercise:overview')
    delete_message_extra = gettext_lazy('This will delete the exercise from all workouts.')
    messages = gettext_lazy('Successfully deleted')
    permission_required = 'exercises.delete_exercise'

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super(ExerciseDeleteView, self).get_context_data(**kwargs)
        context['title'] = _('Delete {0}?').format(self.object.name)
        return context
