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
from argparse import RawTextHelpFormatter

# Django
from django.core.management.base import BaseCommand

# Third Party
from PIL import (
    Image,
    UnidentifiedImageError,
)

# wger
from wger.gallery.models import Image as GalleryImage


class Command(BaseCommand):
    """
    Check existing gallery images in the database for validation issues.

    This command validates all existing gallery images against the same rules
    that would be applied to new uploads, including:
    - File size limits (20MB max)
    - Supported formats (JPEG, PNG, WEBP)
    - Static images only (no animated images)
    - File accessibility
    """

    help = (
        'Check existing gallery images in the database for validation issues.\n\n'
        'This command will:\n'
        '- Check if image files exist on disk\n'
        '- Validate file size (max 20MB)\n'
        '- Validate supported formats (JPEG, PNG, WEBP)\n'
        '- Check for animated images (reject animated WEBP)\n'
        '- Report any issues found\n\n'
        'Use --delete-invalid to remove invalid images from the database.\n'
        'Use --dry-run to see what would be done without making changes.'
    )

    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Show what would be done without making any changes',
        )

        parser.add_argument(
            '--delete-invalid',
            action='store_true',
            dest='delete_invalid',
            default=False,
            help='Delete invalid images from the database and filesystem',
        )

        parser.add_argument(
            '--user-id',
            type=int,
            dest='user_id',
            help='Check only images for a specific user ID',
        )

        parser.add_argument(
            '--verbose',
            action='store_true',
            dest='verbose',
            default=False,
            help='Show detailed output for each image processed',
        )

    def handle(self, **options):
        """
        Process the gallery images validation
        """
        dry_run = options['dry_run']
        delete_invalid = options['delete_invalid']
        user_id = options['user_id']
        verbose = options['verbose']

        if delete_invalid and dry_run:
            self.stdout.write(self.style.ERROR('Cannot use --delete-invalid with --dry-run'))
            return

        # Get the queryset
        queryset = GalleryImage.objects.all()
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        total_images = queryset.count()
        if total_images == 0:
            self.stdout.write('No gallery images found to check.')
            return

        self.stdout.write(f'Checking {total_images} gallery images...')
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        # Statistics
        valid_count = 0
        invalid_count = 0
        missing_files = 0
        animated_images = 0
        invalid_formats = 0
        oversized_files = 0
        corrupted_files = 0

        for gallery_image in queryset:
            try:
                result = self._validate_image(gallery_image, verbose)

                if result['valid']:
                    valid_count += 1

                else:
                    invalid_count += 1
                    issue_type = result['issue_type']

                    if issue_type == 'missing_file':
                        missing_files += 1
                    elif issue_type == 'animated':
                        animated_images += 1
                    elif issue_type == 'invalid_format':
                        invalid_formats += 1
                    elif issue_type == 'oversized':
                        oversized_files += 1
                    elif issue_type == 'corrupted':
                        corrupted_files += 1

                    self.stdout.write(
                        self.style.ERROR(f'✗ Image {gallery_image.id}: {result["message"]}')
                    )

                    # Delete invalid images if requested
                    if delete_invalid:
                        self._delete_invalid_image(gallery_image, result['issue_type'])

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Image {gallery_image.id}: Unexpected error - {str(e)}')
                )
                invalid_count += 1

        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('VALIDATION SUMMARY')
        self.stdout.write('=' * 50)
        self.stdout.write(f'Total images checked: {total_images}')
        self.stdout.write(f'Valid images: {valid_count}')
        self.stdout.write(f'Invalid images: {invalid_count}')

        if invalid_count > 0:
            self.stdout.write('\nInvalid image breakdown:')
            if missing_files > 0:
                self.stdout.write(f'  - Missing files: {missing_files}')
            if animated_images > 0:
                self.stdout.write(f'  - Animated images: {animated_images}')
            if invalid_formats > 0:
                self.stdout.write(f'  - Invalid formats: {invalid_formats}')
            if oversized_files > 0:
                self.stdout.write(f'  - Oversized files: {oversized_files}')
            if corrupted_files > 0:
                self.stdout.write(f'  - Corrupted files: {corrupted_files}')

        if delete_invalid and invalid_count > 0:
            self.stdout.write(f'\n{invalid_count} invalid images have been deleted.')

    def _validate_image(self, gallery_image, verbose=False):
        """
        Validate a single gallery image against the validation rules
        """
        # Check if file exists
        if not gallery_image.image or not gallery_image.image.name:
            return {
                'valid': False,
                'issue_type': 'missing_file',
                'message': 'No image file associated with this record',
            }

        # Check if file exists on disk
        try:
            file_path = gallery_image.image.path
            if not os.path.exists(file_path):
                return {
                    'valid': False,
                    'issue_type': 'missing_file',
                    'message': f'File not found on disk: {file_path}',
                }
        except Exception as e:
            return {
                'valid': False,
                'issue_type': 'missing_file',
                'message': f'Cannot access file: {str(e)}',
            }

        # File size check (20MB max)
        MAX_FILE_SIZE_MB = 20
        try:
            file_size = os.path.getsize(file_path)
            if file_size > 1024 * 1024 * MAX_FILE_SIZE_MB:
                return {
                    'valid': False,
                    'issue_type': 'oversized',
                    'message': f'File too large: {file_size / (1024 * 1024):.1f}MB (max {MAX_FILE_SIZE_MB}MB)',
                }
        except Exception as e:
            return {
                'valid': False,
                'issue_type': 'corrupted',
                'message': f'Cannot determine file size: {str(e)}',
            }

        # Try opening the file with PIL
        try:
            with open(file_path, 'rb') as f:
                img = Image.open(f)
                img_format = img.format.lower() if img.format else 'unknown'
        except UnidentifiedImageError:
            return {
                'valid': False,
                'issue_type': 'corrupted',
                'message': 'File is not a valid image',
            }
        except Exception as e:
            return {
                'valid': False,
                'issue_type': 'corrupted',
                'message': f'Cannot open image: {str(e)}',
            }

        # Supported types
        allowed_formats = {'jpeg', 'jpg', 'png', 'webp'}
        if img_format not in allowed_formats:
            return {
                'valid': False,
                'issue_type': 'invalid_format',
                'message': f'Unsupported format: {img_format} (allowed: {", ".join(allowed_formats)})',
            }

        # Check for animation
        if img_format == 'webp' and getattr(img, 'is_animated', False):
            return {
                'valid': False,
                'issue_type': 'animated',
                'message': 'Animated images are not supported',
            }

        return {'valid': True, 'issue_type': None, 'message': 'Valid image'}

    def _delete_invalid_image(self, gallery_image, issue_type):
        """
        Delete an invalid image from the database and filesystem
        """
        try:
            # The model has a post_delete signal that will handle file cleanup
            gallery_image.delete()
            self.stdout.write(f'  -> Deleted image {gallery_image.id}')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  -> Failed to delete image {gallery_image.id}: {str(e)}')
            )
