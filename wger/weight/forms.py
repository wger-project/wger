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

# Django
from django import forms
from django.forms import (
    CharField,
    DateTimeField,
    Form,
    Textarea,
)
from django.utils.translation import gettext as _

# Third Party
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout


CSV_DATETIME_FORMAT = (
    ('%d.%m.%Y %H:%M:%S', 'DD.MM.YYYY HH:MM:SS (30.01.2012 14:30:00)'),
    ('%d.%m.%Y %H:%M', 'DD.MM.YYYY HH:MM (30.01.2012 14:30)'),
    ('%d.%m.%y %H:%M:%S', 'DD.MM.YY HH:MM:SS (30.01.12 14:30:00)'),
    ('%d.%m.%y %H:%M', 'DD.MM.YY HH:MM (30.01.12 14:30)'),
    ('%Y-%m-%d %H:%M:%S', 'YYYY-MM-DD HH:MM:SS (2012-01-30 14:30:00)'),
    ('%Y-%m-%d %H:%M', 'YYYY-MM-DD HH:MM (2012-01-30 14:30)'),
    ('%y-%m-%d %H:%M:%S', 'YY-MM-DD HH:MM:SS (12-01-30 14:30:00)'),
    ('%y-%m-%d %H:%M', 'YY-MM-DD HH:MM (12-01-30 14:30)'),
    ('%m/%d/%Y %H:%M:%S', 'MM/DD/YYYY HH:MM:SS (01/30/2012 14:30:00)'),
    ('%m/%d/%Y %H:%M', 'MM/DD/YYYY HH:MM (01/30/2012 14:30)'),
    ('%m/%d/%y %H:%M:%S', 'MM/DD/YY HH:MM:SS (01/30/12 14:30:00)'),
    ('%m/%d/%y %H:%M', 'MM/DD/YY HH:MM (01/30/12 14:30)'),
)


class WeightCsvImportForm(Form):
    """
    A helper form with only a textarea
    """

    csv_input = CharField(widget=Textarea, label=_('Input'))
    date_format = forms.ChoiceField(choices=CSV_DATETIME_FORMAT, label=_('Date format'))

    def __init__(self, *args, **kwargs):
        super(WeightCsvImportForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'csv_input',
            'date_format',
        )
        self.helper.form_tag = False
