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

# Django
from django.core.files import File
from django.urls import reverse

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import (
    WgerAddTestCase,
    WgerDeleteTestCase,
    WgerEditTestCase,
    WgerTestCase,
)
from wger.exercises.models import (
    Exercise,
    ExerciseImage,
)


class MainImageTestCase(WgerTestCase):
    """
    Tests the methods to make sure there is always a main image per picture
    """

    def save_image(self, exercise, filename, db_filename=None) -> int:
        """
        Helper function to save an image to an exercise
        """
        with open(f'wger/exercises/tests/{filename}', 'rb') as inFile:
            if not db_filename:
                db_filename = filename
            image = ExerciseImage()
            image.exercise_base = exercise.exercise_base
            image.image.save(db_filename, File(inFile))
            image.save()
            return image.pk

    def test_auto_main_image(self):
        """
        Tests that the first uploaded image is automatically a main image
        """

        exercise = Exercise.objects.get(pk=2)
        pk = self.save_image(exercise, 'protestschwein.jpg')

        image = ExerciseImage.objects.get(pk=pk)
        self.assertTrue(image.is_main)

    def test_auto_main_image_multiple(self):
        """
        Tests that there is always a main image after deleting one
        """

        exercise = Exercise.objects.get(pk=2)
        pk1 = self.save_image(exercise, 'protestschwein.jpg')
        pk2 = self.save_image(exercise, 'wildschwein.jpg')

        image = ExerciseImage.objects.get(pk=pk1)
        self.assertTrue(image.is_main)

        image = ExerciseImage.objects.get(pk=pk2)
        self.assertFalse(image.is_main)

    def test_delete_main_image(self):
        """
        Tests that there is always a main image after deleting one
        """

        exercise = Exercise.objects.get(pk=2)
        pk1 = self.save_image(exercise, 'protestschwein.jpg')
        pk2 = self.save_image(exercise, 'protestschwein.jpg')
        pk3 = self.save_image(exercise, 'wildschwein.jpg')
        pk4 = self.save_image(exercise, 'wildschwein.jpg')
        pk5 = self.save_image(exercise, 'wildschwein.jpg')

        image = ExerciseImage.objects.get(pk=pk1)
        self.assertTrue(image.is_main)
        image.delete()

        self.assertFalse(ExerciseImage.objects.get(pk=pk2).is_main)
        self.assertFalse(ExerciseImage.objects.get(pk=pk3).is_main)
        self.assertFalse(ExerciseImage.objects.get(pk=pk4).is_main)
        self.assertFalse(ExerciseImage.objects.get(pk=pk5).is_main)

        image = ExerciseImage.objects.get(pk=pk2)
        self.assertFalse(image.is_main)
        image.delete()

        self.assertFalse(ExerciseImage.objects.get(pk=pk3).is_main)
        self.assertFalse(ExerciseImage.objects.get(pk=pk4).is_main)
        self.assertFalse(ExerciseImage.objects.get(pk=pk5).is_main)


# TODO: add POST and DELETE tests
class ExerciseImagesApiTestCase(
    api_base_test.BaseTestCase,
    api_base_test.ApiBaseTestCase,
    api_base_test.ApiGetTestCase,
):
    """
    Tests the exercise image resource
    """

    pk = 1
    private_resource = False
    resource = ExerciseImage
    overview_cached = True
