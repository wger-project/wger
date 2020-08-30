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

# Django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import (
    HttpResponseForbidden,
    HttpResponseRedirect
)
from django.shortcuts import get_object_or_404

# wger
from wger.groups.models import (
    Application,
    Group,
    Membership
)


@login_required
def apply(request, group_pk):
    """
    Lets a user apply for membership in a private group
    """
    group = get_object_or_404(Group, pk=group_pk)

    if group.public or \
            group.membership_set.filter(user=request.user).exists() or \
            group.application_set.filter(user=request.user).exists():
        return HttpResponseRedirect(group.get_absolute_url())

    application = Application()
    application.group = group
    application.user = request.user
    application.save()

    return HttpResponseRedirect(group.get_absolute_url())


@login_required
def accept(request, group_pk, user_pk):
    """
    Accepts a user's application to join a private group
    """
    group = get_object_or_404(Group, pk=group_pk)
    user = get_object_or_404(User, pk=user_pk)

    # Sanity checks
    if not group.membership_set.filter(user=request.user, admin=True).exists()\
            or not group.application_set.filter(user=user).exists():
        return HttpResponseForbidden()

    # Add user to group...
    membership = Membership()
    membership.group = group
    membership.user = user
    membership.admin = False
    membership.save()

    # ...and delete the application
    group.application_set.filter(user=user).delete()

    return HttpResponseRedirect(group.get_absolute_url())


@login_required
def deny(request, group_pk, user_pk):
    """
    Denies a user's application to join a private group
    """
    group = get_object_or_404(Group, pk=group_pk)
    user = get_object_or_404(User, pk=user_pk)

    # Sanity checks
    if not group.membership_set.filter(user=request.user, admin=True).exists()\
            or not group.application_set.filter(user=user).exists():
        return HttpResponseForbidden()

    # Delete the application
    group.application_set.filter(user=user).delete()

    return HttpResponseRedirect(group.get_absolute_url())
