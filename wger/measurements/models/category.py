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

# Django
from django.contrib.auth.models import User
from django.db import models

# wger
from wger.utils.uuid import uuid7


class MetricType(models.TextChoices):
    """
    Semantic type of a measurement category
    """

    CUSTOM = 'custom'  # free-form, no mapping
    BODY_WEIGHT = 'body_weight'
    BODY_FAT = 'body_fat'
    HEIGHT = 'height'
    BLOOD_PRESSURE = 'blood_pressure'
    HEART_RATE = 'heart_rate'
    STEPS = 'steps'
    DISTANCE = 'distance'
    ENERGY = 'energy'
    SLEEP = 'sleep'


class Category(models.Model):
    class Meta:
        ordering = [
            'order',
            '-name',
        ]
        constraints = [
            # official category per (user, metric_type) where is_official=True
            # user-created categories are unaffected
            models.UniqueConstraint(
                fields=['user', 'metric_type'],
                condition=models.Q(is_official=True),
                name='unique_official_category_per_metric_type',
            )
        ]

    id = models.UUIDField(
        default=uuid7,
        primary_key=True,
    )

    user = models.ForeignKey(
        User,
        verbose_name='User',
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        verbose_name='Name',
        max_length=100,
    )

    unit = models.CharField(
        verbose_name='Unit',
        max_length=30,
    )

    metric_type = models.CharField(
        verbose_name='Metric type',
        max_length=20,
        choices=MetricType.choices,
        default=MetricType.CUSTOM,
    )

    # Multi-value measurements (e.g. blood pressure) are modelled as a parent
    # category holding one child category per component. Only leaf categories
    # (no children) carry measurements; nesting is limited to one level.
    parent = models.ForeignKey(
        'self',
        verbose_name='Parent',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
    )

    # Position in the category list; for children, the position within the group
    order = models.IntegerField(
        verbose_name='Order',
        default=0,
    )

    is_official = models.BooleanField(
        verbose_name='Official category',
        default=False,
    )

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

    @classmethod
    def get_or_create_official(cls, user, metric_type, *, name, unit):
        """
        Returns the user's official category for `metric_type`. Used also by
        the legacy weight endpoint
        """
        category, _ = cls.objects.get_or_create(
            user=user,
            metric_type=metric_type,
            is_official=True,
            defaults={'name': name, 'unit': unit},
        )
        return category
