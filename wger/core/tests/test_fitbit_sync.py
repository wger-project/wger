from django.core.urlresolvers import reverse
from wger.core.tests.base_testcase import WorkoutManagerTestCase
from django.conf import settings
import requests
import json


class SyncWithFitbitTestCase(WorkoutManagerTestCase):

    def test_it_shows_instructions(self):
        settings.WGER_SETTINGS['FITBIT_CLIENT_ID'] = '2283MF'
        settings.WGER_SETTINGS['FITBIT_CLIENT_SECRET'] = 'thisisaclientsecret'
        self.user_login()
        r = self.client.get(reverse('core:user:fitbit'))
        self.assertContains(r, "https://www.fitbit.com/oauth2/authorize", status_code=200)

    def test_it_handles_oauth_response(self):
        settings.WGER_SETTINGS['FITBIT_CLIENT_ID'] = '2283MF'
        settings.WGER_SETTINGS['FITBIT_CLIENT_SECRET'] = 'thisisaclientsecret'
        oauth_response = {"access_token": "test-token"}

        url = reverse('core:user:fitbit')
        params = {"code": "759r07e59et763"}
        self.user_login()
        r = self.client.get(url, params=params)

        self.assertEqual(r.status_code, 200)
