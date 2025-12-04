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

# Standard Library
import datetime
from decimal import Decimal

# Django
from django.contrib.auth.models import User

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.trophies.checkers.count_based import CountBasedChecker
from wger.trophies.checkers.date_based import DateBasedChecker
from wger.trophies.checkers.inactivity_return import InactivityReturnChecker
from wger.trophies.checkers.streak import StreakChecker
from wger.trophies.checkers.time_based import TimeBasedChecker
from wger.trophies.checkers.volume import VolumeChecker
from wger.trophies.checkers.weekend_warrior import WeekendWarriorChecker
from wger.trophies.models import (
    Trophy,
    UserStatistics,
)


class CountBasedCheckerTestCase(WgerTestCase):
    """
    Test the CountBasedChecker
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='admin')
        self.trophy = Trophy.objects.create(
            name='Beginner',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='count_based',
            checker_params={'count': 10},
        )
        self.stats, _ = UserStatistics.objects.get_or_create(user=self.user)

    def test_check_not_achieved(self):
        """Test check returns False when count not reached"""
        self.stats.total_workouts = 5
        self.stats.save()

        checker = CountBasedChecker(self.user, self.trophy, {'count': 10})
        self.assertFalse(checker.check())

    def test_check_achieved(self):
        """Test check returns True when count reached"""
        self.stats.total_workouts = 10
        self.stats.save()

        checker = CountBasedChecker(self.user, self.trophy, {'count': 10})
        self.assertTrue(checker.check())

    def test_check_exceeded(self):
        """Test check returns True when count exceeded"""
        self.stats.total_workouts = 15
        self.stats.save()

        checker = CountBasedChecker(self.user, self.trophy, {'count': 10})
        self.assertTrue(checker.check())

    def test_progress_calculation(self):
        """Test progress calculation"""
        self.stats.total_workouts = 5
        self.stats.save()

        checker = CountBasedChecker(self.user, self.trophy, {'count': 10})
        self.assertEqual(checker.get_progress(), 50.0)

    def test_progress_capped_at_100(self):
        """Test progress is capped at 100%"""
        self.stats.total_workouts = 15
        self.stats.save()

        checker = CountBasedChecker(self.user, self.trophy, {'count': 10})
        self.assertEqual(checker.get_progress(), 100.0)

    def test_get_current_value(self):
        """Test getting current workout count"""
        self.stats.total_workouts = 7
        self.stats.save()

        checker = CountBasedChecker(self.user, self.trophy, {'count': 10})
        self.assertEqual(checker.get_current_value(), 7)

    def test_get_target_value(self):
        """Test getting target workout count"""
        checker = CountBasedChecker(self.user, self.trophy, {'count': 10})
        self.assertEqual(checker.get_target_value(), 10)


class StreakCheckerTestCase(WgerTestCase):
    """
    Test the StreakChecker
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='admin')
        self.trophy = Trophy.objects.create(
            name='Unstoppable',
            trophy_type=Trophy.TYPE_SEQUENCE,
            checker_class='streak',
            checker_params={'days': 30},
        )
        self.stats, _ = UserStatistics.objects.get_or_create(user=self.user)

    def test_check_not_achieved(self):
        """Test check returns False when streak not reached"""
        self.stats.current_streak = 15
        self.stats.save()

        checker = StreakChecker(self.user, self.trophy, {'days': 30})
        self.assertFalse(checker.check())

    def test_check_achieved(self):
        """Test check returns True when streak reached"""
        self.stats.current_streak = 30
        self.stats.save()

        checker = StreakChecker(self.user, self.trophy, {'days': 30})
        self.assertTrue(checker.check())

    def test_check_exceeded(self):
        """Test check returns True when streak exceeded"""
        self.stats.current_streak = 45
        self.stats.save()

        checker = StreakChecker(self.user, self.trophy, {'days': 30})
        self.assertTrue(checker.check())

    def test_progress_calculation(self):
        """Test progress calculation"""
        self.stats.current_streak = 15
        self.stats.save()

        checker = StreakChecker(self.user, self.trophy, {'days': 30})
        self.assertEqual(checker.get_progress(), 50.0)

    def test_get_current_value(self):
        """Test getting current streak"""
        self.stats.current_streak = 20
        self.stats.save()

        checker = StreakChecker(self.user, self.trophy, {'days': 30})
        self.assertEqual(checker.get_current_value(), 20)

    def test_get_target_value(self):
        """Test getting target streak"""
        checker = StreakChecker(self.user, self.trophy, {'days': 30})
        self.assertEqual(checker.get_target_value(), 30)


class WeekendWarriorCheckerTestCase(WgerTestCase):
    """
    Test the WeekendWarriorChecker
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='admin')
        self.trophy = Trophy.objects.create(
            name='Weekend Warrior',
            trophy_type=Trophy.TYPE_SEQUENCE,
            checker_class='weekend_warrior',
            checker_params={'weekends': 4},
        )
        self.stats, _ = UserStatistics.objects.get_or_create(user=self.user)

    def test_check_not_achieved(self):
        """Test check returns False when weekend streak not reached"""
        self.stats.weekend_workout_streak = 2
        self.stats.save()

        checker = WeekendWarriorChecker(self.user, self.trophy, {'weekends': 4})
        self.assertFalse(checker.check())

    def test_check_achieved(self):
        """Test check returns True when weekend streak reached"""
        self.stats.weekend_workout_streak = 4
        self.stats.save()

        checker = WeekendWarriorChecker(self.user, self.trophy, {'weekends': 4})
        self.assertTrue(checker.check())

    def test_check_exceeded(self):
        """Test check returns True when weekend streak exceeded"""
        self.stats.weekend_workout_streak = 6
        self.stats.save()

        checker = WeekendWarriorChecker(self.user, self.trophy, {'weekends': 4})
        self.assertTrue(checker.check())

    def test_progress_calculation(self):
        """Test progress calculation"""
        self.stats.weekend_workout_streak = 2
        self.stats.save()

        checker = WeekendWarriorChecker(self.user, self.trophy, {'weekends': 4})
        self.assertEqual(checker.get_progress(), 50.0)

    def test_get_current_value(self):
        """Test getting current weekend streak"""
        self.stats.weekend_workout_streak = 3
        self.stats.save()

        checker = WeekendWarriorChecker(self.user, self.trophy, {'weekends': 4})
        self.assertEqual(checker.get_current_value(), 3)

    def test_get_target_value(self):
        """Test getting target weekend streak"""
        checker = WeekendWarriorChecker(self.user, self.trophy, {'weekends': 4})
        self.assertEqual(checker.get_target_value(), 4)


class VolumeCheckerTestCase(WgerTestCase):
    """
    Test the VolumeChecker
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='admin')
        self.trophy = Trophy.objects.create(
            name='Lifter',
            trophy_type=Trophy.TYPE_VOLUME,
            checker_class='volume',
            checker_params={'kg': 5000},
        )
        self.stats, _ = UserStatistics.objects.get_or_create(user=self.user)

    def test_check_not_achieved(self):
        """Test check returns False when volume not reached"""
        self.stats.total_weight_lifted = Decimal('2500.00')
        self.stats.save()

        checker = VolumeChecker(self.user, self.trophy, {'kg': 5000})
        self.assertFalse(checker.check())

    def test_check_achieved(self):
        """Test check returns True when volume reached"""
        self.stats.total_weight_lifted = Decimal('5000.00')
        self.stats.save()

        checker = VolumeChecker(self.user, self.trophy, {'kg': 5000})
        self.assertTrue(checker.check())

    def test_check_exceeded(self):
        """Test check returns True when volume exceeded"""
        self.stats.total_weight_lifted = Decimal('7500.00')
        self.stats.save()

        checker = VolumeChecker(self.user, self.trophy, {'kg': 5000})
        self.assertTrue(checker.check())

    def test_progress_calculation(self):
        """Test progress calculation"""
        self.stats.total_weight_lifted = Decimal('2500.00')
        self.stats.save()

        checker = VolumeChecker(self.user, self.trophy, {'kg': 5000})
        self.assertEqual(checker.get_progress(), 50.0)

    def test_progress_with_decimals(self):
        """Test progress calculation with decimal weights"""
        self.stats.total_weight_lifted = Decimal('1234.56')
        self.stats.save()

        checker = VolumeChecker(self.user, self.trophy, {'kg': 5000})
        progress = checker.get_progress()
        self.assertAlmostEqual(progress, 24.69, places=2)

    def test_get_current_value(self):
        """Test getting current weight lifted"""
        self.stats.total_weight_lifted = Decimal('3000.00')
        self.stats.save()

        checker = VolumeChecker(self.user, self.trophy, {'kg': 5000})
        self.assertEqual(checker.get_current_value(), 3000)

    def test_get_target_value(self):
        """Test getting target weight"""
        checker = VolumeChecker(self.user, self.trophy, {'kg': 5000})
        self.assertEqual(checker.get_target_value(), 5000)


class TimeBasedCheckerTestCase(WgerTestCase):
    """
    Test the TimeBasedChecker
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='admin')
        self.stats, _ = UserStatistics.objects.get_or_create(user=self.user)

    def test_early_bird_achieved(self):
        """Test Early Bird trophy (before 6:00 AM)"""
        trophy = Trophy.objects.create(
            name='Early Bird',
            trophy_type=Trophy.TYPE_TIME,
            checker_class='time_based',
            checker_params={'before': '06:00'},
        )

        self.stats.earliest_workout_time = datetime.time(5, 30)
        self.stats.save()

        checker = TimeBasedChecker(self.user, trophy, {'before': '06:00'})
        self.assertTrue(checker.check())

    def test_early_bird_not_achieved(self):
        """Test Early Bird trophy not achieved (after 6:00 AM)"""
        trophy = Trophy.objects.create(
            name='Early Bird',
            trophy_type=Trophy.TYPE_TIME,
            checker_class='time_based',
            checker_params={'before': '06:00'},
        )

        self.stats.earliest_workout_time = datetime.time(7, 0)
        self.stats.save()

        checker = TimeBasedChecker(self.user, trophy, {'before': '06:00'})
        self.assertFalse(checker.check())

    def test_night_owl_achieved(self):
        """Test Night Owl trophy (after 9:00 PM)"""
        trophy = Trophy.objects.create(
            name='Night Owl',
            trophy_type=Trophy.TYPE_TIME,
            checker_class='time_based',
            checker_params={'after': '21:00'},
        )

        self.stats.latest_workout_time = datetime.time(22, 30)
        self.stats.save()

        checker = TimeBasedChecker(self.user, trophy, {'after': '21:00'})
        self.assertTrue(checker.check())

    def test_night_owl_not_achieved(self):
        """Test Night Owl trophy not achieved (before 9:00 PM)"""
        trophy = Trophy.objects.create(
            name='Night Owl',
            trophy_type=Trophy.TYPE_TIME,
            checker_class='time_based',
            checker_params={'after': '21:00'},
        )

        self.stats.latest_workout_time = datetime.time(20, 0)
        self.stats.save()

        checker = TimeBasedChecker(self.user, trophy, {'after': '21:00'})
        self.assertFalse(checker.check())

    def test_no_workout_time_recorded(self):
        """Test when no workout time is recorded"""
        trophy = Trophy.objects.create(
            name='Early Bird',
            trophy_type=Trophy.TYPE_TIME,
            checker_class='time_based',
            checker_params={'before': '06:00'},
        )

        checker = TimeBasedChecker(self.user, trophy, {'before': '06:00'})
        self.assertFalse(checker.check())


class DateBasedCheckerTestCase(WgerTestCase):
    """
    Test the DateBasedChecker
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='admin')
        self.trophy = Trophy.objects.create(
            name='New Year, New Me',
            trophy_type=Trophy.TYPE_DATE,
            checker_class='date_based',
            checker_params={'month': 1, 'day': 1},
        )
        self.stats, _ = UserStatistics.objects.get_or_create(user=self.user)

    def test_check_achieved(self):
        """Test check returns True when worked out on Jan 1st"""
        self.stats.worked_out_jan_1 = True
        self.stats.save()

        checker = DateBasedChecker(self.user, self.trophy, {'month': 1, 'day': 1})
        self.assertTrue(checker.check())

    def test_check_not_achieved(self):
        """Test check returns False when not worked out on Jan 1st"""
        self.stats.worked_out_jan_1 = False
        self.stats.save()

        checker = DateBasedChecker(self.user, self.trophy, {'month': 1, 'day': 1})
        self.assertFalse(checker.check())

    def test_get_progress(self):
        """Test progress is either 0 or 100 for date-based trophies"""
        self.stats.worked_out_jan_1 = False
        self.stats.save()

        checker = DateBasedChecker(self.user, self.trophy, {'month': 1, 'day': 1})
        self.assertEqual(checker.get_progress(), 0.0)

        self.stats.worked_out_jan_1 = True
        self.stats.save()

        checker = DateBasedChecker(self.user, self.trophy, {'month': 1, 'day': 1})
        self.assertEqual(checker.get_progress(), 100.0)


class InactivityReturnCheckerTestCase(WgerTestCase):
    """
    Test the InactivityReturnChecker
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='admin')
        self.trophy = Trophy.objects.create(
            name='Phoenix',
            trophy_type=Trophy.TYPE_OTHER,
            checker_class='inactivity_return',
            checker_params={'inactive_days': 30},
        )
        self.stats, _ = UserStatistics.objects.get_or_create(user=self.user)

    def test_check_achieved(self):
        """Test check returns True when returned after 30+ days inactive"""
        self.stats.last_inactive_date = datetime.date.today() - datetime.timedelta(days=35)
        self.stats.last_workout_date = datetime.date.today()
        self.stats.save()

        checker = InactivityReturnChecker(self.user, self.trophy, {'inactive_days': 30})
        self.assertTrue(checker.check())

    def test_check_not_achieved_no_inactivity(self):
        """Test check returns False when no inactivity period recorded"""
        self.stats.last_inactive_date = None
        self.stats.save()

        checker = InactivityReturnChecker(self.user, self.trophy, {'inactive_days': 30})
        self.assertFalse(checker.check())

    def test_check_not_achieved_no_return(self):
        """Test check returns False when inactive but no return"""
        self.stats.last_inactive_date = datetime.date.today() - datetime.timedelta(days=35)
        self.stats.last_workout_date = None
        self.stats.save()

        checker = InactivityReturnChecker(self.user, self.trophy, {'inactive_days': 30})
        self.assertFalse(checker.check())

    def test_get_progress(self):
        """Test progress is either 0 or 100 for inactivity return"""
        self.stats.last_inactive_date = None
        self.stats.save()

        checker = InactivityReturnChecker(self.user, self.trophy, {'inactive_days': 30})
        self.assertEqual(checker.get_progress(), 0.0)

        self.stats.last_inactive_date = datetime.date.today() - datetime.timedelta(days=35)
        self.stats.last_workout_date = datetime.date.today()
        self.stats.save()

        checker = InactivityReturnChecker(self.user, self.trophy, {'inactive_days': 30})
        self.assertEqual(checker.get_progress(), 100.0)
