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
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

# Third Party
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

# wger
from wger.core.forms import UserPersonalInformationForm
from wger.utils.widgets import BootstrapSelectMultiple


class GymUserPermissionForm(forms.ModelForm):
    """
    Form used to set the permission group of a gym member
    """

    USER = 'user'
    GYM_ADMIN = 'admin'
    TRAINER = 'trainer'
    MANAGER = 'manager'

    # Empty default roles, they are always set at run time
    ROLES = ()

    class Meta:
        model = User
        fields = ('role',)

    role = forms.MultipleChoiceField(choices=ROLES, initial=USER)

    def __init__(self, available_roles=None, *args, **kwargs):
        """
        Custom logic to reduce the available permissions
        """
        super(GymUserPermissionForm, self).__init__(*args, **kwargs)

        if available_roles is None:
            available_roles = []
        field_choices = [(self.USER, _('User'))]
        if 'trainer' in available_roles:
            field_choices.append((self.TRAINER, _('Trainer')))
        if 'admin' in available_roles:
            field_choices.append((self.GYM_ADMIN, _('Gym administrator')))
        if 'manager' in available_roles:
            field_choices.append((self.MANAGER, _('General manager')))

        self.fields['role'] = forms.MultipleChoiceField(
            choices=field_choices,
            initial=User,
            widget=BootstrapSelectMultiple(),
        )
        self.helper = FormHelper()
        self.helper.form_class = 'wger-form'
        self.helper.add_input(Submit('submit', _('Save'), css_class='btn-success btn-block'))


class GymUserAddForm(GymUserPermissionForm, UserPersonalInformationForm):
    """
    Form used when adding a user to a gym
    """

    birthdate = forms.DateField(required=False)

    class Meta:
        model = User
        widgets = {'role': BootstrapSelectMultiple()}
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'role',
        )

    username = forms.RegexField(
        label=_('Username'),
        max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_('Required. 30 characters or fewer. Letters, digits and ' '@/./+/-/_ only.'),
        error_messages={
            'invalid': _('This value may contain only letters, numbers and ' '@/.//-/_ characters.')
        },
    )

    def clean_username(self):
        """
        Since User.username is unique, this check is redundant,
        but it sets a nicer error message than the ORM. See #13147.
        """
        username = self.cleaned_data['username']
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_('A user with that username already exists.'))
