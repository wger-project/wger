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

# Third Party
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

# wger
from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.utils.helpers import make_token


class WorkoutJSONLogExportTestCase(WorkoutManagerTestCase):
    '''
    Tests exporting a workout as a JSON file
    '''

    def export_JSON_token(self):
        '''
        Helper function to test exporting a workout as a JSON file using tokens
        '''

        user = User.objects.get(username='test')
        uid, token = make_token(user)
        response = self.client.get(reverse('manager:workout:json-workout', kwargs={'id': 3,
                                                                                   'uidb64': uid,
                                                                                   'token': token}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename=Workout-3.json')

    def export_JSON_token_wrong(self):
        '''
        Helper function to test exporting a workout as a JSON file using a wrong token
        '''

        uid = 'AB'
        token = 'abc-11223344556677889900'
        response = self.client.get(reverse('manager:workout:json-workout', kwargs={'id': 3,
                                                                                   'uidb64': uid,
                                                                                   'token': token}))

        self.assertEqual(response.status_code, 403)

    def export_JSON(self, fail=False):
        '''
        Helper function to test exporting a workout as a JSON file
        '''

        response = self.client.get(reverse('manager:workout:json-workout', kwargs={'id': 3}))

        if fail:
            self.assertIn(response.status_code, (403, 404, 302))
        else:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
            self.assertEqual(response['Content-Disposition'], 'attachment; filename=Workout-3.json')

    def test_export_JSON_anonymous(self):
        '''
        Tests exporting a workout as a JSON file as an anonymous user
        '''

        self.export_JSON(fail=True)
        self.export_JSON_token()
        self.export_JSON_token_wrong()

    def test_export_JSON_owner(self):
        '''
        Tests exporting a workout as a JSON file as the owner user
        '''

        self.user_login('test')
        self.export_JSON(fail=False)
        self.export_JSON_token()
        self.export_JSON_token_wrong()

    def test_export_JSON_other(self):
        '''
        Tests exporting a workout as a JSON file as a logged user not owning the data
        '''

        self.user_login('admin')
        self.export_JSON(fail=True)
        self.export_JSON_token()
        self.export_JSON_token_wrong()
