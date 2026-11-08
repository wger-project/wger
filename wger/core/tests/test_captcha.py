#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#
#  wger Workout Manager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  wger Workout Manager is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
from unittest import mock

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import (
    SimpleTestCase,
    override_settings,
)
from django.urls import reverse

# Third Party
import requests

# wger
from wger.core.captcha import (
    TURNSTILE_VERIFY_URL,
    TurnstileField,
    captcha_field,
)
from wger.core.tests.base_testcase import WgerTestCase


def verify_response(payload) -> mock.Mock:
    """A stand-in for the response of Cloudflare's siteverify endpoint"""
    response = mock.Mock()
    response.json.return_value = payload
    return response


@override_settings(TURNSTILE_SITE_KEY='site-key', TURNSTILE_SECRET_KEY='secret-key')
class TurnstileFieldTestCase(SimpleTestCase):
    """Tests for the Turnstile form field and widget"""

    @mock.patch('wger.core.captcha.requests.post')
    def test_accepts_verified_token(self, mock_post):
        """A token Cloudflare confirms is accepted, the secret and token are sent"""
        mock_post.return_value = verify_response({'success': True})

        self.assertEqual(TurnstileField('register').clean('the-token'), 'the-token')
        mock_post.assert_called_once()
        self.assertEqual(mock_post.call_args.args[0], TURNSTILE_VERIFY_URL)
        self.assertEqual(
            mock_post.call_args.kwargs['data'],
            {'secret': 'secret-key', 'response': 'the-token'},
        )

    @mock.patch('wger.core.captcha.requests.post')
    def test_rejects_unverified_token(self, mock_post):
        """A token Cloudflare rejects is a validation error"""
        mock_post.return_value = verify_response(
            {'success': False, 'error-codes': ['invalid-input-response']}
        )

        with self.assertRaises(ValidationError):
            TurnstileField('register').clean('the-token')

    @mock.patch('wger.core.captcha.requests.post')
    def test_rejects_on_network_error(self, mock_post):
        """An unreachable endpoint rejects the token"""
        mock_post.side_effect = requests.ConnectionError()

        with self.assertRaises(ValidationError):
            TurnstileField('register').clean('the-token')

    @mock.patch('wger.core.captcha.requests.post')
    def test_rejects_on_http_error(self, mock_post):
        """An error status of the endpoint rejects the token"""
        response = verify_response({'success': True})
        response.raise_for_status.side_effect = requests.HTTPError()
        mock_post.return_value = response

        with self.assertRaises(ValidationError):
            TurnstileField('register').clean('the-token')

    @mock.patch('wger.core.captcha.requests.post')
    def test_rejects_unexpected_payload(self, mock_post):
        """A body that is no JSON object, or has no boolean success, rejects the token"""
        for payload in (['success'], {'success': 'true'}, {}):
            with self.subTest(payload=payload):
                mock_post.return_value = verify_response(payload)
                with self.assertRaises(ValidationError):
                    TurnstileField('register').clean('the-token')

        mock_post.return_value.json.side_effect = ValueError()
        with self.assertRaises(ValidationError):
            TurnstileField('register').clean('the-token')

    @mock.patch('wger.core.captcha.requests.post')
    def test_missing_token(self, mock_post):
        """A missing token is rejected without asking Cloudflare"""
        with self.assertRaises(ValidationError):
            TurnstileField('register').clean('')
        mock_post.assert_not_called()

    def test_widget(self):
        """The widget renders the site key and action and reads Cloudflare's input"""
        widget = TurnstileField('password_reset').widget

        html = widget.render('captcha', None)
        self.assertIn('data-sitekey="site-key"', html)
        self.assertIn('data-action="password_reset"', html)
        self.assertEqual(
            widget.value_from_datadict({'cf-turnstile-response': 'abc'}, {}, 'captcha'),
            'abc',
        )


class CaptchaFieldTestCase(SimpleTestCase):
    """Tests for the provider lookup of captcha_field"""

    def test_no_field(self):
        """'none' and unknown providers give no field"""
        for provider in ('none', 'unknown'):
            with self.subTest(provider=provider):
                with override_settings(
                    WGER_SETTINGS={**settings.WGER_SETTINGS, 'CAPTCHA_PROVIDER': provider}
                ):
                    self.assertIsNone(captcha_field('register'))


@override_settings(
    WGER_SETTINGS={**settings.WGER_SETTINGS, 'CAPTCHA_PROVIDER': 'turnstile'},
    TURNSTILE_SITE_KEY='site-key',
    TURNSTILE_SECRET_KEY='secret-key',
)
class TurnstileSignupTestCase(WgerTestCase):
    """Signing up with Turnstile as the captcha provider"""

    data = {
        'username': 'turnstileuser',
        'email': 'turnstile@example.com',
        'password1': 'quai8fai7Zae',
        'password2': 'quai8fai7Zae',
        'cf-turnstile-response': 'the-token',
    }

    @mock.patch('wger.core.captcha.requests.post')
    def test_signup_with_verified_token(self, mock_post):
        """A verified token creates the account"""
        mock_post.return_value = verify_response({'success': True})

        response = self.client.post(reverse('core:user:registration'), self.data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='turnstileuser').exists())

    @mock.patch('wger.core.captcha.requests.post')
    def test_signup_with_rejected_token(self, mock_post):
        """
        A rejected token shows the form again with the widget marked invalid (so
        Bootstrap shows the error), no account is created
        """
        mock_post.return_value = verify_response({'success': False, 'error-codes': []})

        response = self.client.post(reverse('core:user:registration'), self.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('captcha', response.context['form'].errors)
        self.assertRegex(response.content.decode(), r'class="cf-turnstile [^"]*\bis-invalid\b')
        self.assertFalse(User.objects.filter(username='turnstileuser').exists())
