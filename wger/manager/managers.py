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

# wger
from wger.manager.consts import (
    REP_UNIT_REPETITIONS,
    WEIGHT_UNIT_KG,
    WEIGHT_UNIT_LB,
)


class WorkoutLogQuerySet(models.QuerySet):
    def kg(self):
        """Return all entries with kg as weight"""
        return self.filter(weight_unit_id=WEIGHT_UNIT_KG)

    def lb(self):
        """Return all entries with lb as weight"""
        return self.filter(weight_unit_id=WEIGHT_UNIT_LB)

    def reps(self):
        """Return all entries with reps as unit"""
        return self.filter(repetitions_unit_id=REP_UNIT_REPETITIONS)


class WorkoutLogManager(models.Manager):
    """Custom manager for log entries"""

    def get_queryset(self):
        return WorkoutLogQuerySet(self.model, using=self._db)

    def kg(self):
        """Return all entries with kg as weight"""
        return self.get_queryset().kg()

    def lb(self):
        """Return all entries with lb as weight"""
        return self.get_queryset().lb()

    def reps(self):
        """Return all entries with reps as unit"""
        return self.get_queryset().reps()


class RoutineManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class RoutineTemplateManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_template=True)


class PublicRoutineTemplateManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_template=True, is_public=True)
