# -*- coding: utf-8 -*-

# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class WeightEntry(models.Model):
    '''
    Model for a weight point
    '''
    creation_date = models.DateField(verbose_name=_('Date'))
    weight = models.FloatField(verbose_name=_('Weight'))
    user = models.ForeignKey(User,
                             verbose_name=_('User'),
                             editable=False)

     # Metaclass to set some other properties
    class Meta:

        # Order by creation_date, ascending (oldest last), better for diagram
        ordering = ["creation_date", ]

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return "%s: %s kg" % (self.creation_date, self.weight)

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self
