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

from django.core.files import File
from django.core.urlresolvers import reverse

from wger.core.tests.base_testcase import (
    WorkoutManagerTestCase,
    WorkoutManagerEditTestCase,
    WorkoutManagerAddTestCase,
    WorkoutManagerDeleteTestCase
)
from wger.exercises.models import Exercise, ExerciseImage


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
            File(open('wger/exercises/tests/{0}'.format(filename), 'rb'))
        )
        image.save()
        return(image.pk)

    def test_auto_main_image(self):
        '''
        Tests that the first uploaded image is automatically a main image
        '''

        exercise = Exercise.objects.get(pk=2)
        pk = self.save_image(exercise, 'protestschwein.jpg')

        image = ExerciseImage.objects.get(pk=pk)
        self.assertTrue(image.is_main)

    def test_auto_main_image_multiple(self):
        '''
        Tests that there is always a main image after deleting one
        '''

        exercise = Exercise.objects.get(pk=2)
        pk1 = self.save_image(exercise, 'protestschwein.jpg')
        pk2 = self.save_image(exercise, 'wildschwein.jpg')

        image = ExerciseImage.objects.get(pk=pk1)
        self.assertTrue(image.is_main)

        image = ExerciseImage.objects.get(pk=pk2)
        self.assertFalse(image.is_main)

    def test_delete_main_image(self):
        '''
        Tests that there is always a main image after deleting one
        '''

        exercise = Exercise.objects.get(pk=2)
        pk1 = self.save_image(exercise, 'protestschwein.jpg')
        pk2 = self.save_image(exercise, 'protestschwein.jpg')
        pk3 = self.save_image(exercise, 'wildschwein.jpg')
        pk4 = self.save_image(exercise, 'wildschwein.jpg')
        pk5 = self.save_image(exercise, 'wildschwein.jpg')

        image = ExerciseImage.objects.get(pk=pk1)
        self.assertTrue(image.is_main)
        image.delete()

        self.assertTrue(ExerciseImage.objects.get(pk=pk2).is_main)
        self.assertFalse(ExerciseImage.objects.get(pk=pk3).is_main)
        self.assertFalse(ExerciseImage.objects.get(pk=pk4).is_main)
        self.assertFalse(ExerciseImage.objects.get(pk=pk5).is_main)

        image = ExerciseImage.objects.get(pk=pk2)
        self.assertTrue(image.is_main)
        image.delete()

        self.assertTrue(ExerciseImage.objects.get(pk=pk3).is_main)
        self.assertFalse(ExerciseImage.objects.get(pk=pk4).is_main)
        self.assertFalse(ExerciseImage.objects.get(pk=pk5).is_main)


class AddExerciseImageTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding an image to an exercise
    '''

    object_class = ExerciseImage
    url = reverse('exercise:image:add', kwargs={'exercise_pk': 1})
    user_fail = False
    data = {'is_main': True,
            'image': open('wger/exercises/tests/protestschwein.jpg', 'rb'),
            'license': 1}


class EditExerciseImageTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing an image to an exercise
    '''

    object_class = ExerciseImage
    url = 'exercise:image:edit'
    pk = 2
    data = {'is_main': True,
            'license': 1}


class DeleteExerciseImageTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting an image to an exercise
    '''

    object_class = ExerciseImage
    url = reverse('exercise:image:delete', kwargs={'exercise_pk': 1, 'pk': 1})
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
