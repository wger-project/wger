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

from wger.exercises.models import Exercise
from wger.exercises.models import ExerciseComment

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase


class AddExerciseCommentTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a comment to an exercise
    '''

    object_class = ExerciseComment
    url = reverse('exercisecomment-add', kwargs={'exercise_pk': 1})
    pk = 3
    user_fail = False
    data = {'comment': 'a new cool comment'}


class EditExerciseCommentTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a comment to an exercise
    '''

    object_class = ExerciseComment
    url = 'exercisecomment-edit'
    pk = 1
    data = {'comment': 'an edited comment'}


class ExercisecommentsTestCase(WorkoutManagerTestCase):

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
        '''
        Tests the exercise comments
        '''

        self.user_login('test')
        self.exercise_delete_comment(fail=True)
        self.user_logout()

    def test_exercise_delete_comment_not_logged_in(self):
        '''
        Tests the exercise comments
        '''

        self.exercise_delete_comment(fail=True)

    def test_exercise_delete_comment_authorized(self):
        '''
        Tests the exercise comments
        '''

        self.user_login()
        self.exercise_delete_comment(fail=False)
