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


from django.db.models.signals import pre_save
from django.db.models.signals import post_delete
from django.dispatch import receiver

from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.signal_handlers import generate_aliases
from easy_thumbnails.signals import saved_file

from wger.groups.models import Group


@receiver(post_delete, sender=Group)
def delete_group_image_on_delete(sender, instance, **kwargs):
    '''
    Delete the image, along with its thumbnails, from the disk
    '''

    thumbnailer = get_thumbnailer(instance.image)
    thumbnailer.delete_thumbnails()
    instance.image.delete(save=False)


@receiver(pre_save, sender=Group)
def delete_group_image_on_update(sender, instance, **kwargs):
    '''
    Delete the corresponding image from the filesystem when the Group object is changed
    '''
    if not instance.pk:
        return False

    try:
        old_file = Group.objects.get(pk=instance.pk).image
    except Group.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        thumbnailer = get_thumbnailer(old_file)
        thumbnailer.delete_thumbnails()
        old_file.delete(save=False)
