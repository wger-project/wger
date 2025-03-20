# Standard Library
from decimal import Decimal

# Third Party
from rest_framework import serializers


class DecimalOrIntegerField(serializers.DecimalField):
    """
    Custom field to represent Decimal values as integers when they are whole numbers.
    """

    def to_representation(self, value):
        value = super().to_representation(value)
        if value is not None:
            value = Decimal(value)
            if value == value.to_integral_value():
                return str(int(value))
        return str(value)
