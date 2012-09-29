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


"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse

from exercises.models import Exercise
from exercises.models import ExerciseCategory

from exercises.tests.testcase import WorkoutManagerTestCase

class ExerciseCategoryTestCase(WorkoutManagerTestCase):
    """Exercise category test case"""
  
    def delete_category(self, fail = False):
        """Helper function to test deleting categories"""
        
        # Delete the category
        count_before =  ExerciseCategory.objects.count()
        response = self.client.get(reverse('exercises.views.exercise_category_delete',
                                           kwargs={'id': 4}))
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
        """Test deleting a category by an unauthorized user"""
        
        self.user_login('test')
        self.delete_category(fail=True)
        self.user_logout()
    
    def test_delete_category_anonymous(self):
        """Test deleting a category by an anonymous user"""
        
        self.user_logout()
        self.delete_category(fail=True)
        self.user_logout()
    
    def test_delete_category_authorized(self):
        """Test deleting a category by an authorized user"""
        
        self.user_login()
        self.delete_category()
        self.user_logout()
    
    
    def edit_category(self, fail = False):
        """Helper function to test editing categories"""
        
        category = ExerciseCategory.objects.get(pk = 3)
        old_name = category.name
        
        response = self.client.post(reverse('exercises.views.exercise_category_edit',
                                           kwargs={'id': 3}),
                                   {'name': 'A different name'})
        
        # There is a redirect
        self.assertEqual(response.status_code, 302)
        
        category = ExerciseCategory.objects.get(pk = 3)
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
            response = self.client.post(reverse('exercises.views.exercise_category_edit',
                                           kwargs={'id': 3}),
                                        {'name': ''})

            self.assertTrue(response.context['category_form'].errors['name'])
        
    def test_edit_category_unauthorized(self):
        """Test deleting a category by an unauthorized user"""
        
        self.user_login('test')
        self.edit_category(fail=True)
        self.user_logout()
    
    def test_edit_category_anonymous(self):
        """Test deleting a category by an anonymous user"""
        
        self.user_logout()
        self.edit_category(fail=True)
        self.user_logout()
    
    def test_edit_category_authorized(self):
        """Test deleting a category by an authorized user"""
        
        self.user_login()
        self.edit_category()
        self.user_logout()
    
