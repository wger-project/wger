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


class TrophyIntegrationTestCase(WgerTestCase):
    """
    Integration tests for end-to-end trophy workflows
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='admin')

        # Set recent login to avoid being skipped by should_skip_user
        from django.utils import timezone
        self.user.last_login = timezone.now()
        self.user.save()

        # Delete workout data, migration trophies, and existing data to ensure clean state
        WorkoutLog.objects.filter(user=self.user).delete()
        WorkoutSession.objects.filter(user=self.user).delete()
        Trophy.objects.all().delete()
        UserTrophy.objects.all().delete()
        UserStatistics.objects.all().delete()

        # Create the standard trophies
        self.beginner_trophy = Trophy.objects.create(
            name='Beginner',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='count_based',
            checker_params={'count': 1},
            is_active=True,
        )

        self.lifter_trophy = Trophy.objects.create(
            name='Lifter',
            trophy_type=Trophy.TYPE_VOLUME,
            checker_class='volume',
            checker_params={'kg': 5000},
            is_active=True,
            is_progressive=True,
        )

        self.unstoppable_trophy = Trophy.objects.create(
            name='Unstoppable',
            trophy_type=Trophy.TYPE_SEQUENCE,
            checker_class='streak',
            checker_params={'days': 30},
            is_active=True,
            is_progressive=True,
        )

    def test_first_workout_earns_beginner_trophy(self):
        """Test that completing first workout earns Beginner trophy"""
        # Create user statistics
        stats, _ = UserStatistics.objects.get_or_create(user=self.user, defaults={'total_workouts': 0})

        # Verify no trophies earned yet
        self.assertEqual(UserTrophy.objects.filter(user=self.user).count(), 0)

        # Simulate first workout
        stats.total_workouts = 1
        stats.save()

        # Evaluate trophies
        awarded = TrophyService.evaluate_all_trophies(self.user)

        # Should earn Beginner trophy
        self.assertEqual(len(awarded), 1)
        self.assertEqual(awarded[0].trophy, self.beginner_trophy)

    def test_lifting_5000kg_earns_lifter_trophy(self):
        """Test that lifting 5000kg total earns Lifter trophy"""
        # Create user statistics
        stats, _ = UserStatistics.objects.get_or_create(
            user=self.user,
            defaults={
                'total_workouts': 10,
                'total_weight_lifted': Decimal('4999'),
            }
        )

        # Evaluate - should not earn yet
        awarded = TrophyService.evaluate_all_trophies(self.user)
        lifter_awards = [a for a in awarded if a.trophy == self.lifter_trophy]
        self.assertEqual(len(lifter_awards), 0)

        # Lift one more kg
        stats.total_weight_lifted = Decimal('5000')
        stats.save()

        # Evaluate again
        awarded = TrophyService.evaluate_all_trophies(self.user)
        lifter_awards = [a for a in awarded if a.trophy == self.lifter_trophy]

        # Should now earn Lifter trophy
        self.assertEqual(len(lifter_awards), 1)

    def test_30_day_streak_earns_unstoppable_trophy(self):
        """Test that 30-day workout streak earns Unstoppable trophy"""
        # Create user statistics
        stats, _ = UserStatistics.objects.get_or_create(
            user=self.user,
            defaults={
                'total_workouts': 30,
                'current_streak': 29,
                'last_workout_date': datetime.date.today(),
            }
        )

        # Evaluate - should not earn yet (only 29 days)
        awarded = TrophyService.evaluate_all_trophies(self.user)
        unstoppable_awards = [a for a in awarded if a.trophy == self.unstoppable_trophy]
        self.assertEqual(len(unstoppable_awards), 0)

        # Extend streak to 30 days
        stats.current_streak = 30
        stats.save()

        # Evaluate again
        awarded = TrophyService.evaluate_all_trophies(self.user)
        unstoppable_awards = [a for a in awarded if a.trophy == self.unstoppable_trophy]

        # Should now earn Unstoppable trophy
        self.assertEqual(len(unstoppable_awards), 1)

    def test_multiple_trophies_earned_together(self):
        """Test user can earn multiple trophies at once"""
        # Create user statistics with conditions for multiple trophies
        stats, _ = UserStatistics.objects.get_or_create(
            user=self.user,
            defaults={
                'total_workouts': 1,  # Qualifies for Beginner
                'total_weight_lifted': Decimal('5000'),  # Qualifies for Lifter
                'current_streak': 30,  # Qualifies for Unstoppable
            }
        )

        # Evaluate all trophies
        awarded = TrophyService.evaluate_all_trophies(self.user)

        # Should earn all three trophies
        self.assertEqual(len(awarded), 3)

        trophy_ids = {a.trophy.id for a in awarded}
        self.assertIn(self.beginner_trophy.id, trophy_ids)
        self.assertIn(self.lifter_trophy.id, trophy_ids)
        self.assertIn(self.unstoppable_trophy.id, trophy_ids)

    def test_progressive_trophy_shows_partial_progress(self):
        """Test progressive trophies show partial progress"""
        # Create user statistics
        stats, _ = UserStatistics.objects.get_or_create(
            user=self.user,
            defaults={
                'total_weight_lifted': Decimal('2500'),  # 50% of 5000kg
            }
        )

        # Get progress for all trophies
        progress_list = TrophyService.get_all_trophy_progress(self.user)

        # Find Lifter trophy progress
        lifter_progress = next(
            (p for p in progress_list if p['trophy'].id == self.lifter_trophy.id),
            None
        )

        self.assertIsNotNone(lifter_progress)
        self.assertEqual(lifter_progress['progress'], 50.0)
        self.assertFalse(lifter_progress['is_earned'])
        self.assertEqual(lifter_progress['current_value'], 2500)
        self.assertEqual(lifter_progress['target_value'], 5000)

    def test_trophy_not_awarded_twice(self):
        """Test same trophy is not awarded twice"""
        # Create user statistics
        stats, _ = UserStatistics.objects.get_or_create(
            user=self.user,
            defaults={
                'total_workouts': 1,
            }
        )

        # Evaluate and earn Beginner trophy
        awarded1 = TrophyService.evaluate_all_trophies(self.user)
        self.assertEqual(len(awarded1), 1)

        # Do more workouts
        stats.total_workouts = 10
        stats.save()

        # Evaluate again
        awarded2 = TrophyService.evaluate_all_trophies(self.user)

        # Should not award Beginner again (already earned)
        self.assertEqual(len(awarded2), 0)
        self.assertEqual(UserTrophy.objects.filter(user=self.user, trophy=self.beginner_trophy).count(), 1)

    def test_statistics_service_updates_correctly(self):
        """Test that statistics service updates all fields correctly"""
        # Update statistics (with no workout data in test DB)
        stats = UserStatisticsService.update_statistics(self.user)

        # Verify stats were created and initialized
        self.assertIsNotNone(stats)
        self.assertEqual(stats.total_workouts, 0)
        self.assertEqual(stats.total_weight_lifted, Decimal('0'))
        self.assertEqual(stats.current_streak, 0)
        self.assertEqual(stats.longest_streak, 0)

    def test_hidden_trophy_not_visible_until_earned(self):
        """Test hidden trophies are not visible until earned"""
        # Create a hidden trophy
        hidden_trophy = Trophy.objects.create(
            name='Secret Achievement',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='count_based',
            checker_params={'count': 100},
            is_active=True,
            is_hidden=True,
        )

        # Get progress without including hidden
        progress_list = TrophyService.get_all_trophy_progress(self.user, include_hidden=False)

        # Hidden trophy should not be in list
        trophy_ids = [p['trophy'].id for p in progress_list]
        self.assertNotIn(hidden_trophy.id, trophy_ids)

        # Award the hidden trophy
        UserTrophy.objects.create(user=self.user, trophy=hidden_trophy)

        # Get progress again
        progress_list = TrophyService.get_all_trophy_progress(self.user, include_hidden=False)

        # Hidden trophy should now be visible
        trophy_ids = [p['trophy'].id for p in progress_list]
        self.assertIn(hidden_trophy.id, trophy_ids)

    def test_inactive_trophy_not_evaluated(self):
        """Test inactive trophies are not evaluated"""
        # Create user statistics that would qualify for trophy
        stats, _ = UserStatistics.objects.get_or_create(
            user=self.user,
            defaults={
                'total_workouts': 1,
            }
        )

        # Deactivate the Beginner trophy
        self.beginner_trophy.is_active = False
        self.beginner_trophy.save()

        # Evaluate trophies
        awarded = TrophyService.evaluate_all_trophies(self.user)

        # Should not earn the inactive trophy
        beginner_awards = [a for a in awarded if a.trophy == self.beginner_trophy]
        self.assertEqual(len(beginner_awards), 0)

    def test_reevaluate_trophies_for_multiple_users(self):
        """Test re-evaluating trophies for multiple users"""
        user2 = User.objects.get(username='test')

        # Create statistics for both users
        UserStatistics.objects.get_or_create(user=self.user, defaults={'total_workouts': 1})
        UserStatistics.objects.get_or_create(user=user2, defaults={'total_workouts': 1})

        # Set recent login for both
        from django.utils import timezone
        self.user.last_login = timezone.now()
        self.user.save()
        user2.last_login = timezone.now()
        user2.save()

        # Re-evaluate all trophies
        results = TrophyService.reevaluate_trophies()

        # Both users should be checked and earn Beginner trophy
        self.assertEqual(results['users_checked'], 2)
        self.assertEqual(results['trophies_awarded'], 2)

        # Verify both users have the trophy
        self.assertTrue(UserTrophy.objects.filter(user=self.user, trophy=self.beginner_trophy).exists())
        self.assertTrue(UserTrophy.objects.filter(user=user2, trophy=self.beginner_trophy).exists())

    def test_complete_user_journey(self):
        """Test complete user journey: signup -> workouts -> earn trophies"""
        # Day 1: New user, first workout
        stats, _ = UserStatistics.objects.get_or_create(
            user=self.user,
            defaults={
                'total_workouts': 1,
                'total_weight_lifted': Decimal('100'),
                'current_streak': 1,
                'last_workout_date': datetime.date.today(),
            }
        )

        awarded = TrophyService.evaluate_all_trophies(self.user)
        # Should earn Beginner
        self.assertEqual(len(awarded), 1)
        self.assertEqual(awarded[0].trophy.name, 'Beginner')

        # Week 1-4: Consistent workouts, building volume
        stats.total_workouts = 20
        stats.total_weight_lifted = Decimal('2500')
        stats.current_streak = 20
        stats.save()

        # Check progress
        progress_list = TrophyService.get_all_trophy_progress(self.user)
        lifter_progress = next(p for p in progress_list if p['trophy'].id == self.lifter_trophy.id)
        self.assertEqual(lifter_progress['progress'], 50.0)  # Halfway to Lifter

        # Month 2: Reach 5000kg
        stats.total_weight_lifted = Decimal('5000')
        stats.save()

        awarded = TrophyService.evaluate_all_trophies(self.user)
        # Should earn Lifter (Beginner already earned)
        lifter_awards = [a for a in awarded if a.trophy.name == 'Lifter']
        self.assertEqual(len(lifter_awards), 1)

        # Month 2: Complete 30-day streak
        stats.current_streak = 30
        stats.save()

        awarded = TrophyService.evaluate_all_trophies(self.user)
        # Should earn Unstoppable
        unstoppable_awards = [a for a in awarded if a.trophy.name == 'Unstoppable']
        self.assertEqual(len(unstoppable_awards), 1)

        # Verify final trophy count
        total_trophies = UserTrophy.objects.filter(user=self.user).count()
        self.assertEqual(total_trophies, 3)  # Beginner, Lifter, Unstoppable
