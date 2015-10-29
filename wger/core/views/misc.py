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

import logging

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
from django.core import mail
from django.utils.translation import ugettext as _
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as django_login
from django.template.loader import render_to_string


from wger.core.forms import FeedbackRegisteredForm, FeedbackAnonymousForm
from wger.core.demo import create_demo_entries, create_temporary_user
from wger.core.models import DaysOfWeek
from wger.manager.models import Schedule
from wger.nutrition.models import NutritionPlan
from wger.weight.models import WeightEntry


logger = logging.getLogger(__name__)


# ************************
# Misc functions
# ************************
def index(request):
    '''
    Index page
    '''
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('core:dashboard'))
    else:
        return HttpResponseRedirect(reverse('software:features'))


def demo_entries(request):
    '''
    Creates a set of sample entries for guest users
    '''
    if (((not request.user.is_authenticated() or request.user.userprofile.is_temporary)
         and not request.session['has_demo_data'])):
        # If we reach this from a page that has no user created by the
        # middleware, do that now
        if not request.user.is_authenticated():
            user = create_temporary_user()
            django_login(request, user)

        # OK, continue
        create_demo_entries(request.user)
        request.session['has_demo_data'] = True
        messages.success(request, _('We have created sample workout, workout schedules, weight '
                                    'logs, (body) weight and nutrition plan entries so you can '
                                    'better see what  this site can do. Feel free to edit or '
                                    'delete them!'))
    return HttpResponseRedirect(reverse('core:dashboard'))


@login_required
def dashboard(request):
    '''
    Show the index page, in our case, the last workout and nutritional plan
    and the current weight
    '''

    template_data = {}

    # Load the last workout, either from a schedule or a 'regular' one
    (current_workout, schedule) = Schedule.objects.get_current_workout(request.user)

    template_data['current_workout'] = current_workout
    template_data['schedule'] = schedule

    # Load the last nutritional plan, if one exists
    try:
        plan = NutritionPlan.objects.filter(user=request.user).latest('creation_date')
    except ObjectDoesNotExist:
        plan = False
    template_data['plan'] = plan

    # Load the last logged weight entry, if one exists
    try:
        weight = WeightEntry.objects.filter(user=request.user).latest('date')
    except ObjectDoesNotExist:
        weight = False
    template_data['weight'] = weight

    if current_workout:
        # Format a bit the days so it doesn't have to be done in the template
        used_days = {}
        for day in current_workout.day_set.select_related():
            for day_of_week in day.day.select_related():
                used_days[day_of_week.id] = day.description

        week_day_result = []
        for week in DaysOfWeek.objects.all():
            day_has_workout = False

            if week.id in used_days:
                day_has_workout = True
                week_day_result.append((_(week.day_of_week), used_days[week.id], True))

            if not day_has_workout:
                week_day_result.append((_(week.day_of_week), _('Rest day'), False))

        template_data['weekdays'] = week_day_result

    if plan:

        # Load the nutritional info
        template_data['nutritional_info'] = plan.get_nutritional_values()

    return render(request, 'index.html', template_data)


class ContactClassView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(ContactClassView, self).get_context_data(**kwargs)
        context.update({'contribute': reverse('software:contribute'),
                        'issues': reverse('software:issues'),
                        'feedback': reverse('core:feedback')})
        return context


class FeedbackClass(FormView):
    template_name = 'form.html'
    success_url = reverse_lazy('core:contact')

    def get_initial(self):
        '''
        Fill in the contact, if available
        '''
        if self.request.user.is_authenticated():
            return {'contact': self.request.user.email}
        return {}

    def get_context_data(self, **kwargs):
        '''
        Set necessary template data to correctly render the form
        '''
        context = super(FeedbackClass, self).get_context_data(**kwargs)
        context['title'] = _('Feedback')
        context['form_fields'] = kwargs['form']
        context['form_action'] = reverse('core:feedback')
        context['submit_text'] = _('Send')
        context['contribute_url'] = reverse('software:contribute')
        context['extend_template'] = 'base_empty.html' if self.request.is_ajax() else 'base.html'
        return context

    def get_form_class(self):
        '''
        Load the correct feedback form depending on the user
        (either with reCaptcha field or not)
        '''
        if self.request.user.is_anonymous() or self.request.user.userprofile.is_temporary:
            return FeedbackAnonymousForm
        else:
            return FeedbackRegisteredForm

    def form_valid(self, form):
        '''
        Send the feedback to the administrators
        '''
        messages.success(self.request, _('Your feedback was successfully sent. Thank you!'))

        context = {}
        context['user'] = self.request.user
        context['form_data'] = form.cleaned_data

        subject = 'New feedback'
        message = render_to_string('user/email_feedback.html', context)
        mail.mail_admins(subject, message)

        return super(FeedbackClass, self).form_valid(form)
