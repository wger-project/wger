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
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

# wger
from exercises.views.helper import HistoryModes
from wger.exercises.models import Exercise

from actstream.models import Action

logger = logging.getLogger(__name__)


@permission_required('exercises.change_exercise')
def overview(request):
    """
    Generic view to list the history of the exercises
    """

    print(HistoryModes.ADDED.value)
    context = {
        'stream': Action.objects.all(),

        # We can't pass the enmu to the template, so we have to do this
        # https://stackoverflow.com/questions/35953132/
        'modes': HistoryModes.__members__
    }
    return render(request, 'history/list.html', context)


@permission_required('exercises.change_exercise')
def overview2(request):
    """
    Generic view to list the history of the exercises
    """
    context = {}

    out = []
    history = Exercise.history.all()
    for entry in history:
        if entry.prev_record:
            out.append({'record': entry, 'delta': entry.diff_against(entry.prev_record)})

    context['history'] = out

    return render(request, 'history/list.html', context)
