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
import csv

# Django
from django.core.management.base import BaseCommand

# wger
from wger.core.models import Language
from wger.exercises.models import (
    Exercise,
    ExerciseBase,
)


class Command(BaseCommand):
    """
    ONE OFF SCRIPT!

    This script reads out the exercise database and writes it to a CSV file,
    so that mass corrections can be done. The file can be read in with
    read-exercises-cleanup.py
    """

    def handle(self, **options):
        out = []

        languages = Language.objects.all()
        for base in ExerciseBase.objects.all():
            data = {
                'base': {
                    'uuid': base.uuid,
                    'category': base.category.name,
                    'equipment': ','.join([e.name for e in base.equipment.all()]),
                    'variations': base.variations.id if base.variations else '',
                }
            }

            for language in languages:
                exercise_data = {
                    'uuid': '',
                    'name': '',
                    'description': '',
                    'aliases': '',
                    'license': '',
                    'author': '',
                }

                exercise = Exercise.objects.filter(exercise_base=base, language=language).first()
                if exercise:
                    exercise_data['uuid'] = exercise.uuid
                    exercise_data['name'] = exercise.name
                    exercise_data['description'] = exercise.description
                    exercise_data['license'] = exercise.license.short_name
                    exercise_data['author'] = exercise.license_author
                    exercise_data['aliases'] = ','.join([a.alias for a in exercise.alias_set.all()])

                data[language.short_name] = exercise_data
            out.append(data)

        with open('exercise_cleanup.csv', 'w', newline='') as csvfile:
            file_writer = csv.writer(
                csvfile,
            )

            header = ['base:uuid', 'base:category', 'base:equipment', 'base:variations']
            for language in languages:
                header += [
                    f'{language.short_name}:uuid',
                    f'{language.short_name}:name',
                    f'{language.short_name}:alias',
                    f'{language.short_name}:description',
                    f'{language.short_name}:license',
                    f'{language.short_name}:author',
                ]

            file_writer.writerow(header)

            for entry in out:
                data = [
                    entry['base']['uuid'],
                    entry['base']['category'],
                    entry['base']['equipment'],
                    entry['base']['variations'],
                ]
                for language in languages:
                    data += [
                        entry[language.short_name]['uuid'],
                        entry[language.short_name]['name'],
                        entry[language.short_name]['aliases'],
                        entry[language.short_name]['description'],
                        entry[language.short_name]['license'],
                        entry[language.short_name]['author'],
                    ]

                file_writer.writerow(data)
