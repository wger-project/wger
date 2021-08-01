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
from wger.core.models import License
from wger.utils.helpers import BaseImage
from wger.utils.models import AbstractLicenseModel


def ingredient_image_upload_dir(instance, filename):
    """
    Returns the upload target for exercise images
    """
    ext = pathlib.Path(filename).suffix
    return "ingredients/{0}/{1}{2}".format(instance.ingredient.uuid, instance.uuid, ext)


class Image(AbstractLicenseModel, models.Model, BaseImage):
    """
    Model for an ingredient image
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        verbose_name='UUID',
    )
    """Globally unique ID, to identify the image across installations"""

    image = models.ImageField(
        verbose_name=_('Image'),
        help_text=_('Only PNG and JPEG formats are supported'),
        upload_to=ingredient_image_upload_dir,
    )
    """Uploaded image"""

    last_update = models.DateTimeField(auto_now=True)
    """The date when this image was last synchronized """

    size = models.IntegerField()
    """The size of the image in bytes"""

    source_url = models.URLField()
    """The source of the image"""

    @classmethod
    def from_json(
        cls, connect_to, retrieved_image, json_data: dict, headers, generate_uuid: bool = False
    ):
        image: cls = super().from_json(
            connect_to, retrieved_image, json_data, headers, generate_uuid
        )

        image.ingredient = connect_to
        image.license = License.objects.get(pk=2)
        image.license_author = json_data['license_author']
        image.size = json_data['size']

        image.save_image(retrieved_image, json_data)

        image.save()

        connect_to.image = image
        connect_to.save()
        return image
