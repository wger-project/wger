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


from django.test import TestCase
from django.core.urlresolvers import reverse

from wger.exercises.models import Exercise
from wger.exercises.models import ExerciseCategory

from wger.manager.tests.testcase import WorkoutManagerTestCase


class ExercisecommentsTestCase(WorkoutManagerTestCase):
    
    def exercise_add_comment(self, fail=True):
        """Tests the exercise comments (fails because of permissions)"""
        
        # Load the exercise
        exercise_1 = Exercise.objects.get(pk=1)
        
        # Comments are loaded
        comments = exercise_1.exercisecomment_set.all()
        comment_1 = comments[0]
        self.assertEqual(comment_1.id, 1)
        self.assertEqual(comment_1.comment, "test 123")
        self.assertEqual(len(comments), 1)
        
        # Post a comment
        response = self.client.post(reverse('exercisecomment-add', kwargs={'exercise_pk': 1}),
                                    {'comment': 'a new cool comment'})
        comments = exercise_1.exercisecomment_set.all()
        
        self.assertEqual(response.status_code, 302)
        if fail:
            comments = exercise_1.exercisecomment_set.all()
            self.assertEqual(len(comments), 1)

        else:
            self.assertEqual(len(comments), 2)
        
        # Post an empty comment and check it doesn't get added
        response = self.client.post(reverse('exercisecomment-add', kwargs={'exercise_pk': 1}), 
                                    {'comment': ''})
        comments = exercise_1.exercisecomment_set.all()
        
        if fail:
            self.assertEqual(len(comments), 1)
        else:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(comments), 2)
        
        
    def test_exercise_add_comment_no_authorized(self):
        """Tests the exercise comments"""
        
        self.user_login('test')
        self.exercise_add_comment(fail=True)
        self.user_logout()
    
    def test_exercise_add_comment_not_logged_in(self):
        """Tests the exercise comments"""
        
        self.exercise_add_comment(fail=True)
        
    
    def test_exercise_add_comment_authorized(self):
        """Tests the exercise comments"""
        
        self.user_login()
        self.exercise_add_comment(fail=False)
        
    
    def exercise_delete_comment(self, fail=True):
        '''
        Tests the deletion of exercise comments
        '''
        
        # Load the exercise
        exercise_1 = Exercise.objects.get(pk=1)
        
        # Comments are loaded
        comments = exercise_1.exercisecomment_set.all()
        comment_1 = comments[0]
        self.assertEqual(comment_1.id, 1)
        self.assertEqual(comment_1.comment, "test 123")
        self.assertEqual(len(comments), 1)
        
        # Delete the comment
        response = self.client.post(reverse('exercisecomment-delete', kwargs={'id': 1}))
        comments = exercise_1.exercisecomment_set.all()
        
        self.assertEqual(response.status_code, 302)
        if fail:
            comments = exercise_1.exercisecomment_set.all()
            self.assertEqual(len(comments), 1)

        else:
            self.assertEqual(len(comments), 0)
        
        
    def test_exercise_delete_comment_no_authorized(self):
        """Tests the exercise comments"""
        
        self.user_login('test')
        self.exercise_delete_comment(fail=True)
        self.user_logout()
    
    def test_exercise_delete_comment_not_logged_in(self):
        """Tests the exercise comments"""
        
        self.exercise_delete_comment(fail=True)
        
    
    def test_exercise_delete_comment_authorized(self):
        """Tests the exercise comments"""
        
        self.user_login()
        self.exercise_delete_comment(fail=False)
        
        
    def exercise_edit_comment(self, fail=True):
        """Tests the exercise comments (fails because of permissions)"""
        
        # Load the exercise
        exercise_1 = Exercise.objects.get(pk=1)
        comment_before = 'test 123'
        comment_after = 'a new cool comment'
        
        # Comments are loaded
        comments = exercise_1.exercisecomment_set.all()
        comment_1 = comments[0]
        self.assertEqual(comment_1.id, 1)
        self.assertEqual(comment_1.comment, comment_before)
        self.assertEqual(len(comments), 1)
        
        # Open the edit page
        response = self.client.get(reverse('exercisecomment-edit', kwargs={'pk': 1}))
        if fail:
            self.assertEqual(response.status_code, 302)
        else:
            self.assertEqual(response.status_code, 200)   
        
        # Edit the comment
        response = self.client.post(reverse('exercisecomment-edit', kwargs={'pk': 1}),
                                    {'comment': comment_after})
        comments = exercise_1.exercisecomment_set.all()
        comment_1 = comments[0]
        
        if fail:
            self.assertEqual(comment_1.comment, comment_before)
        else:
            self.assertEqual(comment_1.comment, comment_after)
        
        
        
    def test_exercise_edit_comment_no_authorized(self):
        """Tests the exercise comments"""
        
        self.user_login('test')
        self.exercise_edit_comment(fail=True)
    
    def test_exercise_edit_comment_not_logged_in(self):
        """Tests the exercise comments"""
        
        self.exercise_edit_comment(fail=True)
        
    def test_exercise_edit_comment_authorized(self):
        """Tests the exercise comments"""
        
        self.user_login()
        self.exercise_edit_comment(fail=False)
