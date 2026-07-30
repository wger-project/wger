# -*- coding: utf-8 -*-

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
from rest_framework import serializers

# wger
from wger.measurements.models import Measurement


class WeightEntrySerializer(serializers.ModelSerializer):
    """
    Weight serializer
    """

    user = serializers.PrimaryKeyRelatedField(source='category.user', read_only=True)
    weight = serializers.DecimalField(
        source='value',
        max_digits=5,
        decimal_places=2,
        min_value=Decimal(30),
        max_value=Decimal(600),
    )

    class Meta:
        model = Measurement
        fields = (
            'id',
            'date',
            'weight',
            'user',
        )

    def to_representation(self, instance):
        """
        Weight values are returned in the user's preferred weight unit,
        entries themselves may be stored in other units
        """
        data = super().to_representation(instance)
        unit = self.context['request'].user.userprofile.weight_unit
        data['weight'] = self.fields['weight'].to_representation(instance.value_in(unit))
        return data
