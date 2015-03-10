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

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase


class StatusUserTestCase(WorkoutManagerTestCase):
    '''
    Tests activating and deactivating users
    '''

    def activate(self, fail=False):
        '''
        Helper function to test activating users
        '''
        user = User.objects.get(pk=2)
        user.is_active = False
        user.save()
        self.assertFalse(user.is_active)

        response = self.client.get(reverse('core:user:activate', kwargs={'pk': user.pk}))
        user = User.objects.get(pk=2)

        if fail:
            self.assertEqual(response.status_code, 403)
            self.assertFalse(user.is_active)
        else:
            self.assertEqual(response.status_code, 302)
            self.assertTrue(user.is_active)

    def test_activate_authorized(self):
        '''
        Tests activating a user as an administrator
        '''
        self.user_login('admin')
        self.activate()

    def test_activate_unauthorized(self):
        '''
        Tests activating a user as another logged in user
        '''
        self.user_login('demo')
        self.activate(fail=True)

    def test_activate_logged_out(self):
        '''
        Tests activating a user a logged out user
        '''
        self.activate(fail=True)

    def deactivate(self, fail=False):
        '''
        Helper function to test deactivating users
        '''
        user = User.objects.get(pk=2)
        self.assertTrue(user.is_active)

        response = self.client.get(reverse('core:user:deactivate', kwargs={'pk': user.pk}))
        user = User.objects.get(pk=2)

        if fail:
            self.assertEqual(response.status_code, 403)
            self.assertTrue(user.is_active)
        else:
            self.assertEqual(response.status_code, 302)
            self.assertFalse(user.is_active)

    def test_deactivate_authorized(self):
        '''
        Tests deactivating a user as an administrator
        '''
        self.user_login('admin')
        self.deactivate()

    def test_deactivate_unauthorized(self):
        '''
        Tests deactivating a user as another logged in user
        '''
        self.user_login('demo')
        self.deactivate(fail=True)

    def test_deactivate_logged_out(self):
        '''
        Tests deactivating a user a logged out user
        '''
        self.deactivate(fail=True)


class EditUserTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a user by an admin
    '''

    object_class = User
    url = 'core:user:edit'
    pk = 2
    data = {'email': 'another.email@example.com',
            'first_name': 'Name',
            'last_name': 'Lastname'}
