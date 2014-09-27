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
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from wger.core.models import UserProfile
from wger.core.models import Gym
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

        response = self.client.get(reverse('core:user-activate', kwargs={'pk': user.pk}))
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

        response = self.client.get(reverse('core:user-deactivate', kwargs={'pk': user.pk}))
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


class GymAddUserTestCase(WorkoutManagerTestCase):
    '''
    Tests admin adding users to gyms
    '''

    def add_user(self, fail=False):
        '''
        Helper function to add users
        '''
        count_before = User.objects.all().count()
        response = self.client.get(reverse('core:gym:add-user', kwargs={'gym_pk': 1}))
        if fail:
            self.assertEqual(response.status_code, 403)
        else:
            self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('core:gym:add-user', kwargs={'gym_pk': 1}),
                                    {'first_name': 'Cletus',
                                     'last_name': 'Spuckle',
                                     'username': 'cletus',
                                     'email': 'cletus@spuckle-megacorp.com',
                                     'role': 'admin'})
        count_after = User.objects.all().count()
        if fail:
            self.assertEqual(response.status_code, 403)
            self.assertEqual(count_before, count_after)
            self.assertFalse(self.client.session.get('gym.user'))
        else:
            self.assertEqual(count_before + 1, count_after)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(self.client.session['gym.user']['user_pk'], 3)
            self.assertTrue(self.client.session['gym.user']['password'])
            self.assertEqual(len(self.client.session['gym.user']['password']), 15)
            new_user = User.objects.get(pk=self.client.session['gym.user']['user_pk'])
            self.assertEqual(new_user.userprofile.gym_id, 1)

    def test_add_user_authorized(self):
        '''
        Tests adding a user as an administrator
        '''
        self.user_login('admin')
        self.add_user()

    def test_add_user_unauthorized(self):
        '''
        Tests adding a user a different user
        '''
        self.user_login('test')
        self.add_user(fail=True)

    def test_add_user_logged_out(self):
        '''
        Tests adding a user a logged out user
        '''
        self.add_user(fail=True)


class TrainerLoginTestCase(WorkoutManagerTestCase):
    '''
    Tests the trainer login view (switching to user ID)
    '''

    def test_anonymous(self):
        '''
        Test the trainer login as an anonymous user
        '''
        response = self.client.get(reverse('core:trainer-login', kwargs={'user_pk': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('trainer.identity'))

    def test_user(self):
        '''
        Test the trainer login as a logged in user without rights
        '''
        self.user_login('test')
        response = self.client.get(reverse('core:trainer-login', kwargs={'user_pk': 1}))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.client.session.get('trainer.identity'))

    def test_trainer(self):
        '''
        Test the trainer login as a logged in user with enough rights
        '''
        self.user_login('admin')
        response = self.client.get(reverse('core:trainer-login', kwargs={'user_pk': 2}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('trainer.identity'))

    def test_wrong_gym(self):
        '''
        Test changing the identity to a user in a different gym
        '''
        profile = UserProfile.objects.get(user_id=2)
        profile.gym_id = 2
        profile.save()
        self.user_login('admin')
        response = self.client.get(reverse('core:trainer-login', kwargs={'user_pk': 2}))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.client.session.get('trainer.identity'))

    def test_gym_trainer(self):
        '''
        Test changing the identity to a user with trainer rights
        '''
        user = User.objects.get(pk=2)
        content_type = ContentType.objects.get_for_model(Gym)
        permission = Permission.objects.get(content_type=content_type, codename='gym_trainer')
        user.user_permissions.add(permission)

        self.user_login('admin')
        response = self.client.get(reverse('core:trainer-login', kwargs={'user_pk': 2}))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.client.session.get('trainer.identity'))

    def test_gym_manager(self):
        '''
        Test changing the identity to a user with gym management rights
        '''
        user = User.objects.get(pk=2)
        content_type = ContentType.objects.get_for_model(Gym)
        permission = Permission.objects.get(content_type=content_type, codename='manage_gym')
        user.user_permissions.add(permission)

        self.user_login('admin')
        response = self.client.get(reverse('core:trainer-login', kwargs={'user_pk': 2}))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.client.session.get('trainer.identity'))

    def test_gyms_manager(self):
        '''
        Test changing the identity to a user with gyms management rights
        '''
        user = User.objects.get(pk=2)
        content_type = ContentType.objects.get_for_model(Gym)
        permission = Permission.objects.get(content_type=content_type, codename='manage_gyms')
        user.user_permissions.add(permission)

        self.user_login('admin')
        response = self.client.get(reverse('core:trainer-login', kwargs={'user_pk': 2}))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.client.session.get('trainer.identity'))


class TrainerLogoutTestCase(WorkoutManagerTestCase):
    '''
    Tests the trainer logout view (switching back to trainer ID)
    '''

    def test_logout(self):
        '''
        Test the trainer login as an anonymous user
        '''
        self.user_login('admin')
        response = self.client.get(reverse('core:trainer-login', kwargs={'user_pk': 2}))
        self.assertTrue(self.client.session.get('trainer.identity'))

        response = self.client.get(reverse('core:trainer-login', kwargs={'user_pk': 1}))
        self.assertFalse(self.client.session.get('trainer.identity'))


class EditUserTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a user by an admin
    '''

    object_class = User
    url = 'core:user-edit'
    pk = 2
    data = {'email': 'another.email@example.com',
            'first_name': 'Name',
            'last_name': 'Lastname'}
