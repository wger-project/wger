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
from django.db import models as m
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# wger
from wger.gym.managers import GymManager


class Gym(m.Model):
    """
    Model for a gym
    """

    class Meta:
        permissions = (
            ('gym_trainer', _('Trainer: can see the users for a gym')),
            ('manage_gym', _('Admin: can manage users for a gym')),
            ('manage_gyms', _('Admin: can administrate the different gyms')),
        )
        ordering = [
            'name',
        ]

    objects = GymManager()
    """
    Custom Gym Query Manager
    """

    name = m.CharField(max_length=60, verbose_name=_('Name'))
    """Gym name"""

    phone = m.CharField(
        verbose_name=_('Phone'),
        max_length=20,
        blank=True,
        null=True,
    )
    """Phone number"""

    email = m.EmailField(
        verbose_name=_('Email'),
        blank=True,
        null=True,
    )
    """Email"""

    owner = m.CharField(
        verbose_name=_('Owner'),
        max_length=100,
        blank=True,
        null=True,
    )
    """Gym owner"""

    zip_code = m.CharField(
        _('ZIP code'),
        max_length=10,
        blank=True,
        null=True,
    )
    """ZIP code"""

    city = m.CharField(
        _('City'),
        max_length=30,
        blank=True,
        null=True,
    )
    """City"""

    street = m.CharField(
        _('Street'),
        max_length=30,
        blank=True,
        null=True,
    )
    """Street"""

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.name

    def get_absolute_url(self):
        """
        Return the URL for this object
        """
        return reverse('gym:gym:user-list', kwargs={'pk': self.pk})

    def get_owner_object(self):
        """
        Gym has no owner information
        """
        return None
