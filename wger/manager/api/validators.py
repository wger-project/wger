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
from rest_framework import serializers


def validate_requirements(value: dict | None):
    """Validates the requirements field."""

    if value is None:
        return

    if not isinstance(value, dict):
        raise serializers.ValidationError('Requirements must be a JSON object.')

    required_keys = {'rules'}  # Set of required keys
    if not all(key in value for key in required_keys):
        raise serializers.ValidationError("Missing required keys: 'rules'")  # More specific

    if 'rules' in value and not isinstance(value['rules'], list):
        raise serializers.ValidationError("'rules' must be a list.")
