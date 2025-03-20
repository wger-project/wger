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

# Standard Library
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Standard Library
import logging

# Django
from django.forms import fields
from django.forms.widgets import (
    CheckboxSelectMultiple,
    DateInput,
    Select,
    TextInput,
)
from django.utils.translation import gettext as _


logger = logging.getLogger(__name__)


#
# Date and time related fields
#


class Html5DateInput(DateInput):
    """
    Custom Input class that is rendered with an HTML5 type="date"
    """

    template_name = 'forms/html5_date.html'
    input_type = 'date'

    def get_context(self, name, value, attrs):
        """Pass the value as a date to the template. This is necessary because
        django's default behaviour is to convert it to a string, where it can't
        be formatted anymore."""

        context = super(Html5DateInput, self).get_context(name, value, attrs)
        context['widget']['orig_value'] = value
        return context


class Html5FormDateField(fields.DateField):
    """
    HTML5 form date field
    """

    widget = Html5DateInput


class Html5TimeInput(TextInput):
    """
    Custom Input class that is rendered with an HTML5 type="time"

    This is specially useful in mobile devices and not available
    with older versions of django.
    """

    input_type = 'time'


class Html5FormTimeField(fields.TimeField):
    """
    HTML5 form time field
    """

    widget = Html5TimeInput


#
# Number related fields
#


class Html5NumberInput(TextInput):
    """
    Custom Input class that is rendered with an HTML5 type="number"

    This is specially useful in mobile devices and not available
    with older versions of django.
    """

    input_type = 'number'


class BootstrapSelectMultiple(CheckboxSelectMultiple):
    pass
    # renderer = CheckboxBootstrapRenderer


class TranslatedSelect(Select):
    """
    A Select widget that translates the options
    """

    def render_option(self, selected_choices, option_value, option_label):
        return super(TranslatedSelect, self).render_option(
            selected_choices, option_value, _(option_label)
        )
