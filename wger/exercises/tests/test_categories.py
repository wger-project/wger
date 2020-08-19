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
from django.core.cache.utils import make_template_fragment_key
from django.urls import reverse

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import (
    WgerAccessTestCase,
    WgerAddTestCase,
    WgerDeleteTestCase,
    WgerEditTestCase,
    WgerTestCase
)
from wger.exercises.models import ExerciseCategory


class ExerciseCategoryRepresentationTestCase(WgerTestCase):
    """
    Test the representation of a model
    """

    def test_representation(self):
        """
        Test that the representation of an object is correct
        """
        self.assertEqual("{0}".format(ExerciseCategory.objects.get(pk=1)), 'Category')


class CategoryOverviewTestCase(WgerAccessTestCase):
    """
    Test that only admins see the edit links
    """
    url = 'exercise:category:list'
    anonymous_fail = True
    user_success = 'admin'
    user_fail = ('manager1',
                 'manager2'
                 'general_manager1',
                 'manager3',
                 'manager4',
                 'test',
                 'member1',
                 'member2',
                 'member3',
                 'member4',
                 'member5')


class DeleteExerciseCategoryTestCase(WgerDeleteTestCase):
    """
    Exercise category delete test case
    """

    object_class = ExerciseCategory
    url = 'exercise:category:delete'
    pk = 4
    user_success = 'admin'
    user_fail = 'test'


class EditExerciseCategoryTestCase(WgerEditTestCase):
    """
    Tests editing an exercise category
    """

    object_class = ExerciseCategory
    url = 'exercise:category:edit'
    pk = 3
    data = {'name': 'A different name'}


class AddExerciseCategoryTestCase(WgerAddTestCase):
    """
    Tests adding an exercise category
    """

    object_class = ExerciseCategory
    url = 'exercise:category:add'
    data = {'name': 'A new category'}


class ExerciseCategoryCacheTestCase(WgerTestCase):
    """
    Cache test case
    """

    def test_overview_cache_update(self):
        """
        Test that the template cache for the overview is correctly reseted when
        performing certain operations
        """

        self.client.get(reverse('exercise:exercise:overview'))
        self.client.get(reverse('exercise:exercise:view', kwargs={'id': 2}))

        old_exercise_overview = cache.get(make_template_fragment_key('exercise-overview', [2]))

        category = ExerciseCategory.objects.get(pk=2)
        category.name = 'Cool category'
        category.save()

        self.assertFalse(cache.get(make_template_fragment_key('exercise-overview', [2])))

        self.client.get(reverse('exercise:exercise:overview'))
        self.client.get(reverse('exercise:muscle:overview'))
        self.client.get(reverse('exercise:exercise:view', kwargs={'id': 2}))

        new_exercise_overview = cache.get(make_template_fragment_key('exercise-overview', [2]))

        self.assertNotEqual(old_exercise_overview, new_exercise_overview)


class ExerciseCategoryApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the exercise category overview resource
    """
    pk = 2
    resource = ExerciseCategory
    private_resource = False
