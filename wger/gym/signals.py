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
from django.dispatch import receiver

from wger.gym.models import (
    Gym,
    GymConfig,
    UserDocument
)


@receiver(post_save, sender=Gym)
def gym_config(sender, instance, created, **kwargs):
    '''
    Creates a configuration entry for newly added gyms
    '''
    if not created or kwargs['raw']:
        return

    config = GymConfig()
    config.gym = instance
    config.save()


@receiver(post_delete, sender=UserDocument)
def delete_user_document_on_delete(sender, instance, **kwargs):
    '''
    Deletes the document from the disk as well
    '''

    instance.document.delete(save=False)
