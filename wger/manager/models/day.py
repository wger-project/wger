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
    def days_txt(self):
        return ', '.join([str(_(i.day_of_week)) for i in self.day.all()])

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
    def canonical_representation(self):
        """
        Return the canonical representation for this day

        This is extracted from the workout representation because that one is cached
        and this isn't.
        """
        for i in self.training.canonical_representation['day_list']:
            if int(i['obj'].pk) == int(self.pk):
                return i

    def get_canonical_representation(self):
        """
        Creates a canonical representation for this day
        """
        # Local
        from .setting import Setting

        canonical_repr = []
        muscles_front = []
        muscles_back = []
        muscles_front_secondary = []
        muscles_back_secondary = []

        for set_obj in self.set_set.select_related():
            exercise_tmp = []

            for base in set_obj.exercise_bases:
                setting_tmp = []
                exercise_images_tmp = []

                # Muscles for this set
                for muscle in base.muscles.all():
                    if muscle.is_front and muscle not in muscles_front:
                        muscles_front.append(muscle)
                    elif not muscle.is_front and muscle not in muscles_back:
                        muscles_back.append(muscle)

                for muscle in base.muscles_secondary.all():
                    if muscle.is_front and muscle not in muscles_front:
                        muscles_front_secondary.append(muscle)
                    elif not muscle.is_front and muscle.id not in muscles_back:
                        muscles_back_secondary.append(muscle)

                for setting in Setting.objects.filter(set=set_obj, exercise_base=base).order_by(
                    'order', 'id'
                ):
                    setting_tmp.append(setting)

                # "Smart" textual representation
                setting_text = set_obj.reps_smart_text(base)

                # Exercise comments
                comment_list = []
                # for i in base.exercisecomment_set.all():
                #    comment_list.append(i.comment)

                # Flag indicating whether any of the settings has saved weight
                has_weight = False
                for i in setting_tmp:
                    if i.weight:
                        has_weight = True
                        break

                # Collect exercise images
                for image in base.exerciseimage_set.all():
                    exercise_images_tmp.append(
                        {
                            'image': image.image.url,
                            'is_main': image.is_main,
                        }
                    )

                # Put it all together
                exercise_tmp.append(
                    {
                        'obj': base,
                        'setting_obj_list': setting_tmp,
                        'setting_text': setting_text,
                        'has_weight': has_weight,
                        'comment_list': comment_list,
                        'image_list': exercise_images_tmp,
                    }
                )

            # If it's a superset, check that all exercises have the same repetitions.
            # If not, just take the smallest number and drop the rest, because otherwise
            # it doesn't make sense

            # if len(exercise_tmp) > 1:
            #     common_reps = 100
            #     for exercise in exercise_tmp:
            #         if len(exercise['setting_list']) < common_reps:
            #             common_reps = len(exercise['setting_list'])

            #     for exercise in exercise_tmp:
            #         if len(exercise['setting_list']) > common_reps:
            #             exercise['setting_list'].pop(-1)
            #             exercise['setting_obj_list'].pop(-1)
            #             setting_text, setting_list = set_obj.reps_smart_text(exercise)
            #             exercise['setting_text'] = setting_text

            canonical_repr.append(
                {
                    'obj': set_obj,
                    'exercise_list': exercise_tmp,
                    'is_superset': True if len(exercise_tmp) > 1 else False,
                    'settings_computed': set_obj.compute_settings,
                    'muscles': {
                        'back': muscles_back,
                        'front': muscles_front,
                        'frontsecondary': muscles_front_secondary,
                        'backsecondary': muscles_front_secondary,
                    },
                }
            )

        # Days of the week
        tmp_days_of_week = []
        for day_of_week in self.day.select_related():
            tmp_days_of_week.append(day_of_week)

        return {
            'obj': self,
            'days_of_week': {
                'text': ', '.join([str(_(i.day_of_week)) for i in tmp_days_of_week]),
                'day_list': tmp_days_of_week,
            },
            'muscles': {
                'back': muscles_back,
                'front': muscles_front,
                'frontsecondary': muscles_front_secondary,
                'backsecondary': muscles_front_secondary,
            },
            'set_list': canonical_repr,
        }
