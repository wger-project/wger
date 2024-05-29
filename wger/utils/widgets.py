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
import logging
#
# You should have received a copy of the GNU Affero General Public License
import uuid
from itertools import chain

# Django
from django.forms import fields
from django.forms.widgets import (
    CheckboxInput,
    CheckboxSelectMultiple,
    DateInput,
    Select,
    SelectMultiple,
    TextInput,
)
from django.utils.encoding import force_str
from django.utils.html import (
    conditional_escape,
    escape,
)
from django.utils.safestring import mark_safe
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


#
# Others
#
class ExerciseAjaxSelect(SelectMultiple):
    """
    Custom widget that allows to select exercises from an autocompleter

    This is basically a modified MultipleSelect widget
    """

    def render(self, name, value, attrs=None, choices=(), renderer=None):
        if value is None:
            value = []

        output = [
            '<div>',
            '<input type="text" id="exercise-search" class="form-control">',
            '</div>',
            '<div id="exercise-search-log">',
        ]

        options = self.render_options(choices, value)
        if options:
            output.append(options)
        output.append('</div>')

        return mark_safe('\n'.join(output))

    def render_options(self, choices, selected_choices):
        # Normalize to strings.
        selected_choices = set(force_str(v) for v in selected_choices)
        output = []
        for option_value, option_label in chain(self.choices, choices):
            output.append(self.render_option(selected_choices, option_value, option_label))
        return '\n'.join(output)

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_str(option_value)
        if option_value in selected_choices:
            return """
                    <div id="a%(div_id)s" class="ajax-exercise-select">
                        <a href="#">
                        <img src="/static/images/icons/status-off.svg"
                             width="14"
                             height="14"
                             alt="Delete">
                        </a> %(value)s
                        <input type="hidden" name="exercises" value="%(id)s">
                    </div>
            """ % {
                'value': conditional_escape(force_str(option_label)),
                'id': escape(option_value),
                'div_id': uuid.uuid4(),
            }

        else:
            return ''


class CheckboxChoiceInputTranslated(CheckboxInput):
    """
    Overwritten CheckboxInput

    This only translated the text for the select widgets
    """

    input_type = 'checkbox'

    def __init__(self, name, value, attrs, choice, index):
        choice = (choice[0], _(choice[1]))

        super(CheckboxChoiceInputTranslated, self).__init__(name, value, attrs, choice, index)


class CheckboxChoiceInputTranslatedOriginal(CheckboxInput):
    """
    Overwritten CheckboxInput

    This only translated the text for the select widgets, showing the original
    string as well.
    """

    input_type = 'checkbox'

    def __init__(self, name, value, attrs, choice, index):
        if _(choice[1]) != choice[1]:
            choice = (choice[0], f'{choice[1]} ({_(choice[1])})')
        else:
            choice = (choice[0], _(choice[1]))

        super(CheckboxChoiceInputTranslatedOriginal, self).__init__(
            name, value, attrs, choice, index
        )


class CheckboxFieldRendererTranslated(CheckboxSelectMultiple):
    choice_input_class = CheckboxChoiceInputTranslated


class CheckboxFieldRendererTranslatedOriginal(CheckboxSelectMultiple):
    choice_input_class = CheckboxChoiceInputTranslatedOriginal


class BootstrapSelectMultiple(CheckboxSelectMultiple):
    pass
    # renderer = CheckboxBootstrapRenderer


class BootstrapSelectMultipleTranslatedOriginal(CheckboxSelectMultiple):
    pass
    # renderer = CheckboxBootstrapRendererTranslatedOriginal


class TranslatedSelectMultiple(BootstrapSelectMultiple):
    """
    A SelectMultiple widget that translates the options
    """

    pass


class TranslatedOriginalSelectMultiple(BootstrapSelectMultipleTranslatedOriginal):
    """
    A SelectMultiple widget that translates the options, showing the original
    string as well. This is currently only used in the muscle list, where the
    translated muscles as well as the latin names are shown.
    """

    pass


class TranslatedSelect(Select):
    """
    A Select widget that translates the options
    """

    def render_option(self, selected_choices, option_value, option_label):
        return super(TranslatedSelect, self).render_option(
            selected_choices, option_value, _(option_label)
        )
