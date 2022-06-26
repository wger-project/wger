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
from datetime import datetime, timedelta
import logging

# Django
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render

# Third Party
from actstream.models import Action

# wger
from wger.exercises.models import Exercise
from wger.exercises.views.helper import StreamVerbs


logger = logging.getLogger(__name__)


@permission_required('exercises.change_exercise')
def overview(request):
    """
    Generic view to list the history of the exercises
    """
    context = {
        'stream': Action.objects.all(),

        # We can't pass the enum to the template, so we have to do this
        # https://stackoverflow.com/questions/35953132/
        'modes': StreamVerbs.__members__
    }

    return render(request, 'history/list.html', context)


@permission_required('exercises.change_exercise')
def overview2(request):
    """
    Generic view to list the history of the exercises
    """
    out = []
    for entry in Exercise.history.all():
        if entry.prev_record:
            out.append({'record': entry, 'delta': entry.diff_against(entry.prev_record)})

    return render(request, 'history/list2.html', {'history': out})


@permission_required('exercises.change_exercise')
def control(request):
    """
    Admin view of the history of the exercises
    """
    object_content_type_ID = ContentType.objects.get_for_model(Exercise).id

    stream = Action.objects.filter(
        action_object_content_type_id=object_content_type_ID,
    )

    out = []
    for entry in stream:
        # Fetch history
        hist_id = entry.data['data']['history_id']
        hist = Exercise.history.filter(history_id=hist_id).first()

        if hist.prev_record:
            out.append({
                'history': {'record': hist, 'delta': hist.diff_against(hist.prev_record)},
                'stream': entry
            })
        else:
            out.append({
                'history': {'record': hist, 'delta': None},
                'stream': entry
            })

    print(out)

    return render(request, 'history/list3.html', {
        'history': out,
    })
