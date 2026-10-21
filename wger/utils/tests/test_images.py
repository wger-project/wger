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
import io
from tempfile import NamedTemporaryFile
from unittest import (
    mock,
    skipUnless,
)

# Django
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

# Third Party
from PIL import (
    Image,
    features,
)

# wger
from wger.utils.images import (
    MAX_FILE_SIZE_MB,
    validate_image_static_no_animation,
)


def make_image(image_format: str, frames: int = 1) -> bytes:
    """An encoded 4x4 image, with one colour per frame"""
    images = [Image.new('RGB', (4, 4), colour) for colour in ('red', 'green', 'blue')[:frames]]
    buffer = io.BytesIO()
    images[0].save(buffer, format=image_format, save_all=frames > 1, append_images=images[1:])
    return buffer.getvalue()


def upload(content: bytes) -> SimpleUploadedFile:
    return SimpleUploadedFile('image', content)


class ValidateImageStaticNoAnimationTestCase(SimpleTestCase):
    def test_static_images_are_accepted(self):
        for image_format in ('JPEG', 'PNG', 'WEBP'):
            with self.subTest(image_format=image_format):
                validate_image_static_no_animation(upload(make_image(image_format)))

    @skipUnless(features.check('avif'), 'Pillow was built without AVIF support')
    def test_static_avif_is_accepted(self):
        validate_image_static_no_animation(upload(make_image('AVIF')))

    def test_other_image_formats_are_rejected(self):
        for image_format in ('GIF', 'BMP', 'TIFF'):
            with self.subTest(image_format=image_format):
                with self.assertRaisesMessage(ValidationError, 'File type is not supported'):
                    validate_image_static_no_animation(upload(make_image(image_format)))

    def test_animated_webp_is_rejected(self):
        with self.assertRaisesMessage(ValidationError, 'Animated images are not supported'):
            validate_image_static_no_animation(upload(make_image('WEBP', frames=2)))

    @skipUnless(features.check('avif'), 'Pillow was built without AVIF support')
    def test_animated_avif_is_rejected(self):
        with self.assertRaisesMessage(ValidationError, 'Animated images are not supported'):
            validate_image_static_no_animation(upload(make_image('AVIF', frames=2)))

    def test_animated_png_is_rejected(self):
        with self.assertRaisesMessage(ValidationError, 'Animated images are not supported'):
            validate_image_static_no_animation(upload(make_image('PNG', frames=2)))

    def test_truncated_image_is_rejected(self):
        with self.assertRaisesMessage(ValidationError, 'File is not a valid image'):
            validate_image_static_no_animation(upload(make_image('JPEG')[:200]))

    def test_decompression_bomb_is_rejected(self):
        # 16 pixels are more than twice the limit, which is where Pillow raises
        with mock.patch.object(Image, 'MAX_IMAGE_PIXELS', 7):
            with self.assertRaisesMessage(ValidationError, 'The image dimensions are too large'):
                validate_image_static_no_animation(upload(make_image('PNG')))

    def test_files_that_are_no_image_are_rejected(self):
        for content in (b'', b'not an image'):
            with self.subTest(content=content):
                with self.assertRaisesMessage(ValidationError, 'File is not a valid image'):
                    validate_image_static_no_animation(upload(content))

    def test_files_over_the_size_limit_are_rejected_before_being_opened(self):
        content = b'\0' * (MAX_FILE_SIZE_MB * 1024 * 1024 + 1)

        with self.assertRaisesMessage(ValidationError, 'The maximum image file size is'):
            validate_image_static_no_animation(upload(content))

    def test_files_at_the_size_limit_pass_the_size_check(self):
        content = b'\0' * (MAX_FILE_SIZE_MB * 1024 * 1024)

        # Fails only later, as not being an image
        with self.assertRaisesMessage(ValidationError, 'File is not a valid image'):
            validate_image_static_no_animation(upload(content))

    def test_temporary_file_from_the_sync_is_accepted(self):
        # The sync validates the download right after writing it, at the end of the file
        with NamedTemporaryFile() as temp_file:
            temp_file.write(make_image('PNG'))
            temp_file.flush()

            validate_image_static_no_animation(File(temp_file))
