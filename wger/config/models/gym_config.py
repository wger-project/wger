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
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import UserProfile
from wger.gym.helpers import is_any_gym_admin
from wger.gym.models import (
    Gym,
    GymUserConfig,
)


logger = logging.getLogger(__name__)


class GymConfig(models.Model):
    """
    System wide configuration for gyms

    At the moment this only allows to set one gym as the default
    TODO: close registration (users can only become members thorough an admin)
    """

    default_gym = models.ForeignKey(
        Gym,
        verbose_name=_('Default gym'),
        help_text=_(
            'Select the default gym for this installation. '
            'This will assign all new registered users to this '
            'gym and update all existing users without a '
            'gym.'
        ),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    """
    Default gym for the wger installation
    """

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'Default gym {self.default_gym}'

    def save(self, *args, **kwargs):
        """
        Perform additional tasks
        """
        if self.default_gym:
            # All users that have no gym set in the profile are edited
            UserProfile.objects.filter(gym=None).update(gym=self.default_gym)

            # All users in the gym must have a gym config
            for profile in UserProfile.objects.filter(gym=self.default_gym):
                user = profile.user
                if not is_any_gym_admin(user):
                    try:
                        user.gymuserconfig
                    except GymUserConfig.DoesNotExist:
                        config = GymUserConfig()
                        config.gym = self.default_gym
                        config.user = user
                        config.save()
                        logger.debug(f'Creating GymUserConfig for user {user.username}')

        return super(GymConfig, self).save(*args, **kwargs)
