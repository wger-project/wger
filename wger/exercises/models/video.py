#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) 2013 - 2021 wger Team
#
#  wger Workout Manager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  wger Workout Manager is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
import pathlib
import uuid

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.exercises.models import ExerciseBase
from wger.utils.models import AbstractLicenseModel


def exercise_video_upload_dir(instance, filename):
    """
    Returns the upload target for exercise videos
    """
    ext = pathlib.Path(filename).suffix
    return "exercise-video/{0}/{1}{2}".format(instance.exercise_base.id, instance.uuid, ext)


class ExerciseVideo(AbstractLicenseModel, models.Model):
    """
    Model for an exercise image
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        verbose_name='UUID',
    )
    """Globally unique ID, to identify the image across installations"""

    exercise_base = models.ForeignKey(
        ExerciseBase,
        verbose_name=_('Exercise'),
        on_delete=models.CASCADE,
    )
    """The exercise the image belongs to"""

    video = models.FileField(
        verbose_name=_('Video'),
        upload_to=exercise_video_upload_dir,
    )
    """Uploaded video"""

    is_main = models.BooleanField(
        verbose_name=_('Main video'),
        default=False,
    )
    """A flag indicating whether the image is the exercise's main image"""

    class Meta:
        """
        Set default ordering
        """
        ordering = ['-is_main', 'id']

    def get_owner_object(self):
        """
        Image has no owner information
        """
        return False
