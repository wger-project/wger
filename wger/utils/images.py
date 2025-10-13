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

# Third Party
from PIL import (
    Image,
    UnidentifiedImageError,
)


MAX_FILE_SIZE_MB = 20

IMAGE_ALLOWED_FORMATS = ('jpeg', 'jpg', 'png', 'webp', 'avif')


def validate_image_static_no_animation(value):
    # File size check
    if value.size > 1024 * 1024 * MAX_FILE_SIZE_MB:
        raise ValidationError(f'The maximum image file size is {MAX_FILE_SIZE_MB}MB.')

    # Try opening the file with PIL
    try:
        value.open()
        img = Image.open(value)
        img_format = img.format.lower()
    except UnidentifiedImageError:
        raise ValidationError('File is not a valid image.')

    # Supported types
    if img_format not in IMAGE_ALLOWED_FORMATS:
        raise ValidationError(
            f'File type is not supported. Allowed formats: {", ".join(IMAGE_ALLOWED_FORMATS)}.'
        )

    # Check for animation
    if img_format in ('webp', 'avif') and getattr(img, 'is_animated'):
        raise ValidationError('Animated images are not supported.')
