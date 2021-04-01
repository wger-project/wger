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
    ValidationError
)
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import (
    BaseCommand,
    CommandError
)
from django.core.validators import URLValidator

# Third Party
import requests
from requests.utils import default_user_agent

# wger
from wger import get_version
from wger.exercises.models import (
    ExerciseBase,
    ExerciseImage
)


IMAGE_API = "{0}/api/v2/exerciseimage/?status=2"


class Command(BaseCommand):
    """
    Download exercise images from wger.de and updates the local database

    Both the exercises and the images are identified by their UUID, which can't
    be modified via the GUI.
    """

    help = ('Download exercise images from wger.de and update the local database\n'
            '\n'
            'ATTENTION: The script will download the images from the server and add them\n'
            '           to your local exercises. The exercises are identified by\n'
            '           their UUID field, if you manually edited or changed it\n'
            '           the script will not be able to match them.')

    def add_arguments(self, parser):
        parser.add_argument('--remote-url',
                            action='store',
                            dest='remote_url',
                            default='https://wger.de',
                            help='Remote URL to fetch the exercises from (default: '
                                 'https://wger.de)')

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

        # Get all images
        page = 1
        all_images_processed = False
        result = requests.get(IMAGE_API.format(remote_url), headers=headers).json()
        self.stdout.write('*** Processing images ***')
        while not all_images_processed:
            self.stdout.write('')
            self.stdout.write(f'*** Page {page}')
            self.stdout.write('')
            page += 1

            if result['next']:
                result = requests.get(result['next'], headers=headers).json()
            else:
                all_images_processed = True

            for image_data in result['results']:
                image_uuid = image_data['uuid']

                self.stdout.write(f'Processing image {image_uuid}')

                try:
                    exercise_base = ExerciseBase.objects.get(id=image_data['exercise'])
                except ExerciseBase.DoesNotExist:
                    self.stdout.write('    Remote exercise base not found in local DB, skipping...')
                    continue

                try:
                    image = ExerciseImage.objects.get(uuid=image_uuid)
                    self.stdout.write('    Image already present locally, skipping...')
                    continue
                except ExerciseImage.DoesNotExist:
                    self.stdout.write('    Image not found in local DB, creating now...')
                    image = ExerciseImage()
                    image.uuid = image_uuid

                # Save the downloaded image
                # http://stackoverflow.com/questions/1308386/programmatically-saving-image-to-
                retrieved_image = requests.get(image_data['image'], headers=headers)

                # Temporary files on windows don't support the delete attribute
                if os.name == 'nt':
                    img_temp = NamedTemporaryFile()
                else:
                    img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(retrieved_image.content)
                img_temp.flush()

                image.exercise = exercise_base
                image.is_main = image_data['is_main']
                image.status = image_data['status']
                image.image.save(
                    os.path.basename(os.path.basename(image_data['image'])),
                    File(img_temp),
                )
                image.save()
                self.stdout.write(self.style.SUCCESS('    successfully saved'))
