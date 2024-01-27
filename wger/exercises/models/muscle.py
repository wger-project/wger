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
import logging

# Django
from django.db import models
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger(__name__)


class Muscle(models.Model):
    """
    Muscle an exercise works out
    """

    name = models.CharField(
        max_length=50,
        verbose_name=_('Name'),
        help_text=_('In latin, e.g. "Pectoralis major"'),
    )

    # Whether to use the front or the back image for background
    is_front = models.BooleanField(default=1)

    # The name of the muscle in layman's terms
    name_en = models.CharField(
        max_length=50,
        default='',
        verbose_name=_('Alternative name'),
        help_text=_('A more basic name for the muscle'),
    )

    # Metaclass to set some other properties
    class Meta:
        ordering = [
            'name',
        ]

    # Image to use when displaying this as a main muscle in an exercise
    @property
    def image_url_main(self):
        return static(f'images/muscles/main/muscle-{self.id}.svg')

    # Image to use when displaying this as a secondary muscle in an exercise
    @property
    def image_url_secondary(self):
        return static(f'images/muscles/secondary/muscle-{self.id}.svg')

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.name

    def get_owner_object(self):
        """
        Muscle has no owner information
        """
        return False
