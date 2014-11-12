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

logger = logging.getLogger('wger.custom')


class SquatConfig(ExerciseConfig):

    data = {
        1: {1: [1, 2, 3, 4, 5, 6, 7],
            2: [1, 2, 3, 4, 5, 6, 7],
            3: [1, 2, 3, 4, 5, 6, 7, 8]},
        2: {1: [1, 2, 3, 4],
            2: [1, 2, 3, 4, 5],
            3: [1, 2, 3, 4, 5, 6, 7],
            4: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
        3: {1: [1, 2, 3, 4],
            2: [1, 2, 3, 4, 5],
            3: [1, 2, 3, 4, 5, 6, 7],
            4: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
        4: {1: [1, 2, 3, 4],
            2: [1, 2, 3, 4, 5],
            3: [1, 2, 3, 4, 5, 6, 7],
            4: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
        5: {1: [1],
            2: [1]}
    }

    def get_routine(self):
        max_squat = self.user_config['max_squat']

        # Week 1
        if self.current_week == 1:
            if 1 <= self.current_day <= 2:
                if 1 <= self.current_set <= 3:
                    return 8, max_squat * 0.65
                elif self.current_set == 4:
                    return 5, max_squat * 0.70
                elif 5 <= self.current_set <= 6:
                    return 2, max_squat * 0.75
                elif self.current_set == 7:
                    return 2, max_squat * 0.80
            elif self.current_day == 3:
                if 1 <= self.current_set <= 4:
                    return 5, max_squat * 0.70
                elif self.current_set == 5:
                    return 3, max_squat * 0.75
                elif 6 <= self.current_set <= 7:
                    return 2, max_squat * 0.80
                elif self.current_set == 8:
                    return 1, max_squat * 0.90

        # Week 2
        elif self.current_week == 2:
            if self.current_day == 1:
                return 9, max_squat * 0.70
            elif self.current_day == 2:
                return 7, max_squat * 0.75
            elif self.current_day == 3:
                return 5, max_squat * 0.80
            elif self.current_day == 4:
                return 3, max_squat * 0.85

        # Week 3
        elif self.current_week == 3:
            if self.current_day == 1:
                return 9, (max_squat * 0.70) + 9
            elif self.current_day == 2:
                return 7, (max_squat * 0.75) + 9
            elif self.current_day == 3:
                return 5, (max_squat * 0.80) + 9
            elif self.current_day == 4:
                return 3, (max_squat * 0.85) + 9

        # Week 4
        elif self.current_week == 4:
            if self.current_day == 1:
                return 9, (max_squat * 0.70) + 13
            elif self.current_day == 2:
                return 7, (max_squat * 0.75) + 13
            elif self.current_day == 3:
                return 5, (max_squat * 0.80) + 13
            elif self.current_day == 4:
                return 3, (max_squat * 0.85) + 13

        # Week 5
        elif self.current_week == 5:
            return 1, 'max'


def get_routine():
    '''
    Initialise and return this routine
    '''

    smolov = Routine(weeks=5,
                     name='Smolov Squat - Part 1',
                     slug=os.path.splitext(os.path.basename(__file__))[0],
                     description=_("This is the part one of a two part routine. Bang this thing "
                                   "out, get a new max, then take the new max on over to part "
                                   "two and wreck that as well."))

    squat = RoutineExercise(mapper_pk=2)
    squat.add_config(SquatConfig())

    smolov.add(squat)

    return smolov
