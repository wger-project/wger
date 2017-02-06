from django.core.urlresolvers import reverse
from wger.core.tests.base_testcase import WorkoutManagerTestCase
import requests
import json


class SyncWithFitbitTestCase(WorkoutManagerTestCase):

    def test_it_shows_instructions(self):
        self.user_login()
        r = self.client.get(reverse('core:user:fitbit'))
        self.assertContains(r, "https://www.fitbit.com/oauth2/authorize", status_code=200)

    def test_it_handles_oauth_response(self):
        oauth_response = {"access_token": "test-token"}

        url = reverse('core:user:fitbit')
        params = {"code": "759r07e59et763"}
        self.user_login()
        r = self.client.get(url, params=params)

        self.assertEqual(r.status_code, 200)
