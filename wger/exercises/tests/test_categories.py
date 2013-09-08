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


from wger.exercises.models import ExerciseCategory
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase
from wger.manager.tests.testcase import ApiBaseResourceTestCase


class DeleteExerciseCategoryTestCase(WorkoutManagerDeleteTestCase):
    '''
    Exercise category delete test case
    '''

    object_class = ExerciseCategory
    url = 'exercisecategory-delete'
    pk = 4
    user_success = 'admin'
    user_fail = 'test'


class EditExerciseCategoryTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing an exercise category
    '''

    object_class = ExerciseCategory
    url = 'exercisecategory-edit'
    pk = 3
    data = {'name': 'A different name'}


class AddExerciseCategoryTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding an exercise category
    '''

    object_class = ExerciseCategory
    url = 'exercisecategory-add'
    pk = 5
    data = {'name': 'A new category'}


class ExerciseCategoryApiTestCase(ApiBaseResourceTestCase):
    '''
    Tests the exercise category overview resource
    '''
    resource = 'exercisecategory'
    user = None
    resource_updatable = False


class ExerciseCategoryDetailApiTestCase(ApiBaseResourceTestCase):
    '''
    Tests accessing a specific exercise category
    '''
    resource = 'exercisecategory/2'
    user = None
    resource_updatable = False
