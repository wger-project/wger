#  This file is part of wger Workout Manager <https://github.com/wger-project>.
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
import uuid

# Django
from django.db import models


class DeletionLog(models.Model):
    """
    Model to log deleted exercises

    This is needed to keep the local instances in sync with upstream wger. Sometimes
    it is necessary to delete entries, either because they are duplicated, the submission
    wasn't of the needed quality, or other reasons and these would land in the
    different DBs, without any way of cleaning them up.
    """

    MODEL_BASE = 'base'
    MODEL_TRANSLATION = 'translation'
    MODEL_IMAGE = 'image'
    MODEL_VIDEO = 'video'

    MODELS = [
        (MODEL_BASE, 'base'),
        (MODEL_TRANSLATION, 'translation'),
        (MODEL_IMAGE, 'image'),
        (MODEL_VIDEO, 'video'),
    ]

    model_type = models.CharField(
        max_length=11,
        choices=MODELS,
    )

    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='UUID',
    )

    replaced_by = models.UUIDField(
        default=None,
        unique=False,
        editable=False,
        null=True,
        verbose_name='Replaced by',
        help_text='UUID of the object replaced by the deleted one. At the moment only available '
        'for exercise bases',
    )

    timestamp = models.DateTimeField(auto_now=True)

    comment = models.CharField(max_length=200, default='')
