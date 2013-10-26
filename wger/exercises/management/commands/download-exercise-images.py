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

import json
import urllib
import os
from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.core.files import File
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from wger.exercises.models import Exercise
from wger.exercises.models import ExerciseImage


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
            '           to local exercises. If you happen to have edited them, the script\n'
            '           *might* add the wrong images to the wrong exercises if they match\n'
            '           the remote ID.')

    def handle(self, *args, **options):

        remote_url = options['remote_url']
        val = URLValidator()
        try:
            val(remote_url)
        except ValidationError:
            raise CommandError('Please enter a valid URL')

        # Get all exercises
        result = json.load(urllib.urlopen("{0}/api/v1/exercise/?limit=0".format(remote_url)))
        for exercise_json in result['objects']:
            exercise_name = exercise_json['name']
            exercise_id = exercise_json['id']

            self.stdout.write(u"*** Processing {0} (ID: {1})".format(exercise_name, exercise_id))

            try:
                exercise = Exercise.objects.get(pk=exercise_id)
            except Exercise.DoesNotExist:
                self.stdout.write('Remote exercise not found in local DB, skipping...')
                self.stdout.write('')
                continue

            if exercise_json['images']:

                # Get all images
                for image_resource in exercise_json['images']:

                    result = json.load(urllib.urlopen("{0}{1}".format(remote_url, image_resource)))
                    image_name = os.path.basename(result['image'])
                    self.stdout.write('Fetching image {0} - {1}'.format(result['id'], image_name))

                    image_id = result['id']

                    try:
                        image = ExerciseImage.objects.get(pk=image_id)
                        self.stdout.write('--> Image already present locally, skipping...')
                        continue
                    except ExerciseImage.DoesNotExist:
                        self.stdout.write('--> Image not found in local DB, creating now...')
                        image = ExerciseImage()
                        image.pk = image_id

                    # Save the downloaded image, see link for details
                    # http://stackoverflow.com/questions/1308386/programmatically-saving-image-to-
                    retrieved_image = urllib.urlretrieve(result['image'])
                    image.exercise = exercise
                    image.is_main = result['is_main']
                    image.image.save(
                        os.path.basename(image_name),
                        File(open(retrieved_image[0]), 'rb')
                    )
                    image.save()
            else:
                self.stdout.write('No images for this exercise, nothing to do')

            self.stdout.write('')
