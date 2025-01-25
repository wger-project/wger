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

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import (
    WgerAccessTestCase,
    WgerAddTestCase,
    WgerDeleteTestCase,
    WgerEditTestCase,
    WgerTestCase,
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
        self.assertEqual(str(ExerciseCategory.objects.get(pk=1)), 'Category')


class CategoryOverviewTestCase(WgerAccessTestCase):
    """
    Test that only admins see the edit links
    """

    url = 'exercise:category:list'
    anonymous_fail = True
    user_success = 'admin'
    user_fail = (
        'manager1',
        'manager2general_manager1',
        'manager3',
        'manager4',
        'test',
        'member1',
        'member2',
        'member3',
        'member4',
        'member5',
    )


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


class ExerciseCategoryApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the exercise category overview resource
    """

    pk = 2
    resource = ExerciseCategory
    private_resource = False
    overview_cached = True
