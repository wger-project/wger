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
import logging

# Django
from django.contrib.auth.models import User
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase


logger = logging.getLogger(__name__)


class ChangePasswordTestCase(WgerTestCase):
    """
    Tests changing the password of a registered user
    """

    def change_password(self, fail=True):

        # Fetch the change passwort page
        response = self.client.get(reverse('core:user:change-password'))

        if fail:
            self.assertEqual(response.status_code, 302)
        else:
            self.assertEqual(response.status_code, 200)

        # Fill in the change password form
        form_data = {'old_password': 'testtest',
                     'new_password1': 'shuZoh2oGu7i',
                     'new_password2': 'shuZoh2oGu7i'}

        response = self.client.post(reverse('core:user:change-password'), form_data)
        self.assertEqual(response.status_code, 302)

        # Check the new password was accepted
        user = User.objects.get(username='test')
        if fail:
            self.assertTrue(user.check_password('testtest'))
        else:
            self.assertTrue(user.check_password('shuZoh2oGu7i'))

    def test_change_password_anonymous(self):
        """
        Test changing a password as an anonymous user
        """

        self.change_password()

    def test_copy_workout_logged_in(self, fail=True):
        """
        Test changing a password as a logged in user
        """

        self.user_login('test')
        self.change_password(fail=False)
