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
from django.core.cache import cache
from django.core.management.base import (
    BaseCommand,
    CommandError,
)


class Command(BaseCommand):
    """
    Clears caches
    """

    help = (
        'Clears the application cache. You *must* pass an option selecting '
        'what exactly you want to clear. See available options.'
    )

    def add_arguments(self, parser):

        parser.add_argument(
            '--clear-all',
            action='store_true',
            dest='clear_all',
            default=False,
            help='Clear ALL cached entries',
        )

    def handle(self, **options):
        """
        Process the options
        """

        if not options['clear_all']:
            raise CommandError('Please select what cache you need to delete, see help')

        # Nuclear option, clear all
        if options['clear_all']:
            cache.clear()
