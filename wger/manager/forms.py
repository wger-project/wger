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

'''
This file contains forms used in the application
'''

from django.forms import Form
from django.forms import ModelForm
from django.forms import EmailField
from django.forms import DateField
from django.forms import CharField
from django.forms import DecimalField
from django.forms import ValidationError
from django.forms import widgets

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User as Django_User

from django.utils.translation import ugettext as _

from captcha.fields import ReCaptchaField

from wger.manager.models import UserProfile
from wger.manager.models import Workout
from wger.manager.models import Day
from wger.manager.models import Set
from wger.manager.models import WorkoutLog

from wger.utils.widgets import TranslatedSelectMultiple
from wger.utils.widgets import ExerciseAjaxSelect
from wger.utils.constants import DATE_FORMATS
from wger.utils.widgets import Html5DateInput
from wger.utils.widgets import Html5NumberInput


class UserPreferencesForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('show_comments',
                  'show_english_ingredients',
                  'workout_reminder_active',
                  'workout_reminder',
                  'workout_duration',
                  'notification_language')


class UserEmailForm(ModelForm):
    email = EmailField(label=_("Email"),
                       help_text=_("Only needed to reset your password in case you forget it."),
                       required=False)

    class Meta:
        model = Django_User
        fields = ('email', )

    def clean_email(self):
        # Email must be unique systemwide
        email = self.cleaned_data["email"]
        if not email:
            return email
        try:
            Django_User.objects.get(email=email)
        except Django_User.DoesNotExist:
            return email
        raise ValidationError(_("This email is already used."))


class RegistrationForm(UserCreationForm, UserEmailForm):
    captcha = ReCaptchaField(attrs={'theme': 'clean'},
                             label=_('Confirmation text'),
                             help_text=_('As a security measure, please enter the previous words'),)


class DemoUserForm(Form):
    captcha = ReCaptchaField(attrs={'theme': 'clean'},
                             label=_('Confirmation text'),
                             help_text=_('As a security measure, please enter the previous words'),)


class WorkoutForm(ModelForm):
    class Meta:
        model = Workout
        exclude = ('user',)


class WorkoutCopyForm(Form):
    comment = CharField(max_length=100,
                        help_text=_('The goal or description of the new workout.'),
                        required=False)


class FeedbackRegisteredForm(Form):
    '''
    Feedback form used for logged in users
    '''
    comment = CharField(max_length=500,
                        min_length=10,
                        widget=widgets.Textarea,
                        help_text=_('What do you want to say?'),
                        required=True)


class FeedbackAnonymousForm(FeedbackRegisteredForm):
    '''
    Feedback form used for anonymous users (has additionally a reCaptcha field)
    '''
    captcha = ReCaptchaField(attrs={'theme': 'clean'},
                             label=_('Confirmation text'),
                             help_text=_('As a security measure, please enter the previous words'),)


class DayForm(ModelForm):
    class Meta:
        model = Day

        widgets = {'day': TranslatedSelectMultiple()}


class SetForm(ModelForm):
    class Meta:
        model = Set
        widgets = {'exercises': ExerciseAjaxSelect(), }

    # We need to overwrite the init method here because otherwise Django
    # will outut a default help text, regardless of the widget used
    # https://code.djangoproject.com/ticket/9321
    def __init__(self, *args, **kwargs):
        super(SetForm, self).__init__(*args, **kwargs)
        self.fields['exercises'].help_text = _('You can search for more than one exercise, '
                                               'they will be grouped together for a superset.')

from wger.exercises.models import Exercise
from django.forms import ModelChoiceField


class SetFormMobile(ModelForm):
    '''
    Don't use the autocompleter when accessing the mobile version
    '''
    exercise_list = ModelChoiceField(Exercise.objects)

    class Meta:
        model = Set

    # We need to overwrite the init method here because otherwise Django
    # will outut a default help text, regardless of the widget used
    # https://code.djangoproject.com/ticket/9321
    def __init__(self, *args, **kwargs):
        super(SetFormMobile, self).__init__(*args, **kwargs)
        self.fields['exercises'].help_text = _('You can search for more than one exercise, '
                                               'they will be grouped together for a superset.')


class HelperDateForm(Form):
    '''
    A helper form with only a date input
    '''
    date = DateField(input_formats=DATE_FORMATS, widget=Html5DateInput())


class WorkoutLogForm(ModelForm):
    '''
    Helper form for a WorkoutLog.

    The field for the weight is overwritten here, activating localization (so a
    German user can  use ',' as the separator)
    '''
    weight = DecimalField(decimal_places=2,
                          max_digits=5,
                          localize=True,
                          widget=Html5NumberInput())

    class Meta:
        model = WorkoutLog
        exclude = ('exercise', )
