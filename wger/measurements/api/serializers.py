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
from decimal import Decimal

# Third Party
import jsonschema
from rest_framework import serializers

# wger
from wger.measurements.models import (
    Category,
    Measurement,
)


class UnitSerializer(serializers.ModelSerializer):
    """
    Measurement unit serializer
    """

    class Meta:
        model = Category
        fields = ('id', 'name', 'unit', 'dynamic_type', 'dynamic_params')

    def validate(self, data):
        """
        Validate the dynamic_params JSON matches the required schema for the selected dynamic_type.
        """
        # get type and params
        dynamic_type = data.get(
            'dynamic_type', getattr(self.instance, 'dynamic_type', Category.DynamicType.NONE)
        )
        dynamic_params = data.get('dynamic_params', getattr(self.instance, 'dynamic_params', {}))

        # if dynamic type is none, just clear params to avoid excessive validation
        if dynamic_type == Category.DynamicType.NONE:
            data['dynamic_params'] = {}
            return super().validate(data)

        # define the allowed JSON structures
        schemas = {
            Category.DynamicType.BMI: {
                'type': 'object',
                'additionalProperties': False,
            },
            # when one rep max is added it can go here
            # Category.DynamicType.ONE_REP_MAX: {
            #     "type": "object",
            #     "properties": {"exercise_id": {"type": "integer"}, "max_reps": {"type": "integer"}},
            #     "required": ["exercise_id"],
            #     "additionalProperties": False
            # }
        }

        schema = schemas.get(dynamic_type)
        if schema:
            try:
                jsonschema.validate(instance=dynamic_params, schema=schema)
            except jsonschema.exceptions.ValidationError as e:
                raise serializers.ValidationError({'dynamic_params': e.message})

        return super().validate(data)


class MeasurementSerializer(serializers.ModelSerializer):
    """
    Measurement serializer
    """

    # Manually set the serializer to set the coerce_to_string option
    value = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        min_value=Decimal(0.0),
        max_value=Decimal(5000.0),
        coerce_to_string=False,
    )

    class Meta:
        model = Measurement
        fields = (
            'id',
            'category',
            'date',
            'value',
            'notes',
        )
