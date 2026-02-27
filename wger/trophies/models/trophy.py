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


class Trophy(models.Model):
    """
    Model representing a trophy/achievement that users can earn
    """

    TYPE_TIME = 'time'
    TYPE_VOLUME = 'volume'
    TYPE_COUNT = 'count'
    TYPE_SEQUENCE = 'sequence'
    TYPE_DATE = 'date'
    TYPE_PR = 'pr'
    TYPE_OTHER = 'other'

    TROPHY_TYPES = (
        (TYPE_TIME, 'Time-based'),
        (TYPE_VOLUME, 'Volume-based'),
        (TYPE_COUNT, 'Count-based'),
        (TYPE_SEQUENCE, 'Sequence-based'),
        (TYPE_DATE, 'Date-based'),
        (TYPE_PR, 'Personal Record'),
        (TYPE_OTHER, 'Other'),
    )

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    """Unique identifier for the trophy (also used for image filenames)"""

    name = models.CharField(
        max_length=100,
        verbose_name='Name',
        help_text='The name of the trophy',
    )
    """The user-facing name of the trophy"""

    description = models.TextField(
        verbose_name='Description',
        help_text='A description of how to earn this trophy',
        blank=True,
        default='',
    )
    """Description of the trophy and how to earn it"""

    trophy_type = models.CharField(
        max_length=20,
        choices=TROPHY_TYPES,
        default=TYPE_OTHER,
        verbose_name='Trophy type',
        help_text='The type of criteria used to evaluate this trophy',
    )
    """The type of trophy (time, volume, count, sequence, date, other)"""

    checker_class = models.CharField(
        max_length=255,
        verbose_name='Checker class',
        help_text='The Python class path used to check if this trophy is earned',
    )
    """Python path to the checker class (e.g., 'wger.trophies.checkers.CountBasedChecker')"""

    checker_params = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Checker parameters',
        help_text='JSON parameters passed to the checker class',
    )
    """Parameters for the checker class (e.g., {'count': 1} for workout count)"""

    is_hidden = models.BooleanField(
        default=False,
        verbose_name='Hidden',
        help_text='If true, this trophy is hidden until earned',
    )
    """Whether the trophy is hidden until earned"""

    is_progressive = models.BooleanField(
        default=False,
        verbose_name='Progressive',
        help_text='If true, this trophy shows progress towards completion',
    )
    """Whether to show progress towards earning the trophy"""

    is_active = models.BooleanField(
        default=True,
        verbose_name='Active',
        help_text='If false, this trophy cannot be earned',
    )
    """Whether the trophy is active and can be earned"""

    is_repeatable = models.BooleanField(
        default=False,
        verbose_name='Repeatable',
        help_text='If true, this trophy can be earned multiple times',
    )
    """Whether the trophy can be earned multiple times"""

    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Order',
        help_text='Display order of the trophy',
    )
    """Display order for the trophy"""

    created = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    """When the trophy was created"""

    updated = models.DateTimeField(
        auto_now=True,
        editable=False,
    )
    """When the trophy was last updated"""

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Trophy'
        verbose_name_plural = 'Trophies'

    def __str__(self):
        return self.name

    def get_owner_object(self):
        """
        Trophies don't have an owner - they are global
        """
        return None

    @property
    def image_rel_path(self):
        """
        Returns the relative (to the static folder) path to the trophy image
        """
        return f'trophies/{self.trophy_type}/{self.uuid}.png'
