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

# Django
from django.core.management import call_command

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.measurements.models.category import MetricType


class MeasurementGeneratorTestCase(WgerTestCase):
    def test_generator_categories(self):
        # Arrange
        Category.objects.all().delete()

        # Act
        call_command(
            'dummy-generator-measurement-categories',
            '--nr-categories',
            10,
        )

        # Assert
        self.assertEqual(Category.objects.filter(user_id=1).count(), 10)

    def test_generator_entries(self):
        # Arrange
        Category.objects.all().delete()

        # Act
        call_command(
            'dummy-generator-measurement-categories',
            '--nr-categories',
            1,
        )
        call_command(
            'dummy-generator-measurements',
            '--nr-measurements',
            10,
        )

        # Assert
        self.assertEqual(Measurement.objects.filter(category__user_id=1).count(), 10)

    def test_generator_health_blood_pressure(self):
        """
        The health generator writes into the components of the group
        """
        # Act
        call_command(
            'dummy-generator-health-measurements',
            '--days',
            5,
            '--metrics',
            'blood_pressure',
        )

        # Assert
        group = Category.objects.get(user_id=1, metric_type=MetricType.BLOOD_PRESSURE)
        components = group.children.order_by('order')
        self.assertEqual(
            [c.metric_type for c in components],
            [MetricType.BLOOD_PRESSURE_SYSTOLIC, MetricType.BLOOD_PRESSURE_DIASTOLIC],
        )
        self.assertFalse(group.measurement_set.exists())
        self.assertTrue(all(c.measurement_set.exists() for c in components))


class BodyWeightGeneratorTestCase(WgerTestCase):
    def test_generator(self):
        # Arrange
        Measurement.objects.all().delete()

        # Act
        call_command('dummy-generator-body-weight', '--nr-entries', 100)

        # Assert
        self.assertEqual(Measurement.body_weight_for(1).count(), 100)
