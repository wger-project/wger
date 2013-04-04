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

from django.core.urlresolvers import reverse
from django.core.management import call_command

from django.contrib.auth.models import User

from wger.manager.tests.testcase import WorkoutManagerTestCase


class DemoUserTestCase(WorkoutManagerTestCase):
    '''
    Tests the demo user
    '''

    def test_demo_user(self):
        '''
        Tests creating a demo user
        '''

        # Open the copy workout form
        response = self.client.get(reverse('demo-account'))
        self.assertEqual(response.status_code, 200)

        # Submit the form
        count_before = User.objects.count()
        response = self.client.post(reverse('demo-account'),
                                    {'recaptcha_response_field': 'PASSED'})
        count_after = User.objects.count()

        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('dashboard'))

        # Check that the demo user was correctly created
        self.assertEqual(count_before + 1, count_after)
        self.assertTrue(User.objects.filter(userprofile__is_temporary=1).count(), 2)

    def test_demo_user_notice(self):
        '''
        Tests that demo users see a notice on every page
        '''
        demo_notice_text = 'You are using a temporary account'
        self.user_login('demo')
        self.assertContains(self.client.get(reverse('dashboard')), demo_notice_text)
        self.assertContains(self.client.get(reverse('wger.manager.views.workout.overview')),
                            demo_notice_text)
        self.assertContains(self.client.get(reverse('wger.exercises.views.exercises.overview')),
                            demo_notice_text)
        self.assertContains(self.client.get(reverse('muscle-overview')), demo_notice_text)
        self.assertContains(self.client.get(reverse('wger.nutrition.views.plan.overview')),
                            demo_notice_text)
        self.assertContains(self.client.get(reverse('software:issues')), demo_notice_text)
        self.assertContains(self.client.get(reverse('software:license')), demo_notice_text)

    def test_command_delete_old_users(self):
        '''
        Tests that old demo users are deleted by the management command
        '''

        # Create some new demo users
        self.client.post(reverse('demo-account'), {'recaptcha_response_field': 'PASSED'})
        self.client.post(reverse('demo-account'), {'recaptcha_response_field': 'PASSED'})
        self.client.post(reverse('demo-account'), {'recaptcha_response_field': 'PASSED'})
        self.client.post(reverse('demo-account'), {'recaptcha_response_field': 'PASSED'})
        self.client.post(reverse('demo-account'), {'recaptcha_response_field': 'PASSED'})
        self.client.post(reverse('demo-account'), {'recaptcha_response_field': 'PASSED'})
        User.objects.filter().update(date_joined='2013-01-01 00:00+01:00')

        # These ones keep the date_joined field
        self.client.post(reverse('demo-account'), {'recaptcha_response_field': 'PASSED'})
        self.client.post(reverse('demo-account'), {'recaptcha_response_field': 'PASSED'})

        # Check and delete
        self.assertEqual(User.objects.filter(userprofile__is_temporary=1).count(), 9)
        call_command('delete-temp-users')
        self.assertEqual(User.objects.filter(userprofile__is_temporary=1).count(), 2)
