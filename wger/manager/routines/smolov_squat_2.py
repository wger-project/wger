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
    responsibility = {
        1: {1: [1, 2, 3, 4],
            2: [1, 2, 3, 4, 5],
            3: [1, 2, 3]},
        2: {1: [1, 2, 3, 4, 5],
            2: [1, 2, 3, 4, 5],
            3: [1, 2, 3, 4]},
        3: {1: [1, 2, 3, 4],
            2: [1, 2, 3, 4],
            3: [1, 2, 3, 4]},
        4: {1: [1, 2, 3],
            2: [1, 2, 3],
            3: [1, 2, 3]},
        5: {1: [1, 2, 3, 4],
            2: [1, 2],
            3: [1]}
    }

    def get_routine(self):
        max_squat = AbstractWeight(self.user_config['max_squat'], self.user_config['unit'])

        # Week 1
        if self.current_week == 1:
            if self.current_day == 1:
                if self.current_set == 1:
                    return 1, 3, max_squat * 0.65
                elif self.current_set == 2:
                    return 1, 4, max_squat * 0.75
                elif self.current_set == 3:
                    return 3, 4, max_squat * 0.85
                elif self.current_set == 4:
                    return 1, 5, max_squat * 0.85
            elif self.current_day == 2:
                if self.current_set == 1:
                    return 1, 3, max_squat * 0.60
                elif self.current_set == 2:
                    return 1, 3, max_squat * 0.70
                elif self.current_set == 3:
                    return 1, 4, max_squat * 0.80
                elif self.current_set == 4:
                    return 1, 3, max_squat * 0.90
                elif self.current_set == 5:
                    return 2, 5, max_squat * 0.85
            elif self.current_day == 3:
                if self.current_set == 1:
                    return 1, 4, max_squat * 0.65
                elif self.current_set == 2:
                    return 1, 4, max_squat * 0.70
                elif self.current_set == 3:
                    return 5, 4, max_squat * 0.80

        # Week 2
        elif self.current_week == 2:
            if self.current_day == 1:
                if self.current_set == 1:
                    return 1, 4, max_squat * 0.60
                elif self.current_set == 2:
                    return 1, 4, max_squat * 0.70
                elif self.current_set == 3:
                    return 1, 4, max_squat * 0.80
                elif self.current_set == 4:
                    return 1, 3, max_squat * 0.90
                elif self.current_set == 5:
                    return 2, 4, max_squat * 0.90
            elif self.current_day == 2:
                if self.current_set == 1:
                    return 1, 3, max_squat * 0.65
                elif self.current_set == 2:
                    return 1, 3, max_squat * 0.75
                elif self.current_set == 3:
                    return 1, 3, max_squat * 0.85
                elif self.current_set == 4:
                    return 3, 3, max_squat * 0.90
                elif self.current_set == 5:
                    return 1, 3, max_squat * 0.95
            elif self.current_day == 3:
                if self.current_set == 1:
                    return 1, 3, max_squat * 0.65
                elif self.current_set == 2:
                    return 1, 3, max_squat * 0.75
                elif self.current_set == 3:
                    return 1, 4, max_squat * 0.85
                elif self.current_set == 4:
                    return 4, 5, max_squat * 0.90

        # Week 3
        elif self.current_week == 3:
            if self.current_day == 1:
                if self.current_set == 1:
                    return 1, 3, max_squat * 0.60
                elif self.current_set == 2:
                    return 1, 3, max_squat * 0.70
                elif self.current_set == 3:
                    return 1, 3, max_squat * 0.80
                elif self.current_set == 4:
                    return 4, 5, max_squat * 0.90
            elif self.current_day == 2:
                if self.current_set == 1:
                    return 1, 3, max_squat * 0.60
                elif self.current_set == 2:
                    return 1, 3, max_squat * 0.70
                elif self.current_set == 3:
                    return 1, 3, max_squat * 0.80
                elif self.current_set == 4:
                    return 2, 3, max_squat * 0.90
            elif self.current_day == 3:
                if self.current_set == 1:
                    return 1, 3, max_squat * 0.65
                elif self.current_set == 2:
                    return 1, 3, max_squat * 0.75
                elif self.current_set == 3:
                    return 1, 3, max_squat * 0.85
                elif self.current_set == 4:
                    return 4, 3, max_squat * 0.95

        # Week 4
        elif self.current_week == 4:
            if self.current_day == 1:
                if self.current_set == 1:
                    return 1, 3, max_squat * 0.70
                elif self.current_set == 2:
                    return 1, 4, max_squat * 0.80
                elif self.current_set == 3:
                    return 5, 5, max_squat * 0.95
            elif self.current_day == 2:
                if self.current_set == 1:
                    return 1, 3, max_squat * 0.70
                elif self.current_set == 2:
                    return 1, 3, max_squat * 0.80
                elif self.current_set == 3:
                    return 4, 3, max_squat * 0.95
            elif self.current_day == 3:
                if self.current_set == 1:
                    return 1, 3, max_squat * 0.75
                elif self.current_set == 2:
                    return 1, 4, max_squat * 0.90
                elif self.current_set == 3:
                    return 3, 4, max_squat * 0.95

        # Week 5
        elif self.current_week == 5:
            if self.current_day == 1:
                if self.current_set == 1:
                    return 1, 3, max_squat * 0.70
                elif self.current_set == 2:
                    return 1, 3, max_squat * 0.80
                elif self.current_set == 3:
                    return 2, 5, max_squat * 0.90
                elif self.current_set == 4:
                    return 3, 4, max_squat * 0.95
            elif self.current_day == 2:
                if self.current_set == 1:
                    return 1, 4, max_squat * 0.75
                elif self.current_set == 2:
                    return 4, 4, max_squat * 0.85
            elif self.current_day == 3:
                return 1, 1, 'max'


def get_routine():
    '''
    Initialise and return this routine
    '''

    smolov = Routine(name='Smolov Squat - Part 2',
                     slug=os.path.splitext(os.path.basename(__file__))[0],
                     description=_("This is part two of a two part routine. You should have "
                                   "established a fresh squat max in part one that you will "
                                   "use now to grind out another PR at the end of these brutal "
                                   "sessions."))

    squat = RoutineExercise(mapper_pk=2)
    squat.add_config(SquatConfig())

    smolov.add(squat)

    return smolov
