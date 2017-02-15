# -*- coding: utf-8 *-*

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

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from wger.gym.helpers import is_any_gym_admin
from wger.gym.models import GymUserConfig, GymAdminConfig


class Command(BaseCommand):
    '''
    Check that all gym trainers and users have configurations
    '''
    help = 'Check that all gym trainers and users have configurations'

    def handle(self, **options):
        '''
        Process all users
        '''

        for user in User.objects.all():
            if is_any_gym_admin(user):
                try:
                    user.gymadminconfig
                except ObjectDoesNotExist:
                    config = GymAdminConfig()
                    config.user = user
                    config.gym = user.userprofile.gym
                    config.save()

            else:
                if user.userprofile.gym_id:
                    try:
                        user.gymuserconfig
                    except ObjectDoesNotExist:
                        config = GymUserConfig()
                        config.user = user
                        config.gym = user.userprofile.gym
                        config.save()
