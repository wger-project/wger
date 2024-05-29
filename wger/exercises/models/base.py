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
import datetime
import uuid
from typing import (
    List,
    Optional,
)

# Django
from django.core.checks import Warning
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import (
    get_language,
    gettext_lazy as _,
)

# Third Party
from simple_history.models import HistoricalRecords

# wger
from wger.core.models import Language
from wger.exercises.managers import (
    ExerciseBaseManagerAll,
    ExerciseBaseManagerNoTranslations,
    ExerciseBaseManagerTranslations,
)
from wger.utils.cache import reset_exercise_api_cache
from wger.utils.constants import ENGLISH_SHORT_NAME
from wger.utils.models import (
    AbstractHistoryMixin,
    AbstractLicenseModel,
    collect_models_author_history,
)

# Local
from .category import ExerciseCategory
from .equipment import Equipment
from .muscle import Muscle
from .variation import Variation


class ExerciseBase(AbstractLicenseModel, AbstractHistoryMixin, models.Model):
    """
    Model for an exercise base
    """

    objects = ExerciseBaseManagerAll()
    no_translations = ExerciseBaseManagerNoTranslations()
    translations = ExerciseBaseManagerTranslations()
    """
    Custom Query Manager
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name='UUID',
    )
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
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    """Variations of this exercise"""

    created = models.DateTimeField(
        _('Date'),
        auto_now_add=True,
    )
    """The submission datetime"""

    last_update = models.DateTimeField(
        _('Date'),
        auto_now=True,
    )
    """Datetime of last modification"""

    history = HistoricalRecords()
    """Edit history"""

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'base {self.uuid} ({self.get_translation()})'

    def get_absolute_url(self):
        """
        Returns the canonical URL to view an exercise
        """
        return reverse('exercise:exercise:view-base', kwargs={'pk': self.id})

    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)

        no_translations = cls.no_translations.all().count()
        if no_translations:
            errors.append(
                Warning(
                    'exercises without translations',
                    hint=f'There are {no_translations} exercises without translations, this will '
                    'cause problems! You can output or delete them with "python manage.py '
                    'exercises-health-check --help"',
                    id='wger.W002',
                )
            )

        return errors

    #
    # Own methods
    #

    @property
    def total_authors_history(self):
        """
        All authors history related to the BaseExercise.
        """
        collect_for_models = [
            *self.exercises.all(),
            *self.exercisevideo_set.all(),
            *self.exerciseimage_set.all(),
        ]
        return self.author_history.union(collect_models_author_history(collect_for_models))

    @property
    def last_update_global(self):
        """
        The latest update datetime of all exercises, videos and images.
        """
        return max(
            self.last_update,
            *[image.last_update for image in self.exerciseimage_set.all()],
            *[video.last_update for video in self.exercisevideo_set.all()],
            *[translation.last_update for translation in self.exercises.all()],
            datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
        )

    @property
    def main_image(self):
        """
        Return the main image for the exercise or None if nothing is found
        """
        return self.exerciseimage_set.all().filter(is_main=True).first()

    @property
    def languages(self) -> List[Language]:
        """
        Returns the languages from the exercises that use this base
        """
        return [exercise.language for exercise in self.exercises.all()]

    @property
    def base_variations(self):
        """
        Returns the variations of this exercise base, excluding itself
        """
        if not self.variations:
            return []
        return self.variations.exercisebase_set.filter(~Q(id=self.id))

    def get_translation(self, language: Optional[str] = None):
        """
        Returns the exercise for the given language. If the language is not
        available, return the English translation.

        Note that as a fallback, if no English translation is found, the
        first available one is returned. While this is kind of wrong, it won't
        happen in our dataset, but it is possible that some local installations
        have deleted the English translation or similar
        """
        # wger
        from wger.exercises.models import Exercise

        language = language or get_language()

        try:
            translation = self.exercises.get(language__short_name=language)
        except Exercise.DoesNotExist:
            try:
                translation = self.exercises.get(language__short_name=ENGLISH_SHORT_NAME)
            except Exercise.DoesNotExist:
                translation = self.exercises.first()
        except Exercise.MultipleObjectsReturned:
            translation = self.exercises.filter(language__short_name=language).first()

        return translation

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        reset_exercise_api_cache(self.uuid)

    def delete(self, using=None, keep_parents=False, replace_by: str = None):
        """
        Save entry to log
        """
        # wger
        from wger.exercises.models import DeletionLog

        if replace_by:
            try:
                ExerciseBase.objects.get(uuid=replace_by)
            except ExerciseBase.DoesNotExist:
                replace_by = None

        log = DeletionLog(
            model_type=DeletionLog.MODEL_BASE,
            uuid=self.uuid,
            comment=f'Exercise base of {self.get_translation(ENGLISH_SHORT_NAME)}',
            replaced_by=replace_by,
        )
        log.save()

        reset_exercise_api_cache(self.uuid)

        return super().delete(using, keep_parents)
