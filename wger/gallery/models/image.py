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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.
# Standard Library

# Standard Library
import datetime
import pathlib
import uuid

# Django
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


def gallery_upload_dir(instance, filename):
    """
    Returns the upload target for exercise images
    """
    return f'gallery/{instance.user.id}/{uuid.uuid4()}{pathlib.Path(filename).suffix}'


class Image(models.Model):
    class Meta:
        ordering = [
            '-date',
        ]

    date = models.DateField(_('Date'), default=datetime.datetime.now)

    user = models.ForeignKey(
        User,
        verbose_name=_('User'),
        on_delete=models.CASCADE,
    )

    image = models.ImageField(
        verbose_name=_('Image'),
        help_text=_('Only PNG and JPEG formats are supported'),
        upload_to=gallery_upload_dir,
        height_field='height',
        width_field='width',
    )

    height = models.IntegerField(editable=False)
    """Height of the image"""

    width = models.IntegerField(editable=False)
    """Width of the image"""

    description = models.TextField(
        verbose_name=_('Description'),
        max_length=1000,
        blank=True,
    )

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'Gallery image #{self.pk}'

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

    @property
    def is_landscape(self):
        return self.width > self.height


@receiver(models.signals.post_delete, sender=Image)
def auto_delete_file_on_delete(sender, instance: Image, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.image:
        path = pathlib.Path(instance.image.path)
        if path.exists():
            path.unlink()


@receiver(models.signals.pre_save, sender=Image)
def auto_delete_file_on_change(sender, instance: Image, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).image
    except sender.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        path = pathlib.Path(old_file.path)
        if path.is_file():
            path.unlink()
