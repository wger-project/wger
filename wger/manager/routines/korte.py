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

from django.utils.translation import ugettext as _

from wger.utils.routines import Routine
from wger.utils.routines import ExerciseConfig

logger = logging.getLogger('wger.custom')


class KorteRoutine(Routine):
    pass


class SquatConfig(ExerciseConfig):
    data = {
        1: {1: [2, 3, 4],
            2: [1]},
        2: {1: [1, 2],
            3: [5, 6]}
    }

    def get_routine(self):
        if self.current_week == 1:
            if self.current_day == 1:
                if self.current_set == 2:
                    return 8, 100
                elif self.current_set == 3:
                    return 3, 150
                elif self.current_set == 4:
                    return 5, 120
            elif self.current_day == 2:
                return 5, 125
        elif self.current_week == 2:
            return 3, 120


class BenchConfig(ExerciseConfig):
    data = {
        1: {1: [1],
            2: [2, 3, 4, 6, 7]},
        2: {1: [3, 4],
            2: [1, 2, 3, 4, 5, 6]}
    }

    def get_routine(self):
        return 5, 100


class DeadliftConfig(ExerciseConfig):
    data = {
        1: {1: [5, 6, 7, 8, 9],
            2: [5]},
        2: {1: [5, 6],
            3: [1, 2, 3, 4]}
    }

    def get_routine(self):
        return 5, 200


korte = KorteRoutine(weeks=8,
                     name='Korte 3x3',
                     description=_("Pure German volume training (GVT). You will squat, "
                                   "bench, and deadlift. That's it. Good luck."))

e1 = SquatConfig('Squats', None)
e2 = BenchConfig('Bench', None)
e3 = DeadliftConfig('Deadlift', None)

korte.add(e1)
korte.add(e2)
korte.add(e3)
