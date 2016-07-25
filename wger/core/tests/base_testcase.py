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

import six
import os
import decimal
import logging
import tempfile
import shutil

from django.core.urlresolvers import reverse
from django.core.urlresolvers import NoReverseMatch
from django.core.cache import cache
from django.conf import settings
from django.test import TestCase
from wger.utils.constants import TWOPLACES


STATUS_CODES_FAIL = (302, 403, 404)


def get_reverse(url, kwargs={}):
    '''
    Helper function to get the reverse URL
    '''
    try:
        url = reverse(url, kwargs=kwargs)
    except NoReverseMatch:
        # URL needs special care and doesn't need to be reversed here,
        # everything was already done in the individual test case
        url = url

    return six.text_type(url)


def get_user_list(users):
    '''
    Helper function that returns a list with users to test
    '''
    if isinstance(users, tuple):
        return users
    else:
        return [users]


def delete_testcase_add_methods(cls):
    '''
    Helper function that dynamically adds test methods.

    This is a bit of a hack, but it's the easiest way of making sure that
    all the setup and teardown work is performed for each test user (and,
    most importantly for us, that the database is reseted every time).

    This must be called if the testcase has more than one success user
    '''

    for user in get_user_list(cls.user_fail):
        def test_unauthorized(self):
            self.user_login(user)
            self.delete_object(fail=False)
        setattr(cls, 'test_unauthorized_{0}'.format(user), test_unauthorized)

    for user in get_user_list(cls.user_success):
        def test_authorized(self):
            self.user_login(user)
            self.delete_object(fail=False)
        setattr(cls, 'test_authorized_{0}'.format(user), test_authorized)


class BaseTestCase(object):
    '''
    Base test case.

    Generic base testcase that is used for both the regular tests and the
    REST API tests
    '''

    fixtures = ('days_of_week',
                'gym_config',
                'groups',
                'setting_repetition_units',
                'setting_weight_units',
                'test-languages',
                'test-licenses',
                'test-gyms',
                'test-gymsconfig',
                'test-user-data',
                'test-gym-adminconfig.json',
                'test-gym-userconfig.json',
                'test-admin-user-notes',
                'test-gym-user-documents',
                'test-contracts',
                'test-apikeys',
                'test-weight-data',
                'test-equipment',
                'test-exercises',
                'test-exercise-images',
                'test-weight-units',
                'test-ingredients',
                'test-nutrition-data',
                'test-workout-data',
                'test-workout-session',
                'test-schedules')
    current_user = 'anonymous'
    current_password = ''
    is_mobile = False

    def setUp(self):
        '''
        Overwrite some of Django's settings here
        '''

        # Don't check reCaptcha's entries
        os.environ['RECAPTCHA_TESTING'] = 'True'

        # Test the mobile templates
        if os.environ.get('TEST_MOBILE') == 'True':
            settings.FLAVOURS = ('mobile',)
            self.is_mobile = True

        # Set logging level
        logging.disable(logging.INFO)

        # Set MEDIA_ROOT
        self.media_root = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.media_root

    def tearDown(self):
        '''
        Reset settings
        '''
        del os.environ['RECAPTCHA_TESTING']
        cache.clear()

        # Clear MEDIA_ROOT folder
        shutil.rmtree(self.media_root)


class WorkoutManagerTestCase(BaseTestCase, TestCase):
    '''
    Testcase to use with the regular website
    '''

    user_success = 'admin'
    '''
    A list of users to test for success. For convenience, a string can be used
    as well if there is only one user.
    '''

    user_fail = 'test'
    '''
    A list of users to test for failure. For convenience, a string can be used
    as well if there is only one user.
    '''

    def user_login(self, user='admin'):
        '''
        Login the user, by default as 'admin'
        '''
        password = '{0}{0}'.format(user)
        self.client.login(username=user, password=password)
        self.current_user = user
        self.current_password = password

    def user_logout(self):
        '''
        Visit the logout page
        '''
        self.client.logout()
        self.current_user = 'anonymous'

    def compare_fields(self, field, value):
        current_field_class = field.__class__.__name__

        # Standard types, simply compare
        if current_field_class in ('unicode', 'str', 'int', 'float', 'time', 'date'):
            self.assertEqual(field, value)

        # boolean, convert
        elif current_field_class == 'bool':
            self.assertEqual(field, bool(value))

        # decimal, convert
        elif current_field_class == 'Decimal':
            # TODO: use FOURPLACES when routine branch is merged
            self.assertEqual(field.quantize(TWOPLACES), decimal.Decimal(value).quantize(TWOPLACES))

        # Related manager and SortedManyToMany, iterate
        elif current_field_class in ('ManyRelatedManager', 'SortedRelatedManager'):
            for j in field.all():
                self.assertIn(j.id, value)

        # Uploaded image or file, compare the filename
        elif current_field_class in ('ImageFieldFile', 'FieldFile'):
            self.assertEqual(os.path.basename(field.name), os.path.basename(value.name))

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

    pk = None
    url = ''
    object_class = ''

    def delete_object(self, fail=False):
        '''
        Helper function to test deleting a workout
        '''

        # Only perform the checks on derived classes
        if self.__class__.__name__ == 'WorkoutManagerDeleteTestCase':
            return

        # Fetch the delete page
        count_before = self.object_class.objects.count()
        response = self.client.get(get_reverse(self.url, kwargs={'pk': self.pk}))
        count_after = self.object_class.objects.count()
        self.assertEqual(count_before, count_after)

        if fail:
            self.assertIn(response.status_code, STATUS_CODES_FAIL)
        else:
            self.assertEqual(response.status_code, 200)

        # Try deleting the object
        response = self.client.post(get_reverse(self.url, kwargs={'pk': self.pk}))

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

            # TODO: the redirection page might not have a language prefix (e.g. /user/login
            #       instead of /en/user/login) so there is an additional redirect
            # # The page we are redirected to doesn't trigger an error
            # response = self.client.get(response['Location'])
            # self.assertEqual(response.status_code, 200)
        self.post_test_hook()

    def test_delete_object_anonymous(self):
        '''
        Tests deleting the object as an anonymous user
        '''
        self.delete_object(fail=True)

    def test_delete_object_authorized(self):
        '''
        Tests deleting the object as the authorized user
        '''
        if not isinstance(self.user_success, tuple):
            self.user_login(self.user_success)
            self.delete_object(fail=False)

    def test_delete_object_other(self):
        '''
        Tests deleting the object as the unauthorized, logged in users
        '''
        if self.user_fail and not isinstance(self.user_success, tuple):
            for user in get_user_list(self.user_fail):
                self.user_login(user)
                self.delete_object(fail=True)


class WorkoutManagerEditTestCase(WorkoutManagerTestCase):
    '''
    Tests editing an object as an authorized user, a different one and a logged out
    one.
    '''

    object_class = ''
    url = ''
    pk = None
    data = {}
    data_ignore = ()
    fileupload = None
    '''
    If the form requires a file upload, specify the field name and the file path
    here in a list or tuple:

    ['fielname', 'path']
    '''

    def edit_object(self, fail=False):
        '''
        Helper function to test editing an object
        '''

        # Only perform the checks on derived classes
        if self.__class__.__name__ == 'WorkoutManagerEditTestCase':
            return

        # Fetch the edit page
        response = self.client.get(get_reverse(self.url, kwargs={'pk': self.pk}))
        entry_before = self.object_class.objects.get(pk=self.pk)

        if fail:
            self.assertIn(response.status_code, STATUS_CODES_FAIL)
            self.assertTemplateUsed('login.html')

        else:
            self.assertEqual(response.status_code, 200)

        # Try to edit the object
        # Special care if there are any file uploads
        if self.fileupload:
            field_name = self.fileupload[0]
            filepath = self.fileupload[1]
            with open(filepath, 'rb') as testfile:
                self.data[field_name] = testfile
                url = get_reverse(self.url, kwargs={'pk': self.pk})
                response = self.client.post(url, self.data)
        else:
            response = self.client.post(get_reverse(self.url, kwargs={'pk': self.pk}), self.data)

        entry_after = self.object_class.objects.get(pk=self.pk)

        # Check the results
        if fail:
            self.assertIn(response.status_code, STATUS_CODES_FAIL)
            self.assertTemplateUsed('login.html')
            self.assertEqual(entry_before, entry_after)

        else:
            self.assertEqual(response.status_code, 302)

            # Check that the data is correct
            for i in [j for j in self.data if j not in self.data_ignore]:
                current_field = getattr(entry_after, i)
                self.compare_fields(current_field, self.data[i])

            # TODO: the redirection page might not have a language prefix (e.g. /user/login
            #       instead of /en/user/login) so there is an additional redirect
            # # The page we are redirected to doesn't trigger an error
            # response = self.client.get(response['Location'])
            # self.assertEqual(response.status_code, 200)
        self.post_test_hook()

    def test_edit_object_anonymous(self):
        '''
        Tests editing the object as an anonymous user
        '''
        self.edit_object(fail=True)

    def test_edit_object_authorized(self):
        '''
        Tests editing the object as the authorized users
        '''
        for user in get_user_list(self.user_success):
            self.user_login(user)
            self.edit_object(fail=False)

    def test_edit_object_other(self):
        '''
        Tests editing the object as the unauthorized, logged in users
        '''
        if self.user_fail:
            for user in get_user_list(self.user_fail):
                self.user_login(user)
                self.edit_object(fail=True)


class WorkoutManagerAddTestCase(WorkoutManagerTestCase):
    '''
    Tests adding an object as an authorized user, a different one and a logged out
    one.
    '''

    object_class = ''
    url = ''
    pk_before = None
    pk_after = None
    anonymous_fail = True
    data = {}
    data_ignore = ()
    fileupload = None
    '''
    If the form requires a file upload, specify the field name and the file path
    here in a list or tuple:

    ['fielname', 'path']
    '''

    def add_object(self, fail=False):
        '''
        Helper function to test adding an object
        '''

        # Only perform the checks on derived classes
        if self.__class__.__name__ == 'WorkoutManagerAddTestCase':
            return

        # Fetch the add page
        response = self.client.get(get_reverse(self.url))

        if fail:
            self.assertIn(response.status_code, STATUS_CODES_FAIL)

        else:
            self.assertEqual(response.status_code, 200)

        # Enter the data
        count_before = self.object_class.objects.count()
        self.pk_before = self.object_class.objects.all().order_by('id').last().pk

        # Special care if there are any file uploads
        if self.fileupload:
            field_name = self.fileupload[0]
            filepath = self.fileupload[1]
            with open(filepath, 'rb') as testfile:
                self.data[field_name] = testfile
                response = self.client.post(get_reverse(self.url), self.data)
        else:
            response = self.client.post(get_reverse(self.url), self.data)
        count_after = self.object_class.objects.count()
        self.pk_after = self.object_class.objects.all().order_by('id').last().pk

        if fail:
            self.assertIn(response.status_code, STATUS_CODES_FAIL)
            self.assertEqual(self.pk_before, self.pk_after)
            self.assertEqual(count_before, count_after)

        else:
            self.assertEqual(response.status_code, 302)
            self.assertGreater(self.pk_after, self.pk_before)
            entry = self.object_class.objects.get(pk=self.pk_after)

            # Check that the data is correct
            for i in [j for j in self.data if j not in self.data_ignore]:
                current_field = getattr(entry, i)
                self.compare_fields(current_field, self.data[i])

            self.assertEqual(count_before + 1, count_after)

            # TODO: the redirection page might not have a language prefix (e.g. /user/login
            #       instead of /en/user/login) so there is an additional redirect
            # # The page we are redirected to doesn't trigger an error
            # response = self.client.get(response['Location'])
            # self.assertEqual(response.status_code, 200)
        self.post_test_hook()

    def test_add_object_anonymous(self):
        '''
        Tests adding the object as an anonymous user
        '''

        if self.user_fail:
            self.add_object(fail=self.anonymous_fail)

    def test_add_object_authorized(self):
        '''
        Tests adding the object as the authorized users
        '''

        for user in get_user_list(self.user_success):
            self.user_login(user)
            self.add_object(fail=False)

    def test_add_object_other(self):
        '''
        Tests adding the object as the unauthorized, logged in users
        '''

        if self.user_fail:
            for user in get_user_list(self.user_fail):
                self.user_login(self.user_fail)
                self.add_object(fail=True)


class WorkoutManagerAccessTestCase(WorkoutManagerTestCase):
    '''
    Tests accessing a URL per GET as an authorized user, an unauthorized one and
    a logged out one.
    '''

    url = ''
    anonymous_fail = True

    def access(self, fail=True):

        # Only perform the checks on derived classes
        if self.__class__.__name__ == 'WorkoutManagerAccessTestCase':
            return

        response = self.client.get(get_reverse(self.url))
        if fail:
            self.assertIn(response.status_code, STATUS_CODES_FAIL)

            # TODO: the redirection page might not have a language prefix (e.g. /user/login
            #       instead of /en/user/login) so there is an additional redirect
            # if response.status_code == 302:
            #     # The page we are redirected to doesn't trigger an error
            #     response = self.client.get(response['Location'])
            #     self.assertEqual(response.status_code, 200)

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
        Tests accessing the URL as the authorized users
        '''

        for user in get_user_list(self.user_success):
            self.user_login(user)
            self.access(fail=False)

    def test_access_other(self):
        '''
        Tests accessing the URL as the unauthorized, logged in users
        '''

        if self.user_fail:
            for user in get_user_list(self.user_fail):
                self.user_login(user)
                self.access(fail=True)
                self.user_logout()
