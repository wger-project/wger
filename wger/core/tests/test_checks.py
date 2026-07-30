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
