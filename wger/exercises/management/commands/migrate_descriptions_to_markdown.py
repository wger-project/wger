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
import time

# Django
from django.core.management.base import BaseCommand
from django.db.models import Q

# Third Party
from markdownify import markdownify

# wger
from wger.exercises.models import Translation


class Command(BaseCommand):
    """
    Migrates existing HTML descriptions to Markdown.
    Populates the 'description_source' field using 'markdownify'
    on the existing 'description'.
    """

    help = 'Converts HTML descriptions to Markdown source for the new editing system.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Simulate the migration without saving changes.',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to process per batch.',
        )

    def handle(self, **options):
        dry_run = options['dry_run']

        # Filter: Has description, but NO source (to avoid re-migrating).
        translations_to_migrate = Translation.objects.filter(
            Q(description_source__isnull=True) | Q(description_source=''), description__isnull=False
        ).exclude(description='')

        total = translations_to_migrate.count()
        self.stdout.write(f'Found {total} translations to migrate.')

        count = 0
        errors = 0

        for trans in translations_to_migrate:
            try:
                # ATX to ensure # headings instead of underlined headings.
                md_source = markdownify(trans.description, heading_style='ATX')

                if dry_run:
                    self.stdout.write(
                        f'[Dry Run] ID {trans.id}: '
                        f'converted length {len(trans.description)} -> {len(md_source)}'
                    )
                else:
                    trans.description_source = md_source

                    # save() triggers:
                    # description = render_markdown(description_source)
                    # To ensure a clean HTML cache.
                    trans.save()

                count += 1

                if count % 100 == 0:
                    self.stdout.write(f'Processed {count}/{total}...')

            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f'Error converting ID {trans.id}: {e}'))

        success_msg = f'Successfully migrated {count} descriptions.'
        if dry_run:
            success_msg += ' (Dry Run)'

        self.stdout.write(self.style.SUCCESS(success_msg))
        if errors > 0:
            self.stdout.write(self.style.WARNING(f'Finished with {errors} errors.'))
