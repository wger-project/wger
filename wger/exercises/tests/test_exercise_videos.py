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
import pathlib
import tempfile
from unittest.mock import (
    Mock,
    patch,
)

# Django
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WgerTestCase
from wger.exercises.models import ExerciseVideo
from wger.exercises.tests.api_mixins import ActstreamUpdateMixin


HTML_PAYLOAD = b'<!DOCTYPE html><script>document.title = "xss"</script>'
VIDEO_HEADER = b'\x00\x00\x00\x14ftypqt  \x00\x00\x00\x00qt  '


class ExerciseVideoUploadTestCase(WgerTestCase):
    """
    Tests the file validation when uploading a video
    """

    def setUp(self):
        super().setUp()
        media_root = tempfile.TemporaryDirectory()
        self.addCleanup(media_root.cleanup)
        media_settings = self.settings(MEDIA_ROOT=media_root.name)
        media_settings.enable()
        self.addCleanup(media_settings.disable)
        self.user_login('admin')

    def upload(self, name: str, content: bytes, content_type: str = 'video/mp4'):
        return self.client.post(
            reverse('video-list'),
            {
                'exercise': 1,
                'license': 1,
                'license_author': 'tester',
                'video': SimpleUploadedFile(name, content, content_type=content_type),
            },
        )

    def assert_rejected(self, name: str, content: bytes, content_type: str = 'video/mp4'):
        # 0 bytes in memory forces the temporary file upload handler
        for max_memory_size in (2621440, 0):
            with (
                self.subTest(max_memory_size=max_memory_size),
                self.settings(FILE_UPLOAD_MAX_MEMORY_SIZE=max_memory_size),
            ):
                count_before = ExerciseVideo.objects.count()
                response = self.upload(name, content, content_type)
                self.assertEqual(response.status_code, 400)
                self.assertIn('video', response.data)
                self.assertEqual(ExerciseVideo.objects.count(), count_before)

    def test_html_file_rejected(self):
        """An HTML file declared as video/mp4 is rejected"""
        self.assert_rejected('poc.html', HTML_PAYLOAD)

    def test_svg_file_rejected(self):
        """An SVG file with a video signature is rejected because of its extension"""
        self.assert_rejected('poc.svg', VIDEO_HEADER + b'<svg onload="alert(1)"/>')

    def test_non_video_content_rejected(self):
        """A file with a video extension but without a video signature is rejected"""
        self.assert_rejected('poc.mp4', HTML_PAYLOAD)
        self.assert_rejected('notes.webm', b'just some text', 'text/plain')

    def test_ffmpeg_probe_rejects_invalid_video(self):
        """A file that ffmpeg can't probe is rejected"""
        ffmpeg = Mock(Error=type('Error', (Exception,), {}))
        ffmpeg.probe.side_effect = ffmpeg.Error

        with (
            patch('wger.exercises.models.video.ffmpeg', ffmpeg),
            self.settings(FILE_UPLOAD_MAX_MEMORY_SIZE=0),
        ):
            response = self.upload('clip.mp4', VIDEO_HEADER + b'\x00' * 64)

        self.assertEqual(response.status_code, 400)
        ffmpeg.probe.assert_called_once()

    def test_video_accepted(self):
        """A file with a video extension and signature is stored"""
        response = self.upload('IMG_0001.MOV', VIDEO_HEADER + b'\x00' * 64, 'video/quicktime')

        self.assertEqual(response.status_code, 201)
        video = ExerciseVideo.objects.get(pk=response.data['id'])
        self.assertEqual(pathlib.Path(video.video.name).suffix, '.MOV')


# TODO: add POST and DELETE tests
class ExerciseVideosApiTestCase(
    ActstreamUpdateMixin,
    api_base_test.BaseTestCase,
    api_base_test.ApiBaseTestCase,
    api_base_test.ApiGetTestCase,
):
    """
    Tests the exercise video resource
    """

    pk = 1
    private_resource = False
    resource = ExerciseVideo
    overview_cached = False
    data = {'is_main': True}
    patch_format = 'multipart'

    def get_resource_name(self):
        # The video endpoint is registered as ``video``, not ``exercisevideo``.
        return 'video'
