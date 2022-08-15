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

# Django
from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import Language
from wger.utils.cache import (
    cache_mapper,
    delete_template_fragment_cache,
)


class LanguageConfig(models.Model):
    """
    Configuration for languages

    Allows to specify what exercises and ingredients are shown for each language
    """
    SHOW_ITEM_EXERCISES = '1'
    SHOW_ITEM_INGREDIENTS = '2'
    SHOW_ITEM_LIST = (
        (SHOW_ITEM_EXERCISES, _('Exercises')),
        (SHOW_ITEM_INGREDIENTS, _('Ingredients')),
    )

    language = models.ForeignKey(
        Language,
        related_name='language_source',
        editable=False,
        on_delete=models.CASCADE,
    )
    language_target = models.ForeignKey(
        Language,
        related_name='language_target',
        editable=False,
        on_delete=models.CASCADE,
    )
    item = models.CharField(max_length=2, choices=SHOW_ITEM_LIST, editable=False)
    show = models.BooleanField(default=1)

    class Meta:
        """
        Set some other properties
        """
        ordering = [
            "item",
            "language_target",
        ]

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return "Config for language {0}".format(self.language)

    def save(self, *args, **kwargs):
        """
        Reset all cached infos
        """

        super(LanguageConfig, self).save(*args, **kwargs)

        # Cached objects
        cache.delete(cache_mapper.get_language_config_key(self.language, self.item))

    def delete(self, *args, **kwargs):
        """
        Reset all cached infos
        """

        # Cached objects
        cache.delete(cache_mapper.get_language_config_key(self.language, self.item))

        super(LanguageConfig, self).delete(*args, **kwargs)
