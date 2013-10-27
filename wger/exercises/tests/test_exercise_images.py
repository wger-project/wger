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
from wger.exercises.models import ExerciseImage

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase
from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import ApiBaseResourceTestCase


class AddExerciseImageTestCase(WorkoutManagerAddTestCase):
    '''
    Tests adding an image to an exercise
    '''

    object_class = ExerciseImage
    url = reverse('exerciseimage-add', kwargs={'exercise_pk': 1})
    pk = 3
    user_fail = False
    data = {'is_main': True,
            'image': open('wger/exercises/tests/protestschwein.jpg', 'rb')}


class EditExerciseImageTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing an image to an exercise
    '''

    object_class = ExerciseImage
    url = 'exerciseimage-edit'
    pk = 2
    data = {'is_main': True}


class DeleteExerciseImageTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting an image to an exercise
    '''

    object_class = ExerciseImage
    url = reverse('exerciseimage-delete', kwargs={'exercise_pk': 1, 'pk': 1})
    pk = 1


#class ExerciseImagesApiTestCase(ApiBaseResourceTestCase):
    #'''
    #Tests the exercise image overview resource
    #'''
    #resource = 'exerciseimage'
    #user = None
    #resource_updatable = False
    #data = {"is_main": "true",
            #"exercise": "/api/v1/exercise/1/",
            #"id": 1}


#class ExerciseImageDetailApiTestCase(ApiBaseResourceTestCase):
    #'''
    #Tests accessing a specific exercise image
    #'''
    #resource = 'exerciseimage/1'
    #user = None
    #resource_updatable = False
#