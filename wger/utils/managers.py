# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models
from django.db.models.query import QuerySet
from wger.utils.models import AbstractSubmissionModel


'''
Custom managers and querysets
'''

# TODO: starting with django 1.7 this is simplified, see
#       https://docs.djangoproject.com/en/1.7/topics/db/managers/#creating-manager-with-queryset-methods


class SubmissionQuerySet(QuerySet):
    def accepted(self):
        return self.filter(status=AbstractSubmissionModel.STATUS_ACCEPTED)

    def pending(self):
        return self.filter(status=AbstractSubmissionModel.STATUS_PENDING)


class SubmissionManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return SubmissionQuerySet(self.model, using=self._db)

    def accepted(self):
        return self.get_queryset().accepted()

    def pending(self):
        return self.get_queryset().pending()
