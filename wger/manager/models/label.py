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


class Label(models.Model):
    """
    A free text label for routines

    This can be used for example to label the different weeks, or set other info
    such as "deload", etc.
    """

    routine = models.ForeignKey(
        'Routine',
        verbose_name='Routine',
        on_delete=models.CASCADE,
        related_name='labels',
    )
    """
    The routine this label belongs to
    """

    start_offset = models.PositiveIntegerField(
        verbose_name='Start',
        default=1,
    )
    """
    The number of days after the start of the routine when this label becomes active
    """

    end_offset = models.PositiveIntegerField(
        verbose_name='End',
        default=2,
    )
    """
    The number of days after the start of the routine when this label ceases being active
    """

    label = models.CharField(
        max_length=35,
        verbose_name='Label',
    )
    """
    The label text
    """

    comment = models.CharField(max_length=500, verbose_name='Comment', default='')
    """
    A free text comment
    """

    class Meta:
        """
        Metaclass to set some other properties
        """

        ordering = [
            'start_offset',
        ]

    def clean(self):
        """
        Check that the end offset is greater than the start offset
        """
        if self.end_offset < self.start_offset:
            raise ValueError('End offset must be greater than start offset')

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'Label {self.label} for routine {self.routine}'

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.routine
