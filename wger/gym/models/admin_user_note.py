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


class AdminUserNote(m.Model):
    """
    Administrator notes about a member
    """

    class Meta:
        """
        Order by time
        """

        ordering = [
            '-timestamp_created',
        ]

    user = m.ForeignKey(
        User,
        editable=False,
        related_name='adminusernote_user',
        on_delete=m.CASCADE,
    )
    """
    User this note belongs to
    """

    member = m.ForeignKey(
        User,
        editable=False,
        related_name='adminusernote_member',
        on_delete=m.CASCADE,
    )
    """
    Gym member this note refers to
    """

    timestamp_created = m.DateTimeField(auto_now_add=True)
    """
    Time when this note was created
    """

    timestamp_edited = m.DateTimeField(auto_now=True)
    """
    Last time when this note was edited
    """

    note = m.TextField(verbose_name=_('Note'))
    """
    Actual note
    """

    def get_owner_object(self):
        """
        While the model has a user foreign key, this is editable by all
        trainers in the gym.
        """
        return None
