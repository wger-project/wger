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

# Django
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import Routine


class RoutineApiTrainerTestCase(WgerTestCase):
    """
    Tests filtering routines in the api endpoint
    """

    def setUp(self):
        super().setUp()

        Routine(
            user_id=1,
            name='Admin template',
            is_template=True,
            start=datetime.datetime.now(),
            end=datetime.datetime.now() + datetime.timedelta(days=1),
        ).save()

    def test_routine_overview_user(self):
        """A user can see their own routines"""

        self.user_login('test')
        request = self.client.get(reverse('routine-list'))
        self.assertEqual(request.status_code, 200)

        results = request.json()
        self.assertEqual(results['count'], 4)

    def test_routine_overview_admin(self):
        """An admin can see their own routines"""

        self.user_login('admin')
        request = self.client.get(reverse('routine-list'))
        self.assertEqual(request.status_code, 200)

        results = request.json()
        self.assertEqual(results['count'], 3)

    def test_routine_overview_impersonating_admin(self):
        """
        When a trainer is impersonating a user, they can see the routines
        from the user, plus their own.
        """
        self.user_login('admin')
        self.client.get(reverse('core:user:trainer-login', kwargs={'user_pk': 2}))

        request = self.client.get(reverse('routine-list'))
        self.assertEqual(request.status_code, 200)

        results = request.json()
        self.assertEqual(results['count'], 6)

    def test_routine_template_overview_user(self):
        """A user can see their own routine templates"""

        self.user_login('test')
        request = self.client.get(reverse('templates-list'))
        self.assertEqual(request.status_code, 200)

        results = request.json()
        self.assertEqual(results['count'], 1)

    def test_routine_template_overview_admin(self):
        """An admin can see their own routine templates"""

        self.user_login('admin')
        request = self.client.get(reverse('templates-list'))
        self.assertEqual(request.status_code, 200)

        results = request.json()
        self.assertEqual(results['count'], 1)

    def test_routine_template_overview_impersonating_admin(self):
        """
        When a trainer is impersonating a user, they can see the routines
        from the user, plus their own.
        """
        self.user_login('admin')
        self.client.get(reverse('core:user:trainer-login', kwargs={'user_pk': 2}))

        request = self.client.get(reverse('templates-list'))
        self.assertEqual(request.status_code, 200)

        results = request.json()
        self.assertEqual(results['count'], 2)
