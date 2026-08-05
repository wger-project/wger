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
import uuid

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
    BLOOD_PRESSURE_SYSTOLIC = 'blood_pressure_systolic'
    BLOOD_PRESSURE_DIASTOLIC = 'blood_pressure_diastolic'
    HEART_RATE = 'heart_rate'
    RESTING_HEART_RATE = 'resting_heart_rate'
    STEPS = 'steps'
    DISTANCE = 'distance'
    ENERGY = 'energy'
    SLEEP = 'sleep'
    # Spelled out because the derived labels would read 'Sleep Rem'
    SLEEP_TOTAL = 'sleep_total', 'Total sleep'
    SLEEP_LIGHT = 'sleep_light', 'Light sleep'
    SLEEP_DEEP = 'sleep_deep', 'Deep sleep'
    SLEEP_REM = 'sleep_rem', 'REM sleep'
    SLEEP_AWAKE = 'sleep_awake', 'Awake'

    #
    # Roles. Each type is exactly one of leaf (top-level, carries the
    # measurements), group (top-level container) or component (child of its
    # group, carries the measurements). Asked of a value rather than of a
    # category, because the rules are checked on incoming payloads, before
    # there is a category to ask
    #

    @classmethod
    def is_group(cls, metric_type: str) -> bool:
        """
        Whether the type is a container for components, e.g. blood pressure
        """
        return metric_type in GROUP_COMPONENTS

    @classmethod
    def is_component(cls, metric_type: str) -> bool:
        """
        Whether the type is one component of a group, e.g. systolic
        """
        return metric_type in COMPONENT_GROUPS

    @classmethod
    def group_of(cls, metric_type: str) -> str | None:
        """
        Returns the group a component belongs to, None for every other type
        """
        return COMPONENT_GROUPS.get(metric_type)

    @classmethod
    def components_of(cls, metric_type: str) -> list[tuple[str, str]]:
        """
        Returns the (type, name) of a group's components, in group order
        """
        return GROUP_COMPONENTS.get(metric_type, [])


class ChartType(models.TextChoices):
    """
    Chart a category is drawn as, when the user picked one
    """

    LINE = 'line'
    BAR = 'bar'
    HEATMAP = 'heatmap'
    DELTA = 'delta'
    DISTRIBUTION = 'distribution'


GROUP_COMPONENTS: dict[str, list[tuple[str, str]]] = {
    MetricType.BLOOD_PRESSURE: [
        (MetricType.BLOOD_PRESSURE_SYSTOLIC, 'Systolic'),
        (MetricType.BLOOD_PRESSURE_DIASTOLIC, 'Diastolic'),
    ],
    # The total is a component of its own because a group carries no
    # measurements. It is not the sum of the three stages below it: platforms
    # also report sleep without a stage breakdown, which counts towards the
    # total and has no stage category to live in
    MetricType.SLEEP: [
        (MetricType.SLEEP_TOTAL, 'Total sleep'),
        (MetricType.SLEEP_LIGHT, 'Light sleep'),
        (MetricType.SLEEP_DEEP, 'Deep sleep'),
        (MetricType.SLEEP_REM, 'REM sleep'),
        (MetricType.SLEEP_AWAKE, 'Awake'),
    ],
}
"""
The components of the multi-value metric types, in group order.

This is the single definition of the structure: a group type is a container
that carries no measurements itself, its components are the child categories
that do. The names match the ones the health importer uses so that both sides
create the same categories.
"""

COMPONENT_GROUPS: dict[str, str] = {
    component: group
    for group, components in GROUP_COMPONENTS.items()
    for component, _ in components
}


BODY_WEIGHT_UNITS = ('kg', 'lb')
"""
The units a body weight is stored in, on the category as well as per entry.

Body weight is the one metric whose values are converted on read
(``Measurement.value_in``), so a category holding anything else has no reader:
the legacy weight endpoint, the BMI, the trainer view and the CSV export all
go through that conversion.
"""


CATEGORY_NAMESPACE = uuid.UUID('4c5ef6dd-97c9-5b18-9f8b-2a5c1ed70a2f')
"""Namespace for the derived primary keys, see Category.deterministic_id()"""


class Category(models.Model):
    class Meta:
        ordering = [
            'order',
            '-name',
        ]
        constraints = [
            # A typed category is the one place its metric lives: the health
            # importer looks it up by type, and both manual and synced entries
            # have to end up in the same one. Free-form categories keep the
            # default type and are unaffected.
            #
            # This covers the official categories as well, since those are
            # typed by definition (is_official means the server depends on the
            # row existing for that metric type).
            models.UniqueConstraint(
                fields=['user', 'metric_type'],
                condition=~models.Q(metric_type=MetricType.CUSTOM),
                name='unique_typed_category_per_user',
            ),
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
        max_length=30,
        choices=MetricType.choices,
        default=MetricType.CUSTOM,
    )

    # Null means "derive the chart from the metric type", which is what every
    # category does unless the user picked something else. Which of the values
    # are offered is a client decision (a step count is a bar or a heatmap, not
    # a line), and so is what happens to a value that does not fit the category:
    # the clients fall back to the derived default instead of showing nothing,
    # which is also what keeps an older client working when a type is added here
    chart_type = models.CharField(
        verbose_name='Chart type',
        max_length=20,
        choices=ChartType.choices,
        blank=True,
        null=True,
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

    @staticmethod
    def has_deterministic_id(metric_type: str) -> bool:
        """
        Whether the primary key of such a category is derived instead of random.

        Body weight is excluded: the server creates that category on its own
        (registration signal, weight backfill), so no client can race it, and
        the existing rows carry uuid7 keys that every synced device holds
        locally.
        """
        return metric_type not in (MetricType.CUSTOM, MetricType.BODY_WEIGHT)

    @staticmethod
    def deterministic_id(user_id: int, metric_type: str) -> uuid.UUID:
        """
        Returns the primary key a typed category gets for this user.

        Clients create categories while offline, so two devices would otherwise
        end up with two rows for the same metric. Deriving the key from user and
        metric type makes both arrive at the same one: the second push is then an
        idempotent no-op instead of a conflict with the uniqueness constraint.
        """
        return uuid.uuid5(CATEGORY_NAMESPACE, f'{user_id}:{metric_type}')

    def create_components(self) -> None:
        """
        Creates the missing component categories of a multi-value group.

        A group is a container, its readings live in one child category per
        component, so creating e.g. a blood pressure category gives it its
        systolic and diastolic children right away. Does nothing for every other
        metric type.
        """
        for order, (metric_type, name) in enumerate(MetricType.components_of(self.metric_type)):
            Category.objects.get_or_create(
                id=Category.deterministic_id(self.user_id, metric_type),
                defaults={
                    'user_id': self.user_id,
                    'name': name,
                    'unit': self.unit,
                    'metric_type': metric_type,
                    'parent': self,
                    'order': order,
                },
            )

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
