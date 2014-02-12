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

from captcha.fields import ReCaptchaField
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User as Django_User
from django.core.exceptions import ValidationError
from django.forms import ModelForm, EmailField, Form, CharField, widgets
from django.utils.translation import ugettext as _
from wger.core.models import UserProfile


class UserPreferencesForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('show_comments',
                  'show_english_ingredients',
                  'workout_reminder_active',
                  'workout_reminder',
                  'workout_duration',
                  'notification_language',
                  'timer_active',
                  'timer_pause')


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
    '''
    Registration form
    '''
    captcha = ReCaptchaField(attrs={'theme': 'clean'},
                             label=_('Confirmation text'),
                             help_text=_('As a security measure, please enter the previous words'),)


class RegistrationFormNoCaptcha(UserCreationForm, UserEmailForm):
    '''
    Registration form without captcha field

    This is used when registering through an app, in that case there is not
    such a spam danger and simplifies the registration process on a mobile
    device.
    '''
    pass


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
