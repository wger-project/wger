# -*- coding: utf-8 *-*

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

import datetime

from django.utils.timezone import now
from django.core.management.base import BaseCommand
from manager.models import UserProfile


class Command(BaseCommand):
    '''
    Helper admin command to clean up demo users, to be called e.g. by cron
    '''

    help = 'Deletes all temporary users older than 1 week'

    def handle(self, *args, **options):

        user_list = UserProfile.objects.filter(is_temporary=True)
        for profile in user_list:
            delta = now() - profile.user.date_joined

            if (delta >= datetime.timedelta(7)):
                self.stdout.write("Deleting user %s, joined %s days ago\n" % (profile,
                                                                              delta.days))
                profile.user.delete()
