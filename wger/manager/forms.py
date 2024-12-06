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
from django.forms import (
    BooleanField,
    CharField,
    ChoiceField,
    Form,
    ModelForm,
    ModelMultipleChoiceField,
    widgets,
)
from django.utils.translation import (
    gettext as _,
    gettext_lazy,
)

# Third Party
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

# wger
from wger.manager.models import Workout


class WorkoutForm(ModelForm):
    class Meta:
        model = Workout
        fields = (
            'name',
            'description',
        )


class WorkoutMakeTemplateForm(ModelForm):
    class Meta:
        model = Workout
        fields = (
            'is_template',
            'is_public',
        )


class WorkoutCopyForm(Form):
    name = CharField(max_length=100, help_text=_('The name of the workout'), required=False)
    description = CharField(
        max_length=1000,
        help_text=_(
            'A short description or goal of the workout. For '
            "example 'Focus on back' or 'Week 1 of program xy'."
        ),
        widget=widgets.Textarea,
        required=False,
    )


class OrderedModelMultipleChoiceField(ModelMultipleChoiceField):
    """Ordered multiple choice field"""

    def clean(self, value):
        int_list = [int(i) for i in value]
        qs = super(OrderedModelMultipleChoiceField, self).clean(int_list)
        return sorted(qs, key=lambda x: int_list.index(x.pk))


class WorkoutScheduleDownloadForm(Form):
    """
    Form for the workout schedule download
    """

    pdf_type = ChoiceField(
        label=gettext_lazy('Type'),
        choices=(('log', gettext_lazy('Log')), ('table', gettext_lazy('Table'))),
    )
    images = BooleanField(label=gettext_lazy('with images'), required=False)
    comments = BooleanField(label=gettext_lazy('with comments'), required=False)

    def __init__(self):
        super(WorkoutScheduleDownloadForm, self).__init__()
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(
            Submit(
                'submit',
                _('Download'),
                css_class='btn-success btn-block',
                css_id='download-pdf-button-schedule',
            )
        )
