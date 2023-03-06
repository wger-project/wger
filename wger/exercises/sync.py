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
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

# Third Party
import requests

# wger
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
from wger.utils.requests import wger_headers


EXERCISE_API = "{0}/api/v2/exercisebaseinfo/?limit=100"
DELETION_LOG_API = "{0}/api/v2/deletion-log/?limit=100"
CATEGORY_API = "{0}/api/v2/exercisecategory/"
MUSCLE_API = "{0}/api/v2/muscle/"
LANGUAGE_API = "{0}/api/v2/language/"
EQUIPMENT_API = "{0}/api/v2/equipment/"
IMAGE_API = "{0}/api/v2/exerciseimage/"
VIDEO_API = "{0}/api/v2/video/"


def sync_exercises(
    print_fn,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    style_fn=lambda x: x,
):
    """Synchronize the exercises from the remote server"""
    headers = wger_headers()

    print_fn('*** Synchronizing exercises...')
    page = 1
    all_exercise_processed = False
    result = requests.get(EXERCISE_API.format(remote_url), headers=headers).json()
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
            print_fn(f"{'created' if base_created else 'updated'} exercise {uuid}")

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
                print_fn(out)

                translation.name = name
                translation.description = description
                translation.language_id = language_id
                translation.license_id = license_id
                translation.license_author = license_author
                translation.save()
            print_fn('')

        if result['next']:
            page += 1
            result = requests.get(result['next'], headers=headers).json()
        else:
            all_exercise_processed = True
    print_fn(style_fn('done!\n'))


def sync_languages(
    print_fn,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    style_fn=lambda x: x,
):
    """Synchronize the languages from the remote server"""
    headers = wger_headers()

    print_fn('*** Synchronizing languages...')
    result = requests.get(LANGUAGE_API.format(remote_url), headers=headers).json()
    for data in result['results']:
        short_name = data['short_name']
        full_name = data['full_name']

        language, created = Language.objects.get_or_create(
            short_name=short_name,
            defaults={'full_name': full_name},
        )

        if created:
            print_fn(f'Saved new language {full_name}')

    print_fn(style_fn('done!\n'))


def sync_categories(
    print_fn,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    style_fn=lambda x: x,
):
    """Synchronize the categories from the remote server"""

    headers = wger_headers()

    print_fn('*** Synchronizing categories...')
    result = requests.get(CATEGORY_API.format(remote_url), headers=headers).json()
    for data in result['results']:
        category_id = data['id']
        category_name = data['name']

        category, created = ExerciseCategory.objects.get_or_create(
            pk=category_id,
            defaults={'name': category_name},
        )

        if created:
            print_fn(f'Saved new category {category_name}')

    print_fn(style_fn('done!\n'))


def sync_muscles(
    print_fn,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    style_fn=lambda x: x,
):
    """Synchronize the muscles from the remote server"""

    headers = wger_headers()

    print_fn('*** Synchronizing muscles...')
    result = requests.get(MUSCLE_API.format(remote_url), headers=headers).json()
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
            print_fn(f'Saved new muscle {muscle_name}. Save the corresponding images manually:')
            print_fn(f' - {remote_url}{muscle_url_main}')
            print_fn(f' - {remote_url}{muscle_url_secondary}')

    print_fn(style_fn('done!\n'))


def sync_equipment(
    print_fn,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    style_fn=lambda x: x,
):
    """Synchronize the equipment from the remote server"""

    headers = wger_headers()

    print_fn('*** Synchronizing equipment...')
    result = requests.get(EQUIPMENT_API.format(remote_url), headers=headers).json()
    for data in result['results']:
        equipment_id = data['id']
        equipment_name = data['name']

        equipment, created = Equipment.objects.get_or_create(
            pk=equipment_id,
            defaults={'name': equipment_name},
        )

        if created:
            print_fn(f'Saved new equipment {equipment_name}')

    print_fn(style_fn('done!\n'))


def delete_entries(
    print_fn,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    style_fn=lambda x: x,
):
    """Delete exercises that were removed on the server"""

    headers = wger_headers()

    print_fn('*** Deleting exercises data that was removed on the server...')

    page = 1
    all_entries_processed = False
    result = requests.get(DELETION_LOG_API.format(remote_url), headers=headers).json()
    while not all_entries_processed:
        for data in result['results']:
            uuid = data['uuid']
            model_type = data['model_type']

            if model_type == DeletionLog.MODEL_BASE:
                try:
                    obj = ExerciseBase.objects.get(uuid=uuid)
                    obj.delete()
                    print_fn(f'Deleted exercise base {uuid}')
                except ExerciseBase.DoesNotExist:
                    pass

            elif model_type == DeletionLog.MODEL_TRANSLATION:
                try:
                    obj = Exercise.objects.get(uuid=uuid)
                    obj.delete()
                    print_fn(f"Deleted translation {uuid} ({data['comment']})")
                except Exercise.DoesNotExist:
                    pass

            elif model_type == DeletionLog.MODEL_IMAGE:
                try:
                    obj = ExerciseImage.objects.get(uuid=uuid)
                    obj.delete()
                    print_fn(f'Deleted image {uuid}')
                except ExerciseImage.DoesNotExist:
                    pass

            elif model_type == DeletionLog.MODEL_VIDEO:
                try:
                    obj = ExerciseVideo.objects.get(uuid=uuid)
                    obj.delete()
                    print_fn(f'Deleted video {uuid}')
                except ExerciseVideo.DoesNotExist:
                    pass

        if result['next']:
            page += 1
            result = requests.get(result['next'], headers=headers).json()
        else:
            all_entries_processed = True
    print_fn(style_fn('done!\n'))


def download_exercise_images(
    print_fn,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    style_fn=lambda x: x,
):
    headers = wger_headers()

    # Get all images
    page = 1
    all_images_processed = False
    result = requests.get(IMAGE_API.format(remote_url), headers=headers).json()
    print_fn('*** Processing images ***')
    while not all_images_processed:
        print_fn('')
        print_fn(f'*** Page {page}')
        print_fn('')

        for image_data in result['results']:
            image_uuid = image_data['uuid']

            print_fn(f'Processing image {image_uuid}')

            try:
                exercise_base = ExerciseBase.objects.get(id=image_data['exercise_base'])
            except ExerciseBase.DoesNotExist:
                print_fn('    Remote exercise base not found in local DB, skipping...')
                continue

            try:
                ExerciseImage.objects.get(uuid=image_uuid)
                print_fn('    Image already present locally, skipping...')
                continue
            except ExerciseImage.DoesNotExist:
                print_fn('    Image not found in local DB, creating now...')
                retrieved_image = requests.get(image_data['image'], headers=headers)
                image = ExerciseImage.from_json(
                    exercise_base,
                    retrieved_image,
                    image_data,
                    headers,
                )

            # Temporary files on Windows don't support the delete attribute
            if os.name == 'nt':
                img_temp = NamedTemporaryFile()
            else:
                img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(retrieved_image.content)
            img_temp.flush()

            image.exercise_base = exercise_base
            image.is_main = image_data['is_main']
            image.image.save(
                os.path.basename(os.path.basename(image_data['image'])),
                File(img_temp),
            )
            image.save()
            print_fn(style_fn('    successfully saved'))

        if result['next']:
            page += 1
            result = requests.get(result['next'], headers=headers).json()
        else:
            all_images_processed = True


def download_exercise_videos(
    print_fn,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    style_fn=lambda x: x,
):
    headers = wger_headers()

    # Get all videos
    page = 1
    all_videos_processed = False
    result = requests.get(VIDEO_API.format(remote_url), headers=headers).json()
    print_fn('*** Processing videos ***')
    while not all_videos_processed:
        print_fn('')
        print_fn(f'*** Page {page}')
        print_fn('')

        for video_data in result['results']:
            video_uuid = video_data['uuid']
            print_fn(f'Processing video {video_uuid}')

            try:
                exercise_base = ExerciseBase.objects.get(uuid=video_data['exercise_base_uuid'])
            except ExerciseBase.DoesNotExist:
                print_fn('    Remote exercise base not found in local DB, skipping...')
                continue

            try:
                ExerciseVideo.objects.get(uuid=video_uuid)
                print_fn('    Video already present locally, skipping...')
                continue
            except ExerciseVideo.DoesNotExist:
                print_fn('    Video not found in local DB, creating now...')
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
            print_fn(style_fn('    saved successfully'))

        if result['next']:
            page += 1
            result = requests.get(result['next'], headers=headers).json()
        else:
            all_videos_processed = True
