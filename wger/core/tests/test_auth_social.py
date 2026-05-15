# This file is part of wger Workout Manager.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
from unittest import mock

# Django
from django.conf import settings
from django.test import (
    RequestFactory,
    SimpleTestCase,
    override_settings,
)
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.core.views.user import WgerLoginView


class _StubProvider:
    """
    Mocks an allauth ``Provider`` instance
    """

    id = 'wger'
    name = 'Wger Test Provider'
    uses_apps = False

    def get_login_url(self, request, **kwargs):
        return '/accounts/wger-social/login/'


@override_settings(
    INSTALLED_APPS=[*settings.INSTALLED_APPS, 'allauth.socialaccount'],
    WGER_SOCIAL_PROVIDERS=['wger'],
)
class SocialAuthEnabledLoginPageTestCase(WgerTestCase):
    """When social auth is enabled, the login page renders the provider section."""

    @mock.patch(
        'allauth.socialaccount.adapter.DefaultSocialAccountAdapter.list_providers',
        return_value=[_StubProvider()],
    )
    def test_login_page_shows_social_section(self, _):
        response = self.client.get(reverse('core:user:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['use_social_auth'])
        self.assertContains(response, 'or login with')
        self.assertContains(response, 'Wger Test Provider')
        # The button must POST (CSRF-safe), not GET.
        self.assertContains(
            response,
            '<form method="post" action="/accounts/wger-social/login/"',
        )

    @mock.patch(
        'allauth.socialaccount.adapter.DefaultSocialAccountAdapter.list_providers',
        return_value=[],
    )
    def test_no_section_without_configured_providers(self, _):
        """If no SocialApp rows exist, ``get_providers`` is empty and the section is hidden."""
        response = self.client.get(reverse('core:user:login'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'or login with')


class WgerLoginViewContextTestCase(SimpleTestCase):
    """Unit tests for ``WgerLoginView.get_context_data``."""

    def _build_view(self):
        view = WgerLoginView()
        view.request = RequestFactory().get(reverse('core:user:login'))
        view.setup(view.request)
        return view

    @override_settings(WGER_SOCIAL_PROVIDERS=[])
    def test_use_social_auth_false_when_no_providers(self):
        ctx = self._build_view().get_context_data()
        self.assertFalse(ctx['use_social_auth'])

    @override_settings(WGER_SOCIAL_PROVIDERS=['google'])
    def test_use_social_auth_true_when_providers_configured(self):
        ctx = self._build_view().get_context_data()
        self.assertTrue(ctx['use_social_auth'])
