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


from django.core.cache import cache
from django.core.urlresolvers import reverse

from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import (
    WorkoutManagerTestCase,
    WorkoutManagerEditTestCase,
    WorkoutManagerAddTestCase
)
from wger.exercises.models import Exercise, ExerciseComment
from wger.utils.cache import cache_mapper


class ExerciseCommentRepresentationTestCase(WorkoutManagerTestCase):
    '''
    Test the representation of a model
    '''

    def test_representation(self):
        '''
        Test that the representation of an object is correct
        '''
        self.assertEqual("{0}".format(ExerciseComment.objects.get(pk=1)), 'test 123')


class AddExerciseCommentTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding a comment to an exercise
    '''

    object_class = ExerciseComment
    url = reverse('exercise:comment:add', kwargs={'exercise_pk': 1})
    user_fail = False
    data = {'comment': 'a new cool comment'}


class EditExerciseCommentTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing a comment to an exercise
    '''

    object_class = ExerciseComment
    url = 'exercise:comment:edit'
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
        response = self.client.post(reverse('exercise:comment:delete', kwargs={'id': 1}))
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


class WorkoutCacheTestCase(WorkoutManagerTestCase):
    '''
    Workout cache test case
    '''

    def test_canonical_form_cache_save(self):
        '''
        Tests the workout cache when saving
        '''
        comment = ExerciseComment.objects.get(pk=1)
        for set in comment.exercise.set_set.all():
            set.exerciseday.training.canonical_representation
            workout_id = set.exerciseday.training_id
            self.assertTrue(cache.get(cache_mapper.get_workout_canonical(workout_id)))

            comment.save()
            self.assertFalse(cache.get(cache_mapper.get_workout_canonical(workout_id)))

    def test_canonical_form_cache_delete(self):
        '''
        Tests the workout cache when deleting
        '''
        comment = ExerciseComment.objects.get(pk=1)

        workout_ids = []
        for set in comment.exercise.set_set.all():
            workout_id = set.exerciseday.training_id
            workout_ids.append(workout_id)
            set.exerciseday.training.canonical_representation
            self.assertTrue(cache.get(cache_mapper.get_workout_canonical(workout_id)))

        comment.delete()
        for workout_id in workout_ids:
            self.assertFalse(cache.get(cache_mapper.get_workout_canonical(workout_id)))


class ExerciseCommentApiTestCase(api_base_test.ApiBaseResourceTestCase):
    '''
    Tests the exercise comment overview resource
    '''
    pk = 1
    resource = ExerciseComment
    private_resource = False
    data = {"comment": "a cool comment",
            "exercise": "1",
            "id": 1}
