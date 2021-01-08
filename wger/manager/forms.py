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
    widgets
)
from django.utils.translation import (
    ugettext as _,
    ugettext_lazy
)

# Third Party
from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Column,
    Layout,
    Row,
    Submit
)

# wger
from wger.core.models import (
    RepetitionUnit,
    WeightUnit
)
from wger.exercises.models import Exercise
from wger.manager.models import (
    RIR_OPTIONS,
    Day,
    Set,
    Setting,
    Workout,
    WorkoutLog,
    WorkoutSession
)
from wger.utils.widgets import (
    ExerciseAjaxSelect,
    TranslatedSelectMultiple
)


class DemoUserForm(Form):
    captcha = ReCaptchaField(label=_('Confirmation text'),
                             help_text=_('As a security measure, please enter the previous words'),)


class WorkoutForm(ModelForm):
    class Meta:
        model = Workout
        exclude = ('user',)


class WorkoutCopyForm(Form):
    comment = CharField(max_length=100,
                        help_text=_('The goal or description of the new workout.'),
                        required=False)


class DayForm(ModelForm):
    class Meta:
        model = Day
        exclude = ('training',)
        widgets = {'day': TranslatedSelectMultiple()}


class SetForm(ModelForm):
    class Meta:
        model = Set
        exclude = ('order', 'exerciseday')
        widgets = {'exercises': ExerciseAjaxSelect(), }

    # We need to overwrite the init method here because otherwise Django
    # will output a default help text, regardless of the widget used
    # https://code.djangoproject.com/ticket/9321
    def __init__(self, *args, **kwargs):
        super(SetForm, self).__init__(*args, **kwargs)
        self.fields['exercises'].help_text = _('You can search for more than one exercise, '
                                               'they will be grouped together for a superset.')


class SettingForm(ModelForm):
    class Meta:
        model = Setting
        exclude = ('set', 'exercise', 'order', 'comment')


class WorkoutLogForm(ModelForm):
    """
    Helper form for a WorkoutLog.

    These fields are re-defined here only to make them optional. Otherwise
    all the entries in the formset would be required, which is not really what
    we want. This form is one prime candidate to rework with some modern JS
    framework, there is a ton of ugly logic like this just to make it work.
    """
    repetition_unit = ModelChoiceField(queryset=RepetitionUnit.objects.all(),
                                       label=_('Unit'),
                                       required=False)
    weight_unit = ModelChoiceField(queryset=WeightUnit.objects.all(),
                                   label=_('Unit'),
                                   required=False)
    exercise = ModelChoiceField(queryset=Exercise.objects.all(),
                                label=_('Exercise'),
                                required=False)
    reps = IntegerField(label=_('Repetitions'),
                        required=False)
    weight = DecimalField(label=_('Weight'),
                          initial=0,
                          required=False)
    rir = ChoiceField(label=_('RiR'),
                      choices=RIR_OPTIONS,
                      required=False)

    class Meta:
        model = WorkoutLog
        exclude = ('workout', )


class WorkoutLogFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
            Row(
                Column('reps', css_class='form-group col-2 mb-0'),
                Column('repetition_unit', css_class='form-group col-3 mb-0'),
                Column('weight', css_class='form-group col-2 mb-0'),
                Column('weight_unit', css_class='form-group col-3 mb-0'),
                Column('rir', css_class='form-group col-2 mb-0'),
                css_class='form-row'
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
                Column('date', css_class='form-group col-6 mb-0'),
                Column('impression', css_class='form-group col-6 mb-0'),
                css_class='form-row'
            ),
            'notes',
            Row(
                Column('time_start', css_class='form-group col-6 mb-0'),
                Column('time_end', css_class='form-group col-6 mb-0'),
                css_class='form-row'
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
                Column('time_start', css_class='form-group col-6 mb-0'),
                Column('time_end', css_class='form-group col-6 mb-0'),
                css_class='form-row'
            ),
        )


class WorkoutScheduleDownloadForm(Form):
    """
    Form for the workout schedule download
    """
    pdf_type = ChoiceField(
        label=ugettext_lazy("Type"),
        choices=(("log", ugettext_lazy("Log")),
                 ("table", ugettext_lazy("Table")))
    )
    images = BooleanField(label=ugettext_lazy("with images"),
                          required=False)
    comments = BooleanField(label=ugettext_lazy("with comments"),
                            required=False)

    def __init__(self):
        super(WorkoutScheduleDownloadForm, self).__init__()
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _("Download"),
                                     css_class='btn-success btn-block',
                                     css_id="download-pdf-button-schedule"))


class WorkoutSessionHiddenFieldsForm(ModelForm):
    """
    Workout Session form used in the timer view
    """
    class Meta:
        model = WorkoutSession
        exclude = []
        widgets = {'time_start': widgets.HiddenInput(),
                   'time_end': widgets.HiddenInput(),
                   'user': widgets.HiddenInput(),
                   'notes': widgets.Textarea(attrs={'rows': 3})}
