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
from wger.core.models import (
    RepetitionUnit,
    WeightUnit,
)
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
            return (
                text.lower()
                .replace(' ', '_')
                .replace('-', '_')
                .replace('/', '_')
                .replace('(', '_')
                .replace(')', '_')
            )

        # Collect all translatable items
        data = (
            [i for i in ExerciseCategory.objects.all()]
            + [i for i in Equipment.objects.all()]
            + [i.name_en for i in Muscle.objects.all() if i.name_en]
            + [i for i in RepetitionUnit.objects.all()]
            + [i for i in WeightUnit.objects.all()]
        )

        # Make entries unique and sort alphabetically
        data = sorted(set([i.__str__() for i in data]))

        #
        # Django - write to .tpl file
        with open('wger/i18n.tpl', 'w') as f:
            out = '{% load i18n %}\n'
            for i in data:
                out += f'{{% translate "{i}" %}}\n'
            f.write(out)
            self.stdout.write(self.style.SUCCESS(f'Wrote content to wger/i18n.tpl'))

        #
        # React - copy the file to src/i18n.tsx in the React repo
        with open('wger/i18n.tsx', 'w') as f:
            out = """
                // This code is autogenerated in the backend repo in extract-i18n.py do not edit!

                // Translate dynamic strings that are returned from the server
                // These strings such as categories or equipment are returned by the server
                // in English and need to be translated here in the application (there are
                // probably better ways to do this, but that's the way it is right now).

                import { useTranslation } from "react-i18next";

                // eslint-disable-next-line @typescript-eslint/no-unused-vars
                const DummyComponent = () => {
                const [t] = useTranslation();"""
            for i in data:
                out += f't("server.{cleanup_name(i.__str__())}");\n'

            out += """
                return (<p></p>);
                };"""
            f.write(out)
            self.stdout.write(self.style.SUCCESS(f'Wrote content to wger/i18n.tsx'))

        #
        # Flutter - copy content to the end of lib/l10n/app_en.arb in the flutter repo
        with open('wger/app_en.arb', 'w') as f:
            out = ''
            for i in data:
                out += f'"{cleanup_name(i.__str__())}": "{i}",\n'
                out += f'"@{cleanup_name(i.__str__())}": {{ \n'
                out += f'"description": "Generated entry for translation for server strings"\n'
                out += '},\n'
            f.write(out)
            self.stdout.write(self.style.SUCCESS(f'Wrote content to app_en.arb'))

        # Copy to lib/helpers/i18n.dart in the flutter repo
        with open('wger/i18n.dart', 'w') as f:
            out = """
            /// This code is autogenerated in the backend repo in extract-i18n.py do not edit!

            /// Translate dynamic strings that are returned from the server
            /// These strings such as categories or equipment are returned by the server
            /// in English and need to be translated here in the application (there are
            /// probably better ways to do this, but that's the way it is right now).

            import 'dart:developer';

            import 'package:flutter/widgets.dart';
            import 'package:flutter_gen/gen_l10n/app_localizations.dart';
            import 'package:logging/logging.dart';

            String getTranslation(String value, BuildContext context) {
                  switch (value) {"""
            for i in data:
                out += f"""
                case '{i}':
                    return AppLocalizations.of(context).{cleanup_name(i.__str__())};
                """

            out += """
                default:
                    log('Could not translate the server string $value', level: Level.WARNING.value);
                    return value;
                }
            }"""

            f.write(out)
            self.stdout.write(self.style.SUCCESS('Wrote content to wger/i18n.dart'))
