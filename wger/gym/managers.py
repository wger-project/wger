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
from django.db.models import Q
from django.contrib.auth.models import (
    Permission,
    User
)


class GymManager(models.Manager):
    '''
    Custom query manager for Gyms
    '''
    def get_members(self, gym_pk):
        '''
        Returns all members for this gym (i.e non-admin ones)
        '''
        perm_gym = Permission.objects.get(codename='manage_gym')
        perm_gyms = Permission.objects.get(codename='manage_gyms')
        perm_trainer = Permission.objects.get(codename='gym_trainer')

        users = User.objects.filter(userprofile__gym_id=gym_pk)
        return users.exclude(Q(groups__permissions=perm_gym) |
                             Q(groups__permissions=perm_gyms) |
                             Q(groups__permissions=perm_trainer)).distinct()

    def get_admins(self, gym_pk):
        '''
        Returns all admins for this gym (i.e trainers, managers, etc.)
        '''
        perm_gym = Permission.objects.get(codename='manage_gym')
        perm_gyms = Permission.objects.get(codename='manage_gyms')
        perm_trainer = Permission.objects.get(codename='gym_trainer')

        users = User.objects.filter(userprofile__gym_id=gym_pk)
        return users.filter(Q(groups__permissions=perm_gym) |
                            Q(groups__permissions=perm_gyms) |
                            Q(groups__permissions=perm_trainer)).distinct()
