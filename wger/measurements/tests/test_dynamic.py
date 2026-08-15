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
from unittest.mock import patch

# Django
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

# Third Party
from rest_framework import status

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.consts import WEIGHT_UNIT_LB
from wger.manager.models import WorkoutLog
from wger.measurements.dynamic.engine import reconcile
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.measurements.models.measurement import MeasurementSource
from wger.measurements.powersync import MeasurementHandler
from wger.measurements.tasks import reconcile_all_dynamic_categories_task


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

    def make_log(
        self,
        weight,
        reps,
        days_ago: int = 0,
        weight_unit: int = 1,
        exercise_id: int = 1,
    ) -> WorkoutLog:
        with self.captureOnCommitCallbacks(execute=True):
            log = WorkoutLog(
                user=self.user,
                exercise_id=exercise_id,
                weight=Decimal(weight),
                repetitions=Decimal(reps),
                weight_unit_id=weight_unit,
                date=timezone.now() - datetime.timedelta(days=days_ago),
            )
            log.save()
        return log

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


class TypedCategoryTestCase(DynamicMeasurementTestCase):
    """
    Calculated types belong on custom categories, not on the typed ones the
    server and the health importer maintain themselves
    """

    def setUp(self):
        super().setUp()
        self.user_login('test')

    def test_official_category_refuses_dynamic_type(self):
        """
        The official body weight category cannot be turned into a BMI one
        """
        response = self.client.patch(
            reverse('measurement-category-detail', kwargs={'pk': self.weight_category.pk}),
            {'dynamic_type': 'BMI'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.weight_category.refresh_from_db()
        self.assertEqual(self.weight_category.dynamic_type, Category.DynamicType.NONE)

    def test_calculated_rows_never_feed_themselves(self):
        """
        A BMI computation ignores calculated entries, so a category that ends
        up as the source of its own type does not grow with every run
        """
        self.create_weight('81.00')

        # Past the check above this is only reachable through a bulk write
        with self.captureOnCommitCallbacks(execute=True):
            self.weight_category.dynamic_type = Category.DynamicType.BMI
            self.weight_category.save()
        first_run = self.calculated_rows(self.weight_category).count()

        reconcile(self.weight_category)

        self.assertEqual(self.calculated_rows(self.weight_category).count(), first_run)


class ExistingEntriesTestCase(DynamicMeasurementTestCase):
    """
    Entries a user wrote themselves stay theirs, also in a category that was
    switched to a calculated type afterwards
    """

    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(user=self.user, name='Waist', unit='cm')
        self.entry = Measurement.objects.create(
            category=self.category,
            date=timezone.now(),
            value=Decimal('90.00'),
        )
        self.user_login('test')

    def test_activation_refused_with_own_entries(self):
        """
        A category holding entries of its own cannot be switched over
        """
        response = self.client.patch(
            reverse('measurement-category-detail', kwargs={'pk': self.category.pk}),
            {'dynamic_type': 'BMI'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_own_entries_stay_editable(self):
        """
        An entry of the user's own remains editable, the block is about the
        calculated rows and not about the category
        """
        with self.captureOnCommitCallbacks(execute=True):
            self.category.dynamic_type = Category.DynamicType.BMI
            self.category.save()

        response = self.client.patch(
            reverse('measurement-detail', kwargs={'pk': self.entry.pk}),
            {'value': 95},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_own_entries_stay_deletable(self):
        """
        The same for deleting, on the REST and the PowerSync path
        """
        with self.captureOnCommitCallbacks(execute=True):
            self.category.dynamic_type = Category.DynamicType.BMI
            self.category.save()

        response = self.client.delete(
            reverse('measurement-detail', kwargs={'pk': self.entry.pk}),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_own_entries_stay_deletable_over_powersync(self):
        """
        The synced delete of an own entry is not refused either
        """
        with self.captureOnCommitCallbacks(execute=True):
            self.category.dynamic_type = Category.DynamicType.BMI
            self.category.save()

        MeasurementHandler().handle_delete({'id': str(self.entry.pk)}, self.user.pk)

        self.assertFalse(Measurement.objects.filter(pk=self.entry.pk).exists())


class ReconcileFailureTestCase(DynamicMeasurementTestCase):
    """
    A computation that raises stays contained: neither the safety net nor an
    unrelated request goes down with it
    """

    def test_catch_all_continues_after_a_failure(self):
        """
        The daily task reconciles the remaining categories
        """
        first = self.enable_bmi()
        second = Category.objects.create(
            user=self.user,
            name='Second',
            unit='',
            dynamic_type=Category.DynamicType.BMI,
        )
        order = list(
            Category.objects.exclude(dynamic_type=Category.DynamicType.NONE).values_list(
                'pk', flat=True
            )
        )
        self.assertEqual(set(order), {first.pk, second.pk})

        seen = []

        def reconcile(category):
            seen.append(category.pk)
            if category.pk == order[0]:
                raise ValueError('boom')

        with patch('wger.measurements.tasks.reconcile', side_effect=reconcile):
            reconcile_all_dynamic_categories_task()

        self.assertEqual(seen, order)

    def test_scheduled_reconcile_does_not_reach_the_request(self):
        """
        The callback runs after the commit, a failure there must not turn an
        unrelated write into a 500
        """
        category = self.enable_bmi()

        with patch(
            'wger.measurements.dynamic.engine.reconcile_by_id',
            side_effect=ValueError('boom'),
        ):
            with self.captureOnCommitCallbacks(execute=True):
                Measurement.objects.create(
                    category=self.weight_category,
                    date=timezone.now(),
                    value=Decimal('81.00'),
                )

        self.assertTrue(Category.objects.filter(pk=category.pk).exists())


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


class WhtrTestCase(DynamicMeasurementTestCase):
    """
    The waist-to-height ratio derives from a user-chosen source category
    """

    def setUp(self):
        super().setUp()
        self.waist = Category.objects.create(user=self.user, name='Waist', unit='cm')

    def create_waist(self, value, days_ago: int = 0) -> Measurement:
        with self.captureOnCommitCallbacks(execute=True):
            entry = Measurement.objects.create(
                category=self.waist,
                date=timezone.now() - datetime.timedelta(days=days_ago),
                value=Decimal(value),
            )
        return entry

    def enable_whtr(self, source: Category = None) -> Category:
        with self.captureOnCommitCallbacks(execute=True):
            category = Category.objects.create(
                user=self.user,
                name='WHtR',
                unit='',
                dynamic_type=Category.DynamicType.WHTR,
                dynamic_params={'category_id': str((source or self.waist).pk)},
            )
        return category

    def test_backfill(self):
        """
        Enabling the ratio computes one row per source entry
        """
        self.create_waist('90.00', days_ago=10)
        self.create_waist('99.00')

        category = self.enable_whtr()
        rows = self.calculated_rows(category)

        # height 180: 90 / 180 = 0.50, 99 / 180 = 0.55
        self.assertEqual(rows.count(), 2)
        self.assertEqual(rows[0].value, Decimal('0.50'))
        self.assertEqual(rows[1].value, Decimal('0.55'))

    def test_source_entry_update_recomputes(self):
        """
        Editing a source entry updates its ratio row
        """
        entry = self.create_waist('90.00')
        category = self.enable_whtr()

        with self.captureOnCommitCallbacks(execute=True):
            entry.value = Decimal('81.00')
            entry.save()

        rows = self.calculated_rows(category)
        self.assertEqual(rows[0].value, Decimal('0.45'))

    def test_foreign_source_stays_empty(self):
        """
        Params pointing at another user's category yield no rows
        """
        admin = User.objects.get(username='admin')
        foreign = Category.objects.create(user=admin, name='Waist', unit='cm')
        Measurement.objects.create(
            category=foreign,
            date=timezone.now(),
            value=Decimal('90.00'),
        )

        category = self.enable_whtr(source=foreign)
        self.assertEqual(self.calculated_rows(category).count(), 0)

    def test_api_refuses_foreign_source(self):
        """
        Creating a ratio category over another user's category returns a 400
        """
        admin = User.objects.get(username='admin')
        foreign = Category.objects.create(user=admin, name='Waist', unit='cm')

        self.user_login('test')
        response = self.client.post(
            reverse('measurement-category-list'),
            {
                'name': 'WHtR',
                'unit': '',
                'dynamic_type': 'WHTR',
                'dynamic_params': {'category_id': str(foreign.pk)},
            },
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dynamic_params', response.data)

    def test_api_refuses_dynamic_source(self):
        """
        A calculated category cannot be the source of another one
        """
        bmi = self.enable_bmi()

        self.user_login('test')
        response = self.client.post(
            reverse('measurement-category-list'),
            {
                'name': 'WHtR',
                'unit': '',
                'dynamic_type': 'WHTR',
                'dynamic_params': {'category_id': str(bmi.pk)},
            },
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_source_in_inches_is_converted(self):
        """
        A source measured in inches is read as centimeters
        """
        self.waist.unit = 'in'
        self.waist.save()
        self.create_waist('34.00')

        category = self.enable_whtr()
        rows = self.calculated_rows(category)

        # 34 in = 86.36 cm, / 180 = 0.48 (and not the raw 34 / 180 = 0.19)
        self.assertEqual(rows[0].value, Decimal('0.48'))

    def test_api_refuses_a_source_that_is_not_a_length(self):
        """
        A category holding kilograms cannot be the source of a ratio
        """
        weights = Category.objects.create(user=self.user, name='Dumbbells', unit='kg')

        self.user_login('test')
        response = self.client.post(
            reverse('measurement-category-list'),
            {
                'name': 'WHtR',
                'unit': '',
                'dynamic_type': 'WHTR',
                'dynamic_params': {'category_id': str(weights.pk)},
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dynamic_params', response.data)

    def test_unrelated_patch_survives_a_deleted_source(self):
        """
        Renaming the category still works once its source is gone; only a
        payload that moves the configuration is checked against the data
        """
        self.create_waist('90.00')
        category = self.enable_whtr()
        self.waist.delete()

        self.user_login('test')
        response = self.client.patch(
            reverse('measurement-category-detail', kwargs={'pk': category.pk}),
            {'name': 'Ratio'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_full_object_patch_survives_a_deleted_source(self):
        """
        A client that sends the whole category back, configuration included,
        can rename it as well
        """
        self.create_waist('90.00')
        category = self.enable_whtr()
        self.waist.delete()

        self.user_login('test')
        response = self.client.patch(
            reverse('measurement-category-detail', kwargs={'pk': category.pk}),
            {
                'name': 'Ratio',
                'unit': '',
                'dynamic_type': 'WHTR',
                'dynamic_params': category.dynamic_params,
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_requires_source(self):
        """
        The category_id param is mandatory
        """
        self.user_login('test')
        response = self.client.post(
            reverse('measurement-category-list'),
            {'name': 'WHtR', 'unit': '', 'dynamic_type': 'WHTR'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OneRepMaxTestCase(DynamicMeasurementTestCase):
    """
    The 1RM type condenses the workout logs of one exercise into one
    estimate per day
    """

    def enable_one_rm(self, **params) -> Category:
        with self.captureOnCommitCallbacks(execute=True):
            category = Category.objects.create(
                user=self.user,
                name='1RM',
                unit='kg',
                dynamic_type=Category.DynamicType.ONE_REP_MAX,
                dynamic_params={'exercise_id': 1, **params},
            )
        return category

    def test_backfill_best_set_per_day(self):
        """
        Each day with logs gets one row holding its highest estimate
        """
        self.make_log('100', 5)
        self.make_log('90', 5)
        self.make_log('80', 3, days_ago=3)

        category = self.enable_one_rm()
        rows = self.calculated_rows(category)

        self.assertEqual(rows.count(), 2)
        # Brzycki: 80 / (1.0278 - 0.0278 * 3), 100 / (1.0278 - 0.0278 * 5)
        self.assertEqual(rows[0].value, Decimal('84.71'))
        self.assertEqual(rows[1].value, Decimal('112.51'))

    def test_high_rep_sets_are_ignored(self):
        """
        Sets over max_reps do not enter the estimate
        """
        self.make_log('120', 8)
        self.make_log('100', 5)

        category = self.enable_one_rm()
        rows = self.calculated_rows(category)

        self.assertEqual(rows.count(), 1)
        self.assertEqual(rows[0].value, Decimal('112.51'))

    def test_max_reps_param(self):
        """
        The rep cap is configurable
        """
        self.make_log('120', 8)

        category = self.enable_one_rm(max_reps=8)
        rows = self.calculated_rows(category)

        self.assertEqual(rows.count(), 1)
        # 120 / (1.0278 - 0.0278 * 8)
        self.assertEqual(rows[0].value, Decimal('148.99'))

    def test_pound_logs_are_converted(self):
        """
        A log in lb is converted to kg before the formula
        """
        self.make_log('100', 1, weight_unit=WEIGHT_UNIT_LB)

        category = self.enable_one_rm()
        rows = self.calculated_rows(category)

        # 100 lb = 45.36 kg, at one rep the estimate is the weight itself
        self.assertEqual(rows[0].value, Decimal('45.36'))

    def test_other_exercises_are_ignored(self):
        """
        Only logs of the configured exercise count
        """
        self.make_log('100', 5, exercise_id=2)

        category = self.enable_one_rm()
        self.assertEqual(self.calculated_rows(category).count(), 0)

    def test_new_log_adds_row(self):
        """
        A log written after the category exists gets its day row
        """
        category = self.enable_one_rm()
        self.make_log('100', 5)

        rows = self.calculated_rows(category)
        self.assertEqual(rows.count(), 1)
        self.assertEqual(rows[0].value, Decimal('112.51'))

    def test_deleted_log_removes_day(self):
        """
        Deleting the only log of a day deletes the day's row
        """
        log = self.make_log('100', 5)
        category = self.enable_one_rm()
        self.assertEqual(self.calculated_rows(category).count(), 1)

        with self.captureOnCommitCallbacks(execute=True):
            log.delete()

        self.assertEqual(self.calculated_rows(category).count(), 0)

    def test_api_refuses_unknown_exercise(self):
        """
        An exercise id that does not exist returns a 400
        """
        self.user_login('test')
        response = self.client.post(
            reverse('measurement-category-list'),
            {
                'name': '1RM',
                'unit': 'kg',
                'dynamic_type': 'ONE_REP_MAX',
                'dynamic_params': {'exercise_id': 999999},
            },
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dynamic_params', response.data)

    def test_api_refuses_out_of_range_cap(self):
        """
        The rep cap is bounded by the validity of the formula
        """
        self.user_login('test')
        response = self.client.post(
            reverse('measurement-category-list'),
            {
                'name': '1RM',
                'unit': 'kg',
                'dynamic_type': 'ONE_REP_MAX',
                'dynamic_params': {'exercise_id': 1, 'max_reps': 15},
            },
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OneRmTotalTestCase(DynamicMeasurementTestCase):
    """
    The 1RM total sums the rolling-window maxima of several exercises
    """

    def enable_total(self, **params) -> Category:
        with self.captureOnCommitCallbacks(execute=True):
            category = Category.objects.create(
                user=self.user,
                name='Total',
                unit='kg',
                dynamic_type=Category.DynamicType.ONE_RM_TOTAL,
                dynamic_params={'exercise_ids': [1, 2], **params},
            )
        return category

    def test_sums_the_window_maxima(self):
        """
        A training day sums the best in-window estimate of every exercise
        """
        self.make_log('100', 5, exercise_id=1)
        self.make_log('80', 3, exercise_id=2)

        category = self.enable_total()
        rows = self.calculated_rows(category)

        # 112.51 + 84.71
        self.assertEqual(rows.count(), 1)
        self.assertEqual(rows[0].value, Decimal('197.22'))

    def test_window_max_beats_todays_set(self):
        """
        The best set of the window counts, not the most recent one
        """
        self.make_log('110', 5, days_ago=10, exercise_id=1)
        self.make_log('100', 5, exercise_id=1)
        self.make_log('80', 3, exercise_id=2)

        category = self.enable_total()
        rows = self.calculated_rows(category)

        # Today: brzycki(110, 5) + brzycki(80, 3) = 123.76 + 84.71. The day
        # ten days back has no second exercise in its window, so no entry.
        self.assertEqual(rows.count(), 1)
        self.assertEqual(rows[0].value, Decimal('208.47'))

    def test_no_entry_without_full_coverage(self):
        """
        A day where one exercise has nothing in its window gets no entry
        """
        self.make_log('100', 5, exercise_id=1)
        self.make_log('80', 3, days_ago=40, exercise_id=2)

        category = self.enable_total()

        self.assertEqual(self.calculated_rows(category).count(), 0)

    def test_window_days_param(self):
        """
        A wider window keeps older sets in the total
        """
        self.make_log('100', 5, exercise_id=1)
        self.make_log('80', 3, days_ago=40, exercise_id=2)

        category = self.enable_total(window_days=60)
        rows = self.calculated_rows(category)

        self.assertEqual(rows.count(), 1)
        self.assertEqual(rows[0].value, Decimal('197.22'))

    def test_every_training_day_gets_a_point(self):
        """
        Each day one of the exercises was trained carries the total of its
        own window
        """
        self.make_log('80', 3, days_ago=10, exercise_id=2)
        self.make_log('100', 5, days_ago=5, exercise_id=1)
        self.make_log('110', 5, exercise_id=1)

        category = self.enable_total()
        rows = self.calculated_rows(category)

        # Day -10 has no exercise 1 in its window yet: no entry. Day -5 and
        # today pair their own squat best with the day -10 deadlift.
        self.assertEqual(rows.count(), 2)
        self.assertEqual(rows[0].value, Decimal('197.22'))
        self.assertEqual(rows[1].value, Decimal('208.47'))

    def test_api_refuses_single_exercise(self):
        """
        A total needs at least two exercises
        """
        self.user_login('test')
        response = self.client.post(
            reverse('measurement-category-list'),
            {
                'name': 'Total',
                'unit': 'kg',
                'dynamic_type': 'ONE_RM_TOTAL',
                'dynamic_params': {'exercise_ids': [1]},
            },
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_refuses_duplicate_exercises(self):
        """
        The same exercise cannot enter the total twice
        """
        self.user_login('test')
        response = self.client.post(
            reverse('measurement-category-list'),
            {
                'name': 'Total',
                'unit': 'kg',
                'dynamic_type': 'ONE_RM_TOTAL',
                'dynamic_params': {'exercise_ids': [1, 1]},
            },
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_refuses_unknown_exercises(self):
        """
        Every exercise of the list has to exist
        """
        self.user_login('test')
        response = self.client.post(
            reverse('measurement-category-list'),
            {
                'name': 'Total',
                'unit': 'kg',
                'dynamic_type': 'ONE_RM_TOTAL',
                'dynamic_params': {'exercise_ids': [1, 999999]},
            },
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dynamic_params', response.data)
