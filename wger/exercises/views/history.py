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
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import (
    reverse,
)

# Third Party
from actstream.models import Action
from actstream import action as actstream_action

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
    object_content_type = ContentType.objects.get_for_model(Exercise)

    stream = Action.objects.filter(
        action_object_content_type_id=object_content_type.id,
    )

    out = []
    for entry in stream:
        if entry.verb == StreamVerbs.CREATED.value:
            out.append({
                'history': None,
                'stream': entry
            })
            continue
        elif entry.verb == StreamVerbs.UPDATED.value:
            entry_data = entry.data
            if entry_data is None:
                continue

            entry_dict = entry_data.get('data', {})
            history_id = entry_dict.get('history_id', 0)
            if history_id == 0:
                continue

            hist = Exercise.history.get(history_id=history_id)
            if hist.prev_record:
                out.append({
                    'history': {'record': hist, 'delta': hist.diff_against(hist.prev_record)},
                    'stream': entry
                })

    return render(request, 'history/list3.html', {
        'context': out,

        # We can't pass the enum to the template, so we have to do this
        # https://stackoverflow.com/questions/35953132/
        'modes': StreamVerbs.__members__
    })


@permission_required('exercises.change_exercise')
def history_revert(request, pk):
    """
    Used to revert history objects
    """
    hist = Exercise.history.get(history_id=pk)
    if hist is None:
        return HttpResponseRedirect(reverse('exercise:history:admin-control'))

    revert_obj = hist.prev_record
    if revert_obj is None:
        return HttpResponseRedirect(reverse('exercise:history:admin-control'))

    diff = hist.diff_against(hist.prev_record)

    current_obj = Exercise.objects.get(id=revert_obj.instance.id)
    if current_obj is None:
        return HttpResponseRedirect(reverse('exercise:history:admin-control'))

    for change in diff.changes:
        try:
            setattr(current_obj, change.field, change.old)
        except:
            logger.warn(f"Failed setting field: {change.field} to {change.old} for Exercise {current_obj.id}")

    current_obj.save()

    most_recent_history = current_obj.history.order_by('history_date').last()

    actstream_action.send(
        request.user,
        verb=StreamVerbs.UPDATED.value,
        action_object=revert_obj.instance,
        data={
            'history_id': most_recent_history.history_id,
        }
    )

    return HttpResponseRedirect(reverse('exercise:history:admin-control'))
