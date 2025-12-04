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
from decimal import Decimal

# Django
from django.contrib.auth.models import User
from django.db import IntegrityError

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.trophies.models import (
    Trophy,
    UserStatistics,
    UserTrophy,
)


class TrophyModelTestCase(WgerTestCase):
    """
    Test the Trophy model
    """

    def test_create_trophy(self):
        """Test creating a trophy"""
        trophy = Trophy.objects.create(
            name='Test Trophy',
            description='Test Description',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='count_based',
            checker_params={'count': 10},
        )

        self.assertEqual(trophy.name, 'Test Trophy')
        self.assertEqual(trophy.description, 'Test Description')
        self.assertEqual(trophy.trophy_type, Trophy.TYPE_COUNT)
        self.assertEqual(trophy.checker_class, 'count_based')
        self.assertEqual(trophy.checker_params, {'count': 10})

    def test_trophy_defaults(self):
        """Test trophy default values"""
        trophy = Trophy.objects.create(
            name='Test Trophy',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='count_based',
        )

        self.assertTrue(trophy.is_active)
        self.assertFalse(trophy.is_hidden)
        self.assertFalse(trophy.is_progressive)
        self.assertEqual(trophy.order, 0)
        self.assertEqual(trophy.description, '')

    def test_trophy_str(self):
        """Test trophy string representation"""
        trophy = Trophy.objects.create(
            name='Amazing Trophy',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='count_based',
        )

        self.assertEqual(str(trophy), 'Amazing Trophy')

    def test_trophy_ordering(self):
        """Test trophies are ordered by order field then name"""
        # Delete any existing trophies from migration
        Trophy.objects.all().delete()

        trophy1 = Trophy.objects.create(
            name='B Trophy',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='count_based',
            order=2,
        )
        trophy2 = Trophy.objects.create(
            name='A Trophy',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='count_based',
            order=1,
        )
        trophy3 = Trophy.objects.create(
            name='C Trophy',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='count_based',
            order=1,
        )

        trophies = list(Trophy.objects.all())
        # Should be ordered by order (1, 1, 2), then by name (A, C, B)
        self.assertEqual(trophies[0], trophy2)  # A Trophy (order 1)
        self.assertEqual(trophies[1], trophy3)  # C Trophy (order 1)
        self.assertEqual(trophies[2], trophy1)  # B Trophy (order 2)

    def test_trophy_types(self):
        """Test all trophy types are available"""
        types = [choice[0] for choice in Trophy.TROPHY_TYPES]
        self.assertIn(Trophy.TYPE_TIME, types)
        self.assertIn(Trophy.TYPE_VOLUME, types)
        self.assertIn(Trophy.TYPE_COUNT, types)
        self.assertIn(Trophy.TYPE_SEQUENCE, types)
        self.assertIn(Trophy.TYPE_DATE, types)
        self.assertIn(Trophy.TYPE_OTHER, types)

    def test_trophy_uuid_generated(self):
        """Test UUID is automatically generated"""
        trophy = Trophy.objects.create(
            name='Test Trophy',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='count_based',
        )

        self.assertIsNotNone(trophy.uuid)
        self.assertEqual(len(str(trophy.uuid)), 36)  # UUID4 string length

    def test_trophy_update(self):
        """Test updating a trophy"""
        trophy = Trophy.objects.create(
            name='Original Name',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='count_based',
        )

        trophy.name = 'Updated Name'
        trophy.is_active = False
        trophy.save()

        updated = Trophy.objects.get(pk=trophy.pk)
        self.assertEqual(updated.name, 'Updated Name')
        self.assertFalse(updated.is_active)

    def test_trophy_delete(self):
        """Test deleting a trophy"""
        trophy = Trophy.objects.create(
            name='Test Trophy',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='count_based',
        )
        trophy_id = trophy.pk

        trophy.delete()

        self.assertEqual(Trophy.objects.filter(pk=trophy_id).count(), 0)


class UserTrophyModelTestCase(WgerTestCase):
    """
    Test the UserTrophy model
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='admin')
        self.trophy = Trophy.objects.create(
            name='Test Trophy',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='count_based',
        )

    def test_award_trophy(self):
        """Test awarding a trophy to a user"""
        user_trophy = UserTrophy.objects.create(
            user=self.user,
            trophy=self.trophy,
        )

        self.assertEqual(user_trophy.user, self.user)
        self.assertEqual(user_trophy.trophy, self.trophy)
        self.assertIsNotNone(user_trophy.earned_at)

    def test_unique_constraint(self):
        """Test a user can't earn the same trophy twice"""
        UserTrophy.objects.create(
            user=self.user,
            trophy=self.trophy,
        )

        # Try to award the same trophy again
        with self.assertRaises(IntegrityError):
            UserTrophy.objects.create(
                user=self.user,
                trophy=self.trophy,
            )

    def test_progress_field(self):
        """Test progress field for progressive trophies"""
        user_trophy = UserTrophy.objects.create(
            user=self.user,
            trophy=self.trophy,
            progress=75.5,
        )

        self.assertEqual(user_trophy.progress, 75.5)

    def test_is_notified_default(self):
        """Test is_notified defaults to False"""
        user_trophy = UserTrophy.objects.create(
            user=self.user,
            trophy=self.trophy,
        )

        self.assertFalse(user_trophy.is_notified)

    def test_multiple_users_same_trophy(self):
        """Test multiple users can earn the same trophy"""
        user2 = User.objects.get(username='test')

        user_trophy1 = UserTrophy.objects.create(
            user=self.user,
            trophy=self.trophy,
        )
        user_trophy2 = UserTrophy.objects.create(
            user=user2,
            trophy=self.trophy,
        )

        self.assertNotEqual(user_trophy1, user_trophy2)
        self.assertEqual(UserTrophy.objects.filter(trophy=self.trophy).count(), 2)

    def test_user_multiple_trophies(self):
        """Test a user can earn multiple different trophies"""
        trophy2 = Trophy.objects.create(
            name='Another Trophy',
            trophy_type=Trophy.TYPE_VOLUME,
            checker_class='volume',
        )

        user_trophy1 = UserTrophy.objects.create(
            user=self.user,
            trophy=self.trophy,
        )
        user_trophy2 = UserTrophy.objects.create(
            user=self.user,
            trophy=trophy2,
        )

        self.assertEqual(UserTrophy.objects.filter(user=self.user).count(), 2)

    def test_cascade_delete_trophy(self):
        """Test deleting a trophy deletes associated UserTrophy records"""
        UserTrophy.objects.create(
            user=self.user,
            trophy=self.trophy,
        )

        self.assertEqual(UserTrophy.objects.filter(trophy=self.trophy).count(), 1)

        self.trophy.delete()

        self.assertEqual(UserTrophy.objects.filter(user=self.user).count(), 0)

    def test_cascade_delete_user(self):
        """Test deleting a user deletes associated UserTrophy records"""
        test_user = User.objects.create_user(username='temp_user', password='temp')
        UserTrophy.objects.create(
            user=test_user,
            trophy=self.trophy,
        )

        self.assertEqual(UserTrophy.objects.filter(user=test_user).count(), 1)

        test_user.delete()

        self.assertEqual(UserTrophy.objects.filter(trophy=self.trophy).count(), 0)


class UserStatisticsModelTestCase(WgerTestCase):
    """
    Test the UserStatistics model
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='admin')

    def test_create_statistics(self):
        """Test creating user statistics"""
        stats, _ = UserStatistics.objects.get_or_create(user=self.user)

        self.assertEqual(stats.user, self.user)
        self.assertIsNotNone(stats.last_updated)

    def test_default_values(self):
        """Test default values are set correctly"""
        # Delete any existing statistics and create fresh ones
        UserStatistics.objects.filter(user=self.user).delete()
        stats, _ = UserStatistics.objects.get_or_create(user=self.user)

        self.assertEqual(stats.total_weight_lifted, Decimal('0'))
        self.assertEqual(stats.total_workouts, 0)
        self.assertEqual(stats.current_streak, 0)
        self.assertEqual(stats.longest_streak, 0)
        self.assertEqual(stats.weekend_workout_streak, 0)
        self.assertIsNone(stats.last_workout_date)
        self.assertIsNone(stats.earliest_workout_time)
        self.assertIsNone(stats.latest_workout_time)
        self.assertIsNone(stats.last_complete_weekend_date)
        self.assertIsNone(stats.last_inactive_date)
        self.assertFalse(stats.worked_out_jan_1)

    def test_one_to_one_constraint(self):
        """Test one user can only have one statistics record"""
        # Delete any existing statistics first
        UserStatistics.objects.filter(user=self.user).delete()

        UserStatistics.objects.create(user=self.user)

        # Try to create another statistics record for the same user
        with self.assertRaises(IntegrityError):
            UserStatistics.objects.create(user=self.user)

    def test_update_statistics(self):
        """Test updating statistics"""
        stats, _ = UserStatistics.objects.get_or_create(user=self.user)

        stats.total_weight_lifted = Decimal('5000.50')
        stats.total_workouts = 25
        stats.current_streak = 10
        stats.save()

        updated = UserStatistics.objects.get(user=self.user)
        self.assertEqual(updated.total_weight_lifted, Decimal('5000.50'))
        self.assertEqual(updated.total_workouts, 25)
        self.assertEqual(updated.current_streak, 10)

    def test_cascade_delete_user(self):
        """Test deleting a user deletes their statistics"""
        test_user = User.objects.create_user(username='temp_user', password='temp')
        UserStatistics.objects.get_or_create(user=test_user)

        self.assertEqual(UserStatistics.objects.filter(user=test_user).count(), 1)

        user_id = test_user.id
        test_user.delete()

        # Verify statistics for this user ID no longer exist
        self.assertEqual(UserStatistics.objects.filter(user_id=user_id).count(), 0)

    def test_str_representation(self):
        """Test string representation of statistics"""
        stats, _ = UserStatistics.objects.get_or_create(user=self.user)

        str_repr = str(stats)
        self.assertIn(self.user.username, str_repr)
