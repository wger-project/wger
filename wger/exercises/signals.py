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
from django.db.models.signals import (
    post_delete,
    pre_delete,
    pre_save,
)
from django.dispatch import receiver

# Third Party
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.signal_handlers import generate_aliases
from easy_thumbnails.signals import saved_file

# wger
from wger.exercises.models import (
    DeletionLog,
    ExerciseImage,
    ExerciseVideo,
    Translation,
)


@receiver(post_delete, sender=ExerciseImage)
def delete_exercise_image_on_delete(sender, instance: ExerciseImage, **kwargs):
    """
    Delete the image along with its thumbnails
    """
    thumbnailer = get_thumbnailer(instance.image)
    thumbnailer.delete_thumbnails()
    instance.image.delete(save=False)


@receiver(pre_save, sender=ExerciseImage)
def delete_exercise_image_on_update(sender, instance: ExerciseImage, **kwargs):
    """
    Delete the corresponding image from the filesystem when the ExerciseImage
    object was edited
    """
    if not instance.pk:
        return False

    try:
        old_file = ExerciseImage.objects.get(pk=instance.pk).image
    except ExerciseImage.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        # Deletes the image as well as the thumbnails
        thumbnailer = get_thumbnailer(instance.image)
        thumbnailer.delete_thumbnails()
        instance.image.delete(save=False)
    return None


# Generate thumbnails when uploading a new image
saved_file.connect(generate_aliases)


@receiver(post_delete, sender=ExerciseVideo)
def auto_delete_video_on_delete(sender, instance: ExerciseVideo, **kwargs):
    """
    Deletes file when corresponding ExerciseVideo object is deleted
    """
    if instance.video:
        instance.video.delete(save=False)


@receiver(pre_save, sender=ExerciseVideo)
def delete_exercise_video_on_update(sender, instance: ExerciseVideo, **kwargs):
    """
    Deletes file when corresponding ExerciseVideo object was edited
    """
    if not instance.pk:
        return False

    try:
        old_file = ExerciseVideo.objects.get(pk=instance.pk).video
    except ExerciseVideo.DoesNotExist:
        return False

    new_file = instance.video
    if not old_file == new_file and old_file:
        old_file.delete(save=False)
    return None


@receiver(pre_delete, sender=Translation)
def add_deletion_log_translation(sender, instance: Translation, **kwargs):
    DeletionLog(
        model_type=DeletionLog.MODEL_TRANSLATION,
        uuid=instance.uuid,
        comment=instance.name,
    ).save()


@receiver(pre_delete, sender=ExerciseImage)
def add_deletion_log_image(sender, instance: ExerciseImage, **kwargs):
    DeletionLog(
        model_type=DeletionLog.MODEL_IMAGE,
        uuid=instance.uuid,
    ).save()


@receiver(pre_delete, sender=ExerciseVideo)
def add_deletion_log_video(sender, instance: ExerciseVideo, **kwargs):
    DeletionLog(
        model_type=DeletionLog.MODEL_VIDEO,
        uuid=instance.uuid,
    ).save()
