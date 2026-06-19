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
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models import (
    Alias,
    Exercise,
    ExerciseComment,
    ExerciseImage,
    Translation,
)
from wger.utils.cache import cache_mapper


class ExerciseApiCacheTestCase(WgerTestCase):
    """
    Tests the API cache for the exerciseinfo endpoint
    """

    exercise_id = 1
    exercise_uuid = 'acad3949-36fb-4481-9a72-be2ddae2bc05'
    url = '/api/v2/exerciseinfo/1/'

    cache_key = cache_mapper.get_exercise_api_key('acad3949-36fb-4481-9a72-be2ddae2bc05')

    def test_edit_exercise(self):
        """
        Tests editing an exercise
        """
        self.assertFalse(cache.get(self.cache_key))
        self.client.get(self.url)
        self.assertTrue(cache.get(self.cache_key))

        exercise = Exercise.objects.get(pk=1)
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

        exercise = Exercise.objects.get(pk=1)
        exercise.delete()

        self.assertFalse(cache.get(self.cache_key))

    def test_edit_translation(self):
        """
        Tests editing a translation
        """
        self.assertFalse(cache.get(self.cache_key))
        self.client.get(self.url)
        self.assertTrue(cache.get(self.cache_key))

        translation = Translation.objects.get(pk=1)
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

        translation = Translation.objects.get(pk=1)
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


class ExerciseInfoListCacheTestCase(WgerTestCase):
    """
    Tests the bulk cache handling of the exerciseinfo list endpoint
    """

    def test_warm_list_skips_prefetch_joins(self):
        """
        A warm list request reads the cached representations in bulk and must not
        query the related tables that the heavy queryset would otherwise prefetch.
        """
        list_url = reverse('exerciseinfo-list')

        # Warm the cache for every exercise
        self.client.get(list_url, {'limit': 900})

        related_tables = (
            Translation._meta.db_table,
            Alias._meta.db_table,
            ExerciseComment._meta.db_table,
            ExerciseImage._meta.db_table,
        )

        with CaptureQueriesContext(connection) as context:
            self.client.get(list_url, {'limit': 900})

        executed = ' '.join(query['sql'] for query in context.captured_queries)
        for table in related_tables:
            self.assertNotIn(table, executed)

    def test_list_reuses_per_exercise_cache_from_retrieve(self):
        """
        retrieve() and list() share the same per-exercise cache entry, so an
        exercise warmed through the detail endpoint is reused by the list.
        """
        exercise = Exercise.objects.get(pk=1)
        key = cache_mapper.get_exercise_api_key(exercise.uuid)

        self.assertFalse(cache.get(key))
        detail = self.client.get(reverse('exerciseinfo-detail', kwargs={'pk': exercise.pk})).json()
        self.assertTrue(cache.get(key))

        results = self.client.get(reverse('exerciseinfo-list'), {'limit': 900}).json()['results']
        listed = next(row for row in results if row['id'] == exercise.pk)
        self.assertEqual(listed, detail)
