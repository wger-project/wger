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

import requests
import os

from wger import get_version
from optparse import make_option
from requests.utils import default_user_agent
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.conf import settings

from wger.exercises.models import Exercise, ExerciseImage


class Command(BaseCommand):
    '''
    Download exercise images from wger.de and updates the local database

    The script assumes that the local IDs correspond to the remote ones, which
    is the case if the user installed the exercises from the JSON fixtures.
    Otherwise, the exercise is simply skipped
    '''

    option_list = BaseCommand.option_list + (
        make_option('--remote-url',
                    action='store',
                    dest='remote_url',
                    default='https://wger.de',
                    help='Remote URL to fetch the exercises from (default: https://wger.de)'),
    )

    help = ('Download exercise images from wger.de and update the local database\n'
            '\n'
            'ATTENTION: The script will download the images from the server and add them\n'
            '           to your local exercises. The exercises are identified by\n'
            '           their UUID field, if you manually edited or changed it\n'
            '           the script will not be able to match them.')

    def handle(self, **options):

        if not settings.MEDIA_ROOT:
            raise ImproperlyConfigured('Please set MEDIA_ROOT in your settings file')

        remote_url = options['remote_url']
        try:
            val = URLValidator()
            val(remote_url)
        except ValidationError:
            raise CommandError('Please enter a valid URL')

        exercise_api = "{0}/api/v2/exercise/?limit=999"
        image_api = "{0}/api/v2/exerciseimage/?exercise={1}"
        thumbnail_api = "{0}/api/v2/exerciseimage/{1}/thumbnails/"

        headers = {'User-agent': default_user_agent('wger/{} + requests'.format(get_version()))}

        # Get all exercises
        result = requests.get(exercise_api.format(remote_url), headers=headers).json()
        for exercise_json in result['results']:
            exercise_name = exercise_json['name'].encode('utf-8')
            exercise_uuid = exercise_json['uuid']
            exercise_id = exercise_json['id']

            self.stdout.write('')
            self.stdout.write(u"*** Processing {0} (ID: {1}, UUID: {2})".format(exercise_name,
                                                                                exercise_id,
                                                                                exercise_uuid))

            try:
                exercise = Exercise.objects.get(uuid=exercise_uuid)
            except Exercise.DoesNotExist:
                self.stdout.write('    Remote exercise not found in local DB, skipping...')
                continue

            # Get all images
            images = requests.get(image_api.format(remote_url, exercise_id), headers=headers).json()

            if images['count']:

                for image_json in images['results']:
                    image_id = image_json['id']
                    result = requests.get(thumbnail_api.format(remote_url, image_id),
                                          headers=headers).json()

                    image_name = os.path.basename(result['original'])
                    self.stdout.write('    Fetching image {0} - {1}'.format(image_id, image_name))

                    try:
                        image = ExerciseImage.objects.get(pk=image_id)
                        self.stdout.write('    --> Image already present locally, skipping...')
                        continue
                    except ExerciseImage.DoesNotExist:
                        self.stdout.write('    --> Image not found in local DB, creating now...')
                        image = ExerciseImage()
                        image.pk = image_id

                    # Save the downloaded image, see link for details
                    # http://stackoverflow.com/questions/1308386/programmatically-saving-image-to-
                    retrieved_image = requests.get(result['original'], headers=headers)
                    img_temp = NamedTemporaryFile(delete=True)
                    img_temp.write(retrieved_image.content)
                    img_temp.flush()

                    image.exercise = exercise
                    image.is_main = image_json['is_main']
                    image.status = image_json['status']
                    image.image.save(
                        os.path.basename(image_name),
                        File(img_temp),
                    )
                    image.save()

            else:
                self.stdout.write('    No images for this exercise, nothing to do')
