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
from django.core.management.base import BaseCommand

from wger.gym.helpers import get_user_last_activity


class Command(BaseCommand):
    '''
    Updates the user cache table
    '''

    help = 'Update the user cache-table. This is only needed when the python' \
           'code used to calculate any of the cached entries is changed and ' \
           'the ones in the database need to be updated to reflect the new logic.'

    def handle(self, **options):
        '''
        Process the options
        '''

        print('** Updating last activity')
        for user in User.objects.all():
            user.usercache.last_activity = get_user_last_activity(user)
            user.usercache.save()
