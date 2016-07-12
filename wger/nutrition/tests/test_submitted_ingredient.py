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
from wger.nutrition.models import Ingredient


class IngredientsPendingTestCase(WorkoutManagerTestCase):
    '''
    Tests the pending ingredients overview page
    '''

    def pending_overview(self, fail=False):
        '''
        Helper function
        '''
        response = self.client.get(reverse('nutrition:ingredient:pending'))
        if not fail:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context['ingredient_list']), 1)
        else:
            self.assertIn(response.status_code, (302, 403))

    def test_pending_overview_admin(self):
        '''
        Tests the pending exercises overview page as an admin user
        '''

        self.user_login('admin')
        self.pending_overview()

    def test_pending_overview_user(self):
        '''
        Tests the pending exercises overview page as a regular user
        '''

        self.user_login('test')
        self.pending_overview(fail=True)

    def test_pending_overview_logged_out(self):
        '''
        Tests the pending exercises overview page as a logged out user
        '''

        self.pending_overview(fail=True)


class IngredientsPendingDetailTestCase(WorkoutManagerTestCase):
    '''
    Tests the detail page of a pending ingredient
    '''

    def pending_view(self, fail=False):
        '''
        Helper function
        '''
        response = self.client.get(reverse('nutrition:ingredient:view', kwargs={'id': 7}))
        self.assertContains(response, 'pending review')

        if not fail:
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Please select one of the options below')
            self.assertContains(response, 'Accept')
            self.assertContains(response, 'Decline')
        else:
            self.assertNotContains(response, 'Please select one of the options below')
            self.assertNotContains(response, 'Accept')
            self.assertNotContains(response, 'Decline')

    def test_pending_view_admin(self):
        '''
        Tests the detail page of a pending exercise as an admin user
        '''

        self.user_login('admin')
        self.pending_view()

    def test_pending_view_user(self):
        '''
        Tests the detail page of a pending exercise as a regular user
        '''

        self.user_login('test')
        self.pending_view(fail=True)

    def test_pending_view_logged_out(self):
        '''
        Tests the detail page of a pending exercise as a logged out user
        '''

        self.pending_view(fail=True)


class IngredientAcceptTestCase(WorkoutManagerTestCase):
    '''
    Tests accepting a user submitted ingredient
    '''

    def accept(self, fail=False):
        '''
        Helper function
        '''
        ingredient = Ingredient.objects.get(pk=7)
        self.assertEqual(ingredient.status, Ingredient.INGREDIENT_STATUS_PENDING)
        response = self.client.get(reverse('nutrition:ingredient:accept', kwargs={'pk': 7}))
        ingredient = Ingredient.objects.get(pk=7)
        self.assertEqual(response.status_code, 302)

        if not fail:
            self.assertEqual(ingredient.status, Ingredient.INGREDIENT_STATUS_ACCEPTED)
            response = self.client.get(response['Location'])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(mail.outbox), 1)
        else:
            self.assertEqual(ingredient.status, Ingredient.INGREDIENT_STATUS_PENDING)
            self.assertEqual(len(mail.outbox), 0)

    def test_accept_admin(self):
        '''
        Tests accepting a user submitted ingredient as an admin user
        '''

        self.user_login('admin')
        self.accept(fail=False)

    def test_accept_user(self):
        '''
        Tests accepting a user submitted ingredient as a regular user
        '''

        self.user_login('test')
        self.accept(fail=True)

    def test_accept_logged_out(self):
        '''
        Tests accepting a user submitted ingredient as a logged out user
        '''

        self.accept(fail=True)


class IngredientRejectTestCase(WorkoutManagerTestCase):
    '''
    Tests rejecting a user submitted ingredient
    '''

    def reject(self, fail=False):
        '''
        Helper function
        '''
        ingredient = Ingredient.objects.get(pk=7)
        self.assertEqual(ingredient.status, Ingredient.INGREDIENT_STATUS_PENDING)
        response = self.client.get(reverse('nutrition:ingredient:decline', kwargs={'pk': 7}))
        ingredient = Ingredient.objects.get(pk=7)
        self.assertEqual(response.status_code, 302)

        if not fail:
            self.assertEqual(ingredient.status, Ingredient.INGREDIENT_STATUS_DECLINED)
            response = self.client.get(response['Location'])
            self.assertEqual(response.status_code, 200)

        else:
            self.assertEqual(ingredient.status, Ingredient.INGREDIENT_STATUS_PENDING)

    def test_reject_admin(self):
        '''
        Tests rejecting a user submitted ingredient as an admin user
        '''

        self.user_login('admin')
        self.reject()

    def test_reject_user(self):
        '''
        Tests rejecting a user submitted ingredient as a regular user
        '''

        self.user_login('test')
        self.reject(fail=True)

    def test_reject_logged_out(self):
        '''
        Tests rejecting a user submitted ingredient as a logged out user
        '''

        self.reject(fail=True)
