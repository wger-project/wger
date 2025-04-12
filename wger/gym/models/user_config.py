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
from django.contrib.auth.models import User
from django.db import models as m
from django.utils.translation import gettext_lazy as _

# wger
from wger.gym.models import Gym


class AbstractGymUserConfigModel(m.Model):
    """
    Abstract class for member and admin gym configuration models
    """

    class Meta:
        abstract = True

    gym = m.ForeignKey(
        Gym,
        editable=False,
        on_delete=m.CASCADE,
    )
    """
    Gym this configuration belongs to
    """

    user = m.OneToOneField(
        User,
        editable=False,
        on_delete=m.CASCADE,
    )
    """
    User this configuration belongs to
    """


class GymAdminConfig(AbstractGymUserConfigModel, m.Model):
    """
    Administrator/trainer configuration options for a specific gym
    """

    class Meta:
        unique_together = ('gym', 'user')
        """
        Only one entry per user and gym
        """

    overview_inactive = m.BooleanField(
        verbose_name=_('Overview of inactive members'),
        help_text=_('Receive email overviews of inactive members'),
        default=True,
    )
    """
    Reminder of inactive members
    """

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self


class GymUserConfig(AbstractGymUserConfigModel, m.Model):
    """
    Gym member configuration options for a specific gym
    """

    class Meta:
        unique_together = ('gym', 'user')
        """
        Only one entry per user and gym
        """

    include_inactive = m.BooleanField(
        verbose_name=_('Include in inactive overview'),
        help_text=_('Include this user in the email list with inactive members'),
        default=True,
    )
    """
    Include user in inactive overview
    """

    def get_owner_object(self):
        """
        While the model has a user foreign key, this is editable by all
        trainers in the gym.
        """
        return None
