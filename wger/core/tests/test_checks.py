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
from datetime import timedelta

# Django
from django.conf import settings
from django.test import SimpleTestCase
from django.test.utils import override_settings

# wger
from wger.core.checks import settings_check


class RefreshTokenLifetimeCheckTestCase(SimpleTestCase):
    """Tests for the wger.W003 refresh token lifetime check"""

    @staticmethod
    def check_ids():
        return [entry.id for entry in settings_check(None)]

    @override_settings(SIMPLE_JWT={'REFRESH_TOKEN_LIFETIME': timedelta(hours=24)})
    def test_warns_on_short_lifetime(self):
        """A lifetime below one week triggers the warning"""
        self.assertIn('wger.W003', self.check_ids())

    @override_settings(SIMPLE_JWT={'REFRESH_TOKEN_LIFETIME': timedelta(hours=2880)})
    def test_no_warning_on_default_lifetime(self):
        """The default lifetime of 120 days passes the check"""
        self.assertNotIn('wger.W003', self.check_ids())

    @override_settings(SIMPLE_JWT={'REFRESH_TOKEN_LIFETIME': timedelta(days=7)})
    def test_no_warning_at_threshold(self):
        """Exactly one week is accepted"""
        self.assertNotIn('wger.W003', self.check_ids())


class CaptchaCheckTestCase(SimpleTestCase):
    """Tests for the captcha provider checks"""

    @staticmethod
    def check_ids():
        return [entry.id for entry in settings_check(None)]

    @override_settings(
        WGER_SETTINGS={**settings.WGER_SETTINGS, 'CAPTCHA_PROVIDER': 'none', 'USE_RECAPTCHA': True},
        RECAPTCHA_PUBLIC_KEY='',
        RECAPTCHA_PRIVATE_KEY='',
    )
    def test_use_recaptcha_without_keys(self):
        """The deprecated USE_RECAPTCHA without reCAPTCHA keys triggers the key warning"""
        self.assertIn('wger.W004', self.check_ids())

    @override_settings(WGER_SETTINGS={**settings.WGER_SETTINGS, 'CAPTCHA_PROVIDER': 'hcaptcha'})
    def test_unknown_provider(self):
        """An unknown provider is an error"""
        self.assertIn('wger.E002', self.check_ids())

    @override_settings(
        WGER_SETTINGS={**settings.WGER_SETTINGS, 'CAPTCHA_PROVIDER': 'turnstile'},
        TURNSTILE_SITE_KEY='site-key',
        TURNSTILE_SECRET_KEY='',
    )
    def test_turnstile_without_secret(self):
        """Turnstile without its secret key triggers the key warning"""
        self.assertIn('wger.W004', self.check_ids())

    @override_settings(
        WGER_SETTINGS={**settings.WGER_SETTINGS, 'CAPTCHA_PROVIDER': 'turnstile'},
        TURNSTILE_SITE_KEY='site-key',
        TURNSTILE_SECRET_KEY='secret-key',
    )
    def test_turnstile_configured(self):
        """A fully configured provider passes the checks"""
        ids = self.check_ids()
        self.assertNotIn('wger.W004', ids)
        self.assertNotIn('wger.E002', ids)

    @staticmethod
    def use_recaptcha_warnings():
        return [entry for entry in settings_check(None) if entry.id == 'wger.W005']

    @override_settings(
        WGER_SETTINGS={**settings.WGER_SETTINGS, 'CAPTCHA_PROVIDER': 'none', 'USE_RECAPTCHA': True}
    )
    def test_use_recaptcha_deprecated(self):
        """USE_RECAPTCHA without a provider warns to switch to CAPTCHA_PROVIDER"""
        warnings = self.use_recaptcha_warnings()
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].msg, 'USE_RECAPTCHA is deprecated')

    @override_settings(
        WGER_SETTINGS={
            **settings.WGER_SETTINGS,
            'CAPTCHA_PROVIDER': 'turnstile',
            'USE_RECAPTCHA': True,
        }
    )
    def test_use_recaptcha_ignored(self):
        """USE_RECAPTCHA next to another provider warns that it is ignored"""
        warnings = self.use_recaptcha_warnings()
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].msg, 'USE_RECAPTCHA is ignored')
        self.assertIn('turnstile', warnings[0].hint)

    @override_settings(
        WGER_SETTINGS={
            **settings.WGER_SETTINGS,
            'CAPTCHA_PROVIDER': 'recaptcha',
            'USE_RECAPTCHA': False,
        }
    )
    def test_no_use_recaptcha_warning(self):
        """Without USE_RECAPTCHA there is no deprecation warning"""
        self.assertEqual(self.use_recaptcha_warnings(), [])
