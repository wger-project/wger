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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Third Party
from lingua import LanguageDetectorBuilder
from rest_framework import serializers

# wger
from wger.core.models import Language


def validate_language_matches(text: str, language: Language, source_label: str) -> None:
    """
    Raise ``ValidationError`` if the detected language of ``text`` doesn't
    match the ``short_name`` of the given ``Language``.

    ``source_label`` (e.g. ``'description'``, ``'comment'``) is used in the
    error message to point the caller at the offending field.
    """

    detector = LanguageDetectorBuilder.from_all_languages().build()
    detected_language = detector.detect_language_of(text)
    if detected_language is None:
        raise serializers.ValidationError(
            {
                'language': f'Could not detect the language of the {source_label}. '
                f'Try adding more content or rephrasing your text, language '
                f'detection works better with longer or more complete sentences.'
            }
        )

    detected_language_code = detected_language.iso_code_639_1.name.lower()
    if detected_language_code != language.short_name.lower():
        raise serializers.ValidationError(
            {
                'language': f'The detected language of the {source_label} is '
                f'"{detected_language.name.capitalize()}" ({detected_language_code}), '
                f'which does not match your selected language: "{language.full_name.capitalize()}" '
                f'({language.short_name}). If you believe this is incorrect, try adding '
                f'more content or rephrasing your text, as language detection works '
                f'better with longer or more complete sentences.'
            }
        )
