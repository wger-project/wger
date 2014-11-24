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

import logging
import os

from django.utils.translation import ugettext as _

from wger.utils.routines import Routine
from wger.utils.routines import ExerciseConfig
from wger.utils.routines import RoutineExercise
from wger.utils.units import AbstractWeight

logger = logging.getLogger('wger.custom')


class SquatConfig(ExerciseConfig):
    increment_mode = 'manual'
    sets = 1
    responsibility = {
        1: {1: [1],
            2: [1],
            3: [1]},
        2: {1: [1],
            2: [1],
            3: [1]},
        3: {1: [1],
            2: [1],
            3: [1]},
        4: {1: [1],
            2: [1],
            3: [1]},
        5: {1: [1],
            2: [1],
            3: [1]},
        6: {1: [1],
            2: [1],
            3: [1]},
        7: {1: [1],
            2: [1],
            3: [1]},
        8: {1: [1],
            2: [1],
            3: [1]},
    }

    def get_routine(self):
        max_squat = AbstractWeight(self.user_config['max_squat'], self.user_config['unit'])
        base_weight = max_squat + AbstractWeight(25, 'lb')

        if self.current_week == 1:
            return 8, 5, base_weight * 0.58
        elif self.current_week == 2:
            return 8, 5, base_weight * 0.6
        elif self.current_week == 3:
            return 8, 5, base_weight * 0.62
        elif self.current_week == 4:
            return 8, 5, base_weight * 0.64
        elif self.current_week == 5:
            if self.current_day != 3:
                return 3, 3, base_weight * 0.6
            else:
                return 1, 1, base_weight * 0.80
        elif self.current_week == 6:
            if self.current_day != 3:
                return 3, 3, base_weight * 0.6
            else:
                return 1, 1, base_weight * 0.85
        elif self.current_week == 7:
            if self.current_day != 3:
                return 3, 3, base_weight * 0.6
            else:
                return 1, 1, base_weight * 0.90
        elif self.current_week == 8:
            if self.current_day != 3:
                return 3, 3, base_weight * 0.6
            else:
                return 1, 1, base_weight * 0.95


class BenchConfig(ExerciseConfig):
    increment_mode = 'manual'
    sets = 1
    responsibility = {
        1: {1: [2],
            2: [2],
            3: [2]},
        2: {1: [2],
            2: [2],
            3: [2]},
        3: {1: [2],
            2: [2],
            3: [2]},
        4: {1: [2],
            2: [2],
            3: [2]},
        5: {1: [2],
            2: [2],
            3: [2]},
        6: {1: [2],
            2: [2],
            3: [2]},
        7: {1: [2],
            2: [2],
            3: [2]},
        8: {1: [2],
            2: [2],
            3: [2]},
    }

    def get_routine(self):
        max_bench = AbstractWeight(self.user_config['max_bench'],  self.user_config['unit'])
        base_weight = max_bench + AbstractWeight(10, 'lb')

        if self.current_week == 1:
            return 8, 5, base_weight * 0.58
        elif self.current_week == 2:
            return 8, 5, base_weight * 0.6
        elif self.current_week == 3:
            return 8, 5, base_weight * 0.62
        elif self.current_week == 4:
            return 8, 5, base_weight * 0.64
        elif self.current_week == 5:
            if self.current_day != 2:
                return 5, 4, base_weight * 0.6
            else:
                return 1, 1, base_weight * 0.80
        elif self.current_week == 6:
            if self.current_day == 2:
                return 1, 1, base_weight * 0.85
            else:
                return 5, 4, base_weight * 0.6
        elif self.current_week == 7:
            if self.current_day == 2:
                return 5, 1, base_weight * 0.90
            else:
                return 1, 4, base_weight * 0.6
        elif self.current_week == 8:
            if self.current_day == 2:
                return 5, 1, base_weight * 0.95
            else:
                return 1, 4, base_weight * 0.6


class DeadliftConfig(ExerciseConfig):
    increment_mode = 'manual'
    responsibility = {
        1: {1: [3],
            2: [3],
            3: [3]},
        2: {1: [3],
            2: [3],
            3: [3]},
        3: {1: [3],
            2: [3],
            3: [3]},
        4: {1: [3],
            2: [3],
            3: [3]},
        5: {1: [3],
            2: [3],
            3: [3]},
        6: {1: [3],
            2: [3],
            3: [3]},
        7: {1: [3],
            2: [3],
            3: [3]},
        8: {1: [3],
            2: [3],
            3: [3]},
    }

    def get_routine(self):
        max_deadlift = AbstractWeight(self.user_config['max_deadlift'], self.user_config['unit'])
        base_weight = max_deadlift + AbstractWeight(15, 'lb')

        if self.current_week == 1:
            return 8, 5, base_weight * 0.58
        elif self.current_week == 2:
            return 8, 5, base_weight * 0.6
        elif self.current_week == 3:
            return 8, 5, base_weight * 0.62
        elif self.current_week == 4:
            return 8, 5, base_weight * 0.64
        elif self.current_week == 5:
            if self.current_day == 1:
                return 1, 1, base_weight * 0.80
            else:
                return 3, 3, base_weight * 0.60
        elif self.current_week == 6:
            if self.current_day == 1:
                return 1, 1, base_weight * 0.85
            else:
                return 3, 3, base_weight * 0.60
        elif self.current_week == 7:
            if self.current_day == 1:
                return 1, 1, base_weight * 0.90
            else:
                return 3, 3, base_weight * 0.60
        elif self.current_week == 8:
            if self.current_day == 1:
                return 1, 1, base_weight * 0.95
            else:
                return 3, 3, base_weight * 0.60


def get_routine():
    '''
    Initialise and return this routine
    '''

    korte = Routine(name='Korte 3x3',
                    slug=os.path.splitext(os.path.basename(__file__))[0],
                    description=_("Pure German volume training (GVT). You will squat, "
                                  "bench, and deadlift. That's it. Good luck."))

    squat = RoutineExercise(mapper_pk=2)
    squat.add_config(SquatConfig())

    bench = RoutineExercise(mapper_pk=1)
    bench.add_config(BenchConfig())

    deadlift = RoutineExercise(mapper_pk=3)
    deadlift.add_config(DeadliftConfig())

    korte.add(squat)
    korte.add(bench)
    korte.add(deadlift)

    return korte
