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
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.utils.translation import gettext as _
from django.views.generic import UpdateView

# wger
from wger.manager.forms import WorkoutMakeTemplateForm
from wger.manager.models import (
    Routine,
    Workout,
)
from wger.utils.generic_views import WgerFormMixin


logger = logging.getLogger(__name__)


# ************************
# Workout functions
# ************************


@login_required
def template_overview(request):
    """ """
    return render(
        request,
        'workout/overview.html',
        {
            'workouts': Workout.templates.filter(user=request.user),
            'title': _('Your templates'),
            'template_overview': True,
        },
    )


@login_required
def public_template_overview(request):
    """ """
    return render(
        request,
        'workout/overview.html',
        {
            'workouts': Workout.templates.filter(is_public=True),
            'title': _('Public templates'),
            'template_overview': True,
        },
    )


@login_required()
def template_view(request, pk):
    """
    Show the template with the given ID
    """
    template = get_object_or_404(Workout.templates, pk=pk)

    if not template.is_public and request.user != template.user:
        return HttpResponseForbidden()

    context = {
        'workout': template,
        'muscles': template.canonical_representation['muscles'],
        'is_owner': template.user == request.user,
        'owner_user': template.user,
    }
    return render(request, 'workout/template_view.html', context)


def make_workout(request, pk):
    workout = get_object_or_404(Workout.both, pk=pk)

    if request.user != workout.user:
        return HttpResponseForbidden()

    workout.is_template = False
    workout.is_public = False
    workout.save()

    return HttpResponseRedirect(workout.get_absolute_url())


class WorkoutMarkAsTemplateView(WgerFormMixin, LoginRequiredMixin, UpdateView):
    """
    Generic view to update an existing workout routine
    """

    model = Routine
    form_class = WorkoutMakeTemplateForm

    def get_context_data(self, **kwargs):
        context = super(WorkoutMarkAsTemplateView, self).get_context_data(**kwargs)
        context['title'] = _('Mark as template')
        return context
