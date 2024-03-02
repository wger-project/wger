#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) 2013 - 2021 wger Team
#
#  wger Workout Manager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  wger Workout Manager is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Django
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class ScheduleManager(models.Manager):
    """
    Custom manager for workout schedules
    """

    def get_current_workout(self, user):
        """
        Finds the currently active workout for the user, by checking the schedules
        and the workouts
        :rtype : list
        """
        # wger
        from wger.manager.models import (
            Schedule,
            Workout,
        )

        # Try first to find an active schedule that has steps
        try:
            schedule = Schedule.objects.filter(user=user).get(is_active=True)
            if schedule.schedulestep_set.count():
                # The schedule might exist and have steps, but if it's too far in
                # the past and is not a loop, we won't use it. Doing it like this
                # is kind of wrong, but lets us continue to the correct place
                if not schedule.get_current_scheduled_workout():
                    raise ObjectDoesNotExist

                active_workout = schedule.get_current_scheduled_workout().workout
            else:
                # same as above
                raise ObjectDoesNotExist

        # there are no active schedules, just return the last workout
        except ObjectDoesNotExist:
            schedule = False
            try:
                active_workout = Workout.objects.filter(user=user).latest('creation_date')

            # no luck, there aren't even workouts for the user
            except ObjectDoesNotExist:
                active_workout = False

        return active_workout, schedule


class WorkoutManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_template=False)


class WorkoutTemplateManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_template=True)


class WorkoutAndTemplateManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()
