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
from django.core.files import File
from wger.core.tests import api_base_test

from wger.exercises.models import Exercise
from wger.exercises.models import ExerciseImage

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase


class MainImageTestCase(WorkoutManagerTestCase):
    '''
    Tests the methods to make sure there is always a main image per picture
    '''

    def save_image(self, exercise, filename, db_filename=None):
        '''
        Helper function to save an image to an exercise
        '''
        if not db_filename:
            db_filename = filename
        image = ExerciseImage()
        image.exercise = exercise
        image.status = ExerciseImage.STATUS_ACCEPTED
        image.image.save(
            filename,
            File(open('wger/exercises/tests/{0}'.format(filename)), 'rb')
        )
        image.save()

    def test_auto_main_image(self):
        '''
        Tests that the first uploaded image is automatically a main image
        '''

        exercise = Exercise.objects.get(pk=2)
        self.save_image(exercise, 'protestschwein.jpg')

        image = ExerciseImage.objects.get(pk=4)
        self.assertTrue(image.is_main)

    def test_auto_main_image_multiple(self):
        '''
        Tests that there is always a main image after deleting one
        '''

        exercise = Exercise.objects.get(pk=2)
        self.save_image(exercise, 'protestschwein.jpg')
        self.save_image(exercise, 'wildschwein.jpg')

        image = ExerciseImage.objects.get(pk=4)
        self.assertTrue(image.is_main)

        image = ExerciseImage.objects.get(pk=5)
        self.assertFalse(image.is_main)

    def test_delete_main_image(self):
        '''
        Tests that there is always a main image after deleting one
        '''

        exercise = Exercise.objects.get(pk=2)
        self.save_image(exercise, 'protestschwein.jpg')
        self.save_image(exercise, 'protestschwein.jpg')
        self.save_image(exercise, 'wildschwein.jpg')
        self.save_image(exercise, 'wildschwein.jpg')
        self.save_image(exercise, 'wildschwein.jpg')

        image = ExerciseImage.objects.get(pk=4)
        self.assertTrue(image.is_main)
        image.delete()

        self.assertTrue(ExerciseImage.objects.get(pk=5).is_main)
        self.assertFalse(ExerciseImage.objects.get(pk=6).is_main)
        self.assertFalse(ExerciseImage.objects.get(pk=7).is_main)
        self.assertFalse(ExerciseImage.objects.get(pk=8).is_main)

        image = ExerciseImage.objects.get(pk=5)
        self.assertTrue(image.is_main)
        image.delete()

        self.assertTrue(ExerciseImage.objects.get(pk=6).is_main)
        self.assertFalse(ExerciseImage.objects.get(pk=7).is_main)
        self.assertFalse(ExerciseImage.objects.get(pk=8).is_main)


class AddExerciseImageTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding an image to an exercise
    '''

    object_class = ExerciseImage
    url = reverse('exerciseimage-add', kwargs={'exercise_pk': 1})
    pk = 4
    user_fail = False
    data = {'is_main': True,
            'image': open('wger/exercises/tests/protestschwein.jpg', 'rb'),
            'license': 1}


class EditExerciseImageTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing an image to an exercise
    '''

    object_class = ExerciseImage
    url = 'exerciseimage-edit'
    pk = 2
    data = {'is_main': True,
            'license': 1}


class DeleteExerciseImageTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting an image to an exercise
    '''

    object_class = ExerciseImage
    url = reverse('exerciseimage-delete', kwargs={'exercise_pk': 1, 'pk': 1})
    pk = 1


# TODO: fix test
# class ExerciseImagesApiTestCase(api_base_test.ApiBaseResourceTestCase):
#     '''
#     Tests the exercise image overview resource
#     '''
#     pk = 1
#     resource = ExerciseImage
#     private_resource = False
#     special_endpoints = ('thumbnails',)
#     data = {'is_main': 'true',
#             'exercise': '1',
#             'id': 1}
