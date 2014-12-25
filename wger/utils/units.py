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

import logging
from decimal import Decimal

from wger.utils.constants import TWOPLACES, FOURPLACES


logger = logging.getLogger('wger.custom')


'''
Weight unit classes
'''


class AbstractWeight(object):
    '''
    Helper class to use when working with sensible (kg) or imperial units.

    For consistency, all results are converted to python decimal and quantized
    to four places
    Internally, all values are stored as kilograms and are converted only if
    needed. For consistency, all results are converted to python decimal and
    quantized to four places
    '''

    KG_IN_LBS = Decimal(2.20462262)
    LB_IN_KG = Decimal(0.45359237)

    weight = 0
    is_kg = True

    def __init__(self, weight, mode='kg'):
        '''
        :param weight: the numerical weight
        :param mode: the mode, values 'kg' (default), 'g', 'lb' and 'oz' are supported
        '''
        weight = self.normalize(weight)

        if mode == 'g':
            weight /= Decimal(1000)
        elif mode == 'oz':
            weight /= Decimal(16.0)

        self.weight = weight
        self.is_kg = True if mode in ('kg', 'g') else False

    def __mul__(self, other):
        '''
        Implement multiplying abstract weights.
        '''
        return AbstractWeight(self.weight * Decimal(other))

    def __add__(self, other):
        '''
        Implement adding abstract weights.

        For simplicity, the sum always occurs in kg. If the 'other' number is
        not an abstract weight, it will be converted to one (in kg)
        '''
        if not isinstance(other, AbstractWeight):
            other = AbstractWeight(other)
        return AbstractWeight(self.kg + other.kg)

    @staticmethod
    def normalize(value):
        '''
        Helper method that returns quantized
        :param value:
        :return: a quantized value to four decimal places
        '''

        return Decimal(value).quantize(FOURPLACES)

    @property
    def kg(self):
        '''
        For simplicity, the sum always occurs in kg
        :return: Return the weight in kilograms
        '''
        if self.is_kg:
            return self.normalize(self.weight)
        else:
            return self.normalize(self.weight * self.LB_IN_KG)

    @property
    def kg(self):
        '''
        Return the weight in kilograms

        :return: decimal
        '''
        if self.is_kg:
            return self.normalize(self.weight)
        else:
            return self.normalize(self.weight * self.LB_IN_KG)

    @property
    def g(self):
        '''
        Return the weight in grams

        :return: decimal
        '''
        return self.normalize(self.kg * 1000)

    @property
    def lb(self):
        '''
        Return the weight in pounds

        :return: decimal
        '''
        if self.is_kg:
            return self.normalize(self.weight * self.KG_IN_LBS)
        else:
            return self.normalize(self.weight)

    @property
    def oz(self):
        '''
        Return the weight in ounces

        :return: decimal
        '''
        return self.normalize(self.lb * 16)
