# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

import os

from django.core.urlresolvers import reverse

from django.test import TestCase
from django.test import LiveServerTestCase
from django.db import models

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class WorkoutManagerTestCase(TestCase):
    fixtures = ('tests-user-data',
                'test-weight-data',
                'test-exercises',
                'tests-ingredients',
                'days_of_week',
                'tests-workout-data')

    def setUp(self):
        '''
        Overwrite some of Django's settings here
        '''
        os.environ['RECAPTCHA_TESTING'] = 'True'

    def tearDown(self):
        '''
        Reset settings
        '''
        del os.environ['RECAPTCHA_TESTING']

    def user_login(self, user='admin'):
        '''
        Login the user, by default as 'admin'
        '''
        self.client.login(username=user, password='%(user)s%(user)s' % {'user': user})

    def user_logout(self):
        '''
        Visit the logout page
        '''
        self.client.logout()


class WorkoutManagerDeleteTestCase(WorkoutManagerTestCase):
    '''
    Tests deleting an object as the owner, a different user and a logged out
    one.
    '''

    delete_class = ''
    delete_url = ''
    pk = ''

    def delete_object(self, fail=False):
        '''
        Helper function to test deleting a workout
        '''

        # Only perform the checks on derived classes
        if self.__class__.__name__ == 'WorkoutManagerDeleteTestCase':
            return

        # Fetch the delete page
        count_before = self.delete_class.objects.count()
        response = self.client.get(reverse(self.delete_url, kwargs={'pk': self.pk}))
        count_after = self.delete_class.objects.count()

        self.assertEqual(count_before, count_after)
        if fail:
            self.assertIn(response.status_code, (403, 302))
        else:
            self.assertEqual(response.status_code, 200)

        # Try deleting the object
        response = self.client.post(reverse(self.delete_url, kwargs={'pk': self.pk}))
        count_after = self.delete_class.objects.count()

        if fail:
            self.assertIn(response.status_code, (403, 302))
            self.assertEqual(count_before, count_after)
        else:
            self.assertEqual(response.status_code, 302)
            self.assertEqual(count_before - 1, count_after)
            self.assertRaises(self.delete_class.DoesNotExist,
                              self.delete_class.objects.get,
                              pk=self.pk)

    def test_delete_object_anonymous(self):
        '''
        Tests deleting the object as an anonymous user
        '''

        self.delete_object(fail=True)

    def test_delete_object_owner(self):
        '''
        Tests deleting the object as the owner user
        '''

        self.user_login('test')
        self.delete_object(fail=False)

    def test_delete_object_other(self):
        '''
        Tests deleting the object as a logged in user not owning the data
        '''

        self.user_login('admin')
        self.delete_object(fail=True)
