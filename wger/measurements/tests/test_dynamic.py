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
import datetime
from decimal import Decimal

# Django
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

# Third Party
from rest_framework import status

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.measurements.models.measurement import MeasurementSource
from wger.measurements.powersync import MeasurementHandler


# Pinned in test-measurement-categories.json, the official body weight
# category of user 'test' (height 180 in test-user-data.json)
BODY_WEIGHT_CATEGORY = 'cccccccc-cccc-cccc-cccc-0000000000b0'


class DynamicMeasurementTestCase(WgerTestCase):
    """
    Base with helpers to write body weight entries and read the calculated
    rows with the engine's triggers firing (they run on transaction commit)
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='test')
        self.weight_category = Category.objects.get(pk=BODY_WEIGHT_CATEGORY)
        # The fixtures ship weight entries; the tests build their own history
        Measurement.objects.filter(category=self.weight_category).delete()

    def create_weight(self, value, days_ago: int = 0, unit: str = None) -> Measurement:
        with self.captureOnCommitCallbacks(execute=True):
            entry = Measurement.objects.create(
                category=self.weight_category,
                date=timezone.now() - datetime.timedelta(days=days_ago),
                value=Decimal(value),
                extra_data={'unit': unit} if unit else {},
            )
        return entry

    def enable_bmi(self) -> Category:
        with self.captureOnCommitCallbacks(execute=True):
            category = Category.objects.create(
                user=self.user,
                name='BMI',
                unit='',
                dynamic_type=Category.DynamicType.BMI,
            )
        return category

    def calculated_rows(self, category):
        return Measurement.objects.filter(
            category=category,
            source=MeasurementSource.CALCULATED,
        ).order_by('date')


class EngineTestCase(DynamicMeasurementTestCase):
    """
    The reconcile engine keeps the calculated rows in step with their sources
    """

    def test_enabling_backfills(self):
        """
        Switching a category to BMI computes one row per existing weight entry
        """
        entry_old = self.create_weight('72.90', days_ago=10)
        entry_new = self.create_weight('81.00')

        category = self.enable_bmi()
        rows = self.calculated_rows(category)

        self.assertEqual(rows.count(), 2)
        # height 180: 72.9 / 1.8^2 = 22.5, 81 / 1.8^2 = 25
        self.assertEqual(rows[0].value, Decimal('22.50'))
        self.assertEqual(rows[0].external_id, entry_old.pk)
        self.assertEqual(rows[0].date, entry_old.date)
        self.assertEqual(rows[1].value, Decimal('25.00'))
        self.assertEqual(rows[1].external_id, entry_new.pk)

    def test_new_weight_entry_adds_row(self):
        """
        A weight entry written after the category exists gets its BMI row
        """
        category = self.enable_bmi()
        self.assertEqual(self.calculated_rows(category).count(), 0)

        self.create_weight('81.00')

        rows = self.calculated_rows(category)
        self.assertEqual(rows.count(), 1)
        self.assertEqual(rows[0].value, Decimal('25.00'))

    def test_updated_weight_entry_recomputes_row(self):
        """
        Editing a weight entry updates its BMI row in place
        """
        entry = self.create_weight('81.00')
        category = self.enable_bmi()

        with self.captureOnCommitCallbacks(execute=True):
            entry.value = Decimal('72.90')
            entry.save()

        rows = self.calculated_rows(category)
        self.assertEqual(rows.count(), 1)
        self.assertEqual(rows[0].value, Decimal('22.50'))
        self.assertEqual(rows[0].external_id, entry.pk)

    def test_deleted_weight_entry_removes_row(self):
        """
        Deleting a weight entry deletes the BMI row derived from it
        """
        entry = self.create_weight('81.00')
        keeper = self.create_weight('72.90', days_ago=5)
        category = self.enable_bmi()

        with self.captureOnCommitCallbacks(execute=True):
            entry.delete()

        rows = self.calculated_rows(category)
        self.assertEqual(rows.count(), 1)
        self.assertEqual(rows[0].external_id, keeper.pk)

    def test_pound_entries_are_converted(self):
        """
        A weight entry stored in lb is converted to kg before the formula
        """
        self.create_weight('180', unit='lb')
        category = self.enable_bmi()

        rows = self.calculated_rows(category)
        # 180 lb = 81.65 kg, / 1.8^2 = 25.20 (and not the naive 55.56)
        self.assertEqual(rows[0].value, Decimal('25.20'))

    def test_height_change_recomputes(self):
        """
        Changing the profile height recomputes every BMI row
        """
        self.create_weight('81.00')
        category = self.enable_bmi()

        profile = self.user.userprofile
        with self.captureOnCommitCallbacks(execute=True):
            profile.height = 200
            profile.save()

        rows = self.calculated_rows(category)
        # 81 / 2.0^2
        self.assertEqual(rows[0].value, Decimal('20.25'))

    def test_missing_height_clears_rows(self):
        """
        Without a height there is no BMI, the rows are removed
        """
        self.create_weight('81.00')
        category = self.enable_bmi()
        self.assertEqual(self.calculated_rows(category).count(), 1)

        profile = self.user.userprofile
        with self.captureOnCommitCallbacks(execute=True):
            profile.height = None
            profile.save()

        self.assertEqual(self.calculated_rows(category).count(), 0)

    def test_disabling_clears_rows(self):
        """
        Switching the category back to NONE deletes its calculated rows
        """
        self.create_weight('81.00')
        category = self.enable_bmi()
        self.assertEqual(self.calculated_rows(category).count(), 1)

        with self.captureOnCommitCallbacks(execute=True):
            category.dynamic_type = Category.DynamicType.NONE
            category.save()

        self.assertEqual(self.calculated_rows(category).count(), 0)

    def test_other_users_weight_does_not_leak(self):
        """
        Weight entries of another user do not end up in this user's BMI
        """
        category = self.enable_bmi()

        admin = User.objects.get(username='admin')
        admin_weight = Category.get_or_create_body_weight(admin, unit='kg')
        with self.captureOnCommitCallbacks(execute=True):
            Measurement.objects.create(
                category=admin_weight,
                date=timezone.now(),
                value=Decimal('90.00'),
            )

        self.assertEqual(self.calculated_rows(category).count(), 0)


class ApiWriteBlockTestCase(DynamicMeasurementTestCase):
    """
    The entries of a calculated category cannot be written through the API
    """

    def setUp(self):
        super().setUp()
        self.create_weight('81.00')
        self.category = self.enable_bmi()
        self.row = self.calculated_rows(self.category).first()
        self.user_login('test')

    def test_create_is_refused(self):
        """
        POSTing an entry into a calculated category returns a 400
        """
        response = self.client.post(
            reverse('measurement-list'),
            {
                'category': str(self.category.pk),
                'date': timezone.now().isoformat(),
                'value': 42,
            },
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_is_refused(self):
        """
        PATCHing a calculated row returns a 400 also without a category field
        """
        response = self.client.patch(
            reverse('measurement-detail', kwargs={'pk': self.row.pk}),
            {'value': 42},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_is_refused(self):
        """
        DELETing a calculated row returns a 403
        """
        response = self.client.delete(
            reverse('measurement-detail', kwargs={'pk': self.row.pk}),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_stays_open(self):
        """
        Calculated rows read like any other measurement
        """
        response = self.client.get(
            reverse('measurement-list'),
            {'category': str(self.category.pk)},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


class PowerSyncWriteBlockTestCase(DynamicMeasurementTestCase):
    """
    The PowerSync upload path refuses writes to calculated rows as well
    """

    def setUp(self):
        super().setUp()
        self.create_weight('81.00')
        self.category = self.enable_bmi()
        self.row = self.calculated_rows(self.category).first()

    def test_create_is_refused(self):
        """
        A synced insert into a calculated category is rejected
        """
        result = MeasurementHandler().handle_create(
            {
                'id': 'dddddddd-dddd-dddd-dddd-0000000000ff',
                'category': str(self.category.pk),
                'date': timezone.now().isoformat(),
                'value': '42',
            },
            self.user.pk,
        )
        self.assertIsNotNone(result)
        self.assertIn('error', result)

    def test_delete_is_refused(self):
        """
        A synced delete of a calculated row is rejected
        """
        result = MeasurementHandler().handle_delete({'id': str(self.row.pk)}, self.user.pk)
        self.assertEqual(result['error'], 'Forbidden')
        self.assertTrue(Measurement.objects.filter(pk=self.row.pk).exists())


class DynamicCategoryApiTestCase(DynamicMeasurementTestCase):
    """
    The category endpoint validates the dynamic fields and lists the types
    """

    def setUp(self):
        super().setUp()
        self.user_login('test')

    def test_params_must_match_schema(self):
        """
        BMI takes no parameters, a payload with any is refused
        """
        response = self.client.post(
            reverse('measurement-category-list'),
            {
                'name': 'BMI',
                'unit': '',
                'dynamic_type': 'BMI',
                'dynamic_params': {'exercise_id': 1},
            },
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dynamic_params', response.data)

    def test_params_cleared_without_type(self):
        """
        Params of a category without a dynamic type are stored empty
        """
        response = self.client.post(
            reverse('measurement-category-list'),
            {
                'name': 'Plain',
                'unit': 'cm',
                'dynamic_params': {'stale': True},
            },
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['dynamic_params'], {})

    def test_dynamic_types_endpoint(self):
        """
        The endpoint lists the registered types with their params schema
        """
        response = self.client.get(reverse('measurement-category-dynamic-types'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bmi = next(row for row in response.data if row['value'] == 'BMI')
        self.assertEqual(bmi['label'], 'BMI')
        self.assertIn('params_schema', bmi)

    def test_create_via_api_backfills(self):
        """
        A BMI category created through the API is filled on commit
        """
        self.create_weight('81.00')

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                reverse('measurement-category-list'),
                {'name': 'BMI', 'unit': '', 'dynamic_type': 'BMI'},
                content_type='application/json',
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        rows = self.calculated_rows(Category.objects.get(pk=response.data['id']))
        self.assertEqual(rows.count(), 1)
        self.assertEqual(rows[0].value, Decimal('25.00'))
