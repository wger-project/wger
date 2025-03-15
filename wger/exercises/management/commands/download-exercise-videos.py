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

# Django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# wger
from wger.core.management.wger_command import WgerCommand
from wger.exercises.sync import download_exercise_videos


class Command(WgerCommand):
    """
    Download exercise videos from wger.de and updates the local database

    Both the exercises and the videos are identified by their UUID, which can't
    be modified via the GUI.
    """

    help = 'Download exercise videos from wger.de and update the local database'

    def handle(self, **options):
        if not settings.MEDIA_ROOT:
            raise ImproperlyConfigured('Please set MEDIA_ROOT in your settings file')

        super().handle(**options)

        download_exercise_videos(self.stdout.write, options['remote_url'], self.style.SUCCESS)
