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
from django.core.cache import cache

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models import (
    Alias,
    Exercise,
    ExerciseBase,
    ExerciseComment,
)
from wger.utils.cache import cache_mapper


class ExerciseApiCacheTestCase(WgerTestCase):
    """
    Tests the API cache for the exercisebaseinfo endpoint
    """

    exercise_id = 1
    exercise_uuid = 'acad3949-36fb-4481-9a72-be2ddae2bc05'
    url = '/api/v2/exercisebaseinfo/1/'

    cache_key = cache_mapper.get_exercise_api_key('acad3949-36fb-4481-9a72-be2ddae2bc05')

    def test_edit_exercise(self):
        """
        Tests editing an exercise
        """
        self.assertFalse(cache.get(self.cache_key))
        self.client.get(self.url)
        self.assertTrue(cache.get(self.cache_key))

        exercise = ExerciseBase.objects.get(pk=1)
        exercise.category_id = 1
        exercise.save()

        self.assertFalse(cache.get(self.cache_key))

    def test_delete_exercise(self):
        """
        Tests deleting an exercise
        """
        self.assertFalse(cache.get(self.cache_key))
        self.client.get(self.url)
        self.assertTrue(cache.get(self.cache_key))

        exercise = ExerciseBase.objects.get(pk=1)
        exercise.delete()

        self.assertFalse(cache.get(self.cache_key))

    def test_edit_translation(self):
        """
        Tests editing a translation
        """
        self.assertFalse(cache.get(self.cache_key))
        self.client.get(self.url)
        self.assertTrue(cache.get(self.cache_key))

        translation = Exercise.objects.get(pk=1)
        translation.name = 'something else'
        translation.save()

        self.assertFalse(cache.get(self.cache_key))

    def test_delete_translation(self):
        """
        Tests deleting a translation
        """
        self.assertFalse(cache.get(self.cache_key))
        self.client.get(self.url)
        self.assertTrue(cache.get(self.cache_key))

        translation = Exercise.objects.get(pk=1)
        translation.delete()

        self.assertFalse(cache.get(self.cache_key))

    def test_edit_comment(self):
        """
        Tests editing a comment
        """
        self.assertFalse(cache.get(self.cache_key))
        self.client.get(self.url)
        self.assertTrue(cache.get(self.cache_key))

        comment = ExerciseComment.objects.get(pk=1)
        comment.name = 'The Shiba Inu (柴犬) is a breed of hunting dog from Japan'
        comment.save()

        self.assertFalse(cache.get(self.cache_key))

    def test_delete_comment(self):
        """
        Tests deleting a comment
        """
        self.assertFalse(cache.get(self.cache_key))
        self.client.get(self.url)
        self.assertTrue(cache.get(self.cache_key))

        comment = ExerciseComment.objects.get(pk=1)
        comment.delete()

        self.assertFalse(cache.get(self.cache_key))

    def test_edit_alias(self):
        """
        Tests editing an alias
        """
        self.assertFalse(cache.get(self.cache_key))
        self.client.get(self.url)
        self.assertTrue(cache.get(self.cache_key))

        alias = Alias.objects.get(pk=1)
        alias.name = 'Hachikō'
        alias.save()

        self.assertFalse(cache.get(self.cache_key))

    def test_delete_alias(self):
        """
        Tests deleting an alias
        """
        self.assertFalse(cache.get(self.cache_key))
        self.client.get(self.url)
        self.assertTrue(cache.get(self.cache_key))

        alias = Alias.objects.get(pk=1)
        alias.delete()

        self.assertFalse(cache.get(self.cache_key))
