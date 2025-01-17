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
from wger.core.api.endpoints import (
    LANGUAGE_ENDPOINT,
    LICENSE_ENDPOINT,
)
from wger.core.models import (
    Language,
    License,
)
from wger.exercises.api.endpoints import (
    CATEGORY_ENDPOINT,
    DELETION_LOG_ENDPOINT,
    EQUIPMENT_ENDPOINT,
    EXERCISE_ENDPOINT,
    IMAGE_ENDPOINT,
    MUSCLE_ENDPOINT,
    VIDEO_ENDPOINT,
)
from wger.exercises.models import (
    Alias,
    DeletionLog,
    Equipment,
    Exercise,
    ExerciseBase,
    ExerciseCategory,
    ExerciseComment,
    ExerciseImage,
    ExerciseVideo,
    Muscle,
)
from wger.manager.models import (
    Setting,
    WorkoutLog,
)
from wger.utils.requests import (
    get_all_paginated,
    get_paginated,
    wger_headers,
)
from wger.utils.url import make_uri


def sync_exercises(
    print_fn,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    style_fn=lambda x: x,
):
    """Synchronize the exercises from the remote server"""
    print_fn('*** Synchronizing exercises...')

    url = make_uri(EXERCISE_ENDPOINT, server_url=remote_url, query={'limit': 100})
    for data in get_paginated(url, headers=wger_headers()):
        uuid = data['uuid']
        created = data['created']
        license_id = data['license']['id']
        category_id = data['category']['id']
        license_author = data['license_author']
        equipment = [Equipment.objects.get(pk=i['id']) for i in data['equipment']]
        muscles = [Muscle.objects.get(pk=i['id']) for i in data['muscles']]
        muscles_sec = [Muscle.objects.get(pk=i['id']) for i in data['muscles_secondary']]

        base, base_created = ExerciseBase.objects.update_or_create(
            uuid=uuid,
            defaults={'category_id': category_id, 'created': created},
        )
        print_fn(f'{"created" if base_created else "updated"} exercise {uuid}')

        base.muscles.set(muscles)
        base.muscles_secondary.set(muscles_sec)
        base.equipment.set(equipment)
        base.save()

        for translation_data in data['exercises']:
            trans_uuid = translation_data['uuid']
            name = translation_data['name']
            description = translation_data['description']
            language_id = translation_data['language']

            translation, translation_created = Exercise.objects.update_or_create(
                uuid=trans_uuid,
                defaults={
                    'exercise_base': base,
                    'name': name,
                    'description': description,
                    'license_id': license_id,
                    'license_author': license_author,
                    'language_id': language_id,
                },
            )
            out = (
                f'- {"created" if translation_created else "updated"} translation '
                f'{translation.language.short_name} {trans_uuid} - {name}'
            )
            print_fn(out)

            # TODO: currently (2024-01-06) we always delete all the comments and the aliases
            #       when synchronizing the data, even though we could identify them via the
            #       UUID. However, the UUID created when running the database migrations will
            #       be unique as well, so we will never update. We need to wait a while till
            #       most local instances have run the sync script so that the UUID is the same
            #       locally as well.
            #
            #       -> remove the `.delete()` after the 2024-06-01

            ExerciseComment.objects.filter(exercise=translation).delete()
            for note in translation_data['notes']:
                ExerciseComment.objects.update_or_create(
                    uuid=note['uuid'],
                    defaults={
                        'uuid': note['uuid'],
                        'exercise': translation,
                        'comment': note['comment'],
                    },
                )

            Alias.objects.filter(exercise=translation).delete()
            for alias in translation_data['aliases']:
                Alias.objects.update_or_create(
                    uuid=alias['uuid'],
                    defaults={
                        'uuid': alias['uuid'],
                        'exercise': translation,
                        'alias': alias['alias'],
                    },
                )

        print_fn('')

    print_fn(style_fn('done!\n'))


def sync_languages(
    print_fn,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    style_fn=lambda x: x,
):
    """Synchronize the languages from the remote server"""
    print_fn('*** Synchronizing languages...')
    headers = wger_headers()
    url = make_uri(LANGUAGE_ENDPOINT, server_url=remote_url)

    for data in get_all_paginated(url, headers=headers):
        short_name = data['short_name']
        full_name = data['full_name']
        full_name_en = data['full_name_en']

        language, created = Language.objects.update_or_create(
            short_name=short_name,
            defaults={'full_name': full_name, 'full_name_en': full_name_en},
        )

        if created:
            print_fn(f'Saved new language {full_name}')

    print_fn(style_fn('done!\n'))


def sync_licenses(
    print_fn,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    style_fn=lambda x: x,
):
    """Synchronize the licenses from the remote server"""
    print_fn('*** Synchronizing licenses...')
    url = make_uri(LICENSE_ENDPOINT, server_url=remote_url)

    for data in get_all_paginated(url, headers=wger_headers()):
        short_name = data['short_name']
        full_name = data['full_name']
        license_url = data['url']

        language, created = License.objects.update_or_create(
            short_name=short_name,
            defaults={'full_name': full_name, 'url': license_url},
        )

        if created:
            print_fn(f'Saved new license {full_name}')

    print_fn(style_fn('done!\n'))


def sync_categories(
    print_fn,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    style_fn=lambda x: x,
):
    """Synchronize the categories from the remote server"""

    print_fn('*** Synchronizing categories...')
    url = make_uri(CATEGORY_ENDPOINT, server_url=remote_url)

    for data in get_all_paginated(url, headers=wger_headers()):
        category_id = data['id']
        category_name = data['name']

        category, created = ExerciseCategory.objects.update_or_create(
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

    print_fn('*** Synchronizing muscles...')
    url = make_uri(MUSCLE_ENDPOINT, server_url=remote_url)

    for data in get_all_paginated(url, headers=wger_headers()):
        muscle_id = data['id']
        muscle_name = data['name']
        muscle_is_front = data['is_front']
        muscle_name_en = data['name_en']
        muscle_url_main = data['image_url_main']
        muscle_url_secondary = data['image_url_secondary']

        muscle, created = Muscle.objects.update_or_create(
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
    print_fn('*** Synchronizing equipment...')

    url = make_uri(EQUIPMENT_ENDPOINT, server_url=remote_url)

    for data in get_all_paginated(url, headers=wger_headers()):
        equipment_id = data['id']
        equipment_name = data['name']

        equipment, created = Equipment.objects.update_or_create(
            pk=equipment_id,
            defaults={'name': equipment_name},
        )

        if created:
            print_fn(f'Saved new equipment {equipment_name}')

    print_fn(style_fn('done!\n'))


def handle_deleted_entries(
    print_fn=None,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    style_fn=lambda x: x,
):
    if not print_fn:

        def print_fn(_):
            return None

    """Delete exercises that were removed on the server"""
    print_fn('*** Deleting exercise data that was removed on the server...')

    url = make_uri(DELETION_LOG_ENDPOINT, server_url=remote_url, query={'limit': 100})

    for data in get_paginated(url, headers=wger_headers()):
        uuid = data['uuid']
        replaced_by_uuid = data['replaced_by']
        model_type = data['model_type']

        if model_type == DeletionLog.MODEL_BASE:
            obj_replaced = None
            nr_settings = None
            nr_logs = None
            try:
                obj_replaced = ExerciseBase.objects.get(uuid=replaced_by_uuid)
            except ExerciseBase.DoesNotExist:
                pass

            try:
                obj = ExerciseBase.objects.get(uuid=uuid)

                # Replace exercise in workouts and logs
                if obj_replaced:
                    nr_settings = Setting.objects.filter(exercise_base=obj).update(
                        exercise_base=obj_replaced
                    )
                    nr_logs = WorkoutLog.objects.filter(exercise_base=obj).update(
                        exercise_base=obj_replaced
                    )

                obj.delete()
                print_fn(f'Deleted exercise base {uuid}')
                if nr_settings:
                    print_fn(f'- replaced {nr_settings} time(s) in workouts by {replaced_by_uuid}')
                if nr_logs:
                    print_fn(f'- replaced {nr_logs} time(s) in workout logs by {replaced_by_uuid}')
            except ExerciseBase.DoesNotExist:
                pass

        elif model_type == DeletionLog.MODEL_TRANSLATION:
            try:
                obj = Exercise.objects.get(uuid=uuid)
                obj.delete()
                print_fn(f'Deleted translation {uuid} ({data["comment"]})')
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


def download_exercise_images(
    print_fn,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    style_fn=lambda x: x,
):
    headers = wger_headers()
    url = make_uri(IMAGE_ENDPOINT, server_url=remote_url)

    print_fn('*** Processing images ***')

    # 2023-04-21: Delete all images that have no associated image files
    #
    # This is a temporary fix necessary because we had a bug in this sync
    # script that downloaded the image files and created image entries in the
    # database, but didn't connect them. This deletes the image entries so
    # that they can be re-downloaded (the dangling files are still there, though).
    deleted, rows = ExerciseImage.objects.filter(image='').delete()
    if deleted:
        print_fn(f'Deleted {deleted} images without associated image files')

    for image_data in get_paginated(url, headers=headers):
        image_uuid = image_data['uuid']

        print_fn(f'Processing image {image_uuid}')

        try:
            exercise = ExerciseBase.objects.get(uuid=image_data['exercise_base_uuid'])
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
            image = ExerciseImage.from_json(exercise, retrieved_image, image_data)

        print_fn(style_fn('    successfully saved'))


def download_exercise_videos(
    print_fn,
    remote_url=settings.WGER_SETTINGS['WGER_INSTANCE'],
    style_fn=lambda x: x,
):
    headers = wger_headers()
    url = make_uri(VIDEO_ENDPOINT, server_url=remote_url)

    print_fn('*** Processing videos ***')

    for video_data in get_paginated(url, headers=headers):
        video_uuid = video_data['uuid']
        print_fn(f'Processing video {video_uuid}')

        try:
            exercise = ExerciseBase.objects.get(uuid=video_data['exercise_base_uuid'])
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
            video.exercise_base = exercise
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
