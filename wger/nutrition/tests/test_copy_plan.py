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

from django.core.urlresolvers import reverse

from wger.core.tests.base_testcase import WorkoutManagerTestCase
from wger.nutrition.models import NutritionPlan


class CopyPlanTestCase(WorkoutManagerTestCase):
    '''
    Tests copying a nutritional plan
    '''

    def copy_plan(self, fail=False):
        '''
        Helper function to test copying nutrition plans
        '''

        # Open the copy nutritional plan form
        response = self.client.get(reverse('nutrition:plan:copy', kwargs={'pk': 4}))
        if fail:
            self.assertIn(response.status_code, (302, 403, 404))
        else:
            self.assertEqual(response.status_code, 302)

        # Copy the plan
        count_before = NutritionPlan.objects.count()
        response = self.client.post(reverse('nutrition:plan:copy', kwargs={'pk': 4}),
                                    {'comment': 'A copied plan'})
        count_after = NutritionPlan.objects.count()

        if fail:
            self.assertEqual(count_before, count_after)
        else:
            self.assertGreater(count_after, count_before)
            self.assertEqual(count_after, 7)

        # Test accessing the copied workout
        response = self.client.get(reverse('nutrition:plan:view', kwargs={'id': 4}))

        if fail:
            self.assertIn(response.status_code, (302, 403, 404))
        else:
            self.assertEqual(response.status_code, 200)

    def test_copy_plan_anonymous(self):
        '''
        Test copying a nutritional plan as an anonymous user
        '''

        self.copy_plan(fail=True)

    def test_copy_plan_owner(self):
        '''
        Test copying a nutritional plan as the owner user
        '''

        self.user_login('test')
        self.copy_plan(fail=False)

    def test_copy_plan_other(self):
        '''
        Test copying a nutritional plan as a logged in user not owning the plan
        '''

        self.user_login('admin')
        self.copy_plan(fail=True)
