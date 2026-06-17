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
import re
from argparse import ArgumentParser
from typing import Iterator

# Django
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand


ThumbnailSignature = tuple[int, int, int | None, str | None]


# easy-thumbnails default filename pattern:
#   <original>.<W>x<H>_q<Q>[_crop-<method>].<ext>
# We match the suffix portion that easy-thumbnails appends.
THUMBNAIL_SUFFIX_RE = re.compile(
    r'\.(?P<width>\d+)x(?P<height>\d+)'
    r'(?:_q(?P<quality>\d+))?'
    r'(?:_crop(?:-(?P<crop>[\w-]+))?)?'
    r'\.[A-Za-z0-9]+$'
)


class Command(BaseCommand):
    """
    Delete thumbnail files whose alias is no longer configured.

    When `THUMBNAIL_ALIASES` is changed (e.g. an alias is removed or its size
    changed), easy-thumbnails leaves the old generated files on storage
    forever. This command walks the configured default storage (local FS, S3,
    etc.) and removes any thumbnail file that does not match a currently
    configured alias. Originals are never touched.
    """

    help = (
        'Delete thumbnail files whose alias is no longer present in '
        'THUMBNAIL_ALIASES. Runs as a dry-run by default; pass --delete to '
        'actually remove files.'
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            '--delete',
            action='store_true',
            default=False,
            help='Actually delete files. Without this flag, only reports what would be removed.',
        )
        parser.add_argument(
            '--path',
            default='',
            help=(
                'Subdirectory in the storage backend to scan (e.g. "ingredients"). '
                'Defaults to the storage root.'
            ),
        )

    def handle(self, **options) -> None:
        delete: bool = options['delete']
        start_path: str = options['path']

        allowed = self._allowed_signatures()
        self.stdout.write(
            f'Allowed thumbnail signatures ({len(allowed)}): '
            + ', '.join(sorted(self._format_sig(s) for s in allowed))
        )
        self.stdout.write(f'Storage: {default_storage.__class__.__name__}')
        self.stdout.write(f'Scanning: {start_path or "<root>"}')
        self.stdout.write(f'Mode: {"DELETE" if delete else "dry-run"}')
        self.stdout.write('')

        removed_count = 0
        removed_bytes = 0
        kept_count = 0

        for full_name in self._walk(start_path):
            base = full_name.rsplit('/', 1)[-1]
            match = THUMBNAIL_SUFFIX_RE.search(base)
            if not match:
                continue  # original image, leave alone

            sig = (
                int(match.group('width')),
                int(match.group('height')),
                int(match.group('quality')) if match.group('quality') else None,
                match.group('crop'),  # None for uncropped
            )

            if self._is_allowed(sig, allowed):
                kept_count += 1
                continue

            try:
                size = default_storage.size(full_name)
            except (OSError, NotImplementedError):
                size = 0

            removed_count += 1
            removed_bytes += size

            if delete:
                try:
                    default_storage.delete(full_name)
                except OSError as exc:
                    self.stderr.write(f'Failed to delete {full_name}: {exc}')

        gb = removed_bytes / (1024**3)
        verb = 'Deleted' if delete else 'Would delete'
        self.stdout.write('')
        self.stdout.write(f'{verb}: {removed_count} files ({gb:.2f} GB)')
        self.stdout.write(f'Kept:    {kept_count} thumbnails matching current aliases')
        if not delete and removed_count:
            self.stdout.write('')
            self.stdout.write('Re-run with --delete to remove these files.')

    def _walk(self, path: str) -> Iterator[str]:
        """
        Yield every file under `path` in the configured storage backend.

        Uses Django's storage API (`listdir`) so it works with any backend
        """
        try:
            dirs, files = default_storage.listdir(path)
        except (FileNotFoundError, OSError):
            return

        for f in files:
            yield f'{path}/{f}' if path else f
        for d in dirs:
            sub = f'{path}/{d}' if path else d
            yield from self._walk(sub)

    def _allowed_signatures(self) -> set[ThumbnailSignature]:
        """
        Build the set of (width, height, quality, crop) tuples produced by the
        currently configured aliases. `quality` defaults to 85 in
        easy-thumbnails; `crop` is None unless explicitly set.
        """
        allowed = set()
        for alias_opts in settings.THUMBNAIL_ALIASES.get('', {}).values():
            width, height = alias_opts['size']
            quality = alias_opts.get('quality', 85)
            crop = alias_opts.get('crop')
            crop_key = str(crop) if crop else None
            allowed.add((width, height, quality, crop_key))
        return allowed

    @staticmethod
    def _is_allowed(sig: ThumbnailSignature, allowed: set[ThumbnailSignature]) -> bool:
        width, height, quality, crop = sig
        for aw, ah, aq, ac in allowed:
            if (width, height) != (aw, ah):
                continue
            if crop != ac:
                continue
            # Older thumbnails may lack the _q<N> token; be lenient.
            if quality is not None and quality != aq:
                continue
            return True
        return False

    @staticmethod
    def _format_sig(sig: ThumbnailSignature) -> str:
        w, h, q, c = sig
        s = f'{w}x{h}_q{q}'
        if c:
            s += f'_crop-{c}'
        return s
