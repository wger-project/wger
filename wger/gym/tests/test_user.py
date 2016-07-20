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

import datetime

from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from wger.core.models import UserProfile
from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.gym.models import Gym
from wger.gym.models import GymAdminConfig


class GymAddUserTestCase(WorkoutManagerTestCase):
    '''
    Tests admin adding users to gyms
    '''

    def add_user(self, fail=False):
        '''
        Helper function to add users
        '''
        count_before = User.objects.all().count()
        GymAdminConfig.objects.all().delete()
        response = self.client.get(reverse('gym:gym:add-user', kwargs={'gym_pk': 1}))
        self.assertEqual(GymAdminConfig.objects.all().count(), 0)
        if fail:
            self.assertEqual(response.status_code, 403)
        else:
            self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('gym:gym:add-user', kwargs={'gym_pk': 1}),
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
            self.assertEqual(GymAdminConfig.objects.all().count(), 1)
            self.assertEqual(new_user.userprofile.gym_id, 1)

    def test_add_user_authorized(self):
        '''
        Tests adding a user as authorized user
        '''
        self.user_login('admin')
        self.add_user()

    def test_add_user_authorized2(self):
        '''
        Tests adding a user as authorized user
        '''
        self.user_login('general_manager1')
        self.add_user()

    def test_add_user_unauthorized(self):
        '''
        Tests adding a user an unauthorized user
        '''
        self.user_login('test')
        self.add_user(fail=True)

    def test_add_user_unauthorized2(self):
        '''
        Tests adding a user an unauthorized user
        '''
        self.user_login('trainer1')
        self.add_user(fail=True)

    def test_add_user_unauthorized3(self):
        '''
        Tests adding a user an unauthorized user
        '''
        self.user_login('manager3')
        self.add_user(fail=True)

    def test_add_user_logged_out(self):
        '''
        Tests adding a user a logged out user
        '''
        self.add_user(fail=True)

    def new_user_data_export(self, fail=False):
        '''
        Helper function to test exporting the data of a newly created user
        '''
        response = self.client.get(reverse('gym:gym:new-user-data-export'))
        if fail:
            self.assertIn(response.status_code, (302, 403))
        else:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'text/csv')
            today = datetime.date.today()
            filename = 'User-data-{t.year}-{t.month:02d}-{t.day:02d}-cletus.csv'.format(t=today)
            self.assertEqual(response['Content-Disposition'],
                             'attachment; filename={}'.format(filename))
            self.assertGreaterEqual(len(response.content), 90)
            self.assertLessEqual(len(response.content), 120)

    def test_new_user_data_export(self):
        '''
        Test exporting the data of a newly created user
        '''
        self.user_login('admin')
        self.add_user()
        self.new_user_data_export(fail=False)

        self.user_logout()
        self.new_user_data_export(fail=True)

        self.user_logout()
        self.user_login('test')
        self.new_user_data_export(fail=True)


class TrainerLoginTestCase(WorkoutManagerTestCase):
    '''
    Tests the trainer login view (switching to user ID)
    '''

    def test_anonymous(self):
        '''
        Test the trainer login as an anonymous user
        '''
        response = self.client.get(reverse('core:user:trainer-login', kwargs={'user_pk': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('trainer.identity'))

    def test_user(self):
        '''
        Test the trainer login as a logged in user without rights
        '''
        self.user_login('test')
        response = self.client.get(reverse('core:user:trainer-login', kwargs={'user_pk': 1}))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.client.session.get('trainer.identity'))

    def test_trainer(self):
        '''
        Test the trainer login as a logged in user with enough rights
        '''
        self.user_login('admin')
        response = self.client.get(reverse('core:user:trainer-login', kwargs={'user_pk': 2}))
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
        response = self.client.get(reverse('core:user:trainer-login', kwargs={'user_pk': 2}))
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
        response = self.client.get(reverse('core:user:trainer-login', kwargs={'user_pk': 2}))
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
        response = self.client.get(reverse('core:user:trainer-login', kwargs={'user_pk': 2}))
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
        response = self.client.get(reverse('core:user:trainer-login', kwargs={'user_pk': 2}))
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
        self.client.get(reverse('core:user:trainer-login', kwargs={'user_pk': 2}))
        self.assertTrue(self.client.session.get('trainer.identity'))

        self.client.get(reverse('core:user:trainer-login', kwargs={'user_pk': 1}))
        self.assertFalse(self.client.session.get('trainer.identity'))
