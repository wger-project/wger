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

# Django
from django.conf import settings
from django.core.checks import (
    Warning,
    register,
)


@register()
def exercise_checks(app_configs, **kwargs):
    errors = []

    # All bases should have at least one translation
    # wger
    from wger.exercises.models import ExerciseBase
    no_translations = ExerciseBase.no_translations.all().count()
    if no_translations:
        errors.append(
            Warning(
                'exercises without translations',
                hint=f'There are {no_translations} exercises without translations, this will '
                'cause problems! You can output or delete them with "python manage.py '
                'exercises-health-check"',
                obj=settings,
                id='wger.W002',
            )
        )

    return errors
