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

# wger
from wger.core.models import Language


class WeightUnit(models.Model):
    """
    A more human usable weight unit (spoon, table, slice...)
    """

    language = models.ForeignKey(
        Language,
        verbose_name=_('Language'),
        editable=False,
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_('Name'),
    )

    # Metaclass to set some other properties
    class Meta:
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
        Weight unit has no owner information
        """
        return None
