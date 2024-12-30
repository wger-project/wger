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

# Standard Library
import logging
from decimal import Decimal

# wger
from wger.utils.constants import FOURPLACES


logger = logging.getLogger(__name__)
"""
Weight and height unit classes
"""


class AbstractWeight:
    """
    Helper class to use when working with sensible (kg) or imperial units.

    Internally, all values are stored as kilograms and are converted only if
    needed. For consistency, all results are converted to python decimal and
    quantized to four places
    """

    KG_IN_LBS = Decimal(2.20462262)
    LB_IN_KG = Decimal(0.45359237)

    weight = 0
    is_kg = True

    def __init__(self, weight, mode='kg'):
        """
        :param weight: the numerical weight
        :param mode: the mode, values 'kg' (default), 'g', 'lb' and 'oz' are supported
        """
        weight = self.normalize(weight)

        if mode == 'g':
            weight /= Decimal(1000)
        elif mode == 'oz':
            weight /= Decimal(16.0)

        self.weight = weight
        self.is_kg = mode in ('kg', 'g')

    def __add__(self, other):
        """
        Implement adding abstract weights.

        For simplicity, the sum always occurs in kg
        """
        return AbstractWeight(self.kg + other.kg)

    @staticmethod
    def normalize(value):
        """
        Helper method that returns quantized
        :param value:
        :return: a quantized value to four decimal places
        """

        return Decimal(value).quantize(FOURPLACES)

    @property
    def kg(self):
        """
        Return the weight in kilograms

        :return: decimal
        """
        if self.is_kg:
            return self.normalize(self.weight)
        else:
            return self.normalize(self.weight * self.LB_IN_KG)

    @property
    def g(self):
        """
        Return the weight in grams

        :return: decimal
        """
        return self.normalize(self.kg * 1000)

    @property
    def lb(self):
        """
        Return the weight in pounds

        :return: decimal
        """
        if self.is_kg:
            return self.normalize(self.weight * self.KG_IN_LBS)
        else:
            return self.normalize(self.weight)

    @property
    def oz(self):
        """
        Return the weight in ounces

        :return: decimal
        """
        return self.normalize(self.lb * 16)


class AbstractHeight(object):
    """
    Helper class to use when working with sensible (cm) or imperial units.

    Internally, all values are stored as cm and are converted only if
    needed. For consistency, all results are converted to python decimal and
    quantized to four places
    """

    CM_IN_INCHES = Decimal(0.393701)
    INCHES_IN_CM = Decimal(2.5400)

    height = 0
    is_cm = True

    def __init__(self, height, mode='cm'):
        """
        :param height: the numerical height
        :param mode: the mode, values 'cm' (default), 'inches' are supported
        """
        height = self.normalize(height)

        self.height = height
        self.is_cm = mode == 'cm'

    @staticmethod
    def normalize(value):
        """
        Helper method that returns quantized
        :param value:
        :return: a quantized value to four decimal places
        """

        return Decimal(value).quantize(FOURPLACES)

    @property
    def cm(self):
        """
        Return the height in cm

        :return: decimal
        """
        if self.is_cm:
            return self.normalize(self.height)
        else:
            return self.normalize(self.height * self.INCHES_IN_CM)

    @property
    def inches(self):
        """
        Return the height in inches

        :return: decimal
        """
        if self.is_cm:
            return self.normalize(self.height * self.CM_IN_INCHES)
        else:
            return self.normalize(self.height)
