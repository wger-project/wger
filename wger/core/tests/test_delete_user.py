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

import logging
import datetime
import decimal

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from wger.core.models import UserProfile
from wger.core.tests import api_base_test

from wger.utils.constants import TWOPLACES
from wger.weight.models import WeightEntry
from wger.manager.tests.testcase import WorkoutManagerTestCase

logger = logging.getLogger('wger.custom')


class DeleteUserTestCase(WorkoutManagerTestCase):
    '''
    Tests deleting the user account and all his data
    '''

    def delete_user(self, fail=False):
        '''
        Helper function
        '''
        response = self.client.get(reverse('core:user-delete'))
        self.assertEqual(User.objects.filter(username='test').count(), 1)
        if fail:
            self.assertEqual(response.status_code, 302)
        else:
            self.assertEqual(response.status_code, 200)

        # Wrong user password
        if not fail:
            response = self.client.post(reverse('core:user-delete'),
                                        {'password': 'not the user password'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(User.objects.filter(username='test').count(), 1)

        # Correct user password
        response = self.client.post(reverse('core:user-delete'), {'password': 'testtest'})
        self.assertEqual(response.status_code, 302)
        if not fail:
            self.assertEqual(User.objects.filter(username='test').count(), 0)

    def test_delete_user_logged_in(self):
        '''
        Tests deleting the own account as a logged in user
        '''
        self.user_login('test')
        self.delete_user(fail=False)

    def test_delete_user_anonymous(self):
        '''
        Tests deleting the own account as an anonymous user
        '''
        self.delete_user(fail=True)
