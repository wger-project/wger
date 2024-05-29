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
import re

# Django
from django.core.files import File
from django.core.management.base import BaseCommand

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
from wger.utils.constants import CC_BY_SA_4_ID


UUID_NEW = 'NEW'
VIDEO_AUTHOR = 'Goulart'
VIDEO_PATH = pathlib.Path('videos-tmp')
VIDEO_EXTENSIONS = ('.MP4', '.MOV')


class Command(BaseCommand):
    """
    ONE OFF SCRIPT!

    Note that running this script more than once will result in duplicate entries
    (specially the entries with 'NEW' as their UUID)

    This script reads back into the database corrections made to a CSV generated with
    exercise-cleanup.py
    """

    help = 'Update the exercise database based on the exercise cleanup spreadsheet'

    def add_arguments(self, parser):
        parser.add_argument(
            '--process-videos',
            action='store_true',
            dest='process_videos',
            default=False,
            help='Flag indicating whether to process and add videos to the exercises',
        )

        parser.add_argument(
            '--create-on-new',
            action='store_true',
            dest='create_on_new',
            default=True,
            help="Controls whether we create new bases or exercises if they have the UUID 'NEW'",
        )

    def handle(self, **options):
        self.process_new_exercises(options)
        # self.delete_duplicates(options)

    def process_new_exercises(self, options):
        csv_file = open('exercises_cleanup.csv', 'r', newline='')
        file_reader = csv.DictReader(csv_file)

        #
        # Sanity check
        #
        languages = Language.objects.all()
        columns = ['uuid', 'name', 'description', 'aliases', 'license', 'author']

        for language in [l.short_name for l in languages]:
            for column in columns:
                name = f'{language}:{column}'
                assert name in file_reader.fieldnames, f'{name} not in {file_reader.fieldnames}'

        default_license = License.objects.get(pk=CC_BY_SA_4_ID)

        #
        # Process the exercises
        #
        for row in file_reader:
            base_uuid = row['base:uuid']
            base_equipment = row['base:equipment']
            base_category = row['base:category']
            base_variation_id = row['base:variation']
            base_video = row['base:video']

            if not base_uuid:
                # self.stdout.write('No base uuid, skipping')
                continue

            self.stdout.write(f'\n*** Processing base-UUID {base_uuid}\n')
            self.stdout.write('-------------------------------------------------------------\n')

            #
            # Load and update the base data
            #
            new_base = base_uuid == UUID_NEW
            if not options['create_on_new'] and new_base:
                self.stdout.write(f'    Skipping creating new exercise base...\n')
                continue

            base = (
                ExerciseBase.objects.get_or_create(
                    uuid=base_uuid,
                    defaults={'category': ExerciseCategory.objects.get(name=base_category)},
                )[0]
                if not new_base
                else ExerciseBase()
            )

            # Update the base data
            base.category = ExerciseCategory.objects.get(name=base_category)

            if new_base:
                base.save()

            base_equipment_list = []
            if base_equipment:
                base_equipment_list = [
                    Equipment.objects.get(name=e.strip()) for e in base_equipment.split(',')
                ]
            base.equipment.set(base_equipment_list)

            # Variations
            if base_variation_id:
                variation, created = Variation.objects.get_or_create(id=base_variation_id)
                base.variations = variation

            base.save()

            # Save the video

            # Note we can't really know if the video is new or not since the name is
            # a generated UUID. We could read the content and compare the size, etc.
            # but that is too much work for this script that will be used only once.
            if base_video and options['process_videos']:
                for video_name in base_video.split('/'):
                    video_processed = False
                    for extension in VIDEO_EXTENSIONS:
                        path = VIDEO_PATH / pathlib.Path(video_name.strip() + extension)

                        if video_processed or not path.exists():
                            continue

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
                            self.stdout.write(f'Saving video {path}\n')
                            video_processed = True

            #
            # Process the translations and create new exercises if necessary
            #
            for language in languages:
                language_short = language.short_name
                exercise_uuid = row[f'{language_short}:uuid']
                exercise_name = row[f'{language_short}:name']
                exercise_description = row[f'{language_short}:description']
                exercise_license = row[f'{language_short}:license']
                exercise_author = row[f'{language_short}:author']
                exercise_aliases = row[f'{language_short}:aliases']

                # Load translation
                if exercise_uuid:
                    message = f'{language_short}: translation uuid: {exercise_uuid}\n'
                    self.stdout.write(message)
                else:
                    # self.stdout.write(f'{language_short}: No UUID for translation, skipping...\n')
                    continue

                if not exercise_name:
                    continue

                new_translation = exercise_uuid == UUID_NEW
                if not new_translation:
                    continue

                translation = (
                    Exercise.objects.get_or_create(
                        uuid=exercise_uuid, defaults={'exercise_base': base, 'language': language}
                    )[0]
                    if not new_translation
                    else Exercise()
                )
                translation.exercise_base = base
                translation.language = language
                translation.name = exercise_name
                translation.name_original = exercise_name
                translation.description = exercise_description

                # Set the license
                if exercise_license:
                    try:
                        exercise_license = License.objects.get(short_name=exercise_license)
                    except License.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f'    License does not exist: {exercise_license}!!!\n'
                            )
                        )
                        exercise_license = default_license
                else:
                    exercise_license = default_license
                translation.license = exercise_license
                translation.license_author = exercise_author

                if not translation.id:
                    message = f'    New translation saved - {exercise_name} ({translation.uuid})'
                    self.stdout.write(self.style.SUCCESS(message))

                if '(imported from Feeel)' in exercise_author:
                    exercise_author = re.sub('\(imported from Feeel\)', '', exercise_author)
                    for author in exercise_author.split(','):
                        author = author.strip()
                        author = f'{author} (imported from Feeel)'
                        self.stdout.write(f'    - Saving individual author {author}')
                        if len(author) >= 60:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'      Author name is longer than 60 characters, skipping...'
                                )
                            )
                            continue
                        translation.license_author = author
                        translation.save()

                # Set the aliases (replaces existing ones)
                if exercise_aliases:
                    Alias.objects.filter(exercise=translation).delete()
                    for a in exercise_aliases.split(','):
                        Alias(exercise=translation, alias=a.strip()).save()

        csv_file.close()

    def delete_duplicates(self, options):
        csv_file = open('exercises_cleanup_duplicates.csv', 'r', newline='')
        file_reader = csv.DictReader(csv_file)
        self.stdout.write(
            self.style.WARNING(f'---> Deleting duplicate bases and translations now...')
        )

        for row in file_reader:
            base_uuid = row['baseUUID:toDelete']
            translation_uuid = row['exerciseUUID:toDelete']
            variation_id = row['variations:toDelete']

            if base_uuid:
                try:
                    ExerciseBase.objects.filter(uuid=base_uuid).delete()
                    self.stdout.write(f'* Deleted base {base_uuid}')
                except ExerciseBase.DoesNotExist:
                    pass

            if translation_uuid:
                try:
                    Exercise.objects.filter(uuid=translation_uuid).delete()
                    self.stdout.write(f'* Deleted translation {translation_uuid}')
                except Exercise.DoesNotExist:
                    pass

            if variation_id:
                try:
                    Variation.objects.filter(id=variation_id).delete()
                    self.stdout.write(f'* Deleted variation {variation_id}')
                except Exercise.DoesNotExist:
                    pass
        csv_file.close()
