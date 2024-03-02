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


class IngredientCategory(models.Model):
    """
    Model for an Ingredient category
    """

    name = models.CharField(max_length=100, verbose_name=_('Name'))

    # Metaclass to set some other properties
    class Meta:
        verbose_name_plural = _('Ingredient Categories')
        ordering = [
            'name',
        ]

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.name

    def get_owner_object(self):
        """
        Category has no owner information
        """
        return False
