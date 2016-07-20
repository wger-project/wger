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

from django.core import mail
from django.core.urlresolvers import reverse

from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.exercises.models import ExerciseImage


class ImagePendingDetailTestCase(WorkoutManagerTestCase):
    '''
    Tests the detail page of an exercise with a pending image
    '''

    def pending_view(self, fail=False):
        '''
        Helper function
        '''
        response = self.client.get(reverse('exercise:exercise:view', kwargs={'id': 2}))
        self.assertEqual(response.status_code, 200)

        if not fail:
            self.assertContains(response, 'Images pending review')
            self.assertContains(response, 'Accept')
            self.assertContains(response, 'Decline')
        else:
            self.assertNotContains(response, 'Images pending review')
            self.assertNotContains(response, 'Accept')
            self.assertNotContains(response, 'Decline')

    def test_pending_view_admin(self):
        '''
        Tests the detail page of an exercise with a pending image as an admin user
        '''

        self.user_login('admin')
        self.pending_view()

    def test_pending_view_user(self):
        '''
        Tests the detail page of an exercise with a pending image as a regular user
        '''

        self.user_login('test')
        self.pending_view(fail=True)

    def test_pending_view_logged_out(self):
        '''
        Tests the detail page of an exercise with a pending image as a logged out user
        '''

        self.pending_view(fail=True)


class ImageAcceptTestCase(WorkoutManagerTestCase):
    '''
    Tests accepting a user submitted exercise image
    '''

    def accept(self, fail=False):
        '''
        Helper function
        '''
        image = ExerciseImage.objects.get(pk=3)
        self.assertEqual(image.status, ExerciseImage.STATUS_PENDING)
        response = self.client.get(reverse('exercise:image:accept', kwargs={'pk': 3}))
        image = ExerciseImage.objects.get(pk=3)
        self.assertEqual(response.status_code, 302)

        if not fail:
            self.assertEqual(image.status, ExerciseImage.STATUS_ACCEPTED)
            response = self.client.get(response['Location'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(mail.outbox), 0)
        else:
            self.assertEqual(image.status, ExerciseImage.STATUS_PENDING)
            self.assertEqual(len(mail.outbox), 0)

    def test_accept_admin(self):
        '''
        Tests accepting a user submitted exercise image as an admin user
        '''

        self.user_login('admin')
        self.accept()

    def test_accept_user(self):
        '''
        Tests accepting a user submitted exercise image as a regular user
        '''

        self.user_login('test')
        self.accept(fail=True)

    def test_accept_logged_out(self):
        '''
        Tests accepting a user submitted exercise as a logged out user
        '''

        self.accept(fail=True)


class ImageRejectTestCase(WorkoutManagerTestCase):
    '''
    Tests rejecting a user submitted exercise image
    '''

    def reject(self, fail=False):
        '''
        Helper function
        '''
        image = ExerciseImage.objects.get(pk=3)
        self.assertEqual(image.status, ExerciseImage.STATUS_PENDING)
        response = self.client.get(reverse('exercise:image:decline', kwargs={'pk': 3}))
        image = ExerciseImage.objects.get(pk=3)
        self.assertEqual(response.status_code, 302)

        if not fail:
            self.assertEqual(image.status, ExerciseImage.STATUS_DECLINED)
            response = self.client.get(response['Location'])
            self.assertEqual(response.status_code, 200)

        else:
            self.assertEqual(image.status, ExerciseImage.STATUS_PENDING)

    def test_reject_admin(self):
        '''
        Tests rejecting a user submitted exercise image as an admin user
        '''

        self.user_login('admin')
        self.reject()

    def test_reject_user(self):
        '''
        Tests rejecting a user submitted exercise image as a regular user
        '''

        self.user_login('test')
        self.reject(fail=True)

    def test_reject_logged_out(self):
        '''
        Tests rejecting a user submitted exercise image as a logged out user
        '''

        self.reject(fail=True)
