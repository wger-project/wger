# -*- coding: utf-8 -*-

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

# Third Party
from django.contrib.auth.models import User
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class BodyMeasurementsEntry(models.Model):
    '''
    Model for a Body Measurements
    '''
    date = models.DateField(verbose_name=_('Date'))
    chest  = models.DecimalField(verbose_name=_(''),
                                 max_digits=5,
                                 decimal_places=2,
                                 validators=[MinValueValidator(30), MaxValueValidator(600)])
    hips  = models.DecimalField(verbose_name=_(''),
                                 max_digits=5,
                                 decimal_places=2,
                                 validators=[MinValueValidator(30), MaxValueValidator(600)])
    waist  = models.DecimalField(verbose_name=_(''),
                                 max_digits=5,
                                 decimal_places=2,
                                 validators=[MinValueValidator(30), MaxValueValidator(600)])
    user = models.ForeignKey(User,
                             verbose_name=_('User'))
    '''
    The user the bodyWeight entry belongs to.
    '''

    class Meta:
        '''
        Metaclass to set some other properties
        '''
        verbose_name = _('Body Measurements')
        ordering = ["date", ]
        get_latest_by = "date"
        unique_together = ("date", "user")

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return u"{0}: {1:.2f} In".format(
            self.date, 
            self.chest 
            )

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self
