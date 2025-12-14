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
from django.urls import reverse

# Third Party
from rest_framework import status

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


class TrophyAPITestCase(WgerTestCase):
    """
    Test the Trophy API endpoints
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='admin')
        self.user_login()

        # Create some test trophies
        self.trophy1 = Trophy.objects.create(
            name='Active Trophy 1',
            description='Test description',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='count_based',
            checker_params={'count': 1},
            is_active=True,
            is_hidden=False,
            order=1,
        )
        self.trophy2 = Trophy.objects.create(
            name='Active Trophy 2',
            description='Another trophy',
            trophy_type=Trophy.TYPE_VOLUME,
            checker_class='volume',
            checker_params={'kg': 5000},
            is_active=True,
            is_progressive=True,
            order=2,
        )
        self.inactive_trophy = Trophy.objects.create(
            name='Inactive Trophy',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='count_based',
            checker_params={'count': 10},
            is_active=False,
        )

    def test_list_trophies_authenticated(self):
        """Test listing trophies as authenticated user"""
        response = self.client.get(reverse('trophy-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('results', data)

    def test_list_trophies_unauthenticated(self):
        """Test listing trophies allows unauthenticated access for non-hidden trophies"""
        self.client.logout()
        response = self.client.get(reverse('trophy-list'))

        # Anonymous users can see non-hidden trophies
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_only_active_trophies(self):
        """Test only active trophies are returned"""
        response = self.client.get(reverse('trophy-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        trophy_ids = [t['id'] for t in data['results']]
        self.assertIn(self.trophy1.id, trophy_ids)
        self.assertIn(self.trophy2.id, trophy_ids)
        self.assertNotIn(self.inactive_trophy.id, trophy_ids)

    def test_trophy_detail(self):
        """Test getting trophy detail"""
        response = self.client.get(reverse('trophy-detail', kwargs={'pk': self.trophy1.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data['id'], self.trophy1.id)
        self.assertEqual(data['name'], 'Active Trophy 1')
        self.assertEqual(data['description'], 'Test description')
        self.assertEqual(data['trophy_type'], Trophy.TYPE_COUNT)
        self.assertFalse(data['is_progressive'])

    def test_trophy_serialization_fields(self):
        """Test trophy serialization includes all required fields"""
        response = self.client.get(reverse('trophy-detail', kwargs={'pk': self.trophy1.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Check all expected fields are present
        expected_fields = ['id', 'name', 'description', 'trophy_type', 'is_hidden', 'is_progressive']
        for field in expected_fields:
            self.assertIn(field, data)

    def test_trophy_ordering(self):
        """Test trophies are ordered correctly"""
        # Delete migration trophies and keep only test trophies
        Trophy.objects.exclude(
            id__in=[self.trophy1.id, self.trophy2.id, self.inactive_trophy.id]
        ).delete()

        response = self.client.get(reverse('trophy-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        trophy_names = [t['name'] for t in data['results']]
        # Should be ordered by order field then name
        self.assertEqual(trophy_names[0], 'Active Trophy 1')  # order=1
        self.assertEqual(trophy_names[1], 'Active Trophy 2')  # order=2

    def test_trophy_read_only(self):
        """Test trophies endpoint is read-only"""
        # Try to create a trophy via API
        response = self.client.post(
            reverse('trophy-list'),
            data={
                'name': 'New Trophy',
                'trophy_type': Trophy.TYPE_COUNT,
                'checker_class': 'count_based',
            },
        )

        # Should not be allowed
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED])


class UserTrophyAPITestCase(WgerTestCase):
    """
    Test the UserTrophy API endpoints
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='admin')
        self.other_user = User.objects.get(username='test')
        self.user_login()

        # Delete workout data, migration trophies, and existing data to ensure clean state
        WorkoutLog.objects.filter(user=self.user).delete()
        WorkoutSession.objects.filter(user=self.user).delete()
        Trophy.objects.all().delete()
        UserTrophy.objects.all().delete()
        UserStatistics.objects.filter(user=self.user).delete()

        # Create trophies
        self.trophy1 = Trophy.objects.create(
            name='Trophy 1',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='count_based',
            checker_params={'count': 1},
            is_active=True,
        )
        self.trophy2 = Trophy.objects.create(
            name='Trophy 2',
            trophy_type=Trophy.TYPE_VOLUME,
            checker_class='volume',
            checker_params={'kg': 5000},
            is_active=True,
            is_progressive=True,
        )
        self.hidden_trophy = Trophy.objects.create(
            name='Hidden Trophy',
            trophy_type=Trophy.TYPE_COUNT,
            checker_class='count_based',
            checker_params={'count': 10},
            is_active=True,
            is_hidden=True,
        )

        # Award trophy1 to current user
        self.user_trophy = UserTrophy.objects.create(
            user=self.user,
            trophy=self.trophy1,
            progress=100.0,
        )

        # Award trophy2 to other user
        UserTrophy.objects.create(
            user=self.other_user,
            trophy=self.trophy2,
            progress=100.0,
        )

        # Create statistics for progress calculation
        self.stats, _ = UserStatistics.objects.get_or_create(
            user=self.user,
            defaults={
                'total_workouts': 1,
                'total_weight_lifted': Decimal('2500'),
            }
        )

    def test_list_user_trophies_authenticated(self):
        """Test listing user's earned trophies"""
        response = self.client.get(reverse('user-trophy-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('results', data)

    def test_list_user_trophies_unauthenticated(self):
        """Test listing user trophies requires authentication"""
        self.client.logout()
        response = self.client.get(reverse('user-trophy-list'))

        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_user_only_sees_own_trophies(self):
        """Test users only see their own earned trophies"""
        response = self.client.get(reverse('user-trophy-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Should only see trophy1 (awarded to self.user)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['trophy']['id'], self.trophy1.id)

    def test_user_trophy_serialization(self):
        """Test user trophy includes earned_at and progress"""
        response = self.client.get(reverse('user-trophy-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        user_trophy_data = data['results'][0]
        self.assertIn('earned_at', user_trophy_data)
        self.assertIn('progress', user_trophy_data)
        self.assertEqual(user_trophy_data['progress'], 100.0)

    def test_trophy_progress_endpoint(self):
        """Test the trophy progress endpoint"""
        response = self.client.get(reverse('trophy-progress'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Should return progress for all active trophies
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_trophy_progress_includes_unearned(self):
        """Test progress endpoint includes unearned trophies"""
        response = self.client.get(reverse('trophy-progress'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        trophy_ids = [t['trophy']['id'] for t in data]

        # Should include trophy1 (earned) and trophy2 (not earned)
        self.assertIn(self.trophy1.id, trophy_ids)
        self.assertIn(self.trophy2.id, trophy_ids)

    def test_trophy_progress_calculations(self):
        """Test progress calculations are correct"""
        response = self.client.get(reverse('trophy-progress'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Find trophy2 (progressive volume trophy)
        trophy2_data = next((t for t in data if t['trophy']['id'] == self.trophy2.id), None)
        self.assertIsNotNone(trophy2_data)

        # User has lifted 2500kg, trophy requires 5000kg = 50%
        self.assertEqual(trophy2_data['progress'], 50.0)
        self.assertFalse(trophy2_data['is_earned'])

    def test_trophy_progress_earned_status(self):
        """Test earned trophies show is_earned=True"""
        response = self.client.get(reverse('trophy-progress'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Find trophy1 (earned)
        trophy1_data = next((t for t in data if t['trophy']['id'] == self.trophy1.id), None)
        self.assertIsNotNone(trophy1_data)

        self.assertTrue(trophy1_data['is_earned'])
        self.assertEqual(trophy1_data['progress'], 100.0)
        self.assertIsNotNone(trophy1_data['earned_at'])

    def test_hidden_trophy_not_in_progress(self):
        """Test hidden trophies not shown in progress unless earned"""
        # Temporarily make user non-staff to test hidden trophy filtering
        self.user.is_staff = False
        self.user.save()

        response = self.client.get(reverse('trophy-progress'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        trophy_ids = [t['trophy']['id'] for t in data]

        # Hidden trophy should not be in the list (not earned) for non-staff users
        self.assertNotIn(self.hidden_trophy.id, trophy_ids)

        # Restore staff status
        self.user.is_staff = True
        self.user.save()

    def test_hidden_trophy_shown_when_earned(self):
        """Test hidden trophies appear in progress once earned"""
        # Award hidden trophy to user
        UserTrophy.objects.create(
            user=self.user,
            trophy=self.hidden_trophy,
            progress=100.0,
        )

        response = self.client.get(reverse('trophy-progress'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        trophy_ids = [t['trophy']['id'] for t in data]

        # Hidden trophy should now be visible
        self.assertIn(self.hidden_trophy.id, trophy_ids)

    def test_user_trophy_read_only(self):
        """Test user trophy endpoints are read-only"""
        # Try to create a user trophy via API
        response = self.client.post(
            reverse('user-trophy-list'),
            data={
                'trophy': self.trophy2.id,
                'progress': 100.0,
            },
        )

        # Should not be allowed
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED])

    def test_trophy_progress_display_format(self):
        """Test progress display includes current and target values"""
        response = self.client.get(reverse('trophy-progress'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Find trophy2 (progressive trophy)
        trophy2_data = next((t for t in data if t['trophy']['id'] == self.trophy2.id), None)

        # Should have current_value and target_value
        self.assertIn('current_value', trophy2_data)
        self.assertIn('target_value', trophy2_data)
        # Values are returned as strings from serialization
        self.assertEqual(trophy2_data['current_value'], '2500.00')
        self.assertEqual(trophy2_data['target_value'], '5000.0')
