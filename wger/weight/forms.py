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

from django import forms
from django.forms import Form, CharField, Textarea, ModelForm, DateField, widgets
from django.utils.translation import ugettext as _

from wger.utils.constants import DATE_FORMATS
from wger.utils.widgets import Html5DateInput
from wger.weight.models import WeightEntry


CSV_DATE_FORMAT = (('%d.%m.%Y', 'DD.MM.YYYY (30.01.2012)'),
                   ('%d.%m.%y', 'DD.MM.YY (30.01.12)'),
                   ('%Y-%m-%d', 'YYYY-MM-DD (2012-01-30)'),
                   ('%y-%m-%d', 'YY-MM-DD (12-01-30)'),
                   ('%m/%d/%Y', 'MM/DD/YYYY (01/30/2012)'),
                   ('%m/%d/%y', 'MM/DD/YY (01/30/12)'),)


class WeightCsvImportForm(Form):
    '''
    A helper form with only a textarea
    '''
    csv_input = CharField(widget=Textarea, label=_('Input'))
    date_format = forms.ChoiceField(choices=CSV_DATE_FORMAT, label=_('Date format'))


class WeightForm(ModelForm):
    date = DateField(input_formats=DATE_FORMATS, widget=Html5DateInput())

    class Meta:
        model = WeightEntry
        exclude = []
        widgets = {
            'user': widgets.HiddenInput(),
        }
