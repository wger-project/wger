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
from wger.utils.constants import TWOPLACES
from wger.utils.units import AbstractWeight
from wger.weight.models import WeightEntry


MIN_WEIGHT_KG = Decimal(30)
MAX_WEIGHT_KG = Decimal(600)


class WeightEntrySerializer(serializers.ModelSerializer):
    """
    Weight serializer
    """

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    weight = serializers.DecimalField(max_digits=7, decimal_places=2)

    def validate_weight(self, value):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        weight_unit = getattr(getattr(user, 'userprofile', None), 'weight_unit', 'kg')

        weight = AbstractWeight(value, weight_unit).kg.quantize(TWOPLACES)

        if weight < MIN_WEIGHT_KG:
            raise serializers.ValidationError(
                f'Ensure this value is greater than or equal to {MIN_WEIGHT_KG}.'
            )

        if weight > MAX_WEIGHT_KG:
            raise serializers.ValidationError(
                f'Ensure this value is less than or equal to {MAX_WEIGHT_KG}.'
            )

        return weight

    class Meta:
        model = WeightEntry
        fields = (
            'id',
            'date',
            'weight',
            'user',
        )
