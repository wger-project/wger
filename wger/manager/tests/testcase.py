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
import decimal
import logging

from django.core.urlresolvers import reverse
from django.core.urlresolvers import NoReverseMatch
from django.core.cache import cache

from django.test import TestCase
from django.test import LiveServerTestCase
from django.db import models

STATUS_CODES_FAIL = (302, 403, 404)


class WorkoutManagerTestCase(TestCase):
    fixtures = ('days_of_week',
                'test-languages',
                'test-user-data',
                'test-weight-data',
                'test-exercises',
                'test-weight-units',
                'test-ingredients',
                'test-nutrition-data',
                'test-workout-data',
                'test-schedules')
    current_user = 'anonymous'

    def setUp(self):
        '''
        Overwrite some of Django's settings here
        '''
        os.environ['RECAPTCHA_TESTING'] = 'True'
        logging.disable(logging.INFO)

    def tearDown(self):
        '''
        Reset settings
        '''
        del os.environ['RECAPTCHA_TESTING']
        cache.clear()

    def user_login(self, user='admin'):
        '''
        Login the user, by default as 'admin'
        '''
        self.client.login(username=user, password='%(user)s%(user)s' % {'user': user})
        self.current_user = user

    def user_logout(self):
        '''
        Visit the logout page
        '''
        self.client.logout()
        self.current_user = 'anonymous'

    def compare_fields(self, field, value):
        current_field_class = field.__class__.__name__

        # Standard types, simply compare
        if current_field_class in ('unicode', 'int', 'float', 'time', 'date'):
            self.assertEqual(field, value)

        # boolean, convert
        elif current_field_class == 'bool':
            self.assertEqual(field, bool(value))

        # decimal, convert
        elif current_field_class == 'Decimal':
            self.assertEqual(field, decimal.Decimal(unicode(value)))

        # Related manager, iterate
        elif current_field_class == 'ManyRelatedManager':
            for j in field.all():
                self.assertIn(j.id, value)

        # Other objects (from foreign keys), check the ID
        else:
            self.assertEqual(field.id, value)

    def post_test_hook(self):
        '''
        Hook to add some more specific tests after the basic add or delete
        operations are finished
        '''
        pass


class WorkoutManagerDeleteTestCase(WorkoutManagerTestCase):
    '''
    Tests deleting an object an authorized user, a different one and a logged out
    one. This assumes the delete action is only triggered with a POST request and
    GET will only show a confirmation dialog.
    '''

    object_class = ''
    url = ''
    pk = None
    user_success = 'admin'
    user_fail = 'test'

    def delete_object(self, fail=False):
        '''
        Helper function to test deleting a workout
        '''

        # Only perform the checks on derived classes
        if self.__class__.__name__ == 'WorkoutManagerDeleteTestCase':
            return

        # Fetch the delete page
        count_before = self.object_class.objects.count()
        response = self.client.get(reverse(self.url, kwargs={'pk': self.pk}))
        count_after = self.object_class.objects.count()
        self.assertEqual(count_before, count_after)

        if fail:
            self.assertIn(response.status_code, STATUS_CODES_FAIL)
        else:
            self.assertEqual(response.status_code, 200)

        # Try deleting the object
        response = self.client.post(reverse(self.url, kwargs={'pk': self.pk}))
        count_after = self.object_class.objects.count()

        if fail:
            self.assertIn(response.status_code, STATUS_CODES_FAIL)
            self.assertEqual(count_before, count_after)
        else:
            self.assertEqual(response.status_code, 302)
            self.assertEqual(count_before - 1, count_after)
            self.assertRaises(self.object_class.DoesNotExist,
                              self.object_class.objects.get,
                              pk=self.pk)

            # The page we are redirected to doesn't trigger an error
            response = self.client.get(response['Location'])
            self.assertEqual(response.status_code, 200)
        self.post_test_hook()

    def test_delete_object_anonymous(self):
        '''
        Tests deleting the object as an anonymous user
        '''

        self.delete_object(fail=True)

    def test_delete_object_authorized(self):
        '''
        Tests deleting the object as an authorized user
        '''

        self.user_login(self.user_success)
        self.delete_object(fail=False)

    def test_delete_object_other(self):
        '''
        Tests deleting the object as an unauthorized, logged in user
        '''

        if self.user_fail:
            self.user_login(self.user_fail)
            self.delete_object(fail=True)


class WorkoutManagerEditTestCase(WorkoutManagerTestCase):
    '''
    Tests editing an object as an authorized user, a different one and a logged out
    one.
    '''

    object_class = ''
    url = ''
    pk = None
    user_success = 'admin'
    user_fail = 'test'
    data = {}
    data_ignore = ()

    def edit_object(self, fail=False):
        '''
        Helper function to test editing an object
        '''

        # Only perform the checks on derived classes
        if self.__class__.__name__ == 'WorkoutManagerEditTestCase':
            return

        # Fetch the edit page
        try:
            response = self.client.get(reverse(self.url, kwargs={'pk': self.pk}))
        except NoReverseMatch:
            # URL needs special care and doesn't need to be reversed here,
            # everything was already done in the individual test case
            response = self.client.get(self.url)
        entry_before = self.object_class.objects.get(pk=self.pk)

        if fail:
            self.assertIn(response.status_code, STATUS_CODES_FAIL)
            self.assertTemplateUsed('login.html')

        else:
            self.assertEqual(response.status_code, 200)

        # Try to edit the object
        try:
            response = self.client.post(reverse(self.url, kwargs={'pk': self.pk}),
                                        self.data)
        except NoReverseMatch:
            # URL needs special care and doesn't need to be reversed here,
            # everything was already done in the individual test case
            response = self.client.post(self.url, self.data)

        entry_after = self.object_class.objects.get(pk=self.pk)

        # Check the results
        if fail:
            self.assertIn(response.status_code, STATUS_CODES_FAIL)
            self.assertTemplateUsed('login.html')
            self.assertEqual(entry_before, entry_after)

        else:
            self.assertEqual(response.status_code, 302)

            # Check that the data is correct
            for i in self.data:
                if i not in self.data_ignore:
                    current_field = getattr(entry_after, i)
                    self.compare_fields(current_field, self.data[i])

            # The page we are redirected to doesn't trigger an error
            response = self.client.get(response['Location'])
            self.assertEqual(response.status_code, 200)
        self.post_test_hook()

    def test_edit_object_anonymous(self):
        '''
        Tests editing the object as an anonymous user
        '''
        self.edit_object(fail=True)

    def test_edit_object_authorized(self):
        '''
        Tests editing the object as an authorized user
        '''

        self.user_login(self.user_success)
        self.edit_object(fail=False)

    def test_edit_object_other(self):
        '''
        Tests editing the object as an unauthorized, logged in user
        '''

        if self.user_fail:
            self.user_login(self.user_fail)
            self.edit_object(fail=True)


class WorkoutManagerAddTestCase(WorkoutManagerTestCase):
    '''
    Tests adding an object as an authorized user, a different one and a logged out
    one.
    '''

    object_class = ''
    url = ''
    pk = None
    user_success = 'admin'
    user_fail = 'test'
    anonymous_fail = True
    data = {}
    data_ignore = ()

    def add_object(self, fail=False):
        '''
        Helper function to test adding an object
        '''

        # Only perform the checks on derived classes
        if self.__class__.__name__ == 'WorkoutManagerAddTestCase':
            return

        # Fetch the add page
        try:
            response = self.client.get(reverse(self.url))
        except NoReverseMatch:
            # URL needs special care and doesn't need to be reversed here,
            # everything was already done in the individual test case
            response = self.client.get(self.url)

        if fail:
            self.assertIn(response.status_code, STATUS_CODES_FAIL)
            #self.assertTemplateUsed('login.html')

        else:
            self.assertEqual(response.status_code, 200)

        # Enter the data
        count_before = self.object_class.objects.count()
        try:
            response = self.client.post(reverse(self.url), self.data)
        except NoReverseMatch:
            # URL needs special care and doesn't need to be reversed here,
            # everything was already done in the individual test case
            response = self.client.post(self.url, self.data)

        count_after = self.object_class.objects.count()
        if fail:
            self.assertIn(response.status_code, STATUS_CODES_FAIL)
            self.assertTemplateUsed('login.html')

            self.assertRaises(self.object_class.DoesNotExist,
                              self.object_class.objects.get,
                              pk=self.pk)
            self.assertEqual(count_before, count_after)

        else:
            self.assertEqual(response.status_code, 302)
            entry = self.object_class.objects.get(pk=self.pk)

            # Check that the data is correct
            for i in self.data:
                if i not in self.data_ignore:
                    current_field = getattr(entry, i)
                    self.compare_fields(current_field, self.data[i])

            self.assertEqual(count_before + 1, count_after)

            # The page we are redirected to doesn't trigger an error
            response = self.client.get(response['Location'])
            self.assertEqual(response.status_code, 200)
        self.post_test_hook()

    def test_add_object_anonymous(self):
        '''
        Tests adding the object as an anonymous user
        '''

        if self.user_fail:
            self.add_object(fail=self.anonymous_fail)

    def test_add_object_authorized(self):
        '''
        Tests adding the object as an authorized user
        '''

        self.user_login(self.user_success)
        self.add_object(fail=False)

    def test_add_object_other(self):
        '''
        Tests adding the object as an unauthorized, logged in user
        '''

        self.user_login(self.user_fail)
        if self.user_fail:
            self.add_object(fail=True)


class WorkoutManagerAccessTestCase(WorkoutManagerTestCase):
    '''
    Tests accessing a URL per GET as an authorized user, an unauthorized one and
    a logged out one.
    '''

    url = ''
    user_success = 'admin'
    user_fail = 'test'
    anonymous_fail = True

    def access(self, fail=True):

        # Only perform the checks on derived classes
        if self.__class__.__name__ == 'WorkoutManagerAccessTestCase':
            return

        try:
            response = self.client.get(reverse(self.url))
        except NoReverseMatch:
            # URL needs special care and doesn't need to be reversed here,
            # everything was already done in the individual test case
            response = self.client.get(self.url)

        if fail:
            #print response
            self.assertIn(response.status_code, STATUS_CODES_FAIL)
            if response.status_code == 302:
                # The page we are redirected to doesn't trigger an error
                response = self.client.get(response['Location'])
                self.assertEqual(response.status_code, 200)

        else:
            self.assertEqual(response.status_code, 200)

    def test_access_anonymous(self):
        '''
        Tests accessing the URL as an anonymous user
        '''

        self.user_logout()
        self.access(fail=self.anonymous_fail)

    def test_access_authorized(self):
        '''
        Tests accessing the URL as an authorized user
        '''

        self.user_login(self.user_success)
        self.access(fail=False)

    def test_access_other(self):
        '''
        Tests accessing the URL as an unauthorized, logged in user
        '''

        self.user_login(self.user_fail)
        self.access(fail=True)
        self.user_logout()
