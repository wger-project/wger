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

# wger
from wger.core.models import UserProfile
from wger.measurements.dynamic.base import (
    Dependency,
    DesiredRow,
    DynamicMeasurementType,
    register,
)
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.measurements.models.category import MetricType
from wger.measurements.utils.bmi import calculate_bmi


@register
class Bmi(DynamicMeasurementType):
    """
    One BMI entry per body weight entry, from the official body weight
    category and the height of the profile
    """

    slug = Category.DynamicType.BMI
    label = 'BMI'
    params_schema = {'type': 'object', 'additionalProperties': False}
    depends_on = [
        Dependency(
            Measurement,
            user_id=lambda entry: entry.category.user_id,
            when=lambda entry: entry.category.metric_type == MetricType.BODY_WEIGHT,
        ),
        # The height lives on the profile
        Dependency(UserProfile, user_id=lambda profile: profile.user_id),
    ]

    def compute(self, category: Category) -> list[DesiredRow]:
        return [
            DesiredRow(
                external_id=row['source_id'],
                date=row['date'],
                value=row['value'],
            )
            for row in calculate_bmi(category.user)
        ]
