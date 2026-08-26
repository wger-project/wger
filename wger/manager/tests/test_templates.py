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

# Third Party
from rest_framework import status

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models.routine import Routine


class RoutineTemplatesTestCase(WgerTestCase):
    """
    Test the different template access methods
    """

    def test_managers(self):
        """
        Test the db managers on the model
        """
        self.assertEqual(Routine.objects.all().count(), 5)
        self.assertEqual(Routine.templates.all().count(), 2)
        self.assertEqual(Routine.public.all().count(), 1)

    def test_routine_api(self):
        self.client.force_login(User.objects.get(username='test'))
        response = self.client.get(reverse('routine-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 4)

    def test_private_template_api(self):
        self.client.force_login(User.objects.get(username='test'))
        response = self.client.get(reverse('templates-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_post_template_api(self):
        self.client.force_login(User.objects.get(username='test'))
        response = self.client.post(reverse('templates-list'), data={})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_public_template_api(self):
        self.client.force_login(User.objects.get(username='test'))
        response = self.client.get(reverse('public-templates-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_post_public_template_api(self):
        self.client.force_login(User.objects.get(username='test'))
        response = self.client.post(reverse('public-templates-list'), data={})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_public_template_detail_api(self):
        """A public template listed by the API can also be retrieved by a non-owner"""
        self.client.force_login(User.objects.get(username='test'))
        listing = self.client.get(reverse('public-templates-list'))
        template = listing.data['results'][0]
        self.assertNotEqual(Routine.objects.get(pk=template['id']).user.username, 'test')

        response = self.client.get(
            reverse('public-templates-detail', kwargs={'pk': template['id']})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], template['id'])

    def test_private_template_detail_api(self):
        """The user's own templates can be retrieved"""
        self.client.force_login(User.objects.get(username='test'))
        listing = self.client.get(reverse('templates-list'))
        template = listing.data['results'][0]

        response = self.client.get(reverse('templates-detail', kwargs={'pk': template['id']}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], template['id'])
