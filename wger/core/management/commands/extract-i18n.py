# -*- coding: utf-8 *-*

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
from wger.core.models import RepetitionUnit
from wger.exercises.models import (
    Equipment,
    ExerciseCategory,
    Muscle,
)


class Command(BaseCommand):
    """
    Helper command to extract translatable content from the database such as
    categories, muscles or equipment names and write it to files, so they can
    be extracted and translated on weblate. This is a bit hacky and ugly, but
    these strings *very* rarely change.
    """

    help = 'Write the translatable strings from the database to a file'

    def handle(self, **options):

        # Collect all translatable items
        data = [i for i in ExerciseCategory.objects.all()] \
            + [i for i in Equipment.objects.all()] \
            + [i for i in Muscle.objects.all()] \
            + [i for i in RepetitionUnit.objects.all()]

        # Django - write to .tpl file
        with open('wger/i18n.tpl', 'w') as f:
            out = '{% load i18n %}\n'
            for i in data:
                out += f'{{% translate "{i}" %}}\n'
            f.write(out)
            self.stdout.write(self.style.SUCCESS(f'Wrote content to i18n.tpl!'))

        # React - write to .tsx file (copy the file into the react repo)
        with open('wger/i18n.tsx', 'w') as f:
            out = '''
                import { useTranslation } from "react-i18next";

                export const DummyComponent = () => {
                const [t, i18n] = useTranslation();'''
            for i in data:
                out += f't("{i}");\n'

            out += '''
                return (<p></p>);
                };'''
            f.write(out)
            self.stdout.write(self.style.SUCCESS(f'Wrote content to i18n.tsx!'))

        # Flutter - write to .dart file (copy the file into the flutter repo)
        # TO BE IMPLEMENTED...
