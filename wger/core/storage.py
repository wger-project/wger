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
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class LenientManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """
    Like ManifestStaticFilesStorage but does not raise when an entry or target file
    referenced from CSS/JS is missing and simply returns the original name in that case.

    This is needed for some node packages that reference files not present (e.g. source maps).
    """

    def stored_name(self, name):
        try:
            return super().stored_name(name)
        except Exception:
            # If the manifest lookup or hashing fails (missing .map etc.), fall back
            # to the original reference so post-processing doesn't raise.
            print(
                f"Can't find name for static file reference: {name}. "
                f'This is expected in some node packages.'
            )

            return name

    def url_converter(self, name, hashed_files, template=None):
        # Wrap the base converter to ignore any errors during conversion and
        # return the original matched text unchanged.
        base_converter = super().url_converter(name, hashed_files, template)

        def converter(matchobj):
            try:
                return base_converter(matchobj)
            except Exception:
                print(
                    f"Can't find name for static file reference: {matchobj.group(0)}. "
                    f'This is expected in some node packages.'
                )
                return matchobj.groupdict().get('matched', matchobj.group(0))

        return converter
