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
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# wger
from wger.manager.managers import (
    WorkoutAndTemplateManager,
    WorkoutManager,
    WorkoutTemplateManager,
)
from wger.utils.cache import (
    cache_mapper,
    reset_workout_canonical_form,
)


class Workout(models.Model):
    """
    Model for a training schedule
    """

    objects = WorkoutManager()
    templates = WorkoutTemplateManager()
    both = WorkoutAndTemplateManager()

    class Meta:
        """
        Meta class to set some other properties
        """

        ordering = [
            '-creation_date',
        ]

    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=100,
        blank=True,
        help_text=_('The name of the workout'),
    )
    description = models.TextField(
        verbose_name=_('Description'),
        max_length=1000,
        blank=True,
        help_text=_(
            'A short description or goal of the workout. For '
            "example 'Focus on back' or 'Week 1 of program "
            "xy'."
        ),
    )
    is_template = models.BooleanField(
        verbose_name=_('Workout template'),
        help_text=_(
            'Marking a workout as a template will freeze it and allow you to make copies of it'
        ),
        default=False,
        null=False,
    )
    is_public = models.BooleanField(
        verbose_name=_('Public template'),
        help_text=_('A public template is available to other users'),
        default=False,
        null=False,
    )

    user = models.ForeignKey(
        User,
        verbose_name=_('User'),
        on_delete=models.CASCADE,
    )

    def get_absolute_url(self):
        """
        Returns the canonical URL to view a workout
        """
        return reverse(
            'manager:template:view' if self.is_template else 'manager:workout:view',
            kwargs={'pk': self.id},
        )

    def __str__(self):
        """
        Return a more human-readable representation
        """
        if self.name:
            return self.name
        else:
            return f'{_("Workout")} ({self.creation_date})'

    def clean(self):
        if self.is_public and not self.is_template:
            raise ValidationError(
                _('You must mark this workout as a template before declaring it public')
            )

    def save(self, *args, **kwargs):
        """
        Reset all cached infos
        """
        reset_workout_canonical_form(self.id)
        super(Workout, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Reset all cached infos
        """
        reset_workout_canonical_form(self.id)
        super(Workout, self).delete(*args, **kwargs)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

    @property
    def canonical_representation(self):
        """
        Returns a canonical representation of the workout

        This form makes it easier to cache and use everywhere where all or part
        of a workout structure is needed. As an additional benefit, the template
        caches are not needed anymore.
        """
        workout_canonical_form = cache.get(cache_mapper.get_workout_canonical(self.pk))
        if not workout_canonical_form:
            day_canonical_repr = []
            muscles_front = []
            muscles_back = []
            muscles_front_secondary = []
            muscles_back_secondary = []

            # Sort list by weekday
            day_list = [i for i in self.day_set.select_related()]
            day_list.sort(key=lambda day: day.get_first_day_id)

            for day in day_list:
                canonical_repr_day = day.get_canonical_representation()

                # Collect all muscles
                for i in canonical_repr_day['muscles']['front']:
                    if i not in muscles_front:
                        muscles_front.append(i)
                for i in canonical_repr_day['muscles']['back']:
                    if i not in muscles_back:
                        muscles_back.append(i)
                for i in canonical_repr_day['muscles']['frontsecondary']:
                    if i not in muscles_front_secondary:
                        muscles_front_secondary.append(i)
                for i in canonical_repr_day['muscles']['backsecondary']:
                    if i not in muscles_back_secondary:
                        muscles_back_secondary.append(i)

                day_canonical_repr.append(canonical_repr_day)

            workout_canonical_form = {
                'obj': self,
                'muscles': {
                    'front': muscles_front,
                    'back': muscles_back,
                    'frontsecondary': muscles_front_secondary,
                    'backsecondary': muscles_back_secondary,
                },
                'day_list': day_canonical_repr,
            }
            # Save to cache
            cache.set(cache_mapper.get_workout_canonical(self.pk), workout_canonical_form)

        return workout_canonical_form
