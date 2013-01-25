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

from wger.exercises.models import ExerciseCategory
from wger.manager.tests.testcase import WorkoutManagerTestCase


class ExerciseCategoryTestCase(WorkoutManagerTestCase):
    '''
    Exercise category test case
    '''

    def delete_category(self, fail=False):
        '''
        Helper function to test deleting categories
        '''

        response = self.client.get(reverse('exercisecategory-delete',
                                           kwargs={'pk': 4}))
        # Can the user access the page
        if fail:
            self.assertEqual(response.status_code, 302)
        else:
            self.assertEqual(response.status_code, 200)

        # Delete the category
        count_before = ExerciseCategory.objects.count()
        response = self.client.post(reverse('exercisecategory-delete',
                                            kwargs={'pk': 4}))
        count_after = ExerciseCategory.objects.count()

        # There is a redirect
        self.assertEqual(response.status_code, 302)

        # Check the deletion
        if fail:
            self.assertEqual(count_before,
                             count_after,
                             'Category was deleted by unauthorzed user')
        else:
            self.assertTrue(count_before > count_after,
                            'Category was not deleted by authorized user')

    def test_delete_category_unauthorized(self):
        '''
        Test deleting a category by an unauthorized user
        '''

        self.user_login('test')
        self.delete_category(fail=True)

    def test_delete_category_anonymous(self):
        '''
        Test deleting a category by an anonymous user
        '''

        self.user_logout()
        self.delete_category(fail=True)
        self.user_logout()

    def test_delete_category_authorized(self):
        '''
        Test deleting a category by an authorized user
        '''

        self.user_login()
        self.delete_category()
        self.user_logout()

    def edit_category(self, fail=False):
        '''
        Helper function to test editing categories
        '''

        category = ExerciseCategory.objects.get(pk=3)
        old_name = category.name

        response = self.client.get(reverse('exercisecategory-edit', kwargs={'pk': 3}))

        # Did it work
        if fail:
            self.assertEqual(response.status_code, 302)
        else:
            self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('exercisecategory-edit',
                                            kwargs={'pk': 3}),
                                    {'name': 'A different name'})

        # There is a redirect
        self.assertEqual(response.status_code, 302)

        category = ExerciseCategory.objects.get(pk=3)
        new_name = category.name

        # Did it work
        if fail:
            self.assertEqual(old_name,
                             new_name,
                             'Category was edited by unauthorzed user')
        else:
            self.assertTrue(old_name != new_name,
                            'Category wasnt deleted by unauthorzed user')

        # No name
        if not fail:
            response = self.client.post(reverse('exercisecategory-edit',
                                                kwargs={'pk': 3}),
                                        {'name': ''})

            self.assertTrue(response.context['form'].errors['name'])

    def test_edit_category_unauthorized(self):
        '''
        Test editing a category by an unauthorized user
        '''

        self.user_login('test')
        self.edit_category(fail=True)

    def test_edit_category_anonymous(self):
        '''
        Test editing a category by an anonymous user
        '''

        self.user_logout()
        self.edit_category(fail=True)

    def test_edit_category_authorized(self):
        '''
        Test editing a category by an authorized user
        '''

        self.user_login()
        self.edit_category()

    def add_category(self, fail=False):
        '''
        Helper function to test adding categories
        '''

        response = self.client.get(reverse('exercisecategory-add'))

        # Did it work?
        if fail:
            self.assertEqual(response.status_code, 302)
        else:
            self.assertEqual(response.status_code, 200)

        count_before = ExerciseCategory.objects.count()
        response = self.client.post(reverse('exercisecategory-add'),
                                    {'name': 'A new category'})
        count_after = ExerciseCategory.objects.count()

        # There is a redirect
        self.assertEqual(response.status_code, 302)

        # Did it work
        if fail:
            self.assertEqual(count_before, count_after)
        else:
            self.assertGreater(count_after, count_before)

    def test_add_category_unauthorized(self):
        '''
        Test adding a category by an unauthorized user
        '''

        self.user_login('test')
        self.add_category(fail=True)

    def test_add_category_anonymous(self):
        '''
        Test adding a category by an anonymous user
        '''

        self.edit_category(fail=True)

    def test_add_category_authorized(self):
        '''
        Test adding a category by an authorized user
        '''

        self.user_login()
        self.add_category()
