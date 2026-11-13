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
from django.db import transaction
from django.http import (
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404

# wger
from wger.manager.models import Routine


logger = logging.getLogger(__name__)


@login_required
@transaction.atomic
def copy_routine(request, pk):
    """
    Makes a copy of a routine
    """
    routine = get_object_or_404(Routine, pk=pk)

    if request.user != routine.user and not routine.is_public:
        # Check if the user is a trainer and the routine belongs to a client, only if it does not
        # belong to the user.
        trainer_identity_pk = request.session.get('trainer.identity', None)
        if not trainer_identity_pk or routine.user.pk != trainer_identity_pk:
            return HttpResponseForbidden()

    routine_copy = routine.copy_for_user(request.user)

    return HttpResponseRedirect(routine_copy.get_absolute_url())
