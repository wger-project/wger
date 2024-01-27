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
from django.http import HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import reverse

# Third Party
from actstream import action as actstream_action
from actstream.models import Action

# wger
from wger.exercises.views.helper import StreamVerbs


logger = logging.getLogger(__name__)


@permission_required('exercises.change_exercise')
def control(request):
    """
    Admin view of the history of the exercises
    """
    all_streams = Action.objects.all()
    out = []
    for entry in all_streams:
        data = {'verb': entry.verb, 'stream': entry}

        if entry.verb == StreamVerbs.UPDATED.value:
            entry_obj = entry.action_object.history.as_of(entry.timestamp)
            historical_entry = entry_obj._history
            previous_entry = historical_entry.prev_record

            data['id'] = historical_entry.id
            data['content_type_id'] = ContentType.objects.get_for_model(entry_obj).id

            if previous_entry:
                data['delta'] = historical_entry.diff_against(previous_entry)
                data['history_id'] = previous_entry.history_id

        out.append(data)

    return render(
        request,
        'history/overview.html',
        {
            'context': out,
            # We can't pass the enum to the template, so we have to do this
            # https://stackoverflow.com/questions/35953132/
            'verbs': StreamVerbs.__members__,
        },
    )


@permission_required('exercises.change_exercise')
def history_revert(request, history_pk, content_type_id):
    """
    Used to revert history objects
    """
    object_type = get_object_or_404(ContentType, pk=content_type_id)
    object_class = object_type.model_class()
    history = object_class.history.get(history_id=history_pk)
    history.instance.save()

    actstream_action.send(
        request.user,
        verb=StreamVerbs.UPDATED.value,
        action_object=history.instance,
        info='reverted history by admin',
    )

    return HttpResponseRedirect(reverse('exercise:history:overview'))
