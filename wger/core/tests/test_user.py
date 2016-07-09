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
from django.core.urlresolvers import reverse, reverse_lazy

from wger.core.tests.base_testcase import (
    WorkoutManagerTestCase,
    WorkoutManagerEditTestCase,
    WorkoutManagerAccessTestCase
)


class StatusUserTestCase(WorkoutManagerTestCase):
    '''
    Test activating and deactivating users
    '''

    user_success = ('general_manager1',
                    'general_manager2',
                    'manager1',
                    'manager2',
                    'trainer1',
                    'trainer2',
                    'trainer3')

    user_fail = ('member1',
                 'member2',
                 'member3',
                 'member4',
                 'manager3',
                 'trainer4')

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

        self.assertIn(response.status_code, (302, 403))
        if fail:
            self.assertFalse(user.is_active)
        else:
            self.assertTrue(user.is_active)

    def test_activate_authorized(self):
        '''
        Tests activating a user as an administrator
        '''
        for username in self.user_success:
            self.user_login(username)
            self.activate()
            self.user_logout()

    def test_activate_unauthorized(self):
        '''
        Tests activating a user as another logged in user
        '''
        for username in self.user_fail:
            self.user_login(username)
            self.activate(fail=True)
            self.user_logout()

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
        user.is_active = True
        user.save()
        self.assertTrue(user.is_active)

        response = self.client.get(reverse('core:user:deactivate', kwargs={'pk': user.pk}))
        user = User.objects.get(pk=2)

        self.assertIn(response.status_code, (302, 403))
        if fail:
            self.assertTrue(user.is_active)
        else:
            self.assertFalse(user.is_active)

    def test_deactivate_authorized(self):
        '''
        Tests deactivating a user as an administrator
        '''
        for username in self.user_success:
            self.user_login(username)
            self.deactivate()
            self.user_logout()

    def test_deactivate_unauthorized(self):
        '''
        Tests deactivating a user as another logged in user
        '''
        for username in self.user_fail:
            self.user_login(username)
            self.deactivate(fail=True)
            self.user_logout()

    def test_deactivate_logged_out(self):
        '''
        Tests deactivating a user a logged out user
        '''
        self.deactivate(fail=True)


class EditUserTestCase(WorkoutManagerEditTestCase):
    '''
    Test editing a user
    '''

    object_class = User
    url = 'core:user:edit'
    pk = 2
    data = {'email': 'another.email@example.com',
            'first_name': 'Name',
            'last_name': 'Last name'}
    user_success = ('admin',
                    'general_manager1',
                    'general_manager2',
                    'manager1',
                    'manager2')
    user_fail = ('member1',
                 'member2',
                 'manager3',
                 'trainer2',
                 'trainer3',
                 'trainer4')


class EditUserTestCase2(WorkoutManagerEditTestCase):
    '''
    Test editing a user
    '''

    object_class = User
    url = 'core:user:edit'
    pk = 19
    data = {'email': 'another.email@example.com',
            'first_name': 'Name',
            'last_name': 'Last name'}
    user_success = ('admin',
                    'general_manager1',
                    'general_manager2',
                    'manager3')
    user_fail = ('member1',
                 'member2',
                 'trainer2',
                 'trainer3',
                 'trainer4')


class UserListTestCase(WorkoutManagerAccessTestCase):
    '''
    Test accessing the general user overview
    '''

    url = 'core:user:list'
    user_success = ('admin',
                    'general_manager1',
                    'general_manager2')
    user_fail = ('member1',
                 'member2',
                 'manager1',
                 'manager2',
                 'manager3',
                 'trainer2',
                 'trainer3',
                 'trainer4')


class UserDetailPageTestCase(WorkoutManagerAccessTestCase):
    '''
    Test accessing the user detail page
    '''

    url = reverse_lazy('core:user:overview', kwargs={'pk': 2})
    user_success = ('trainer1',
                    'trainer2',
                    'manager1',
                    'general_manager1',
                    'general_manager2')
    user_fail = ('trainer4',
                 'trainer5',
                 'manager3',
                 'member1',
                 'member2')


class UserDetailPageTestCase2(WorkoutManagerAccessTestCase):
    '''
    Test accessing the user detail page
    '''

    url = reverse_lazy('core:user:overview', kwargs={'pk': 19})
    user_success = ('trainer4',
                    'trainer5',
                    'manager3',
                    'general_manager1',
                    'general_manager2')
    user_fail = ('trainer1',
                 'trainer2',
                 'manager1',
                 'member1',
                 'member2')
