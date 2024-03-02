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
"""
This file contains forms used in the application
"""

# Django
from django.forms import (
    BooleanField,
    CharField,
    ChoiceField,
    DecimalField,
    Form,
    IntegerField,
    ModelChoiceField,
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
from crispy_forms.layout import (
    Column,
    Layout,
    Row,
    Submit,
)

# wger
from wger.core.models import (
    RepetitionUnit,
    WeightUnit,
)
from wger.exercises.models import (
    Exercise,
    ExerciseBase,
)
from wger.manager.consts import RIR_OPTIONS
from wger.manager.models import (
    Day,
    Set,
    Setting,
    Workout,
    WorkoutLog,
    WorkoutSession,
)
from wger.utils.widgets import (
    ExerciseAjaxSelect,
    TranslatedSelectMultiple,
)


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


class DayForm(ModelForm):
    class Meta:
        model = Day
        exclude = ('training',)
        widgets = {'day': TranslatedSelectMultiple()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'description',
            'day',
        )


class OrderedModelMultipleChoiceField(ModelMultipleChoiceField):
    """Ordered multiple choice field"""

    def clean(self, value):
        int_list = [int(i) for i in value]
        qs = super(OrderedModelMultipleChoiceField, self).clean(int_list)
        return sorted(qs, key=lambda x: int_list.index(x.pk))


class SetForm(ModelForm):
    exercises = OrderedModelMultipleChoiceField(
        queryset=ExerciseBase.objects.all(),
        label=_('Exercises'),
        required=False,
        widget=ExerciseAjaxSelect,
        help_text=_(
            'You can search for more than one '
            'exercise, they will be grouped '
            'together for a superset.'
        ),
    )

    english_results = BooleanField(
        label=gettext_lazy('Also search for names in English'),
        initial=True,
        required=False,
    )

    class Meta:
        model = Set
        exclude = ('order', 'exerciseday')


class SettingForm(ModelForm):
    class Meta:
        model = Setting
        exclude = ('set', 'exercise', 'order', 'name')


class WorkoutLogForm(ModelForm):
    """
    Helper form for a WorkoutLog.

    These fields are re-defined here only to make them optional. Otherwise
    all the entries in the formset would be required, which is not really what
    we want. This form is one prime candidate to rework with some modern JS
    framework, there is a ton of ugly logic like this just to make it work.
    """

    repetition_unit = ModelChoiceField(
        queryset=RepetitionUnit.objects.all(),
        label=_('Unit'),
        required=False,
    )
    weight_unit = ModelChoiceField(
        queryset=WeightUnit.objects.all(),
        label=_('Unit'),
        required=False,
    )
    exercise_base = ModelChoiceField(
        queryset=ExerciseBase.objects.all(),
        label=_('Exercise'),
        required=False,
    )
    reps = IntegerField(
        label=_('Repetitions'),
        required=False,
    )
    weight = DecimalField(
        label=_('Weight'),
        initial=0,
        required=False,
    )
    rir = ChoiceField(
        label=_('RiR'),
        choices=RIR_OPTIONS,
        required=False,
    )

    class Meta:
        model = WorkoutLog
        exclude = ('workout',)


class WorkoutLogFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
            'id',
            Row(
                Column('reps', css_class='col-2'),
                Column('repetition_unit', css_class='col-3'),
                Column('weight', css_class='col-2'),
                Column('weight_unit', css_class='col-3'),
                Column('rir', css_class='col-2'),
                css_class='form-row',
            ),
        )
        self.form_show_labels = False
        self.form_tag = False
        self.disable_csrf = True
        self.render_required_fields = True


class HelperWorkoutSessionForm(ModelForm):
    """
    A helper form used in the workout log view
    """

    class Meta:
        model = WorkoutSession
        exclude = ('user', 'workout')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('date', css_class='col-6'),
                Column('impression', css_class='col-6'),
                css_class='form-row',
            ),
            'notes',
            Row(
                Column('time_start', css_class='col-6'),
                Column('time_end', css_class='col-6'),
                css_class='form-row',
            ),
        )
        self.helper.form_tag = False


class WorkoutSessionForm(ModelForm):
    """
    Workout Session form
    """

    class Meta:
        model = WorkoutSession
        exclude = ('user', 'workout', 'date')

    def __init__(self, *args, **kwargs):
        super(WorkoutSessionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'impression',
            'notes',
            Row(
                Column('time_start', css_class='col-6'),
                Column('time_end', css_class='col-6'),
                css_class='form-row',
            ),
        )


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
