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

import datetime

from django.utils.timezone import now
from django.core.management.base import BaseCommand
from wger.core.models import UserProfile


class Command(BaseCommand):
    '''
    Helper admin command to clean up demo users, to be called e.g. by cron
    '''

    help = 'Deletes all temporary users older than 1 week'

    def handle(self, **options):

        profile_list = UserProfile.objects.filter(is_temporary=True)
        counter = 0
        for profile in profile_list:
            delta = now() - profile.user.date_joined

            if (delta >= datetime.timedelta(7)):
                counter += 1
                profile.user.delete()

        self.stdout.write("Deleted {0} temporary users".format(counter))
