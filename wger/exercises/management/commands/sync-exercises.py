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

# Django
from django.core.exceptions import ValidationError
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
    Equipment,
    Exercise,
    ExerciseBase,
    ExerciseCategory,
    Muscle,
)


EXERCISE_API = "{0}/api/v2/exerciseinfo/?limit=100"
CATEGORY_API = "{0}/api/v2/exercisecategory/"
MUSCLE_API = "{0}/api/v2/muscle/"
EQUIPMENT_API = "{0}/api/v2/equipment/"


class Command(BaseCommand):
    """
    Synchronizes exercise data from a wger instance to the local database
    """

    help = """Synchronizes exercise data from a wger instance to the local database.

            Please note that at the moment the following objects can only identified
            by their id. If you added new objects they might have the same IDs as the
            remote ones and will be overwritten:
            - categories
            - muscles
            - equipment
            """

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

        remote_url = options['remote_url']
        try:
            val = URLValidator()
            val(remote_url)
        except ValidationError:
            raise CommandError('Please enter a valid URL')

        headers = {'User-agent': default_user_agent('wger/{} + requests'.format(get_version()))}
        self.sync_categories(headers, remote_url)
        self.sync_muscles(headers, remote_url)
        self.sync_equipment(headers, remote_url)
        self.sync_exercises(headers, remote_url)

    def sync_exercises(self, headers: dict, remote_url: str):
        self.stdout.write('*** Synchronizing exercises...')
        page = 1
        all_exercise_processed = False
        result = requests.get(EXERCISE_API.format(remote_url), headers=headers).json()
        while not all_exercise_processed:

            for data in result['results']:
                exercise_uuid = data['uuid']
                exercise_name = data['name']
                exercise_description = data['description']
                equipment = [Equipment.objects.get(pk=i['id']) for i in data['equipment']]
                muscles = [Muscle.objects.get(pk=i['id']) for i in data['muscles']]
                muscles_sec = [Muscle.objects.get(pk=i['id']) for i in data['muscles_secondary']]

                try:
                    exercise = Exercise.objects.get(uuid=exercise_uuid)
                    exercise.name = exercise_name
                    exercise.description = exercise_description

                    # Note: this should not happen and is an unnecessary workaround
                    #       https://github.com/wger-project/wger/issues/840
                    if not exercise.exercise_base:
                        warning = f'Exercise {exercise.uuid} has no base, this should not happen!' \
                                  f'Skipping...\n'
                        self.stdout.write(self.style.WARNING(warning))
                        continue
                    exercise.exercise_base.category_id = data['category']['id']
                    exercise.exercise_base.muscles.set(muscles)
                    exercise.exercise_base.muscles_secondary.set(muscles_sec)
                    exercise.exercise_base.equipment.set(equipment)
                    exercise.exercise_base.save()
                    exercise.save()
                except Exercise.DoesNotExist:
                    self.stdout.write(f'Saved new exercise {exercise_name}')
                    exercise = Exercise(
                        uuid=exercise_uuid,
                        name=exercise_name,
                        description=exercise_description,
                        language_id=data['language']['id'],
                        license_id=data['license']['id'],
                        license_author=data['license_author'],
                    )
                    base = ExerciseBase()
                    base.category_id = data['category']['id']
                    base.save()
                    base.muscles.set(muscles)
                    base.muscles_secondary.set(muscles_sec)
                    base.equipment.set(equipment)
                    base.save()
                    exercise.save()

            if result['next']:
                page += 1
                result = requests.get(result['next'], headers=headers).json()
            else:
                all_exercise_processed = True
        self.stdout.write(self.style.SUCCESS('done!\n'))

    def sync_equipment(self, headers: dict, remote_url: str):
        self.stdout.write('*** Synchronizing equipment...')
        result = requests.get(EQUIPMENT_API.format(remote_url), headers=headers).json()
        for equipment_data in result['results']:
            equipment_id = equipment_data['id']
            equipment_name = equipment_data['name']

            try:
                equipment = Equipment.objects.get(pk=equipment_id)
                equipment.name = equipment_name
                equipment.save()
            except Equipment.DoesNotExist:
                self.stdout.write(f'Saved new equipment {equipment_name}')
                equipment = Equipment(id=equipment_id, name=equipment_name)
                equipment.save()
        self.stdout.write(self.style.SUCCESS('done!\n'))

    def sync_muscles(self, headers: dict, remote_url: str):
        self.stdout.write('*** Synchronizing muscles...')
        result = requests.get(MUSCLE_API.format(remote_url), headers=headers).json()
        for muscle_data in result['results']:
            muscle_id = muscle_data['id']
            muscle_name = muscle_data['name']
            muscle_is_front = muscle_data['is_front']
            muscle_name_en = muscle_data['name_en']
            muscle_url_main = muscle_data['image_url_main']
            muscle_url_secondary = muscle_data['image_url_secondary']

            try:
                muscle = Muscle.objects.get(pk=muscle_id)
                muscle.name = muscle_name
                muscle.is_front = muscle_is_front
                muscle.name_en = muscle_name_en
                muscle.save()
            except Muscle.DoesNotExist:
                muscle = Muscle(
                    id=muscle_id,
                    name=muscle_name,
                    is_front=muscle_is_front,
                    name_en=muscle_name_en
                )
                muscle.save()
                self.stdout.write(
                    self.style.WARNING(
                        f'Saved new muscle {muscle_name}. '
                        f'Save the corresponding images manually'
                    )
                )
                self.stdout.write(self.style.WARNING(muscle_url_main))
                self.stdout.write(self.style.WARNING(muscle_url_secondary))
        self.stdout.write(self.style.SUCCESS('done!\n'))

    def sync_categories(self, headers: dict, remote_url: str):
        self.stdout.write('*** Synchronizing categories...')
        result = requests.get(CATEGORY_API.format(remote_url), headers=headers).json()
        for category_data in result['results']:
            category_id = category_data['id']
            category_name = category_data['name']
            try:
                category = ExerciseCategory.objects.get(pk=category_id)
                category.name = category_name
                category.save()
            except ExerciseCategory.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Saving new category {category_name}'))
                category = ExerciseCategory(id=category_id, name=category_name)
                category.save()
        self.stdout.write(self.style.SUCCESS('done!\n'))
