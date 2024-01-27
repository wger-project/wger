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


class WeightUnit(models.Model):
    """
    Weight unit, used in combination with an amount such as '10 kg', '5 plates'
    """

    class Meta:
        """
        Set Meta options
        """

        ordering = [
            'name',
        ]

    name = models.CharField(max_length=100, verbose_name=_('Name'))

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.name

    #
    # Own methods
    #
    def get_owner_object(self):
        """
        Unit has no owner information
        """
        return None

    @property
    def is_weight(self):
        """
        Checks that the unit is a weight proper

        This is done basically to not litter the code with magic IDs
        """
        return self.id in (1, 2)
