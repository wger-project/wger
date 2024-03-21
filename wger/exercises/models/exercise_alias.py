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

# Standard Library
import uuid

# Django
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.utils.translation import gettext_lazy as _

# Third Party
from simple_history.models import HistoricalRecords

# wger
from wger.utils.cache import (
    reset_exercise_api_cache,
    reset_workout_canonical_form,
)

# Local
from .exercise import Exercise


class Alias(models.Model):
    """
    Model for an exercise (name)alias
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name='UUID',
    )
    """Globally unique ID, to identify the alias across installations"""

    exercise = models.ForeignKey(
        Exercise,
        verbose_name=_('Exercise'),
        on_delete=models.CASCADE,
    )

    alias = models.CharField(
        max_length=200,
        verbose_name=_('Alias for an exercise'),
    )

    history = HistoricalRecords()
    """Edit history"""

    class Meta:
        indexes = (GinIndex(fields=['alias']),)

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.alias

    def save(self, *args, **kwargs):
        """
        Reset cached workouts
        """
        # Api cache
        reset_exercise_api_cache(self.exercise.exercise_base.uuid)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Reset cached workouts
        """
        for setting in self.exercise.exercise_base.setting_set.all():
            reset_workout_canonical_form(setting.set.exerciseday.training.pk)

        # Api cache
        reset_exercise_api_cache(self.exercise.exercise_base.uuid)

        super().delete(*args, **kwargs)

    def get_owner_object(self):
        """
        Comment has no owner information
        """
        return False
