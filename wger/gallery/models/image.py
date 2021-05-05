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

# Django
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


def gallery_image_upload_dir(instance, filename):
    """
    Returns the upload target for exercise images
    """
    return "gallery/{0}/{1}".format(instance.user.id, uuid.uuid4())


class Image(models.Model):

    class Meta:
        ordering = ["-date", ]

    date = models.DateField(_('Date'),
                            default=datetime.datetime.now)

    user = models.ForeignKey(User,
                             verbose_name=_('User'),
                             on_delete=models.CASCADE)

    image = models.ImageField(verbose_name=_('Image'),
                              help_text=_('Only PNG and JPEG formats are supported'),
                              upload_to=gallery_image_upload_dir)

    description = models.TextField(verbose_name=_('Description'),
                                   max_length=1000,
                                   blank=True)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self
