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

import datetime

from django.core.urlresolvers import reverse

from wger.nutrition.models import Ingredient

from wger.manager.tests.testcase import WorkoutManagerTestCase


class DeleteIngredientTestCase(WorkoutManagerTestCase):
    '''
    Tests deleting an ingredient
    '''

    def delete_ingredient(self, fail=False):
        '''
        Helper function to test deleting an ingredient
        '''

        # Fetch the edit page
        count_before = Ingredient.objects.count()
        response = self.client.get(reverse('ingredient-delete', kwargs={'pk': 1}))
        count_after = Ingredient.objects.count()

        self.assertEqual(count_before, count_after)

        if fail:
            self.assertIn(response.status_code, (302, 403))
            self.assertTemplateUsed('login.html')

        else:
            self.assertEqual(response.status_code, 200)

        # Try to delete the ingredient
        count_before = Ingredient.objects.count()
        response = self.client.post(reverse('ingredient-delete', kwargs={'pk': 1}))
        count_after = Ingredient.objects.count()

        if fail:
            self.assertIn(response.status_code, (302, 403))
            self.assertTemplateUsed('login.html')
            self.assertEqual(count_before, count_after)

        else:
            self.assertRaises(Ingredient.DoesNotExist, Ingredient.objects.get, pk=1)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(count_before - 1, count_after)

    def test_delete_ingredient_anonymous(self):
        '''
        Test deleting an ingredient as an anonymous users
        '''

        self. delete_ingredient(fail=True)

    def test_delete_ingredient_authorized(self):
        '''
        Test deleting an ingredient as an authorized user
        '''

        self.user_login('admin')
        self.delete_ingredient(fail=False)

    def test_delete_ingredient_other(self):
        '''
        Test deleting an ingredient as an unauthorized, logged in user
        '''

        self.user_login('test')
        self.delete_ingredient(fail=True)
