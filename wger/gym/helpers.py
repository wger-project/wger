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

    # Check workout logs
    log_list = WorkoutLog.objects.filter(user=user).order_by('date')
    last_activity = None
    if log_list.exists():
        last_activity = log_list.last().date

    # Check workout sessions
    log_session = WorkoutSession.objects.filter(user=user).order_by('date')
    if log_session.exists():
        last_session = log_session.last().date
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
