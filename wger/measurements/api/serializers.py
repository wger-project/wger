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
        fields = ['id', 'name', 'unit']


class MeasurementSerializer(serializers.ModelSerializer):
    """
    Measurement serializer
    """

    # Manually set the serializer to set the coerce_to_string option
    value = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        min_value=0,
        max_value=5000,
        coerce_to_string=False,
    )

    class Meta:
        model = Measurement
        fields = [
            'id',
            'category',
            'date',
            'value',
            'notes',
        ]
