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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
import tempfile
from unittest import mock

# Django
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

# Third Party
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.test import APIRequestFactory

# wger
from wger.core.tests.api_base_test import ApiBaseTestCase
from wger.core.tests.base_testcase import BaseTestCase
from wger.exercises.api.throttling import CreateScopedRateThrottle
from wger.exercises.api.views import (
    ExerciseSubmissionViewSet,
    ExerciseTranslationViewSet,
    ExerciseViewSet,
)
from wger.exercises.models import ExerciseVideo
from wger.exercises.tests.test_exercise_videos import VIDEO_HEADER


class ExerciseCreateThrottleTestCase(BaseTestCase, ApiBaseTestCase):
    """
    Tests the write-only create throttle shared by the exercise create endpoints.
    """

    @staticmethod
    def get_payload(name='Throttle Test Exercise'):
        return {
            'category': 3,
            'license': 5,
            'license_author': 'tester',
            'translations': [
                {
                    'name': name,
                    'description_source': (
                        'A sufficiently long English description so the language '
                        'detector recognises it and the minimum length passes.'
                    ),
                    'language': 2,
                    'license_author': 'tester',
                },
            ],
        }

    def test_create_endpoints_use_throttle_scope(self):
        """All create endpoints share the throttle scope and class."""
        for view in (ExerciseViewSet, ExerciseTranslationViewSet, ExerciseSubmissionViewSet):
            self.assertEqual(view.throttle_scope, 'exercise_create')
            self.assertIn(CreateScopedRateThrottle, view.throttle_classes)

    def test_throttle_skips_non_post_requests(self):
        """Only POST is throttled; reads and edits always pass through."""
        throttle = CreateScopedRateThrottle()
        factory = APIRequestFactory()
        view = ExerciseViewSet()
        view.throttle_scope = 'exercise_create'

        for method in ('get', 'put', 'patch', 'delete', 'options', 'head'):
            request = getattr(factory, method)('/api/v2/exercise/')
            self.assertTrue(throttle.allow_request(request, view))

    def test_post_is_throttled(self):
        """A second create within the window is rejected with 429."""
        url = reverse('exercise-submission')
        # trainer1 is a trustworthy contributor without the add_exercise
        # permission, so the throttle applies to them.
        self.authenticate('trainer1')

        with mock.patch.dict(api_settings.DEFAULT_THROTTLE_RATES, {'exercise_create': '1/min'}):
            first = self.client.post(url, data=self.get_payload())
            second = self.client.post(url, data=self.get_payload())

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_add_exercise_permission_is_exempt(self):
        """Users with the add_exercise permission (admins/editors) aren't throttled."""
        url = reverse('exercise-submission')
        self.authenticate('admin')

        with mock.patch.dict(api_settings.DEFAULT_THROTTLE_RATES, {'exercise_create': '1/min'}):
            first = self.client.post(url, data=self.get_payload())
            # A distinct name, otherwise the duplicate-name check would reject
            # the second submission before the throttle exemption is exercised.
            second = self.client.post(url, data=self.get_payload('Completely Different Movement'))

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)


class ExerciseUploadThrottleTestCase(BaseTestCase, ApiBaseTestCase):
    """
    Tests the create throttle of the image and video upload endpoints.
    """

    def setUp(self):
        super().setUp()
        media_root = tempfile.TemporaryDirectory()
        self.addCleanup(media_root.cleanup)
        media_settings = self.settings(MEDIA_ROOT=media_root.name)
        media_settings.enable()
        self.addCleanup(media_settings.disable)

    def upload_video(self):
        return self.client.post(
            reverse('video-list'),
            data={
                'exercise': 1,
                'license_author': 'tester',
                'video': SimpleUploadedFile('clip.mp4', VIDEO_HEADER + b'\x00' * 64),
            },
            format='multipart',
        )

    def upload_image(self):
        with open('wger/exercises/tests/protestschwein.jpg', 'rb') as image:
            return self.client.post(
                reverse('exerciseimage-list'),
                data={'exercise': 1, 'license_author': 'tester', 'image': image},
                format='multipart',
            )

    def test_video_upload_is_throttled(self):
        """A second video upload within the window is rejected with 429."""
        self.authenticate('trainer1')

        with (
            mock.patch.dict(settings.WGER_SETTINGS, {'ALLOW_UPLOAD_VIDEOS': True}),
            mock.patch.dict(
                api_settings.DEFAULT_THROTTLE_RATES, {'exercise_video_upload': '1/min'}
            ),
        ):
            first = self.upload_video()
            second = self.upload_video()

        self.assertEqual(first.status_code, status.HTTP_201_CREATED, first.content)
        self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_image_upload_is_throttled(self):
        """A second image upload within the window is rejected with 429."""
        self.authenticate('trainer1')

        with mock.patch.dict(
            api_settings.DEFAULT_THROTTLE_RATES, {'exercise_image_upload': '1/min'}
        ):
            first = self.upload_image()
            second = self.upload_image()

        self.assertEqual(first.status_code, status.HTTP_201_CREATED, first.content)
        self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_disabled_video_upload_is_rejected(self):
        """With ALLOW_UPLOAD_VIDEOS off, uploading or replacing a video is forbidden."""
        self.authenticate('admin')
        count_before = ExerciseVideo.objects.count()

        with mock.patch.dict(settings.WGER_SETTINGS, {'ALLOW_UPLOAD_VIDEOS': False}):
            response = self.upload_video()
            replace = self.client.patch(
                reverse('video-detail', kwargs={'pk': 1}),
                data={'video': SimpleUploadedFile('clip.mp4', VIDEO_HEADER + b'\x00' * 64)},
                format='multipart',
            )
            edit = self.client.patch(
                reverse('video-detail', kwargs={'pk': 1}),
                data={'license_author': 'someone else'},
                format='multipart',
            )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(replace.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(edit.status_code, status.HTTP_200_OK)
        self.assertEqual(ExerciseVideo.objects.count(), count_before)
