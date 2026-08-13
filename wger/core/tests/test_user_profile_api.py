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

# Django
from django.contrib.auth.models import User
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase


class UserProfileApiTestCase(WgerTestCase):
    """
    Test the user profile endpoint, which serves a single object per user
    """

    def setUp(self):
        super().setUp()
        self.user_login('test')
        self.url = reverse('userprofile')

    def test_get_returns_the_callers_profile(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['username'], 'test')

    def test_patch_updates_the_profile(self):
        response = self.client.patch(
            self.url, data={'calories': 2500}, content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['calories'], 2500)
        self.assertEqual(User.objects.get(username='test').userprofile.calories, 2500)

    def test_post_still_updates_the_profile(self):
        """POST is kept as a deprecated alias for clients written against the old API"""
        response = self.client.post(
            self.url, data={'calories': 2400}, content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.get(username='test').userprofile.calories, 2400)

    def test_post_leaves_unsent_fields_alone(self):
        profile = User.objects.get(username='test').userprofile
        profile.sleep_hours = 9
        profile.save()

        self.client.post(self.url, data={'calories': 2400}, content_type='application/json')

        profile.refresh_from_db()
        self.assertEqual(profile.calories, 2400)
        self.assertEqual(profile.sleep_hours, 9)

    def test_there_is_no_detail_route(self):
        """The profile is addressed without an id, so no other one is reachable"""
        response = self.client.get(f'{self.url}1/')

        self.assertEqual(response.status_code, 404)

    def test_profiles_cannot_be_deleted(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 405)

    def test_anonymous_access_is_refused(self):
        self.client.logout()

        self.assertEqual(self.client.get(self.url).status_code, 403)
