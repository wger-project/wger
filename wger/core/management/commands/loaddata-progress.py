from django.core.management.commands.loaddata import Command as LoadDataCommand
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm  # Assuming you have the tqdm library installed

class Command(LoadDataCommand):
    help = 'Load data from fixture files into the database with progress tracking.'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--progress',
            action='store_true',
            dest='progress',
            help='Show progress bar for loaddata process.',
        )

    def handle(self, *fixture_labels, **options):
        fixture_labels = self.track_progress(fixture_labels)
        super().handle(*fixture_labels, **options)

    def track_progress(self, fixture_labels):
        return tqdm(fixture_labels, desc='Loading fixtures', unit='fixture', ncols=80)

# Usage example:
# python manage.py custom_loaddata --progress my_fixture.json
