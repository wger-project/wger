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

# Django
from django.db import models
from django.db.models import IntegerField
from django.utils import timezone
from django.core.validators import (
    MinValueValidator,
)
from django.utils.translation import gettext_lazy as _


class LicenseAuthorHistory(models.Model):
    """
    Tracks model authors
    """

    MODEL_TYPE_EXERCISE = '1'

    MODEL_TYPES = (
        (MODEL_TYPE_EXERCISE, _('Exercise')),
    )

    model_id = IntegerField(
        verbose_name=_('Model ID'),
        validators=[MinValueValidator(1)]
    )
    """The model ID"""

    model_type = models.CharField(
        max_length=3,
        choices=MODEL_TYPES,
        editable=False,
    )
    """The model type"""

    name = models.CharField(
        max_length=120,
        verbose_name=_('Name'),
    )
    """Name"""

    datetime = models.DateTimeField(verbose_name=_('Date and Time'), default=timezone.now)
    """Date and time entry was created"""

    class Meta:
        """
        Set Meta options
        """
        ordering = [
            "model_id",
            "model_type",
            "name",
            "datetime",
        ]

    #
    # Django methods
    #
    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f"Model type: {self.model_type} Name: {self.name} Datetime: ({self.datetime})"

    #
    # Own methods
    #
    def get_owner_object(self):
        """
        License author history has no owner information
        """
        return None
