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
from django.core.management.base import BaseCommand

# wger
from wger.nutrition.sync import export_ingredient_dump


class Command(BaseCommand):
    """
    Export all ingredients as a gzipped JSONL file for bulk synchronization.

    The generated file is placed in MEDIA_ROOT/ingredients/ and can be
    served to other wger instances for fast bulk imports.
    """

    help = 'Export all ingredients as a gzipped JSONL dump file for bulk synchronization'

    def handle(self, **options):
        export_ingredient_dump(
            self.stdout.write,
            style_fn=self.style.SUCCESS,
            show_progress_bar=True,
        )
