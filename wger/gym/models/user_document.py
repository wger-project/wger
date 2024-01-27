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
from django.contrib.auth.models import User
from django.db import models as m
from django.utils.translation import gettext_lazy as _


def gym_document_upload_dir(instance, filename):
    """
    Returns the upload target for documents
    """
    return f'gym/documents/{instance.member.userprofile.gym.id}/{instance.member.id}/{uuid.uuid4()}'


class UserDocument(m.Model):
    """
    Model for a document
    """

    class Meta:
        """
        Order by time
        """

        ordering = [
            '-timestamp_created',
        ]

    user = m.ForeignKey(User, editable=False, related_name='userdocument_user', on_delete=m.CASCADE)
    """
    User this note belongs to
    """

    member = m.ForeignKey(
        User,
        editable=False,
        related_name='userdocument_member',
        on_delete=m.CASCADE,
    )
    """
    Gym member this note refers to
    """

    timestamp_created = m.DateTimeField(auto_now_add=True)
    """
    Time when this document was created
    """

    timestamp_edited = m.DateTimeField(auto_now=True)
    """
    Last time when this document was edited
    """

    document = m.FileField(verbose_name=_('Document'), upload_to=gym_document_upload_dir)
    """
    Uploaded document
    """

    original_name = m.CharField(max_length=128, editable=False)
    """
    Original document name when uploaded
    """

    name = m.CharField(
        max_length=60,
        verbose_name=_('Name'),
        help_text=_('Will use file name if nothing provided'),
        blank=True,
    )
    """
    Name or description
    """

    note = m.TextField(
        verbose_name=_('Note'),
        blank=True,
        null=True,
    )
    """
    Note with additional information
    """

    def __str__(self):
        """
        Return a more human-readable representation
        """
        if self.name != self.original_name:
            return f'{self.name} ({self.original_name})'
        else:
            return self.name

    def get_owner_object(self):
        """
        While the model has a user foreign key, this is editable by all
        trainers in the gym.
        """
        return None
