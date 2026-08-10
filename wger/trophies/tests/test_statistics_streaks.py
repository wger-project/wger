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
from unittest import mock

# Django
from django.contrib.auth.models import User
from django.test import SimpleTestCase

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import WorkoutSession
from wger.trophies.models import UserStatistics
from wger.trophies.services.statistics import UserStatisticsService


FROZEN_TODAY = datetime.date(2024, 6, 19)
"""A Wednesday; the most recent Saturday is 2024-06-15"""


def frozen_today():
    """
    Freezes datetime.date.today() so the streak calculations are deterministic
    """

    class FrozenDate(datetime.date):
        @classmethod
        def today(cls):
            return FROZEN_TODAY

    return mock.patch('datetime.date', FrozenDate)


def days_ago(days: int) -> datetime.date:
    return FROZEN_TODAY - datetime.timedelta(days=days)


class CalculateStreaksTestCase(SimpleTestCase):
    """
    Tests the full streak calculation over real date sequences
    """

    def calculate(self, dates):
        with frozen_today():
            return UserStatisticsService._calculate_streaks(dates)

    def test_no_workouts(self):
        self.assertEqual(self.calculate([]), (0, 0))

    def test_single_workout_today(self):
        self.assertEqual(self.calculate([FROZEN_TODAY]), (1, 1))

    def test_run_ending_today(self):
        dates = [days_ago(2), days_ago(1), FROZEN_TODAY]
        self.assertEqual(self.calculate(dates), (3, 3))

    def test_run_ending_yesterday_is_still_active(self):
        dates = [days_ago(3), days_ago(2), days_ago(1)]
        self.assertEqual(self.calculate(dates), (3, 3))

    def test_run_ending_two_days_ago_is_broken(self):
        dates = [days_ago(4), days_ago(3), days_ago(2)]
        self.assertEqual(self.calculate(dates), (0, 3))

    def test_longest_streak_in_the_past(self):
        dates = [days_ago(10), days_ago(9), days_ago(8), days_ago(1), FROZEN_TODAY]
        self.assertEqual(self.calculate(dates), (2, 3))

    def test_duplicate_days_count_once(self):
        dates = [days_ago(1), days_ago(1), days_ago(1), FROZEN_TODAY]
        self.assertEqual(self.calculate(dates), (2, 2))

    def test_streak_across_year_boundary(self):
        dates = [
            datetime.date(2023, 12, 30),
            datetime.date(2023, 12, 31),
            datetime.date(2024, 1, 1),
        ]
        self.assertEqual(self.calculate(dates), (0, 3))


class CalculateWeekendStreakTestCase(SimpleTestCase):
    """
    Tests the weekend streak calculation over real date sequences

    With today frozen to Wednesday 2024-06-19, the most recent Saturday
    is 2024-06-15.
    """

    def calculate(self, dates):
        with frozen_today():
            return UserStatisticsService._calculate_weekend_streak(dates)

    def test_no_workouts(self):
        self.assertEqual(self.calculate([]), (0, None))

    def test_last_weekend_complete(self):
        dates = [datetime.date(2024, 6, 15), datetime.date(2024, 6, 16)]
        self.assertEqual(self.calculate(dates), (1, datetime.date(2024, 6, 15)))

    def test_saturday_alone_is_not_a_complete_weekend(self):
        self.assertEqual(self.calculate([datetime.date(2024, 6, 15)]), (0, None))

    def test_two_consecutive_weekends(self):
        dates = [
            datetime.date(2024, 6, 8),
            datetime.date(2024, 6, 9),
            datetime.date(2024, 6, 15),
            datetime.date(2024, 6, 16),
        ]
        self.assertEqual(self.calculate(dates), (2, datetime.date(2024, 6, 15)))

    def test_gap_resets_the_streak(self):
        dates = [
            datetime.date(2024, 6, 1),
            datetime.date(2024, 6, 2),
            # weekend of 2024-06-08 is skipped
            datetime.date(2024, 6, 15),
            datetime.date(2024, 6, 16),
        ]
        self.assertEqual(self.calculate(dates), (1, datetime.date(2024, 6, 15)))

    def test_old_weekend_is_no_current_streak(self):
        dates = [datetime.date(2024, 6, 1), datetime.date(2024, 6, 2)]
        self.assertEqual(self.calculate(dates), (0, datetime.date(2024, 6, 1)))


class IncrementWorkoutStreakTestCase(WgerTestCase):
    """
    Tests the incremental streak bookkeeping used by the signal handlers

    increment_workout does not depend on today's date, so the scenarios run
    with fixed dates.
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='admin')
        UserStatistics.objects.filter(user=self.user).delete()

    def increment(self, date: datetime.date) -> UserStatistics:
        session = WorkoutSession(user=self.user, date=date)
        return UserStatisticsService.increment_workout(self.user, session=session)

    def test_first_workout_starts_a_streak(self):
        stats = self.increment(datetime.date(2024, 3, 1))

        self.assertEqual(stats.current_streak, 1)
        self.assertEqual(stats.longest_streak, 1)
        self.assertEqual(stats.last_workout_date, datetime.date(2024, 3, 1))

    def test_consecutive_day_extends_the_streak(self):
        self.increment(datetime.date(2024, 3, 1))
        stats = self.increment(datetime.date(2024, 3, 2))

        self.assertEqual(stats.current_streak, 2)
        self.assertEqual(stats.longest_streak, 2)

    def test_second_workout_on_the_same_day_does_not_extend(self):
        self.increment(datetime.date(2024, 3, 1))
        self.increment(datetime.date(2024, 3, 2))
        stats = self.increment(datetime.date(2024, 3, 2))

        self.assertEqual(stats.current_streak, 2)

    def test_gap_resets_the_streak_but_keeps_the_longest(self):
        self.increment(datetime.date(2024, 3, 1))
        self.increment(datetime.date(2024, 3, 2))
        self.increment(datetime.date(2024, 3, 3))
        stats = self.increment(datetime.date(2024, 3, 10))

        self.assertEqual(stats.current_streak, 1)
        self.assertEqual(stats.longest_streak, 3)

    def test_streak_across_month_boundary(self):
        self.increment(datetime.date(2024, 3, 31))
        stats = self.increment(datetime.date(2024, 4, 1))

        self.assertEqual(stats.current_streak, 2)

    def test_long_gap_records_the_inactive_date(self):
        self.increment(datetime.date(2024, 3, 1))
        stats = self.increment(datetime.date(2024, 4, 15))

        self.assertEqual(stats.current_streak, 1)
        self.assertEqual(stats.last_inactive_date, datetime.date(2024, 3, 1))

    def test_jan_first_workout_is_flagged(self):
        stats = self.increment(datetime.date(2024, 1, 1))
        self.assertTrue(stats.worked_out_jan_1)
