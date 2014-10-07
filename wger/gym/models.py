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


from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class Gym(models.Model):
    '''
    Model for a gym
    '''

    class Meta:
        permissions = (
            ("gym_trainer", _("Trainer, can see the users for a gym")),
            ("manage_gym", _("Admin, can manage users for a gym")),
            ("manage_gyms", _("Admin, can administrate the different gyms")),
        )
        ordering = ["name", ]

    name = models.CharField(max_length=60,
                            verbose_name=_('Name'))
    '''Gym name'''

    phone = models.CharField(verbose_name=_('Phone'),
                             max_length=20,
                             blank=True,
                             null=True)
    '''Phone number'''

    email = models.EmailField(verbose_name=_('Email'),
                              blank=True,
                              null=True)
    '''Email'''

    owner = models.CharField(verbose_name=_('Owner'),
                             max_length=100,
                             blank=True,
                             null=True)
    '''Gym owner'''

    zip_code = models.IntegerField(_(u'ZIP code'),
                                   max_length=5,
                                   blank=True,
                                   null=True)
    '''ZIP code'''

    city = models.CharField(_(u'City'),
                            max_length=30,
                            blank=True,
                            null=True)
    '''City'''

    street = models.CharField(_(u'Street'),
                              max_length=30,
                              blank=True,
                              null=True)
    '''Street'''

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return self.name

    def delete(self, using=None):
        '''
        Make sure that there are no users with this gym in their profiles
        '''

        # Not accessing the profile directly to avoid cyclic import problems
        for user in User.objects.filter(userprofile__gym=self).all():
            user.userprofile.gym = None
            user.userprofile.save()
        super(Gym, self).delete(using)

    def get_absolute_url(self):
        '''
        Return the URL for this object
        '''
        return reverse('gym:gym:user-list', kwargs={'pk': self.pk})

    def get_owner_object(self):
        '''
        Gym has no owner information
        '''
        return None
