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

from django.db import models

from wger.utils.widgets import Html5FormDateField
from wger.utils.widgets import Html5FormTimeField
from wger.utils.widgets import Html5FormDecimalField
from wger.utils.widgets import Html5FormIntegerField
from wger.utils.widgets import Html5FormFloatField

logger = logging.getLogger('wger.custom')


class Html5TimeField(models.TimeField):
    '''
    Custom Time field that uses the Html5TimeInput widget
    '''

    def formfield(self, **kwargs):
        '''
        Use our custom field
        '''
        defaults = {'form_class': Html5FormTimeField}
        defaults.update(kwargs)
        return super(Html5TimeField, self).formfield(**defaults)


class Html5DateField(models.DateField):
    '''
    Custom Time field that uses the Html5DateInput widget
    '''

    def formfield(self, **kwargs):
        '''
        Use our custom field
        '''
        defaults = {'form_class': Html5FormDateField}
        defaults.update(kwargs)
        return super(Html5DateField, self).formfield(**defaults)


class Html5DecimalField(models.DecimalField):
    '''
    Custom decimal field that uses the Html5NumberInput widget
    '''

    def formfield(self, **kwargs):
        '''
        Use our custom field
        '''
        defaults = {'form_class': Html5FormDecimalField}
        defaults.update(kwargs)
        return super(Html5DecimalField, self).formfield(**defaults)


class Html5FloatField(models.FloatField):
    '''
    Custom decimal field that uses the Html5NumberInput widget
    '''

    def formfield(self, **kwargs):
        '''
        Use our custom field
        '''
        defaults = {'form_class': Html5FormFloatField}
        defaults.update(kwargs)
        return super(Html5FloatField, self).formfield(**defaults)


class Html5IntegerField(models.IntegerField):
    '''
    Custom integer field that uses the Html5NumberInput widget
    '''

    def formfield(self, **kwargs):
        '''
        Use our custom field
        '''
        defaults = {'form_class': Html5FormIntegerField}
        defaults.update(kwargs)
        return super(Html5IntegerField, self).formfield(**defaults)
