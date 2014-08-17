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

from wger.utils.constants import TWOPLACES


logger = logging.getLogger('wger.custom')


'''
Weight unit classes
'''


class AbstractWeight(object):
    '''
    Helper class to use when working with sensible (kg) or imperial units.

    If any conversion happens, the result is a python decimal quantized to
    two places
    '''

    KG_IN_LBS = 2.2046
    LB_IN_KG = 0.4536

    weight = 0
    is_kg = True

    def __init__(self, weight, mode='kg'):
        '''
        :param weight: the numerical weight
        :param mode: the mode, only the values 'kg' (default) and 'lb' are supported
        '''
        self.weight = weight
        self.is_kg = True if mode == 'kg' else False

    @property
    def kg(self):
        '''
        :return: Return the weight in kilograms
        '''
        if self.is_kg:
            return self.weight
        else:
            return Decimal(self.weight * self.LB_IN_KG).quantize(TWOPLACES)

    @property
    def lb(self):
        '''
        :return: Return the weight in pounds
        '''
        if self.is_kg:
            return Decimal(self.weight * self.KG_IN_LBS).quantize(TWOPLACES)
        else:
            return self.weight
