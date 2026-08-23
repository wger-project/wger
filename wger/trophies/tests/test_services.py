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
from unittest.mock import patch

# Django
from django.contrib.auth.models import User
from django.utils import timezone

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import (
    WorkoutLog,
    WorkoutSession,
)
from wger.trophies.models import (
    Trophy,
    UserStatistics,
    UserTrophy,
)
from wger.trophies.services.statistics import UserStatisticsService
from wger.trophies.services.trophy import TrophyService


class UserStatisticsServiceTestCase(WgerTestCase):
    """
    Test the UserStatisticsService
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='admin')
        # Delete workout data and statistics to ensure clean state
        WorkoutLog.objects.filter(user=self.user).delete()
        WorkoutSession.objects.filter(user=self.user).delete()
        UserStatistics.objects.filter(user=self.user).delete()

    def test_get_or_create_creates_new(self):
        """Test get_or_create creates statistics if they don't exist"""
        self.assertEqual(UserStatistics.objects.filter(user=self.user).count(), 0)

        stats = UserStatisticsService.get_or_create_statistics(self.user)

        self.assertIsNotNone(stats)
        self.assertEqual(stats.user, self.user)
        self.assertEqual(UserStatistics.objects.filter(user=self.user).count(), 1)

    def test_get_or_create_returns_existing(self):
        """Test get_or_create returns existing statistics"""
        existing, _ = UserStatistics.objects.get_or_create(
            user=self.user, defaults={'total_workouts': 5}
        )

        stats = UserStatisticsService.get_or_create_statistics(self.user)

        self.assertEqual(stats.pk, existing.pk)
        self.assertEqual(stats.total_workouts, 5)

    def make_session(self, start, end):
        return WorkoutSession.objects.create(
            user=self.user,
            datetime_start=start,
            datetime_end=end,
        )

    def test_workout_times_stay_unset_without_a_reported_zone(self):
        """No time trophies from a guessed timezone: the times stay null"""

        self.make_session(
            datetime.datetime(2024, 6, 19, 1, 30, tzinfo=datetime.timezone.utc),
            datetime.datetime(2024, 6, 19, 2, 30, tzinfo=datetime.timezone.utc),
        )

        stats = UserStatisticsService.update_statistics(self.user)

        self.assertIsNone(stats.earliest_workout_time)
        self.assertIsNone(stats.latest_workout_time)

    def test_increment_skips_the_times_without_a_zone(self):
        """The signal path must not set the times from a guess either"""

        self.make_session(
            datetime.datetime(2024, 6, 19, 1, 30, tzinfo=datetime.timezone.utc),
            datetime.datetime(2024, 6, 19, 2, 30, tzinfo=datetime.timezone.utc),
        )

        stats = UserStatistics.objects.get(user=self.user)
        self.assertIsNone(stats.earliest_workout_time)
        self.assertIsNone(stats.latest_workout_time)

    def test_workout_times_follow_the_reported_zone(self):
        """01:30 UTC is an evening workout for a user in Denver, not an early one"""

        profile = self.user.userprofile
        profile.time_zone = 'America/Denver'
        profile.save()

        self.make_session(
            datetime.datetime(2024, 6, 19, 1, 30, tzinfo=datetime.timezone.utc),
            datetime.datetime(2024, 6, 19, 2, 30, tzinfo=datetime.timezone.utc),
        )

        stats = UserStatisticsService.update_statistics(self.user)

        self.assertEqual(stats.earliest_workout_time, datetime.time(19, 30))
        self.assertEqual(stats.latest_workout_time, datetime.time(19, 30))

    def test_a_late_zone_report_backfills_the_times(self):
        """The first recalculation after the zone arrives fills in the history"""

        self.make_session(
            datetime.datetime(2024, 6, 19, 1, 30, tzinfo=datetime.timezone.utc),
            datetime.datetime(2024, 6, 19, 2, 30, tzinfo=datetime.timezone.utc),
        )
        stats = UserStatisticsService.update_statistics(self.user)
        self.assertIsNone(stats.earliest_workout_time)

        profile = self.user.userprofile
        profile.time_zone = 'America/Denver'
        profile.save()

        stats = UserStatisticsService.update_statistics(self.user)

        self.assertEqual(stats.earliest_workout_time, datetime.time(19, 30))

    def test_update_statistics_creates_if_missing(self):
        """Test update_statistics creates statistics if missing"""
        self.assertEqual(UserStatistics.objects.filter(user=self.user).count(), 0)

        stats = UserStatisticsService.update_statistics(self.user)

        self.assertIsNotNone(stats)
        self.assertEqual(UserStatistics.objects.filter(user=self.user).count(), 1)

    def test_update_statistics_default_values(self):
        """Test update_statistics with no workout data"""
        stats = UserStatisticsService.update_statistics(self.user)

        self.assertEqual(stats.total_workouts, 0)
        self.assertEqual(stats.total_weight_lifted, Decimal('0'))
        self.assertEqual(stats.current_streak, 0)
        self.assertEqual(stats.longest_streak, 0)

    def test_handle_workout_deletion(self):
        """Test handle_workout_deletion triggers full recalculation"""
        UserStatistics.objects.get_or_create(
            user=self.user,
            defaults={
                'total_workouts': 10,
                'total_weight_lifted': Decimal('5000'),
            },
        )

        stats = UserStatisticsService.handle_workout_deletion(self.user)

        # Should recalculate from actual workout data (none in test db)
        self.assertEqual(stats.total_workouts, 0)
        self.assertEqual(stats.total_weight_lifted, Decimal('0'))


class StatisticsTimezoneTestCase(WgerTestCase):
    """
    Test that the day-based statistics follow the zone of the user they belong to
    """

    def setUp(self):
        super().setUp()
        # member1 carries time_zone Pacific/Auckland in the fixtures
        self.member = User.objects.get(username='member1')
        WorkoutLog.objects.filter(user=self.member).delete()
        WorkoutSession.objects.filter(user=self.member).delete()
        UserStatistics.objects.filter(user=self.member).delete()

    def make_session(self, start, end=None):
        return WorkoutSession.objects.create(
            user=self.member,
            datetime_start=start,
            datetime_end=end,
        )

    @staticmethod
    def utc(*args):
        return datetime.datetime(*args, tzinfo=datetime.timezone.utc)

    def test_streak_days_split_in_the_users_zone(self):
        """Two sessions on one server day are two consecutive Auckland days"""

        # 23:00 and 01:00 on the Auckland clock, around midnight
        self.make_session(self.utc(2024, 6, 19, 11, 0))
        self.make_session(self.utc(2024, 6, 19, 13, 0))

        stats = UserStatisticsService.update_statistics(self.member)

        self.assertEqual(stats.longest_streak, 2)
        self.assertEqual(stats.last_workout_date, datetime.date(2024, 6, 20))

    def test_a_zone_change_moves_the_days(self):
        """A recalculation reads the whole history in the newly reported zone"""

        # 02:00 in Auckland on Jun 20, 08:00 in Denver on Jun 19
        self.make_session(self.utc(2024, 6, 19, 14, 0))

        stats = UserStatisticsService.update_statistics(self.member)
        self.assertEqual(stats.last_workout_date, datetime.date(2024, 6, 20))

        profile = self.member.userprofile
        profile.time_zone = 'America/Denver'
        profile.save()

        stats = UserStatisticsService.update_statistics(self.member)
        self.assertEqual(stats.last_workout_date, datetime.date(2024, 6, 19))

    def test_the_workout_time_follows_the_local_clock_across_dst(self):
        """01:30 UTC on the spring-forward day is 03:30 in Berlin, not 02:30"""

        profile = self.member.userprofile
        profile.time_zone = 'Europe/Berlin'
        profile.save()

        self.make_session(
            self.utc(2024, 3, 31, 1, 30),
            self.utc(2024, 3, 31, 2, 30),
        )

        stats = UserStatisticsService.update_statistics(self.member)

        self.assertEqual(stats.earliest_workout_time, datetime.time(3, 30))


class TrophyServiceTestCase(WgerTestCase):
    """
    Test the TrophyService
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='admin')

        # Set recent login to avoid being skipped by should_skip_user
        self.user.last_login = timezone.now()
        self.user.save()

        # Delete workout data, migration trophies, and existing data to ensure clean state
        WorkoutLog.objects.filter(user=self.user).delete()
        WorkoutSession.objects.filter(user=self.user).delete()
        Trophy.objects.all().delete()
        UserTrophy.objects.all().delete()
        UserStatistics.objects.filter(user=self.user).delete()

        self.trophy = Trophy.objects.create(
            name='Test Trophy',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='workout_count_based',
            checker_params={'count': 1},
            is_active=True,
        )
        # Create statistics for the user
        self.stats, _ = UserStatistics.objects.get_or_create(
            user=self.user,
            defaults={'total_workouts': 0},
        )

    def test_award_trophy(self):
        """Test awarding a trophy to a user"""
        user_trophy = TrophyService.award_trophy(self.user, self.trophy)

        self.assertIsNotNone(user_trophy)
        self.assertEqual(user_trophy.user, self.user)
        self.assertEqual(user_trophy.trophy, self.trophy)
        self.assertEqual(user_trophy.progress, 100.0)

    def test_award_trophy_idempotent(self):
        """Test awarding same trophy twice doesn't create duplicates"""
        user_trophy1 = TrophyService.award_trophy(self.user, self.trophy)
        user_trophy2 = TrophyService.award_trophy(self.user, self.trophy)

        self.assertEqual(user_trophy1.pk, user_trophy2.pk)
        self.assertEqual(UserTrophy.objects.filter(user=self.user, trophy=self.trophy).count(), 1)

    def test_evaluate_trophy_earned(self):
        """Test evaluating a trophy that should be earned"""
        # Set stats so trophy is earned
        self.stats.total_workouts = 1
        self.stats.save()

        user_trophy = TrophyService.evaluate_trophy(self.user, self.trophy)

        self.assertIsNotNone(user_trophy)
        self.assertEqual(user_trophy.trophy, self.trophy)

    def test_evaluate_trophy_not_earned(self):
        """Test evaluating a trophy that should not be earned"""
        # Stats show 0 workouts, trophy requires 1
        user_trophy = TrophyService.evaluate_trophy(self.user, self.trophy)

        self.assertIsNone(user_trophy)

    def test_evaluate_trophy_already_earned(self):
        """Test evaluating a trophy that's already been earned"""
        # Award the trophy first
        TrophyService.award_trophy(self.user, self.trophy)

        # Try to evaluate again
        user_trophy = TrophyService.evaluate_trophy(self.user, self.trophy)

        # Should return None (already earned)
        self.assertIsNone(user_trophy)

    def test_evaluate_trophy_inactive(self):
        """Test evaluating an inactive trophy"""
        self.trophy.is_active = False
        self.trophy.save()

        self.stats.total_workouts = 1
        self.stats.save()

        user_trophy = TrophyService.evaluate_trophy(self.user, self.trophy)

        # Inactive trophies should not be awarded
        self.assertIsNone(user_trophy)

    def test_evaluate_all_trophies(self):
        """Test evaluating all trophies for a user"""
        # Create multiple trophies
        Trophy.objects.create(
            name='Trophy 2',
            trophy_type=Trophy.TYPE_SEQUENCE,
            checker_class='streak',
            checker_params={'days': 5},
            is_active=True,
        )

        # Set stats so first trophy is earned
        self.stats.total_workouts = 1
        self.stats.current_streak = 0  # Second trophy not earned
        self.stats.save()

        awarded = TrophyService.evaluate_all_trophies(self.user)

        # Should award only the first trophy
        self.assertEqual(len(awarded), 1)
        self.assertEqual(awarded[0].trophy, self.trophy)

    def test_get_user_trophies(self):
        """Test getting all earned trophies for a user"""
        # Award some trophies
        TrophyService.award_trophy(self.user, self.trophy)

        trophy2 = Trophy.objects.create(
            name='Trophy 2',
            trophy_type=Trophy.TYPE_VOLUME,
            checker_class='volume',
            checker_params={'kg': 1000},
        )
        TrophyService.award_trophy(self.user, trophy2)

        trophies = TrophyService.get_user_trophies(self.user)

        self.assertEqual(len(trophies), 2)

    def test_get_all_trophy_progress(self):
        """Test getting progress for all trophies"""
        # Create a progressive trophy
        progressive_trophy = Trophy.objects.create(
            name='Progressive',
            trophy_type=Trophy.TYPE_VOLUME,
            checker_class='volume',
            checker_params={'kg': 5000},
            is_progressive=True,
            is_active=True,
        )

        # Set some progress
        self.stats.total_weight_lifted = Decimal('2500')
        self.stats.save()

        progress_list = TrophyService.get_all_trophy_progress(self.user)

        # Should include both trophies
        self.assertEqual(len(progress_list), 2)

        # Find the progressive trophy in the list
        prog_trophy_data = next(
            (p for p in progress_list if p['trophy'].id == progressive_trophy.id), None
        )
        self.assertIsNotNone(prog_trophy_data)
        self.assertEqual(prog_trophy_data['progress'], 50.0)

    def test_get_all_trophy_progress_hidden_not_earned(self):
        """Test hidden trophies are excluded unless earned"""
        hidden_trophy = Trophy.objects.create(
            name='Hidden',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='workout_count_based',
            checker_params={'count': 10},
            is_hidden=True,
            is_active=True,
        )

        progress_list = TrophyService.get_all_trophy_progress(self.user, include_hidden=False)

        # Hidden trophy should not be in the list
        hidden_in_list = any(p['trophy'].id == hidden_trophy.id for p in progress_list)
        self.assertFalse(hidden_in_list)

    def test_get_all_trophy_progress_hidden_earned(self):
        """Test hidden trophies are included once earned"""
        hidden_trophy = Trophy.objects.create(
            name='Hidden',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='workout_count_based',
            checker_params={'count': 1},
            is_hidden=True,
            is_active=True,
        )

        # Award the hidden trophy
        TrophyService.award_trophy(self.user, hidden_trophy)

        progress_list = TrophyService.get_all_trophy_progress(self.user, include_hidden=False)

        # Hidden trophy should now be in the list
        hidden_in_list = any(p['trophy'].id == hidden_trophy.id for p in progress_list)
        self.assertTrue(hidden_in_list)

    def test_award_pr_trophy_multiple_times(self):
        """PR trophies can be awarded multiple times via TrophyService"""
        pr_trophy, _ = Trophy.objects.get_or_create(
            name='Personal Record',
            defaults={'is_repeatable': True, 'is_active': True},
        )

        ut1 = TrophyService.award_trophy(
            self.user,
            pr_trophy,
            progress=100.0,
            context_data={'log_id': '0194c3f0-0000-7000-8000-000000000001'},
        )
        ut2 = TrophyService.award_trophy(
            self.user,
            pr_trophy,
            progress=100.0,
            context_data={'log_id': '0194c3f0-0000-7000-8000-000000000002'},
        )

        self.assertEqual(UserTrophy.objects.filter(user=self.user, trophy=pr_trophy).count(), 2)
        self.assertNotEqual(ut1, ut2)

    def test_should_skip_user_inactive(self):
        """Test skipping inactive users"""
        # Set user's last login to over 30 days ago
        self.user.last_login = timezone.now() - timezone.timedelta(days=35)
        self.user.save()

        should_skip = TrophyService.should_skip_user(self.user)

        self.assertTrue(should_skip)

    def test_should_skip_user_active(self):
        """Test not skipping active users"""
        # Set user's last login to recent
        self.user.last_login = timezone.now() - timezone.timedelta(days=5)
        self.user.save()

        should_skip = TrophyService.should_skip_user(self.user)

        self.assertFalse(should_skip)

    @patch('wger.trophies.services.trophy.TROPHIES_ENABLED', False)
    def test_should_skip_user_trophies_disabled(self):
        """Test skipping when trophies are globally disabled"""
        self.user.last_login = timezone.now()
        self.user.save()

        should_skip = TrophyService.should_skip_user(self.user)

        self.assertTrue(should_skip)

    def test_reevaluate_trophies(self):
        """Test re-evaluating trophies for all users"""
        # Set recent login for self.user
        self.user.last_login = timezone.now()
        self.user.save()

        # Create a second user
        user2 = User.objects.get(username='test')
        user2.last_login = timezone.now()
        user2.save()

        # Create stats for both users
        UserStatistics.objects.get_or_create(user=user2, defaults={'total_workouts': 1})
        self.stats.total_workouts = 1
        self.stats.save()

        # Re-evaluate all trophies
        results = TrophyService.reevaluate_trophies()

        # Both users should be checked
        self.assertEqual(results['users_checked'], 2)
        # Both should earn the trophy (count=1, both have 1 workout)
        self.assertEqual(results['trophies_awarded'], 2)

    def test_reevaluate_specific_trophy(self):
        """Test re-evaluating a specific trophy"""
        # Create another trophy
        trophy2 = Trophy.objects.create(
            name='Trophy 2',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='workout_count_based',
            checker_params={'count': 5},
            is_active=True,
        )

        self.user.last_login = timezone.now()
        self.user.save()
        self.stats.total_workouts = 1
        self.stats.save()

        # Re-evaluate only trophy2
        results = TrophyService.reevaluate_trophies(trophy_ids=[trophy2.id])

        # Trophy2 requires 5 workouts, user has 1, shouldn't be awarded
        self.assertEqual(results['trophies_awarded'], 0)

    def test_reevaluate_specific_users(self):
        """Test re-evaluating trophies for specific users"""
        # Set recent login for self.user
        self.user.last_login = timezone.now()
        self.user.save()

        user2 = User.objects.get(username='test')
        user2.last_login = timezone.now()
        user2.save()

        UserStatistics.objects.get_or_create(user=user2, defaults={'total_workouts': 0})
        self.stats.total_workouts = 1
        self.stats.save()

        # Re-evaluate only for self.user
        results = TrophyService.reevaluate_trophies(user_ids=[self.user.id])

        # Only one user checked
        self.assertEqual(results['users_checked'], 1)
        # That user should earn the trophy
        self.assertEqual(results['trophies_awarded'], 1)
