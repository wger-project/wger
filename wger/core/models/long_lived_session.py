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
from django.utils import timezone


class LongLivedSession(models.Model):
    """
    Index of the long-lived sessions backing a user's headless refresh tokens

    The Django session table has no user column and its payload is an opaque
    signed blob, so listing the sessions of one user would mean decoding every
    unexpired row of the whole instance. The mapping is therefore recorded here
    when the session is minted, see wger.utils.headless_long_lived.
    """

    user = models.ForeignKey(
        User,
        editable=False,
        on_delete=models.CASCADE,
        related_name='long_lived_sessions',
    )
    """
    The owner of the session
    """

    session_key = models.CharField(max_length=40, editable=False, unique=True)
    """
    Primary key of the row in the session table
    """

    created = models.DateTimeField(default=timezone.now, editable=False)
    """
    When the token was generated, used to sort the overview
    """

    class Meta:
        ordering = ['-created']

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'Long-lived session for user {self.user}'
