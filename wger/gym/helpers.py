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

from wger.manager.models import WorkoutLog, WorkoutSession


def get_user_last_activity(user):
    '''
    Find out when the user was last active. "Active" means in this context logging
    a weight, or saving a workout session.

    :param user: user object
    :return: a date or None if nothing was found
    '''

    last_activity = None

    # Check workout logs
    last_log = WorkoutLog.objects.filter(user=user).order_by('date').last()
    if last_log:
        last_activity = last_log.date

    # Check workout sessions
    last_session = WorkoutSession.objects.filter(user=user).order_by('date').last()
    if last_session:
        last_session = last_session.date

    # Return the last one
    if last_session:
        if not last_activity:
            last_activity = last_session

        if last_activity < last_session:
            last_activity = last_session

    return last_activity


def is_any_gym_admin(user):
    '''
    Small utility that checks that the user object has any administrator
    permissions
    '''
    return user.has_perm('gym.manage_gym')\
        or user.has_perm('gym.manage_gyms')\
        or user.has_perm('gym.gym_trainer')


def get_permission_list(user):
    '''
    Calculate available user permissions

    This is needed because a user shouldn't be able to create or give another
    account with more permissions than himself.

    :param user: the user creating the account
    :return: a list of permissions
    '''

    form_group_permission = ['user', 'trainer']

    if user.has_perm('gym.manage_gym'):
        form_group_permission.append('admin')

    if user.has_perm('gym.manage_gyms'):
        form_group_permission.append('admin')
        form_group_permission.append('manager')

    return form_group_permission
