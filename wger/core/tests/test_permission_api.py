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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Third Party
from rest_framework import status

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase


class CheckPermissionApiTestCase(BaseTestCase, ApiBaseTestCase):
    url = '/api/v2/check-permission/'
    error_message = "Please pass a permission name in the 'permission' parameter"

    def get_resource_name(self):
        return 'check-permission'

    def test_check_permission_anonymous_no_parameters(self):
        """
        Test that logged-out users get a error message when they don't pass any parameter
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, self.error_message)

    def test_check_permission_anonymous_with_parameter(self):
        """
        Test that logged-out users always get False
        """
        response = self.client.get(self.url + '?permission=exercises.change_muscle')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], False)

    def test_check_no_parameter_logged_in(self):
        """
        Test that authenticated users get an error when not passing a parameter
        """
        self.authenticate('test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, self.error_message)

    def test_check_parameter_logged_in_no_permission(self):
        """
        Test that the api correctly returns the user's permission
        """
        self.authenticate('test')
        response = self.client.get(self.url + '?permission=exercises.change_muscle')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], False)

    def test_check_parameter_logged_in_wrong_permission(self):
        """
        Test that the result if false if passing a non-existent permission

        (this is the default behaviour of django)
        """
        self.authenticate('test')
        response = self.client.get(self.url + '?permission=foo.bar_baz')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], False)

    def test_check_parameter_logged_in_admin(self):
        """
        Test that the api correctly returns the user's permission
        """
        self.authenticate('admin')
        response = self.client.get(self.url + '?permission=exercises.change_muscle')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], True)
