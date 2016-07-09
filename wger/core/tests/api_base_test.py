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
from rest_framework import status
from rest_framework.test import APITestCase

from wger.core.tests.base_testcase import BaseTestCase


class ApiBaseTestCase(APITestCase):
    api_version = 'v2'
    '''
    The current API version to test
    '''

    resource = None
    '''
    The current resource to be tested (Model class)
    '''

    pk = None
    '''
    The pk of the detail view to test
    '''

    private_resource = True
    '''
    A flag indicating whether the resource can be updated (POST, PATCH)
    by the owning user (workout, etc.)
    '''

    user_access = 'test'
    '''
    Owner user authorized to change the data (workout, etc.)
    '''

    user_fail = 'admin'
    '''
    A different user
    '''

    data = {}
    '''
    Dictionary with the data used for testing
    '''

    special_endpoints = ()
    '''
    A list of special endpoints to check, e.g. the canonical representation of
    a workout.
    '''

    def get_resource_name(self):
        '''
        Returns the name of the resource. The default is the name of the model
        class used in lower letters
        '''
        return self.resource.__name__.lower()

    @property
    def url(self):
        '''
        Return the URL to use for testing
        '''
        return '/api/{0}/{1}/'.format(self.api_version, self.get_resource_name())

    @property
    def url_detail(self):
        '''
        Return the detail URL to use for testing
        '''
        return '{0}{1}/'.format(self.url, self.pk)

    def get_credentials(self, username=None):
        '''
        Authenticates a user
        '''
        if not username:
            username = self.user_access
        user_obj = User.objects.get(username=username)

        self.client.force_authenticate(user=user_obj)


class ApiGetTestCase(object):
    '''
    Base test case for testing GET access to the API
    '''
    def test_ordering(self):
        '''
        Test that ordering the resource works
        '''
        pass

        # TODO: implement this

    def test_get_detail(self):
        '''
        Tests accessing the detail view of a resource

        '''

        if self.private_resource:
            response = self.client.get(self.url_detail)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

            # Logged in owner user
            self.get_credentials()
            response = self.client.get(self.url_detail)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Different logged in user
            self.get_credentials(self.user_fail)
            response = self.client.get(self.url_detail)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        else:
            response = self.client.get(self.url_detail)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_overview(self):
        '''
        Test accessing the overview view of a resource
        '''
        if self.private_resource:
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

            # Logged in owner user
            self.get_credentials()
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        else:
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_special_endpoints(self):
        '''
        Test accessing any special endpoint the resource could have
        '''
        for endpoint in self.special_endpoints:
            url = self.url_detail + endpoint + '/'

            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

            # Logged in owner user
            self.get_credentials()
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Different logged in user
            self.get_credentials(self.user_fail)
            response = self.client.get(self.url_detail)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ApiPostTestCase(object):
    '''
    Base test case for testing POST access to the API
    '''

    def test_post_detail(self):
        '''
        POSTing to a detail view is not allowed
        '''

        if self.private_resource:
            # Anonymous user
            response = self.client.post(self.url_detail, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

            # Authorized user (owner)
            self.get_credentials()
            response = self.client.post(self.url_detail, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Different logged in user
            self.get_credentials(self.user_fail)
            response = self.client.post(self.url_detail, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            # Anonymous user
            response = self.client.post(self.url_detail, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Authorized user (owner)
            self.get_credentials()
            response = self.client.post(self.url_detail, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Different logged in user
            self.get_credentials(self.user_fail)
            response = self.client.post(self.url_detail, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post(self):
        '''
        Tests POSTing (adding) a new object
        '''

        if self.private_resource:
            # Anonymous user
            response = self.client.post(self.url, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

            # Authorized user (owner)
            self.get_credentials()
            count_before = self.resource.objects.all().count()
            response = self.client.post(self.url, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            count_after = self.resource.objects.all().count()
            self.assertEqual(count_before + 1, count_after)

            # Different logged in user
            self.get_credentials(self.user_fail)
            response = self.client.post(self.url, data=self.data)
            # self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            # self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        else:
            # Anonymous user
            response = self.client.post(self.url, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Logged in user
            self.get_credentials()
            response = self.client.post(self.url, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Different logged in user
            self.get_credentials(self.user_fail)
            response = self.client.post(self.url, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post_special_endpoints(self):
        '''
        Tests that it's not possible to POST to the special endpoints
        '''
        for endpoint in self.special_endpoints:
            url = self.url_detail + endpoint + '/'

            response = self.client.post(url, self.data)
            if self.private_resource:
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            else:
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Logged in owner user
            self.get_credentials()
            response = self.client.post(url, self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Different logged in user
            self.get_credentials(self.user_fail)
            response = self.client.post(url, self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ApiPatchTestCase(object):
    '''
    Base test case for testing PATCH access to the API
    '''

    def test_patch_detail(self):
        '''
        Test PATCHING a detail view
        '''

        if self.private_resource:
            # Anonymous user
            response = self.client.patch(self.url_detail, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

            # Authorized user (owner)
            self.get_credentials()
            response = self.client.patch(self.url_detail, data=self.data)
            self.assertIn(response.status_code, (status.HTTP_201_CREATED, status.HTTP_200_OK))

            # Try updating each of the object's values
            for key in self.data:
                response = self.client.patch(self.url_detail, data={key: self.data[key]})
                self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Different logged in user
            self.get_credentials(self.user_fail)
            response = self.client.patch(self.url_detail, data=self.data)
            self.assertIn(response.status_code,
                          (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))
        else:
            # Anonymous user
            response = self.client.patch(self.url_detail, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Authorized user (owner)
            self.get_credentials()
            response = self.client.patch(self.url_detail, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Different logged in user
            self.get_credentials(self.user_fail)
            response = self.client.patch(self.url_detail, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch(self):
        '''
        PATCHING to the overview is not allowed
        '''

        if self.private_resource:
            # Anonymous user
            response = self.client.patch(self.url, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        else:
            # Anonymous user
            response = self.client.patch(self.url, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Logged in user
        self.get_credentials()
        response = self.client.patch(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Different logged in user
        self.get_credentials(self.user_fail)
        response = self.client.patch(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_special_endpoints(self):
        '''
        Tests that it's not possible to patch to the special endpoints
        '''
        for endpoint in self.special_endpoints:
            url = self.url_detail + endpoint + '/'

            response = self.client.patch(url, self.data)
            if self.private_resource:
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            else:
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Logged in owner user
            self.get_credentials()
            response = self.client.patch(url, self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Different logged in user
            self.get_credentials(self.user_fail)
            response = self.client.patch(url, self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ApiPutTestCase(object):
    '''
    Base test case for testing PUT access to the API
    '''

    def test_put_detail(self):
        '''
        PUTing to a detail view is allowed
        '''

        if self.private_resource:
            # Anonymous user
            response = self.client.put(self.url_detail, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

            # Authorized user (owner)
            self.get_credentials()
            response = self.client.put(self.url_detail, data=self.data)
            self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED))

            # Different logged in user
            count_before = self.resource.objects.all().count()
            self.get_credentials(self.user_fail)
            response = self.client.put(self.url_detail, data=self.data)
            count_after = self.resource.objects.all().count()

            # Even if we PUT to a detail resource that does not belong to us,
            # the created object will have the correct user assigned.
            #
            # Currently resources that have a 'user' field 'succeed'
            if response.status_code == status.HTTP_201_CREATED:
                # print('201: {0}'.format(self.url_detail))
                obj = self.resource.objects.get(pk=response.data['id'])
                obj2 = self.resource.objects.get(pk=self.pk)
                self.assertNotEqual(obj.get_owner_object().user.username,
                                    obj2.get_owner_object().user.username)
                self.assertEqual(obj.get_owner_object().user.username, self.user_fail)
                self.assertEqual(count_before + 1, count_after)

            elif response.status_code == status.HTTP_403_FORBIDDEN:
                # print('403: {0}'.format(self.url_detail))
                self.assertEqual(count_before, count_after)
        else:
            # Anonymous user
            response = self.client.put(self.url_detail, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Authorized user (owner)
            self.get_credentials()
            response = self.client.put(self.url_detail, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Different logged in user
            self.get_credentials(self.user_fail)
            response = self.client.put(self.url_detail, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put(self):
        '''
        Tests PUTTING (adding) a new object
        '''

        if self.private_resource:
            # Anonymous user
            response = self.client.put(self.url, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        else:
            # Anonymous user
            response = self.client.put(self.url, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Authorized user (owner)
        self.get_credentials()
        response = self.client.put(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Different logged in user
        self.get_credentials(self.user_fail)
        response = self.client.put(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_special_endpoints(self):
        '''
        Tests that it's not possible to PUT to the special endpoints
        '''
        for endpoint in self.special_endpoints:
            url = self.url_detail + endpoint + '/'

            response = self.client.put(url, self.data)
            if self.private_resource:
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            else:
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Logged in owner user
            self.get_credentials()
            response = self.client.put(url, self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Different logged in user
            self.get_credentials(self.user_fail)
            response = self.client.put(url, self.data)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ApiDeleteTestCase(object):
    '''
    Base test case for testing DELETE access to the API
    '''

    def test_delete_detail(self):
        '''
        Tests DELETEing an object
        '''
        if self.private_resource:
            # Anonymous user
            count_before = self.resource.objects.all().count()
            response = self.client.delete(self.url_detail)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            count_after = self.resource.objects.all().count()
            self.assertEqual(count_before, count_after)

            # Authorized user (owner)
            self.get_credentials()
            count_before = self.resource.objects.all().count()
            response = self.client.delete(self.url_detail)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            count_after = self.resource.objects.all().count()
            self.assertEqual(count_before - 1, count_after)

            # Different logged in user
            self.get_credentials(self.user_fail)
            response = self.client.delete(self.url_detail)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        else:
            # Anonymous user
            response = self.client.delete(self.url_detail)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Logged in user
            self.get_credentials()
            response = self.client.delete(self.url_detail)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Different logged in user
            self.get_credentials(self.user_fail)
            response = self.client.delete(self.url_detail)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        '''
        DELETEing to the overview is not allowed
        '''
        if self.private_resource:
            # Anonymous user
            response = self.client.delete(self.url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

            # Authorized user (owner)
            self.get_credentials()
            response = self.client.delete(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Different logged in user
            self.get_credentials(self.user_fail)
            response = self.client.delete(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            # Anonymous user
            response = self.client.delete(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Authorized user (owner)
            self.get_credentials()
            response = self.client.delete(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Different logged in user
            self.get_credentials(self.user_fail)
            response = self.client.delete(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_special_endpoints(self):
        '''
        Tests that it's not possible to delete to the special endpoints
        '''
        for endpoint in self.special_endpoints:
            url = self.url_detail + endpoint + '/'

            response = self.client.delete(url)
            if self.private_resource:
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            else:
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Logged in owner user
            self.get_credentials()
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

            # Different logged in user
            self.get_credentials(self.user_fail)
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ApiBaseResourceTestCase(BaseTestCase,
                              ApiBaseTestCase,

                              ApiGetTestCase,
                              ApiPostTestCase,
                              ApiDeleteTestCase,
                              ApiPutTestCase,
                              ApiPatchTestCase):
    '''
    Base test case for the REST API

    All logic happens in the Api*TestCase classes
    '''
    pass
