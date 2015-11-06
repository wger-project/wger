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


from django.db.models.signals import post_save, post_delete

from wger.gym.helpers import get_user_last_activity
from wger.manager.models import WorkoutLog, WorkoutSession
from wger.core.models import UserCache


def update_activity_cache(sender, instance, **kwargs):
    '''
    Update the user's cached last activity date
    '''

    user = instance.user
    user.usercache.last_activity = get_user_last_activity(user)
    user.usercache.save()


post_save.connect(update_activity_cache, sender=WorkoutSession)
post_save.connect(update_activity_cache, sender=WorkoutLog)

# TODO: this seems to cause problems when users are deleted
#       perhaps because of the cascading, needs to be checked
# post_delete.connect(update_activity_cache, sender=WorkoutSession)
# post_delete.connect(update_activity_cache, sender=WorkoutLog)
