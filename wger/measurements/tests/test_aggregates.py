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
from django.urls import reverse
from django.utils import timezone

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.measurements.models import (
    Category,
    Measurement,
)


class AggregateApiTestCase(WgerTestCase):
    """
    The condensed reads behind the charts
    """

    category_id = 'cccccccc-cccc-cccc-cccc-000000000002'

    def setUp(self):
        super().setUp()
        self.user_login('test')
        self.category = Category.objects.get(pk=self.category_id)
        Measurement.objects.filter(category=self.category).delete()

    def add(self, date, value, unit=None, extra=None):
        data = dict(extra or {})
        if unit:
            data['unit'] = unit
        return Measurement.objects.create(
            category=self.category,
            date=date,
            value=Decimal(str(value)),
            notes='',
            extra_data=data,
        )

    def aggregate(self, **params):
        response = self.client.get(
            reverse('measurement-aggregate'),
            {'category': self.category_id, **params},
        )
        self.assertEqual(response.status_code, 200)
        return response.data

    def value_counts(self, **params):
        response = self.client.get(
            reverse('measurement-value-counts'),
            {'category': self.category_id, **params},
        )
        self.assertEqual(response.status_code, 200)
        return response.data

    def test_a_day_bucket_holds_the_readings_of_that_day(self):
        day = timezone.make_aware(datetime.datetime(2026, 5, 4, 8))
        self.add(day, 60)
        self.add(day + datetime.timedelta(hours=12), 80)

        rows = self.aggregate(bucket='day', tz='UTC')

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['count'], 2)
        self.assertEqual(rows[0]['sum'], '140.00')
        self.assertEqual(rows[0]['min'], '60.00')
        self.assertEqual(rows[0]['max'], '80.00')

    def test_the_ladder_picks_the_finest_unit_that_fits(self):
        # Two readings a day over four days: the hour level is eight points,
        # the day level four, so the day is the first one under the limit
        for day in range(4, 8):
            base = timezone.make_aware(datetime.datetime(2026, 5, day, 8))
            self.add(base, 60)
            self.add(base + datetime.timedelta(hours=12), 80)

        rows = self.aggregate(max_points=5, tz='UTC')

        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]['count'], 2)

    def test_a_fixed_bucket_ignores_the_point_limit(self):
        for day in range(1, 15):
            self.add(timezone.make_aware(datetime.datetime(2026, 5, day, 8)), 60)

        self.assertEqual(len(self.aggregate(bucket='day', max_points=2, tz='UTC')), 14)

    def test_buckets_are_cut_in_the_given_zone(self):
        # 23:30 UTC is the next day in Berlin, so the two readings share a day
        # there and not in UTC
        self.add(datetime.datetime(2026, 5, 4, 23, 30, tzinfo=datetime.UTC), 60)
        self.add(datetime.datetime(2026, 5, 5, 6, 0, tzinfo=datetime.UTC), 80)

        self.assertEqual(len(self.aggregate(bucket='day', tz='UTC')), 2)
        self.assertEqual(len(self.aggregate(bucket='day', tz='Europe/Berlin')), 1)

    def test_mixed_units_are_kept_apart(self):
        # A mean over kg and lb values is a number in neither, so the client
        # converts each row before merging them
        day = timezone.make_aware(datetime.datetime(2026, 5, 4, 8))
        self.add(day, 80, unit='kg')
        self.add(day + datetime.timedelta(hours=1), 180, unit='lb')

        rows = self.aggregate(bucket='day', tz='UTC')

        self.assertEqual(len(rows), 2)
        self.assertEqual({row['unit'] for row in rows}, {'kg', 'lb'})

    def test_a_stored_aggregate_contributes_its_bounds(self):
        # What the health sync writes for heart rate: one row a day holding
        # the day's average with the range it summarises
        self.add(
            timezone.make_aware(datetime.datetime(2026, 5, 4, 8)),
            70,
            extra={'min': 48, 'max': 165},
        )

        rows = self.aggregate(bucket='day', tz='UTC')

        self.assertEqual(rows[0]['min'], '48.00')
        self.assertEqual(rows[0]['max'], '165.00')

    def test_the_date_filters_of_the_list_apply(self):
        self.add(timezone.make_aware(datetime.datetime(2026, 1, 1, 8)), 60)
        self.add(timezone.make_aware(datetime.datetime(2026, 5, 4, 8)), 80)

        rows = self.aggregate(bucket='day', tz='UTC', date__gte='2026-03-01')

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['sum'], '80.00')

    def test_an_unknown_bucket_or_zone_is_refused(self):
        for params in ({'bucket': 'fortnight'}, {'tz': 'Middle/Earth'}):
            response = self.client.get(
                reverse('measurement-aggregate'),
                {'category': self.category_id, **params},
            )
            self.assertEqual(response.status_code, 400)

    def test_another_users_category_is_not_aggregated(self):
        self.user_login('admin')

        self.assertEqual(self.aggregate(bucket='day'), [])

    def test_value_counts_count_how_often_a_value_occurred(self):
        # A year of readings comes back as the distinct values it covers
        for hour, value in ((8, 60), (9, 60), (10, 75)):
            self.add(timezone.make_aware(datetime.datetime(2026, 5, 4, hour)), value)

        rows = self.value_counts()

        self.assertEqual(
            [(row['value'], row['count']) for row in rows],
            [('60.00', 2), ('75.00', 1)],
        )

    def test_value_counts_carry_the_newest_date_of_a_value(self):
        self.add(datetime.datetime(2026, 5, 4, 8, tzinfo=datetime.UTC), 60)
        self.add(datetime.datetime(2026, 5, 6, 8, tzinfo=datetime.UTC), 60)

        rows = self.value_counts()

        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]['newest'].startswith('2026-05-06'))

    def test_value_counts_of_a_summed_metric_are_daily_totals(self):
        for day, hour, value in ((4, 8, 3000), (4, 20, 2000), (5, 8, 5000)):
            self.add(timezone.make_aware(datetime.datetime(2026, 5, day, hour)), value)

        rows = self.value_counts(summed_per_day='true', tz='UTC')

        # Both days total 5000, so the histogram sees one value twice
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['value'], '5000.00')
        self.assertEqual(rows[0]['count'], 2)

    def test_daily_totals_survive_an_ordering_parameter(self):
        for day, hour, value in ((4, 8, 3000), (4, 20, 2000), (5, 8, 5000)):
            self.add(timezone.make_aware(datetime.datetime(2026, 5, day, hour)), value)

        rows = self.value_counts(summed_per_day='true', tz='UTC', ordering='date')

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['value'], '5000.00')
        self.assertEqual(rows[0]['count'], 2)

    def test_a_bound_stored_as_a_string_still_reads(self):
        # Postgres refuses to cast a JSON string to numeric, even a numeric
        # one, so a row predating the write validation would otherwise take
        # every chart read of its category down with it
        self.add(
            timezone.make_aware(datetime.datetime(2026, 5, 4, 8)),
            70,
            extra={'min': '48', 'max': '165'},
        )

        rows = self.aggregate(bucket='day', tz='UTC')

        self.assertEqual(rows[0]['min'], '48.00')
        self.assertEqual(rows[0]['max'], '165.00')
