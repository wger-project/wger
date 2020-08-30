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

from actstream import action

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import (
    HttpResponseForbidden,
    HttpResponseRedirect
)

from wger.groups.models import (
    Group,
    Membership
)


@login_required
def join_public_group(request, group_pk):
    """
    Lets a user join a public group
    """
    group = get_object_or_404(Group, pk=group_pk)
    if not group.public:
        return HttpResponseForbidden()

    membership = Membership()
    membership.group = group
    membership.user = request.user
    membership.admin = False
    membership.save()

    return HttpResponseRedirect(group.get_absolute_url())


@login_required
def leave_group(request, group_pk, user_pk=None):
    """
    Removes a user from a group, either because he left or because an admin removed him
    """
    # TODO: what if it's the last user
    group = get_object_or_404(Group, pk=group_pk)

    if user_pk:
        user = get_object_or_404(User, pk=user_pk)
        if not group.membership_set.filter(user=request.user, admin=True).exists():
            return HttpResponseForbidden()
    else:
        user = request.user
    if not group.membership_set.filter(user=user).exists():
        return HttpResponseForbidden()

    membership = group.membership_set.get(user=user)
    membership.delete()

    # Only return to the group overview if the user itself left the group
    if user.pk == request.user.pk:
        return HttpResponseRedirect(reverse('groups:group:list'))
    else:
        return HttpResponseRedirect(group.get_absolute_url())


@login_required
def promote(request, group_pk, user_pk):
    """
    Promotes a user administrator of a group
    """

    group = get_object_or_404(Group, pk=group_pk)
    user = get_object_or_404(User, pk=user_pk)

    # Sanity checks
    if not group.membership_set.filter(user=request.user, admin=True).exists()\
            or not group.membership_set.filter(user=user).exists():
        return HttpResponseForbidden()

    membership = group.membership_set.get(user=user)
    membership.admin = True
    membership.save()

    # Add event to django activity stream
    action.send(request.user, verb='promoted', action_object=user, target=group)

    return HttpResponseRedirect(group.get_absolute_url())


@login_required
def demote(request, group_pk, user_pk):
    """
    Demotes an administrator user
    """

    # TODO: can one demote oneself?
    group = get_object_or_404(Group, pk=group_pk)
    user = get_object_or_404(User, pk=user_pk)

    # Sanity checks
    if not group.membership_set.filter(user=request.user, admin=True).exists()\
            or not group.membership_set.filter(user=user).exists():
        return HttpResponseForbidden()

    membership = group.membership_set.get(user=user)
    membership.admin = False
    membership.save()

    # Add event to django activity stream
    action.send(request.user, verb='demoted', action_object=user, target=group)

    return HttpResponseRedirect(group.get_absolute_url())
