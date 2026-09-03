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

# Standard Library
from typing import Optional

# Third Party
import jsonschema

# wger
from wger.measurements.dynamic.base import get_type
from wger.measurements.models import Category
from wger.measurements.models.category import MetricType
from wger.measurements.models.measurement import MeasurementSource


class CalculationConfigError(ValueError):
    """
    A calculation a category cannot be configured with.

    Carries the field the message belongs to, so the API can report it where
    the client sent it; the package itself knows nothing about serializers.
    """

    def __init__(self, field: str, message: str):
        super().__init__(message)
        self.field = field


def validate_calculation(
    dynamic_type: str,
    dynamic_params: dict,
    metric_type: str,
    user_id: Optional[int],
    instance=None,
):
    """
    Whether a category may be calculated this way, and whether the parameters
    fit the type it selects.

    ``instance`` is the stored category on an update, None when one is being
    created. Raises [CalculationConfigError]; the caller decides when a stored
    configuration is worth re-checking at all.
    """
    # A typed category has a writer already, the health import or the server
    # itself. Two of them would fight over the same rows, and for body weight
    # the calculated entries would even end up as the input of their own
    # computation
    if metric_type != MetricType.CUSTOM:
        raise CalculationConfigError(
            'dynamic_type', f'A {metric_type} category cannot be calculated'
        )

    if instance is not None and _has_own_entries(instance):
        raise CalculationConfigError(
            'dynamic_type',
            'The category holds entries of its own, move or delete them before calculating it',
        )

    calc = get_type(dynamic_type)
    if calc is None:
        return

    # The same calculation with the same settings yields the same series, so a
    # second category of it would only compute and sync the same values twice
    # (the same reasoning as one category per metric type)
    if _is_duplicate(dynamic_type, dynamic_params, user_id, instance):
        raise CalculationConfigError(
            'dynamic_type', f'You already have a {calc.label} category with these settings'
        )

    try:
        jsonschema.validate(instance=dynamic_params, schema=calc.params_schema)
    except jsonschema.exceptions.ValidationError as e:
        raise CalculationConfigError('dynamic_params', e.message)

    try:
        calc.validate_params(user_id, dynamic_params)
    except ValueError as e:
        raise CalculationConfigError('dynamic_params', str(e))


def _has_own_entries(instance) -> bool:
    """
    Whether the category holds entries that are not the output of a
    calculation. The engine only ever replaces its own rows, so these would
    stay in the series without anything maintaining them.
    """
    return instance.measurement_set.exclude(source=MeasurementSource.CALCULATED).exists()


def _is_duplicate(dynamic_type, dynamic_params, user_id, instance) -> bool:
    """
    Whether the user already has this calculation, configured the same way.

    The parameters are compared as they are stored. A value the user left out
    and one they typed that happens to be the server's default read as two
    configurations here, which lets a duplicate through rather than refusing
    two categories that differ.
    """
    if user_id is None:
        return False

    categories = Category.objects.filter(
        user_id=user_id,
        dynamic_type=dynamic_type,
        dynamic_params=dynamic_params,
    )
    if instance is not None:
        categories = categories.exclude(pk=instance.pk)
    return categories.exists()
