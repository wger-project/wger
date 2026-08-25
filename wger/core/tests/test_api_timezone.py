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
import datetime
import zoneinfo

# Django
from django.contrib.auth.models import User
from django.urls import reverse

# Third Party
from rest_framework import status
from rest_framework.authtoken.models import Token

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import WorkoutSession


class ApiTimezoneActivationTestCase(WgerTestCase):
    """
    Token-authenticated requests run in the requester's profile timezone

    The middleware only sees the session user, so the token classes activate
    the zone themselves once DRF has resolved the credentials; a date filter
    answers the same whichever way the caller logged in.
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='test')
        self.token, _ = Token.objects.get_or_create(user=self.user)

    def get(self, url, params):
        return self.client.get(url, params, HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_date_filter_resolves_in_the_profile_zone(self):
        profile = self.user.userprofile
        profile.time_zone = 'Pacific/Auckland'
        profile.save()

        session = WorkoutSession.objects.create(
            user=self.user,
            routine_id=3,
            datetime_start=datetime.datetime(
                2025, 3, 12, 7, 0, tzinfo=zoneinfo.ZoneInfo('Pacific/Auckland')
            ),
        )

        response = self.get(
            reverse('workoutsession-list'),
            {'datetime_start__date': '2025-03-12'},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [entry['id'] for entry in response.json()['results']]
        self.assertIn(str(session.id), ids)

    def test_a_token_outliving_the_profile_still_authenticates(self):
        self.user.userprofile.delete()

        response = self.get(reverse('workoutsession-list'), {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
