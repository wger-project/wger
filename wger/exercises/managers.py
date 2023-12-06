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
from django.db.models import Count


class ExerciseBaseManagerTranslations(models.Manager):
    """Returns all exercise bases that have at least one translation"""

    def get_queryset(self):
        return super().get_queryset().annotate(count=Count('exercises')).filter(count__gt=0)


class ExerciseBaseManagerNoTranslations(models.Manager):
    """Returns all exercise bases that have no translations"""

    def get_queryset(self):
        return super().get_queryset().annotate(count=Count('exercises')).filter(count=0)


class ExerciseBaseManagerAll(models.Manager):
    """Returns all exercise bases"""

    pass
