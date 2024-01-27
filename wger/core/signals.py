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
import datetime

# Django
from django.contrib.auth.models import User
from django.db.models.signals import (
    post_save,
    pre_save,
)
from django.dispatch import receiver

# wger
from wger.core.models import (
    UserCache,
    UserProfile,
)
from wger.utils.helpers import disable_for_loaddata


@disable_for_loaddata
def create_user_profile(sender, instance, created, **kwargs):
    """
    Every new user gets a profile
    """
    if created:
        UserProfile.objects.create(user=instance)


@disable_for_loaddata
def create_user_cache(sender, instance, created, **kwargs):
    """
    Every new user gets a cache table
    """
    if created:
        UserCache.objects.create(user=instance)


@receiver(pre_save, sender=UserProfile)
def set_user_age(sender, instance, **kwargs):
    """
    Inputting or changing a user's birthdate will auto-update the
    user's age as well if user's age has not been set
    """
    if instance.age is None and instance.birthdate is not None:
        today = datetime.date.today()
        birthday = instance.birthdate
        instance.age = (
            today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
        )


post_save.connect(create_user_profile, sender=User)
post_save.connect(create_user_cache, sender=User)
