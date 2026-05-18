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
from argparse import ArgumentParser

# Django
from django.core.files.storage import (
    FileSystemStorage,
    default_storage,
)
from django.core.management.base import BaseCommand

# wger
from wger.nutrition.models import Image
from wger.nutrition.models.image import ingredient_image_upload_dir


class Command(BaseCommand):
    """
    Migrate ingredient image files from the old flat-per-PK layout
    to the UUID-sharded one.

    Moves the original image **and all sibling files** in the old directory
    (which includes thumbnails), then updates `Image.image` to point at the new
    path.

    Idempotent: an Image already at the new layout is skipped, so the command
    can be interrupted and resumed.
    """

    help = (
        'Move ingredient image files to the sharded directory layout. '
        'Dry-run by default; pass --apply to actually move files and update '
        'the database. Works with any storage backend.'
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            '--apply',
            action='store_true',
            default=False,
            help='Move files and update the database. Without this flag, only reports.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Process at most N ingredients (useful for staged rollouts).',
        )

    def handle(self, **options) -> None:
        apply_changes: bool = options['apply']
        limit: int | None = options['limit']

        is_local = isinstance(default_storage, FileSystemStorage)
        self.stdout.write(f'Storage: {default_storage.__class__.__name__}')
        fast_path = 'yes' if is_local else 'no, using copy+delete'
        self.stdout.write(f'Fast-path (os.rename): {fast_path}')
        self.stdout.write(f'Mode: {"APPLY" if apply_changes else "dry-run"}')
        self.stdout.write('')

        qs = Image.objects.all().order_by('pk')
        if limit:
            qs = qs[:limit]

        migrated = 0
        skipped = 0
        moved_files = 0
        errors = 0

        for img in qs.iterator(chunk_size=200):
            old_name = img.image.name
            new_name = ingredient_image_upload_dir(img, old_name)

            if old_name == new_name:
                skipped += 1
                continue

            old_dir = old_name.rsplit('/', 1)[0]
            new_dir = new_name.rsplit('/', 1)[0]

            # Discover every file in the old directory: original + thumbnails
            try:
                _dirs, files = default_storage.listdir(old_dir)
            except (FileNotFoundError, OSError) as exc:
                self.stderr.write(f'[{img.pk}] cannot list {old_dir}: {exc}')
                errors += 1
                continue

            if not files:
                # Original missing on disk but DB entry still points there.
                # Update the DB to the new path anyway so the layout is
                # consistent; the user can run thumbnail_cleanup afterwards.
                self.stderr.write(f'[{img.pk}] no files in {old_dir}, only updating DB')
                if apply_changes:
                    Image.objects.filter(pk=img.pk).update(image=new_name)
                skipped += 1
                continue

            for fname in files:
                old_path = f'{old_dir}/{fname}'
                new_path = f'{new_dir}/{fname}'

                if not apply_changes:
                    moved_files += 1
                    continue

                ok = self._move(old_path, new_path, is_local)
                if ok:
                    moved_files += 1
                else:
                    errors += 1

            if apply_changes:
                Image.objects.filter(pk=img.pk).update(image=new_name)
                # Best-effort: remove the now-empty old directory
                if is_local:
                    try:
                        os.rmdir(default_storage.path(old_dir))
                    except OSError:
                        pass

            migrated += 1

        self.stdout.write('')
        verb = 'Migrated' if apply_changes else 'Would migrate'
        self.stdout.write(f'{verb}: {migrated} ingredients, {moved_files} files')
        self.stdout.write(f'Skipped (already migrated): {skipped}')
        if errors:
            self.stdout.write(self.style.WARNING(f'Errors: {errors}'))

        if not apply_changes and migrated:
            self.stdout.write('')
            self.stdout.write('Re-run with --apply to perform the migration.')

    def _move(self, old_path: str, new_path: str, is_local: bool) -> bool:
        """Move a single file. Returns True on success, False on error."""

        # If the destination already exists from an earlier interrupted run
        # and the source is also still there, prefer the destination (assume
        # it was written successfully) and drop the source.
        if default_storage.exists(new_path):
            if default_storage.exists(old_path):
                try:
                    default_storage.delete(old_path)
                except OSError as exc:
                    self.stderr.write(f'failed to drop duplicate {old_path}: {exc}')
                    return False
            return True

        try:
            if is_local:
                old_full = default_storage.path(old_path)
                new_full = default_storage.path(new_path)
                os.makedirs(os.path.dirname(new_full), exist_ok=True)
                os.rename(old_full, new_full)
            else:
                with default_storage.open(old_path, 'rb') as src:
                    default_storage.save(new_path, src)
                default_storage.delete(old_path)
        except OSError as exc:
            self.stderr.write(f'failed to move {old_path} → {new_path}: {exc}')
            return False
        return True
