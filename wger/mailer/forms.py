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
    CharField,
    Form,
    Textarea,
)
from django.utils.translation import pgettext

# Third Party
from crispy_forms.helper import FormHelper


class EmailListForm(Form):
    """
    Small form to send emails
    """

    subject = CharField(label=pgettext('As in "email subject"', 'Subject'))
    body = CharField(widget=Textarea, label=pgettext('As in "content of an email"', 'Content'))

    def __init__(self, *args, **kwargs):
        super(EmailListForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
