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


class License(models.Model):
    """
    License for an item (exercise, ingredient, etc.)
    """

    full_name = models.CharField(
        max_length=60,
        verbose_name=_('Full name'),
        help_text=_(
            'If a license has been localized, e.g. the Creative '
            'Commons licenses for the different countries, add '
            'them as separate entries here.'
        ),
    )
    """Full name"""

    short_name = models.CharField(
        max_length=15,
        verbose_name=_('Short name, e.g. CC-BY-SA 3'),
    )
    """Short name, e.g. CC-BY-SA 3"""

    url = models.URLField(
        verbose_name=_('Link'),
        help_text=_('Link to license text or other information'),
        blank=True,
        null=True,
    )
    """URL to full license text or other information"""

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

    #
    # Own methods
    #
    def get_owner_object(self):
        """
        License has no owner information
        """
        return None
