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
from wger.core.models import Language
from wger.exercises.models import (
    DeletionLog,
    Equipment,
    Exercise,
    ExerciseBase,
    ExerciseCategory,
    ExerciseImage,
    ExerciseVideo,
    Muscle,
)


EXERCISE_API = "{0}/api/v2/exercisebaseinfo/?limit=100"
DELETION_LOG_API = "{0}/api/v2/deletion-log/?limit=100"
CATEGORY_API = "{0}/api/v2/exercisecategory/"
MUSCLE_API = "{0}/api/v2/muscle/"
LANGUAGE_API = "{0}/api/v2/language/"
EQUIPMENT_API = "{0}/api/v2/equipment/"


class Command(BaseCommand):
    """
    Synchronizes exercise data from a wger instance to the local database
    """
    remote_url = 'https://wger.de'
    headers = {}

    help = """Synchronizes exercise data from a wger instance to the local database.
            This script also deletes entries that were removed on the server such
            as exercises, images or videos.

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
            default=self.remote_url,
            help=f'Remote URL to fetch the exercises from (default: {self.remote_url})'
        )

        parser.add_argument(
            '--dont-delete',
            action='store_true',
            dest='skip_delete',
            default=False,
            help='Skips deleting any entries'
        )

    def handle(self, **options):

        remote_url = options['remote_url']

        try:
            val = URLValidator()
            val(remote_url)
            self.remote_url = remote_url
        except ValidationError:
            raise CommandError('Please enter a valid URL')

        self.headers = {
            'User-agent': default_user_agent('wger/{} + requests'.format(get_version()))
        }

        # Process everything
        self.sync_languages()
        self.sync_categories()
        self.sync_muscles()
        self.sync_equipment()
        self.sync_exercises()
        if not options['skip_delete']:
            self.delete_entries()

    def sync_exercises(self):
        """Synchronize the exercises from the remote server"""

        self.stdout.write('*** Synchronizing exercises...')
        page = 1
        all_exercise_processed = False
        result = requests.get(EXERCISE_API.format(self.remote_url), headers=self.headers).json()
        while not all_exercise_processed:

            for data in result['results']:

                uuid = data['uuid']
                license_id = data['license']['id']
                category_id = data['category']['id']
                license_author = data['license_author']
                equipment = [Equipment.objects.get(pk=i['id']) for i in data['equipment']]
                muscles = [Muscle.objects.get(pk=i['id']) for i in data['muscles']]
                muscles_sec = [Muscle.objects.get(pk=i['id']) for i in data['muscles_secondary']]

                base, base_created = ExerciseBase.objects.get_or_create(
                    uuid=uuid,
                    defaults={'category_id': category_id},
                )
                self.stdout.write(f"{'created' if base_created else 'updated'} exercise {uuid}")

                base.muscles.set(muscles)
                base.muscles_secondary.set(muscles_sec)
                base.equipment.set(equipment)
                base.save()

                for translation_data in data['exercises']:
                    trans_uuid = translation_data['uuid']
                    name = translation_data['name']
                    description = translation_data['description']
                    language_id = translation_data['language']

                    translation, translation_created = Exercise.objects.get_or_create(
                        uuid=trans_uuid,
                        defaults={
                            'language_id': language_id,
                            'exercise_base': base
                        },
                    )
                    out = f"- {'created' if translation_created else 'updated'} translation " \
                          f"{translation.language.short_name} {trans_uuid} - {name}"
                    self.stdout.write(out)

                    translation.name = name
                    translation.description = description
                    translation.language_id = language_id
                    translation.license_id = license_id
                    translation.license_author = license_author
                    translation.save()
                self.stdout.write('')

            if result['next']:
                page += 1
                result = requests.get(result['next'], headers=self.headers).json()
            else:
                all_exercise_processed = True
        self.stdout.write(self.style.SUCCESS('done!\n'))

    def delete_entries(self):
        """Delete exercises that were removed on the server"""

        self.stdout.write('*** Deleting exercises data that was removed on the server...')

        page = 1
        all_entries_processed = False
        result = requests.get(DELETION_LOG_API.format(self.remote_url), headers=self.headers).json()
        while not all_entries_processed:
            for data in result['results']:
                uuid = data['uuid']
                model_type = data['model_type']

                if model_type == DeletionLog.MODEL_BASE:
                    try:
                        obj = ExerciseBase.objects.get(uuid=uuid)
                        obj.delete()
                        self.stdout.write(f'Deleted exercise base {uuid}')
                    except ExerciseBase.DoesNotExist:
                        pass

                elif model_type == DeletionLog.MODEL_TRANSLATION:
                    try:
                        obj = Exercise.objects.get(uuid=uuid)
                        obj.delete()
                        self.stdout.write(f"Deleted translation {uuid} ({data['comment']})")
                    except Exercise.DoesNotExist:
                        pass

                elif model_type == DeletionLog.MODEL_IMAGE:
                    try:
                        obj = ExerciseImage.objects.get(uuid=uuid)
                        obj.delete()
                        self.stdout.write(f'Deleted image {uuid}')
                    except ExerciseImage.DoesNotExist:
                        pass

                elif model_type == DeletionLog.MODEL_VIDEO:
                    try:
                        obj = ExerciseVideo.objects.get(uuid=uuid)
                        obj.delete()
                        self.stdout.write(f'Deleted video {uuid}')
                    except ExerciseVideo.DoesNotExist:
                        pass

            if result['next']:
                page += 1
                result = requests.get(result['next'], headers=self.headers).json()
            else:
                all_entries_processed = True
        self.stdout.write(self.style.SUCCESS('done!\n'))

    def sync_equipment(self):
        """Synchronize the equipment from the remote server"""

        self.stdout.write('*** Synchronizing equipment...')
        result = requests.get(EQUIPMENT_API.format(self.remote_url), headers=self.headers).json()
        for data in result['results']:
            equipment_id = data['id']
            equipment_name = data['name']

            equipment, created = Equipment.objects.get_or_create(
                pk=equipment_id,
                defaults={'name': equipment_name},
            )

            if created:
                self.stdout.write(f'Saved new equipment {equipment_name}')

        self.stdout.write(self.style.SUCCESS('done!\n'))

    def sync_muscles(self):
        """Synchronize the muscles from the remote server"""

        self.stdout.write('*** Synchronizing muscles...')
        result = requests.get(MUSCLE_API.format(self.remote_url), headers=self.headers).json()
        for data in result['results']:
            muscle_id = data['id']
            muscle_name = data['name']
            muscle_is_front = data['is_front']
            muscle_name_en = data['name_en']
            muscle_url_main = data['image_url_main']
            muscle_url_secondary = data['image_url_secondary']

            muscle, created = Muscle.objects.get_or_create(
                pk=muscle_id,
                defaults={
                    'name': muscle_name,
                    'name_en': muscle_name_en,
                    'is_front': muscle_is_front,
                },
            )

            if created:
                self.stdout.write(
                    f'Saved new muscle {muscle_name}. Save the corresponding images manually:'
                )
                self.stdout.write(f' - {self.remote_url}{muscle_url_main}')
                self.stdout.write(f' - {self.remote_url}{muscle_url_secondary}')

        self.stdout.write(self.style.SUCCESS('done!\n'))

    def sync_categories(self):
        """Synchronize the categories from the remote server"""

        self.stdout.write('*** Synchronizing categories...')
        result = requests.get(CATEGORY_API.format(self.remote_url), headers=self.headers).json()
        for data in result['results']:
            category_id = data['id']
            category_name = data['name']

            category, created = ExerciseCategory.objects.get_or_create(
                pk=category_id,
                defaults={'name': category_name},
            )

            if created:
                self.stdout.write(f'Saved new category {category_name}')

        self.stdout.write(self.style.SUCCESS('done!\n'))

    def sync_languages(self):
        """Synchronize the languages from the remote server"""

        self.stdout.write('*** Synchronizing languages...')
        result = requests.get(LANGUAGE_API.format(self.remote_url), headers=self.headers).json()
        for data in result['results']:
            short_name = data['short_name']
            full_name = data['full_name']

            language, created = Language.objects.get_or_create(
                short_name=short_name,
                defaults={'full_name': full_name},
            )

            if created:
                self.stdout.write(f'Saved new language {full_name}')

        self.stdout.write(self.style.SUCCESS('done!\n'))
