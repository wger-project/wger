# Third Party
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
        fields = [
            'id',
            'name',
            'unit'
        ]


class MeasurementSerializer(serializers.ModelSerializer):
    """
    Measurement serializer
    """

    class Meta:
        model = Measurement
        fields = [
            'id',
            'category',
            'date',
            'value',
            'notes',
        ]
