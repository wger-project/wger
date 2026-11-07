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
from django.contrib.auth.models import User
from django.urls import reverse

# Third Party
from allauth.account.models import EmailAddress

# wger
from wger.core.tests.base_testcase import WgerTestCase


class TrainerLoginAccountManagementTestCase(WgerTestCase):
    """
    A trainer logged in as one of their members can't change the member's
    login or recovery settings
    """

    def setUp(self):
        super().setUp()
        self.member = User.objects.get(username='test')
        self.impersonate_member()

    def impersonate_member(self):
        self.user_login('trainer1')
        response = self.client.post(
            reverse('core:user:trainer-login', kwargs={'user_pk': self.member.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('trainer.identity'))

    def test_email_page_is_not_shown(self):
        """
        The member's email management page is not rendered
        """
        response = self.client.get(reverse('account_email'))
        self.assertEqual(response.status_code, 403)

    def test_email_can_not_be_added(self):
        """
        No email address can be added to the member's account
        """
        email_before = self.member.email

        response = self.client.post(
            reverse('account_email'),
            {'email': 'attacker@example.com', 'action_add': ''},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(EmailAddress.objects.filter(email='attacker@example.com').exists())
        self.member.refresh_from_db()
        self.assertEqual(self.member.email, email_before)

    def test_password_can_not_be_set(self):
        """
        A member without a usable password (social login) doesn't get one
        """
        self.member.set_unusable_password()
        self.member.save()
        self.impersonate_member()

        response = self.client.post(
            reverse('account_set_password'),
            {'password1': 'attacker-pass-123', 'password2': 'attacker-pass-123'},
        )
        self.assertEqual(response.status_code, 403)
        self.member.refresh_from_db()
        self.assertFalse(self.member.has_usable_password())

    def test_account_can_not_be_deleted(self):
        """
        A member without a usable password (social login) can't be deleted by
        typing the username
        """
        self.member.set_unusable_password()
        self.member.save()
        self.impersonate_member()

        response = self.client.post(reverse('core:user:delete'), {'username': 'test'})
        self.assertEqual(response.status_code, 403)
        self.assertTrue(User.objects.filter(pk=self.member.pk).exists())

    def test_logout_still_works(self):
        """
        The session can still be ended
        """
        response = self.client.post(reverse('account_logout'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)
