# Django
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase


class ProxyAuthHeaderTestCase(WgerTestCase):
    """
    Tests using proxy auth for authentication
    """

    def test_basic_auth_proxy_header(self):
        """
        Tests that the proxy auth header works for authenticating
        the user
        """
        with self.settings(
            WGER_SETTINGS={
                "AUTH_PROXY_HEADER": "Remote-User",
                "ALLOW_REGISTRATION": False,
                "ALLOW_GUEST_USERS": False,
                'TWITTER': False,
                'MASTODON': False,
                'MIN_ACCOUNT_AGE_TO_TRUST': 21,
            }
        ):
            response = self.client.get(reverse("core:dashboard"), HTTP_REMOTE_USER="testuser")
            self.assertEqual(response.status_code, 200)
