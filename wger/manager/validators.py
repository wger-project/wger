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
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible

# wger
from wger.manager.consts import RIR_OPTIONS


@deconstructible
class NullMinValueValidator(BaseValidator):
    message = 'Ensure this value is either NULL or greater than or equal to %(limit_value)s.'
    code = 'min_value'

    def compare(self, a, b):
        if a is None or b is None:
            return True

        return a < b


def validate_rir(value):
    if value not in RIR_OPTIONS:
        raise ValidationError(f'{value} is not a valid RiR option: {RIR_OPTIONS}')
