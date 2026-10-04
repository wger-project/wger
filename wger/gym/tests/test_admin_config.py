# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Django
from django.contrib.auth.models import User
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import (
    WgerEditTestCase,
    WgerTestCase,
)
from wger.gym.models import GymAdminConfig


class EditConfigTestCase(WgerEditTestCase):
    """
    Tests editing an admin config
    """

    object_class = GymAdminConfig
    url = 'gym:admin_config:edit'
    pk = 1
    user_success = 'admin'
    user_fail = (
        'member1',
        'manager1',
        'manager2',
        'trainer4',
        'general_manager1',
        'general_manager2',
    )
    data = {'overview_inactive': False}


class EditConfigPermissionTestCase(WgerTestCase):
    """
    Editing the own admin config needs the change_gymadminconfig permission
    """

    def url(self):
        return reverse('gym:admin_config:edit', kwargs={'pk': 4})

    def test_owner_with_permission(self):
        """
        A trainer can edit their own config
        """
        self.user_login('trainer1')
        response = self.client.post(self.url(), {'overview_inactive': ''})

        self.assertEqual(response.status_code, 302)
        self.assertFalse(GymAdminConfig.objects.get(pk=4).overview_inactive)

    def test_owner_without_permission(self):
        """
        Owning the config is not enough without the permission
        """
        user = User.objects.get(username='trainer1')
        user.groups.clear()
        user.user_permissions.clear()

        self.user_login('trainer1')
        response = self.client.post(self.url(), {'overview_inactive': ''})

        self.assertEqual(response.status_code, 403)
        self.assertTrue(GymAdminConfig.objects.get(pk=4).overview_inactive)
