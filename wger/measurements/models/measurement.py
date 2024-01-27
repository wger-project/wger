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
from django.contrib.auth.models import User
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.measurements.models import Category


class Measurement(models.Model):
    class Meta:
        unique_together = ('date', 'category')
        ordering = [
            '-date',
        ]

    category = models.ForeignKey(
        Category,
        verbose_name=_('User'),
        on_delete=models.CASCADE,
    )

    date = models.DateField(
        _('Date'),
        default=datetime.datetime.now,
    )

    value = models.DecimalField(
        verbose_name=_('Value'),
        max_digits=6,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5000),
        ],
    )

    notes = models.CharField(
        verbose_name=_('Description'),
        max_length=100,
        blank=True,
    )

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.category
