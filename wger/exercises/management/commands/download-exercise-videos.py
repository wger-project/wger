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

# Standard Library
import os

# Django
from django.conf import settings
from django.core.exceptions import (
    ImproperlyConfigured,
    ValidationError,
)
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.core.validators import URLValidator

# Third Party
import requests
from requests.utils import default_user_agent

# wger
from wger import get_version
from wger.exercises.models import (
    ExerciseBase,
    ExerciseVideo,
)


VIDEO_API = "{0}/api/v2/video/"


class Command(BaseCommand):
    """
    Download exercise videos from wger.de and updates the local database

    Both the exercises and the videos are identified by their UUID, which can't
    be modified via the GUI.
    """

    help = 'Download exercise videos from wger.de and update the local database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--remote-url',
            action='store',
            dest='remote_url',
            default='https://wger.de',
            help='Remote URL to fetch the exercises from (default: '
            'https://wger.de)'
        )

    def handle(self, **options):

        if not settings.MEDIA_ROOT:
            raise ImproperlyConfigured('Please set MEDIA_ROOT in your settings file')

        remote_url = options['remote_url']
        try:
            val = URLValidator()
            val(remote_url)
        except ValidationError:
            raise CommandError('Please enter a valid URL')

        headers = {'User-agent': default_user_agent('wger/{} + requests'.format(get_version()))}

        # Get all videos
        page = 1
        all_videos_processed = False
        result = requests.get(VIDEO_API.format(remote_url), headers=headers).json()
        self.stdout.write('*** Processing videos ***')
        while not all_videos_processed:
            self.stdout.write('')
            self.stdout.write(f'*** Page {page}')
            self.stdout.write('')

            for video_data in result['results']:
                video_uuid = video_data['uuid']
                self.stdout.write(f'Processing video {video_uuid}')

                try:
                    exercise_base = ExerciseBase.objects.get(uuid=video_data['exercise_base_uuid'])
                except ExerciseBase.DoesNotExist:
                    self.stdout.write('    Remote exercise base not found in local DB, skipping...')
                    continue

                try:
                    ExerciseVideo.objects.get(uuid=video_uuid)
                    self.stdout.write('    Video already present locally, skipping...')
                    continue
                except ExerciseVideo.DoesNotExist:
                    self.stdout.write('    Video not found in local DB, creating now...')
                    video = ExerciseVideo()
                    video.exercise_base = exercise_base
                    video.uuid = video_uuid
                    video.is_main = video_data['is_main']
                    video.license_id = video_data['license']
                    video.license_author = video_data['license_author']
                    video.size = video_data['size']
                    video.width = video_data['width']
                    video.height = video_data['height']
                    video.codec = video_data['codec']
                    video.codec_long = video_data['codec_long']
                    video.duration = video_data['duration']

                # Save the downloaded video
                # http://stackoverflow.com/questions/1308386/programmatically-saving-image-to-
                retrieved_video = requests.get(video_data['video'], headers=headers)

                # Temporary files on Windows don't support the delete attribute
                if os.name == 'nt':
                    img_temp = NamedTemporaryFile()
                else:
                    img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(retrieved_video.content)
                img_temp.flush()

                video.video.save(
                    os.path.basename(os.path.basename(video_data['video'])),
                    File(img_temp),
                )
                video.save()
                self.stdout.write(self.style.SUCCESS('    saved successfully'))

            if result['next']:
                page += 1
                result = requests.get(result['next'], headers=headers).json()
            else:
                all_videos_processed = True
