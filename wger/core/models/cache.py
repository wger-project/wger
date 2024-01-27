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
from django.db import models


class UserCache(models.Model):
    """
    A table used to cache expensive queries or similar
    """

    user = models.OneToOneField(User, editable=False, on_delete=models.CASCADE)
    """
    The user
    """

    last_activity = models.DateField(null=True)
    """
    The user's last activity.

    Values for this entry are saved by signals as calculated by the
    get_user_last_activity helper function.
    """

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'Cache for user {self.user}'
