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
from decimal import Decimal

# Django
from django.contrib.auth.models import User
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone

# wger
from wger.measurements.models import Category
from wger.measurements.models.category import MetricType
from wger.utils.constants import TWOPLACES
from wger.utils.units import AbstractWeight
from wger.utils.uuid import uuid7


class MeasurementSource(models.TextChoices):
    USER = 'user'
    GOOGLE = 'google'
    APPLE = 'apple'


class Measurement(models.Model):
    class Meta:
        ordering = [
            '-date',
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'source', 'external_id'],
                condition=models.Q(external_id__isnull=False),
                name='unique_external_measurement',
            ),
        ]

    id = models.UUIDField(
        default=uuid7,
        primary_key=True,
    )

    category = models.ForeignKey(
        Category,
        verbose_name='Category',
        on_delete=models.CASCADE,
    )

    date = models.DateTimeField(
        verbose_name='Date',
        default=timezone.now,
    )

    value = models.DecimalField(
        verbose_name='Value',
        max_digits=6,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5000),
        ],
    )

    notes = models.CharField(
        verbose_name='Description',
        max_length=100,
        blank=True,
    )

    source = models.CharField(
        verbose_name='Source',
        max_length=10,
        choices=MeasurementSource.choices,
        default=MeasurementSource.USER,
    )

    external_id = models.UUIDField(
        verbose_name='External ID',
        blank=True,
        null=True,
    )

    extra_data = models.JSONField(
        verbose_name='Extra data',
        default=dict,
        blank=True,
    )
    """
    Per-entry metadata. ``unit`` holds the unit the value was entered in
    (falls back to the category unit when absent), external syncs store
    their provenance (source unit, original value, device) here as well.
    """

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.category

    @property
    def unit(self) -> str:
        """
        Returns the unit the value is stored in
        """
        return self.extra_data.get('unit') or self.category.unit

    def value_in(self, unit: str) -> Decimal:
        """
        Returns the value converted to the given weight unit ('kg' or 'lb').

        Only body weight entries carry convertible units, all other metric
        types have a fixed unit.
        """
        if self.unit == unit:
            return self.value
        if unit not in ('kg', 'lb') or self.unit not in ('kg', 'lb'):
            raise ValueError(f'Cannot convert between {self.unit} and {unit}')
        weight = AbstractWeight(self.value, self.unit)
        return (weight.kg if unit == 'kg' else weight.lb).quantize(TWOPLACES)

    @classmethod
    def body_weight_for(cls, user: User) -> models.QuerySet:
        """
        Returns the user's body weight entries: the measurements in the
        official body-weight category
        """
        return cls.objects.filter(
            category__user=user,
            category__metric_type=MetricType.BODY_WEIGHT,
            category__is_official=True,
        )
