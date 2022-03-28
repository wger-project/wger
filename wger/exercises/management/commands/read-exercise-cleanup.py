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
import csv
import pathlib

# Django
from django.core.files import File
from django.core.management.base import BaseCommand

# Third Party
from utils.constants import DEFAULT_LICENSE_ID

# wger
from wger.core.models import (
    Language,
    License,
)
from wger.exercises.models import (
    Alias,
    Equipment,
    Exercise,
    ExerciseBase,
    ExerciseCategory,
    ExerciseVideo,
    Variation,
)


class Command(BaseCommand):
    """
    ONE OFF SCRIPT!

    This script reads back into the database corrections made to a CSV generated with
    exercise-cleanup.py
    """

    help = 'Update the exercise database based on the exercise cleanup spreadsheet'

    def handle(self, **options):
        csv_file = open('exercise_cleanup.csv', 'r', newline='')
        file_reader = csv.DictReader(csv_file)

        UUID_NEW = 'NEW'

        # Controls whether we create new bases or exercises if they have the UUID 'NEW'
        SKIP_CREATE_ENTRIES_ON_NEW = False

        VIDEO_AUTHOR = 'Goulart'

        VIDEO_PATH = pathlib.Path('videos-tmp')
        VIDEO_EXTENSION = '.webm'

        #
        # Sanity check
        #
        available_languages = [
            'en', 'de', 'fr', 'it', 'es', 'nl', 'pt', 'ru', 'cs', 'uk', 'tr', 'sv', 'bg'
        ]
        columns = ['uuid', 'name', 'description', 'aliases', 'license', 'author']

        for language in available_languages:
            for column in columns:
                name = '{0}:{1}'.format(language, column)
                assert (name in file_reader.fieldnames
                        ), '{0} not in {1}'.format(name, file_reader.fieldnames)

        language_objs = [
            Language.objects.get(short_name=language) for language in available_languages
        ]

        default_license = License.objects.get(pk=DEFAULT_LICENSE_ID)

        #
        # Process the exercises
        #
        rows = [f for f in file_reader]
        for row in rows:
            new_exercise = False
            base_uuid = row['base:uuid']
            base_equipment = row['base:equipment']
            base_category = row['base:category']
            base_variation_id = row['base:variation']
            base_video = row['base:video']

            self.stdout.write(f'\n\n*** Processing base-UUID {base_uuid}\n')
            self.stdout.write('-------------------------------------------------------------\n')

            #
            # Load and update the base data
            #
            if not base_uuid:
                self.stdout.write('    No base uuid, skipping')
                continue

            if SKIP_CREATE_ENTRIES_ON_NEW and base_uuid == UUID_NEW:
                self.stdout.write(f'    Skipping creating new base...\n')
                continue
            base = ExerciseBase.objects.get(uuid=base_uuid
                                            ) if base_uuid != UUID_NEW else ExerciseBase()

            # Update the base data
            base.category = ExerciseCategory.objects.get(name=base_category)
            base_equipment_list = []
            if base_equipment:
                base_equipment_list = [
                    Equipment.objects.get(name=e.strip()) for e in base_equipment.split(',')
                ]
            base.equipment.set(base_equipment_list)

            # Variations
            if base_variation_id:
                # First element from get_or_create is the object, the second whether
                # it was created or updated
                variation = Variation.objects.get_or_create(id=base_variation_id)[0]
                base.variations = variation

            base.save()

            # Save the video
            if base_video and not ExerciseVideo.objects.filter(exercise_base=base).exists():
                path = VIDEO_PATH / pathlib.Path(base_video + VIDEO_EXTENSION)
                with path.open('rb') as video_file:
                    video = ExerciseVideo()
                    video.exercise_base = base
                    video.license = default_license
                    video.license_author = VIDEO_AUTHOR
                    video.video.save(
                        path.name,
                        File(video_file),
                    )
                    video.save()
                    self.stdout.write(f'Saving video {video.video}\n')

            #
            # Process the translations and create new exercises if necessary
            #
            for language in language_objs:
                language_short = language.short_name
                exercise_uuid = row[f'{language_short}:uuid']
                exercise_name = row[f'{language_short}:name']
                exercise_description = row[f'{language_short}:description']
                exercise_license = row[f'{language_short}:license']
                exercise_author = row[f'{language_short}:author']
                exercise_aliases = row[f'{language_short}:aliases']

                # Load exercise
                if exercise_uuid:
                    self.stdout.write(f'{language_short}: exercise uuid: {exercise_uuid}\n')

                if SKIP_CREATE_ENTRIES_ON_NEW and exercise_uuid == UUID_NEW:
                    self.stdout.write(f'    Skipping creating new exercise...\n')
                    continue
                try:
                    exercise = Exercise.objects.get(
                        uuid=exercise_uuid
                    ) if (exercise_uuid and exercise_uuid != UUID_NEW) else Exercise()
                except Exercise.DoesNotExist:
                    self.stdout.write(
                        self.style.
                        WARNING(f'    Exercise isn not known locally: {exercise_uuid}!\n')
                    )
                    continue

                exercise.exercise_base = base
                exercise.language = language

                # Set the nane and description, if there is any
                if exercise_name:
                    exercise.name = exercise_name
                    exercise.name_original = exercise_name
                    exercise.description = exercise_description
                else:
                    continue

                # Set the license
                if exercise_license:
                    try:
                        exercise_license = License.objects.get(short_name=exercise_license)
                    except License.DoesNotExist:
                        self.stdout.write(
                            self.style.
                            WARNING(f'    License does not exist: {exercise_license}!!!\n')
                        )
                        exercise_license = default_license
                else:
                    exercise_license = default_license
                exercise.license = exercise_license
                exercise.license_author = exercise_author

                if not exercise.id:
                    new_exercise = True

                exercise.status = Exercise.STATUS_ACCEPTED
                exercise.save()

                # Set the aliases
                if exercise_aliases:
                    Alias.objects.filter(exercise=exercise).delete()
                    for a in exercise_aliases.split('/'):
                        Alias(exercise=exercise, alias=a.strip()).save()

                if new_exercise:
                    self.stdout.write(
                        self.style.
                        SUCCESS(f'    New exercise saved, ID: {exercise.id}, {exercise.name}\n')
                    )
        csv_file.close()
