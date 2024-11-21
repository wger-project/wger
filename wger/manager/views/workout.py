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
import copy
import logging
from typing import List

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
    AbstractChangeConfig,
    Routine,
    SlotEntry,
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


@login_required
def copy_routine(request, pk):
    """
    Makes a copy of a routine
    """
    routine = get_object_or_404(Routine, pk=pk)

    if request.user != routine.user:
        return HttpResponseForbidden()

    def copy_config(configs: List[AbstractChangeConfig], slot_entry: SlotEntry):
        for config in configs:
            config_copy = copy.copy(config)
            config_copy.pk = None
            config_copy.slot_entry = slot_entry
            config_copy.save()

    # Process request
    # Copy workout
    routine_copy: Routine = copy.copy(routine)
    routine_copy.pk = None
    routine_copy.user = request.user
    routine_copy.is_template = False
    routine_copy.is_public = False
    routine_copy.save()

    # Copy the days
    for day in routine.days.all():
        day_copy = copy.copy(day)
        day_copy.pk = None
        day_copy.routine = routine_copy
        day_copy.save()

        # Copy the slots
        for current_slot in day.slots.all():
            slot_copy = copy.copy(current_slot)
            slot_copy.pk = None
            slot_copy.day = day_copy
            slot_copy.save()

            # Copy the slot entries
            for current_entry in current_slot.entries.all():
                slot_entry_copy = copy.copy(current_entry)
                slot_entry_copy.pk = None
                slot_entry_copy.slot = slot_copy
                slot_entry_copy.save()

                copy_config(current_entry.weightconfig_set.all(), slot_entry_copy)
                copy_config(current_entry.maxweightconfig_set.all(), slot_entry_copy)
                copy_config(current_entry.repsconfig_set.all(), slot_entry_copy)
                copy_config(current_entry.maxrepsconfig_set.all(), slot_entry_copy)
                copy_config(current_entry.rirconfig_set.all(), slot_entry_copy)
                copy_config(current_entry.restconfig_set.all(), slot_entry_copy)
                copy_config(current_entry.maxrestconfig_set.all(), slot_entry_copy)
                copy_config(current_entry.setsconfig_set.all(), slot_entry_copy)

    return HttpResponseRedirect(routine_copy.get_absolute_url())


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
