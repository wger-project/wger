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
import logging

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as django_login
from django.contrib.auth.decorators import login_required
from django.core import mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import (
    reverse,
    reverse_lazy,
)
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django.views.generic.edit import FormView

# Third Party
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

# wger
from wger.core.demo import (
    create_demo_entries,
    create_temporary_user,
)
from wger.core.forms import (
    FeedbackAnonymousForm,
    FeedbackRegisteredForm,
)
from wger.core.models import DaysOfWeek
from wger.manager.models import Schedule


logger = logging.getLogger(__name__)


# ************************
# Misc functions
# ************************
def index(request):
    """
    Index page
    """
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('core:dashboard'))
    else:
        return HttpResponseRedirect(reverse('software:features'))


def demo_entries(request):
    """
    Creates a set of sample entries for guest users
    """
    if not settings.WGER_SETTINGS['ALLOW_GUEST_USERS']:
        return HttpResponseRedirect(reverse('software:features'))

    if (
        not request.user.is_authenticated or request.user.userprofile.is_temporary
    ) and not request.session['has_demo_data']:
        # If we reach this from a page that has no user created by the
        # middleware, do that now
        if not request.user.is_authenticated:
            user = create_temporary_user(request)
            django_login(request, user)

        # OK, continue
        create_demo_entries(request.user)
        request.session['has_demo_data'] = True
        messages.success(
            request,
            _(
                'We have created sample workout, workout schedules, weight '
                'logs, (body) weight and nutrition plan entries so you can '
                'better see what  this site can do. Feel free to edit or '
                'delete them!'
            ),
        )
    return HttpResponseRedirect(reverse('core:dashboard'))


@login_required
def dashboard(request):
    """
    Show the index page, in our case, the last workout and nutritional plan
    and the current weight
    """
    return render(request, 'index.html')


class FeedbackClass(FormView):
    template_name = 'form.html'
    success_url = reverse_lazy('software:about-us')

    def get_initial(self):
        """
        Fill in the contact, if available
        """
        if self.request.user.is_authenticated:
            return {'contact': self.request.user.email}
        return {}

    def get_context_data(self, **kwargs):
        """
        Set necessary template data to correctly render the form
        """
        context = super(FeedbackClass, self).get_context_data(**kwargs)
        context['title'] = _('Feedback')
        return context

    def get_form_class(self):
        """
        Load the correct feedback form depending on the user
        (either with reCaptcha field or not)
        """
        if self.request.user.is_anonymous or self.request.user.userprofile.is_temporary:
            return FeedbackAnonymousForm
        else:
            return FeedbackRegisteredForm

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""

        form = super(FeedbackClass, self).get_form(form_class)
        form.helper = FormHelper()
        form.helper.form_id = slugify(self.request.path)
        form.helper.add_input(Submit('submit', _('Submit'), css_class='btn-success btn-block'))
        form.helper.form_class = 'wger-form'
        return form

    def form_valid(self, form):
        """
        Send the feedback to the administrators
        """
        messages.success(self.request, _('Your feedback was successfully sent. Thank you!'))

        context = {'user': self.request.user, 'form_data': form.cleaned_data}
        subject = 'New feedback'
        message = render_to_string('user/email_feedback.html', context)
        mail.mail_admins(subject, message)

        return super(FeedbackClass, self).form_valid(form)
