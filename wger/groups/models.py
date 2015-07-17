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

import datetime
import logging
from django.utils.encoding import python_2_unicode_compatible

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from wger.gym.models import Gym


def group_image_upload_dir(instance, filename):
    '''
    Returns the upload target for group logos
    '''
    return "group-images/{0}/{1}".format(instance.group.id, filename)


@python_2_unicode_compatible
class Group(models.Model):
    '''
    Model for a group
    '''

    class Meta:
        '''
        Meta class to set some other properties
        '''
        ordering = ["name", ]

    name = models.CharField(_('Name'), max_length=30)
    '''The groups name'''

    description = models.TextField(_('Description'), default='', blank=True)
    '''A possibly longer description for the group'''

    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    '''Creation date for the group'''

    public = models.BooleanField(_('Public group'),
                                 default=False,
                                 help_text=_('Public groups can be accessed by all users '
                                             'while private groups are invite-only.'))
    '''Group type: public or private'''

    image = models.ImageField(verbose_name=_('Image'),
                              help_text=_('Only PNG and JPEG formats are supported'),
                              upload_to=group_image_upload_dir)
    '''Group's logo'''

    gym = models.ForeignKey(Gym,
                            null=True,
                            blank=True)
    '''The gym this group belongs to, if any'''

    members = models.ManyToManyField(User, through='Membership')
    '''The group's members'''

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return self.name


class Membership(models.Model):
    '''
    Intermediate table for many-to-many relationship between users and groups
    '''

    group = models.ForeignKey(Group)
    '''The group'''

    user = models.ForeignKey(User)
    '''The user'''

    admin = models.BooleanField(verbose_name=_('Administrator'),
                                default=False)
    '''Flag indicating whether the user is an administrator for the group'''
