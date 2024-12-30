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

# Standard Library
from datetime import date

# Django
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
)
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import (
    CharField,
    EmailField,
    Form,
    PasswordInput,
    widgets,
)
from django.utils.translation import gettext as _

# Third Party
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    HTML,
    ButtonHolder,
    Column,
    Fieldset,
    Layout,
    Row,
    Submit,
)
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

# wger
from wger.core.models import UserProfile


class UserLoginForm(AuthenticationForm):
    """
    Form for logins
    """

    authenticate_on_clean = True

    def __init__(self, authenticate_on_clean=True, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

        self.authenticate_on_clean = authenticate_on_clean

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Login'), css_class='btn-success btn-block'))
        self.helper.form_class = 'wger-form'
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='col-6'),
                Column('password', css_class='col-6'),
                css_class='form-row',
            )
        )

    def clean(self):
        """
        Note: this clean method needs to be able to toggle authenticating directly
        or not. This is needed because django axes expects an explicit request
        parameter and otherwise the login endpoint won't work

        See https://github.com/wger-project/wger/issues/1163
        """
        if self.authenticate_on_clean:
            self.authenticate(self.request)
        return self.cleaned_data

    def authenticate(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(
                request=request,
                username=username,
                password=password,
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)


class UserPreferencesForm(forms.ModelForm):
    first_name = forms.CharField(label=_('First name'), required=False)
    last_name = forms.CharField(label=_('Last name'), required=False)
    email = EmailField(
        label=_('Email'),
        help_text=_('Used for password resets and, optionally, e-mail reminders.'),
        required=False,
    )
    birthdate = forms.DateField(
        label=_('Date of Birth'),
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'max': str(date.today().replace(year=date.today().year - 10)),
                'min': str(date.today().replace(year=date.today().year - 100)),
            },
        ),
    )

    class Meta:
        model = UserProfile
        fields = (
            'show_comments',
            'show_english_ingredients',
            'workout_reminder_active',
            'workout_reminder',
            'workout_duration',
            'notification_language',
            'weight_unit',
            'ro_access',
            'num_days_weight_reminder',
            'birthdate',
            'height',
        )

    def __init__(self, *args, **kwargs):
        super(UserPreferencesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'wger-form'
        self.helper.layout = Layout(
            Fieldset(
                _('Personal data'),
                'email',
                Row(
                    Column('first_name', css_class='col-6'),
                    Column('last_name', css_class='col-6'),
                    css_class='form-row',
                ),
                'birthdate',
                'height',
                HTML('<hr>'),
            ),
            Fieldset(
                _('Workout reminders'),
                'workout_reminder_active',
                'workout_reminder',
                'workout_duration',
                HTML('<hr>'),
            ),
            Fieldset(
                _('Other settings'),
                'ro_access',
                'notification_language',
                'weight_unit',
                'show_comments',
                'show_english_ingredients',
                'num_days_weight_reminder',
            ),
            ButtonHolder(Submit('submit', _('Save'), css_class='btn-success btn-block')),
        )


class UserEmailForm(forms.ModelForm):
    email = EmailField(
        label=_('Email'),
        help_text=_('Used for password resets and, optionally, email reminders.'),
        required=False,
    )

    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        """
        E-mail must be unique system-wide

        However, this check should only be performed when the user changes
        e-mail address, otherwise the uniqueness check will because it will find one user
        (the current one) using the same e-mail. Only when the user changes it, do
        we want to check that nobody else has that e-mail address.
        """

        email = self.cleaned_data['email']
        if not email:
            return email
        try:
            # Performs a case-insensitive lookup
            user = User.objects.get(email__iexact=email)
            if user.email == self.instance.email:
                return email
        except User.DoesNotExist:
            return email

        raise ValidationError(_('This e-mail address is already in use.'))


class UserPersonalInformationForm(UserEmailForm):
    first_name = forms.CharField(label=_('First name'), required=False)
    last_name = forms.CharField(label=_('Last name'), required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class PasswordConfirmationForm(Form):
    """
    A simple password confirmation form.

    This can be used to make sure the user really wants to perform a dangerous
    action. The form must be initialised with a user object.
    """

    password = CharField(
        label=_('Password'),
        widget=PasswordInput,
        help_text=_('Please enter your current password.'),
    )

    def __init__(self, user, data=None):
        self.user = user
        super(PasswordConfirmationForm, self).__init__(data=data)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'password',
            ButtonHolder(Submit('submit', _('Delete'), css_class='btn-danger btn-block')),
        )

    def clean_password(self):
        """
        Check that the password supplied matches the one for the user
        """
        password = self.cleaned_data.get('password', None)
        if not self.user.check_password(password):
            raise ValidationError(_('Invalid password'))
        return self.cleaned_data.get('password')


class RegistrationForm(UserCreationForm, UserEmailForm):
    """
    Registration form with reCAPTCHA field
    """

    captcha = ReCaptchaField(
        widget=ReCaptchaV3,
        label='reCaptcha',
        help_text=_('The form is secured with reCAPTCHA'),
    )

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'wger-form'
        self.helper.layout = Layout(
            'username',
            'email',
            Row(
                Column('password1', css_class='col-md-6 col-12'),
                Column('password2', css_class='col-md-6 col-12'),
                css_class='form-row',
            ),
            'captcha',
            ButtonHolder(Submit('submitBtn', _('Register'), css_class='btn-success btn-block')),
        )


class RegistrationFormNoCaptcha(UserCreationForm, UserEmailForm):
    """
    Registration form without CAPTCHA field
    """

    def __init__(self, *args, **kwargs):
        super(RegistrationFormNoCaptcha, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'wger-form'
        self.helper.layout = Layout(
            'username',
            'email',
            Row(
                Column('password1', css_class='col-md-6 col-12'),
                Column('password2', css_class='col-md-6 col-12'),
                css_class='form-row',
            ),
            ButtonHolder(
                Submit('submit', _('Register'), css_class='btn-success col-sm-6 col-12'),
                css_class='text-center',
            ),
        )


class FeedbackRegisteredForm(forms.Form):
    """
    Feedback form used for logged-in users
    """

    contact = forms.CharField(
        max_length=50,
        min_length=10,
        label=_('Contact'),
        help_text=_('Some way of answering you (e-mail, etc.)'),
        required=False,
    )

    comment = forms.CharField(
        max_length=500,
        min_length=10,
        widget=widgets.Textarea,
        label=_('Comment'),
        help_text=_('What do you want to say?'),
        required=True,
    )


class FeedbackAnonymousForm(FeedbackRegisteredForm):
    """
    Feedback form used for anonymous users (has additionally a reCAPTCHA field)
    """

    captcha = ReCaptchaField(
        widget=ReCaptchaV3,
        label='reCaptcha',
        help_text=_('The form is secured with reCAPTCHA'),
    )
