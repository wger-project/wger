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

# Third Party
from rest_framework import status

# wger
from wger.core.models import UserProfile
from wger.core.tests import powersync_base_test


class UserProfilePowerSyncTestCase(
    powersync_base_test.PowerSyncBaseTestCase,
    powersync_base_test.PowerSyncCreateNotAllowedTestCase,
    powersync_base_test.PowerSyncUpdateTestCase,
):
    """
    PowerSync handler for core.UserProfile. The profile is edit-only: creation
    happens during registration and deletion is refused, only PATCH reaches us.
    """

    table = 'core_userprofile'
    resource = UserProfile

    def setUp(self):
        super().setUp()
        self.pk_owned = UserProfile.objects.get(user__username=self.user_access).pk
        self.update_payload = {'id': self.pk_owned, 'weight_unit': 'lb'}

    def test_update_persists_weight_unit(self):
        """A PATCH round-trips the edited preference into the database."""
        self.authenticate()
        response = self.push('PATCH', {'id': self.pk_owned, 'weight_unit': 'lb'})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)

        profile = UserProfile.objects.get(pk=self.pk_owned)
        self.assertEqual(profile.weight_unit, 'lb')

    def test_delete_method_not_allowed(self):
        """Deleting the profile is refused"""

        self.authenticate()
        before = UserProfile.objects.count()
        response = self.push('DELETE', {'id': self.pk_owned})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('error'), 'Method not allowed')
        self.assertEqual(UserProfile.objects.count(), before)
