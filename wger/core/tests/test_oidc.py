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

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

# Third Party
from allauth.socialaccount.models import SocialAccount

# wger
from wger.core.tests.base_testcase import WgerTestCase


class DisconnectOidcUserTestCase(WgerTestCase):
    """
    Test disconnecting OIDC accounts from the admin user overview.
    """

    user_success = (
        'admin',
        'general_manager1',
        'general_manager2',
        'manager1',
        'manager2',
    )
    user_fail = (
        'member1',
        'member2',
        'manager3',
        'trainer1',
        'trainer2',
        'trainer3',
        'trainer4',
    )

    def disconnect_from_admin_overview(self, fail=False):
        target_user = User.objects.get(pk=2)
        provider_id = getattr(settings, 'OIDC_PROVIDER_ID', 'oidc')
        SocialAccount.objects.filter(user=target_user, provider=provider_id).delete()
        SocialAccount.objects.create(user=target_user, provider=provider_id, uid='oidc-uid-2')

        self.assertTrue(
            SocialAccount.objects.filter(user=target_user, provider=provider_id).exists()
        )

        response = self.client.get(reverse('core:user:disconnect-oidc', kwargs={'pk': 2}))

        self.assertIn(response.status_code, (302, 403))
        account_exists = SocialAccount.objects.filter(
            user=target_user, provider=provider_id
        ).exists()
        if fail:
            self.assertTrue(account_exists)
        else:
            self.assertFalse(account_exists)

    def test_disconnect_oidc_authorized(self):
        for username in self.user_success:
            self.user_login(username)
            self.disconnect_from_admin_overview()
            self.user_logout()

    def test_disconnect_oidc_unauthorized(self):
        for username in self.user_fail:
            self.user_login(username)
            self.disconnect_from_admin_overview(fail=True)
            self.user_logout()

    def test_disconnect_oidc_logged_out(self):
        self.disconnect_from_admin_overview(fail=True)


class DisconnectOwnOidcUserTestCase(WgerTestCase):
    """
    Test disconnecting OIDC accounts from the own preferences endpoint.
    """

    def _create_own_oidc_account(self):
        user = User.objects.get(username='test')
        provider_id = getattr(settings, 'OIDC_PROVIDER_ID', 'oidc')
        SocialAccount.objects.filter(user=user, provider=provider_id).delete()
        SocialAccount.objects.create(user=user, provider=provider_id, uid='oidc-uid-test')
        return user, provider_id

    def test_disconnect_own_oidc_post(self):
        self.user_login('test')
        user, provider_id = self._create_own_oidc_account()

        response = self.client.post(reverse('core:user:disconnect-oidc'))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(SocialAccount.objects.filter(user=user, provider=provider_id).exists())

    def test_disconnect_own_oidc_without_existing_account(self):
        self.user_login('test')
        user = User.objects.get(username='test')
        provider_id = getattr(settings, 'OIDC_PROVIDER_ID', 'oidc')
        SocialAccount.objects.filter(user=user, provider=provider_id).delete()

        response = self.client.post(reverse('core:user:disconnect-oidc'))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(SocialAccount.objects.filter(user=user, provider=provider_id).exists())

    def test_disconnect_own_oidc_requires_post(self):
        self.user_login('test')
        self._create_own_oidc_account()

        response = self.client.get(reverse('core:user:disconnect-oidc'))

        self.assertEqual(response.status_code, 405)
