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
from django.db import models
from django.utils.translation import gettext_lazy as _

# Third Party
from simple_history.models import HistoricalRecords

# wger
from wger.utils.managers import SubmissionManager
from wger.utils.models import (
    AbstractLicenseModel,
    AbstractSubmissionModel,
)

# Local
from .category import ExerciseCategory
from .equipment import Equipment
from .muscle import Muscle
from .variation import Variation


class ExerciseBase(AbstractSubmissionModel, AbstractLicenseModel, models.Model):
    """
    Model for an exercise base
    """

    objects = SubmissionManager()
    """Custom manager"""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='UUID')
    """Globally unique ID, to identify the base across installations"""

    category = models.ForeignKey(
        ExerciseCategory,
        verbose_name=_('Category'),
        on_delete=models.CASCADE,
    )

    muscles = models.ManyToManyField(
        Muscle,
        blank=True,
        verbose_name=_('Primary muscles'),
    )
    """Main muscles trained by the exercise"""

    muscles_secondary = models.ManyToManyField(
        Muscle,
        verbose_name=_('Secondary muscles'),
        related_name='secondary_muscles_base',
        blank=True,
    )
    """Secondary muscles trained by the exercise"""

    equipment = models.ManyToManyField(
        Equipment,
        verbose_name=_('Equipment'),
        blank=True,
    )
    """Equipment needed by this exercise"""

    variations = models.ForeignKey(
        Variation,
        verbose_name=_('Variations'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    """Variations of this exercise"""

    creation_date = models.DateField(
        _('Date'),
        auto_now_add=True,
    )
    """The submission date"""

    update_date = models.DateTimeField(_('Date'), auto_now=True)
    """Datetime of last modification"""

    history = HistoricalRecords()
    """Edit history"""

    #
    # Own methods
    #

    @property
    def get_languages(self):
        """
        Returns the languages from the exercises that use this base
        """
        return [exercise.language for exercise in self.exercises.all()]
