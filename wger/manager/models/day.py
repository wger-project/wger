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
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import DaysOfWeek
from wger.utils.cache import reset_workout_canonical_form

# Local
from ..helpers import MusclesHelper
from .workout import Workout


class Day(models.Model):
    """
    Model for a training day
    """

    training = models.ForeignKey(Workout, verbose_name=_('Workout'), on_delete=models.CASCADE)
    description = models.CharField(
        max_length=100,
        verbose_name=_('Description'),
        help_text=_(
            'A description of what is done on this day (e.g. '
            '"Pull day") or what body parts are trained (e.g. '
            '"Arms and abs")'
        ),
    )
    day = models.ManyToManyField(DaysOfWeek, verbose_name=_('Day'))

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.description

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.training

    @property
    def get_first_day_id(self):
        """
        Return the PK of the first day of the week, this is used in the template
        to order the days in the template
        """
        return self.day.all()[0].pk

    def save(self, *args, **kwargs):
        """
        Reset all cached infos
        """

        reset_workout_canonical_form(self.training_id)
        super(Day, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Reset all cached infos
        """

        reset_workout_canonical_form(self.training_id)
        super(Day, self).delete(*args, **kwargs)

    @property
    def muscles(self) -> MusclesHelper:
        """All trained muscles by the exercises in this day"""
        out = MusclesHelper()

        for set_obj in self.set_set.all():
            for exercise in set_obj.exercises:
                for muscle in exercise.muscles.all():
                    out.add(muscle)

                for muscle in exercise.muscles_secondary.all():
                    out.add(muscle, False)

        return out

    @property
    def sets(self):

        # Local
        from .setting import Setting

        out = []
        for set_obj in self.set_set.select_related():

            set_data = {
                'exercises': [],
                'set': set_obj,
            }
            for exercise in set_obj.exercises:
                exercise_data = {
                    'exercise':
                    exercise,
                    'setting_text':
                    set_obj.reps_smart_text(exercise),
                    'settings':
                    Setting.objects.filter(set=set_obj, exercise=exercise).order_by('order', 'id'),
                }
                set_data['exercises'].append(exercise_data)

            out.append(set_data)

        return out
