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
from django.utils.translation import gettext_lazy as _


def trophy_image_upload_path(instance, filename):
    """
    Returns the upload path for trophy images
    """
    ext = filename.split('.')[-1]
    return f'trophies/{instance.uuid}.{ext}'


class Trophy(models.Model):
    """
    Model representing a trophy/achievement that users can earn
    """

    TYPE_TIME = 'time'
    TYPE_VOLUME = 'volume'
    TYPE_COUNT = 'count'
    TYPE_SEQUENCE = 'sequence'
    TYPE_DATE = 'date'
    TYPE_OTHER = 'other'

    TROPHY_TYPES = (
        (TYPE_TIME, _('Time-based')),
        (TYPE_VOLUME, _('Volume-based')),
        (TYPE_COUNT, _('Count-based')),
        (TYPE_SEQUENCE, _('Sequence-based')),
        (TYPE_DATE, _('Date-based')),
        (TYPE_OTHER, _('Other')),
    )

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    """Unique identifier for the trophy"""

    name = models.CharField(
        max_length=100,
        verbose_name=_('Name'),
        help_text=_('The name of the trophy'),
    )
    """The name of the trophy"""

    description = models.TextField(
        verbose_name=_('Description'),
        help_text=_('A description of how to earn this trophy'),
        blank=True,
        default='',
    )
    """Description of the trophy and how to earn it"""

    image = models.ImageField(
        verbose_name=_('Image'),
        upload_to=trophy_image_upload_path,
        blank=True,
        null=True,
    )
    """Optional image for the trophy"""

    trophy_type = models.CharField(
        max_length=20,
        choices=TROPHY_TYPES,
        default=TYPE_OTHER,
        verbose_name=_('Trophy type'),
        help_text=_('The type of criteria used to evaluate this trophy'),
    )
    """The type of trophy (time, volume, count, sequence, date, other)"""

    checker_class = models.CharField(
        max_length=255,
        verbose_name=_('Checker class'),
        help_text=_('The Python class path used to check if this trophy is earned'),
    )
    """Python path to the checker class (e.g., 'wger.trophies.checkers.CountBasedChecker')"""

    checker_params = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Checker parameters'),
        help_text=_('JSON parameters passed to the checker class'),
    )
    """Parameters for the checker class (e.g., {'count': 1} for workout count)"""

    is_hidden = models.BooleanField(
        default=False,
        verbose_name=_('Hidden'),
        help_text=_('If true, this trophy is hidden until earned'),
    )
    """Whether the trophy is hidden until earned"""

    is_progressive = models.BooleanField(
        default=False,
        verbose_name=_('Progressive'),
        help_text=_('If true, this trophy shows progress towards completion'),
    )
    """Whether to show progress towards earning the trophy"""

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_('If false, this trophy cannot be earned'),
    )
    """Whether the trophy is active and can be earned"""

    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order'),
        help_text=_('Display order of the trophy'),
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
        verbose_name = _('Trophy')
        verbose_name_plural = _('Trophies')

    def __str__(self):
        return self.name

    def get_owner_object(self):
        """
        Trophies don't have an owner - they are global
        """
        return None
