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
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Language(models.Model):
    """
    Language of an item (exercise, workout, etc.)
    """

    # e.g. 'de'
    short_name = models.CharField(
        max_length=2,
        verbose_name=_('Language short name'),
        help_text='ISO 639-1',
        unique=True,
    )

    # e.g. 'Deutsch'
    full_name = models.CharField(
        max_length=30,
        verbose_name=_('Language full name'),
    )

    # e.g. 'German'
    full_name_en = models.CharField(
        max_length=30,
        verbose_name=_('Language full name in English'),
    )

    class Meta:
        """
        Set Meta options
        """

        ordering = [
            'full_name',
        ]

    #
    # Django methods
    #
    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'{self.full_name} ({self.short_name})'

    def get_absolute_url(self):
        """
        Returns the canonical URL to view a language
        """
        return reverse('core:language:view', kwargs={'pk': self.id})

    #
    # Own methods
    #
    def get_owner_object(self):
        """
        Muscle has no owner information
        """
        return False

    @property
    def static_path(self):
        return f'images/icons/flags/{self.short_name}.svg'
