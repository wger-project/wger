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

        # Replace whitespace and other problematic characters with underscores
        def cleanup_name(text: str) -> str:
            return text.lower().\
                replace(' ', '_').\
                replace('-', '_').\
                replace('/', '_').\
                replace('(', '_').\
                replace(')', '_')

        # Collect all translatable items
        data = [i for i in ExerciseCategory.objects.all()] \
            + [i for i in Equipment.objects.all()] \
            + [i.name_en for i in Muscle.objects.all() if i.name_en] \
            + [i for i in RepetitionUnit.objects.all()]

        # + [i for i in Muscle.objects.all()] \

        #
        # Django - write to .tpl file
        with open('wger/i18n.tpl', 'w') as f:
            out = '{% load i18n %}\n'
            for i in data:
                out += f'{{% translate "{i}" %}}\n'
            f.write(out)
            self.stdout.write(self.style.SUCCESS(f'Wrote content to i18n.tpl!'))

        #
        # React - write to .tsx file (copy the file into the react repo)
        with open('wger/i18n.tsx', 'w') as f:
            out = '''
                import { useTranslation } from "react-i18next";

                export const DummyComponent = () => {
                const [t, i18n] = useTranslation();'''
            for i in data:
                out += f't("server.{cleanup_name(i.__str__())}");\n'

            out += '''
                return (<p></p>);
                };'''
            f.write(out)
            self.stdout.write(self.style.SUCCESS(f'Wrote content to i18n.tsx!'))

        #
        # Flutter - write to app_en.arb, copy to the end of app_en.arb in the flutter repo
        with open('wger/app_en.arb', 'w') as f:
            out = ''
            for i in data:
                out += f'"{cleanup_name(i.__str__())}": "{i}",\n'
            f.write(out)
            self.stdout.write(self.style.SUCCESS(f'Wrote content to app_en.arb!'))

        # Copy to i18n.dart in the flutter repo
        with open('wger/i18n.dart', 'w') as f:
            out = '''String getTranslation(String value, BuildContext context) {
                  switch (value) {'''
            for i in data:
                out += f'''
                case '{i}':
                    return AppLocalizations.of(context).{cleanup_name(i.__str__())};
                '''

            out += f'''default:
                  return 'NOT TRANSLATED';
                  }}
                  }}'''

            f.write(out)
            self.stdout.write(self.style.SUCCESS(f'Wrote content to i18n.dart!'))
