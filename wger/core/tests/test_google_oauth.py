import unittest
from django.test import TestCase
from django.conf import settings
from django.urls import resolve

from wger.config.models.gym_config import GymConfig


@unittest.expectedFailure
class GoogleOAuthConfigTests(TestCase):
    def test_allauth_installed(self):
        self.assertIn(
            "allauth",
            settings.INSTALLED_APPS,
            "django-allauth is not installed",
        )

    def test_google_provider_installed(self):
        self.assertIn(
            "allauth.socialaccount",
            settings.INSTALLED_APPS,
            "allauth.socialaccount missing from INSTALLED_APPS",
        )

        self.assertIn(
            "allauth.socialaccount.providers.google",
            settings.INSTALLED_APPS,
            "Google OAuth provider not installed",
        )

@unittest.expectedFailure
class GoogleOAuthURLTests(TestCase):
    """
    Ensure OAuth URLs are reachable.
    These are expected to fail becuase the admins need to set up the path
    """

    def test_google_login_url_exists(self):
        """
        /accounts/google/login/ should exist
        """
        resolver = resolve("/accounts/google/login/")
        self.assertIsNotNone(resolver)


class RegressionLoginTests(TestCase):
    def setUp(self):
        GymConfig.objects.create(pk=1)

    def test_standard_login_page_still_loads(self):
        response = self.client.get("/login/")
        self.assertNotEqual(response.status_code, 500)
