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

from decimal import Decimal

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.utils.constants import FOURPLACES
from wger.utils.routines import Routine, ExerciseConfig, RoutineExercise


'''
Test the different aspects of the routine configuration
'''


class ExerciseConfigTestCase(WorkoutManagerTestCase):
    '''
    General Tests
    '''

    def test_get_step(self):
        '''
        Test the step calculator
        '''
        class TestConfig(ExerciseConfig):
                responsibility = {1: {1: [2, 3, 4],
                                      2: [2, 3],
                                      3: [2]}}
        config1 = TestConfig()

        self.assertIsNone(config1.get_step(1, 1, 1))
        self.assertIsNone(config1.get_step(1, 1, 5))
        self.assertIsNone(config1.get_step(2, 1, 1))
        self.assertIsNone(config1.get_step(4, 1, 1))

        self.assertEqual(config1.get_step(1, 1, 2), 1)
        self.assertEqual(config1.get_step(1, 1, 3), 2)
        self.assertEqual(config1.get_step(1, 1, 4), 3)
        self.assertEqual(config1.get_step(1, 2, 2), 4)
        self.assertEqual(config1.get_step(1, 2, 3), 5)
        self.assertEqual(config1.get_step(1, 3, 2), 6)


class ExerciseConfigWeightTestCase(WorkoutManagerTestCase):
    '''
    Test weight calculations for exercise config objects
    '''

    def test_dynamic_routine(self):
        '''
        Test dynamic routine weight increase
        '''

        class TestConfig(ExerciseConfig):
            increment = 1.25
            start_weight = 100
            responsibility = {1: {1: [1],
                                  2: [2],
                                  3: [2],
                                  4: [2]}}
        config = TestConfig(increment_mode='dynamic')

        for step in [(1, 1, 1), (1, 2, 2), (1, 3, 2), (1, 4, 2)]:
            config.set_current_step(step[0], step[1], step[2])
            self.assertEqual(config.get_routine_data(), u'Dynamic value. Add to schedule.')

    def test_static_routine(self):
        '''
        Test dynamic routine weight increase
        '''

        class TestConfig(ExerciseConfig):
            increment = 1.25
            start_weight = 100
            responsibility = {1: {1: [1],
                                  2: [2],
                                  3: [2],
                                  4: [2]}}
        config = TestConfig(increment_mode='static')
        config.set_current_step(1, 1, 1)
        self.assertEqual(config.get_routine_data(), Decimal(101.25))

        config.set_current_step(1, 2, 2)
        self.assertEqual(config.get_routine_data(), Decimal(102.5))

        config.set_current_step(1, 3, 2)
        self.assertEqual(config.get_routine_data(), Decimal(103.75))

        config.set_current_step(1, 4, 2)
        self.assertEqual(config.get_routine_data(), Decimal(105))

    def test_static_routine_percent(self):
        '''
        Test static routine weight increase, percent increase
        '''

        class TestConfig(ExerciseConfig):
            increment = 5
            start_weight = 100
            responsibility = {1: {1: [1],
                                  2: [2],
                                  3: [2],
                                  4: [2]}}
        config = TestConfig(increment_mode='static', unit='percent')
        config.set_current_step(1, 1, 1)
        self.assertEqual(config.get_routine_data(), Decimal(105))

        config.set_current_step(1, 2, 2)
        self.assertEqual(config.get_routine_data(), Decimal(110.25))

        config.set_current_step(1, 3, 2)
        self.assertEqual(config.get_routine_data(), Decimal(115.7625).quantize(FOURPLACES))

        config.set_current_step(1, 4, 2)
        self.assertEqual(config.get_routine_data(), Decimal(121.5506).quantize(FOURPLACES))

    def test_static_routine_percent_validation(self):
        '''
        Test validations for percentage weight increase
        '''

        class TestConfig(ExerciseConfig):
            increment = 15
            start_weight = 100
            responsibility = {1: {1: [1]}}
        self.assertRaises(ValueError, TestConfig, increment_mode='static', unit='percent')
