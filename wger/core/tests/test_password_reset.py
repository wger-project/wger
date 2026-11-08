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
import re

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.test import override_settings
from django.urls import reverse

# Third Party
from django_cf_turnstile.fields import TurnstileCaptchaField
from django_recaptcha.fields import ReCaptchaField

# wger
from wger.core.tests.base_testcase import WgerTestCase


class PasswordResetTestCase(WgerTestCase):
    """
    Password reset via allauth
    """

    def test_links_point_to_allauth(self):
        """
        The login page links to allauth's reset form, the old URL redirects there
        """
        reset_url = reverse('account_reset_password')

        response = self.client.get(reverse('core:user:login'))
        self.assertContains(response, f'href="{reset_url}"')

        response = self.client.get(reverse('core:user:password_reset'))
        self.assertRedirects(response, reset_url)

    def test_rate_limited(self):
        """
        Requests for the same address are rate-limited
        """
        url = reverse('account_reset_password')
        for _ in range(5):
            response = self.client.post(url, {'email': 'test@example.com'})
            self.assertEqual(response.status_code, 302)

        response = self.client.post(url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, 429)

    @override_settings(WGER_SETTINGS={**settings.WGER_SETTINGS, 'CAPTCHA_PROVIDER': 'recaptcha'})
    def test_captcha_recaptcha(self):
        """
        The reset form has a reCAPTCHA field with its own action when CAPTCHA_PROVIDER
        is 'recaptcha'
        """
        response = self.client.get(reverse('account_reset_password'))

        field = response.context['form'].fields['captcha']
        self.assertIsInstance(field, ReCaptchaField)
        self.assertEqual(field.widget.action, 'password_reset')
        self.assertNotContains(response, 'name="submit"')

    @override_settings(WGER_SETTINGS={**settings.WGER_SETTINGS, 'CAPTCHA_PROVIDER': 'turnstile'})
    def test_captcha_turnstile(self):
        """
        The reset form has a Turnstile field when CAPTCHA_PROVIDER is 'turnstile'
        """
        response = self.client.get(reverse('account_reset_password'))

        self.assertIsInstance(response.context['form'].fields['captcha'], TurnstileCaptchaField)

    @override_settings(WGER_SETTINGS={**settings.WGER_SETTINGS, 'CAPTCHA_PROVIDER': 'none'})
    def test_captcha_none(self):
        """
        The reset form has no captcha field when CAPTCHA_PROVIDER is 'none'
        """
        response = self.client.get(reverse('account_reset_password'))

        self.assertNotIn('captcha', response.context['form'].fields)

    def test_reset_from_email_link(self):
        """
        The link in the email leads to wger's form for the new password
        """
        self.client.post(reverse('account_reset_password'), {'email': 'admin@example.com'})
        self.assertEqual(len(mail.outbox), 1)
        link = re.search(r'https?://\S+/account/password/reset/key/\S+/', mail.outbox[0].body)

        response = self.client.get(link.group(0), follow=True)
        self.assertTemplateUsed(response, 'account/password_reset_from_key.html')
        self.assertIn('password1', response.context['form'].fields)

        response = self.client.post(
            response.redirect_chain[-1][0],
            {'password1': 'Sup3r-Secret-pw!', 'password2': 'Sup3r-Secret-pw!'},
            follow=True,
        )
        self.assertTemplateUsed(response, 'account/password_reset_from_key_done.html')
        self.assertTrue(User.objects.get(username='admin').check_password('Sup3r-Secret-pw!'))
