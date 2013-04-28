# -*- coding: utf-8 -*-

# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

import logging


from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.core import mail
from django.utils.translation import ugettext as _
from django.views.generic.edit import FormView
from django.views.generic import TemplateView

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as django_login

from wger.manager import forms
from wger.manager.demo import create_demo_entries
from wger.manager.demo import create_temporary_user

from wger.manager.models import DaysOfWeek
from wger.manager.models import Workout
from wger.manager.models import Schedule

from wger.nutrition.models import NutritionPlan

from wger.weight.models import WeightEntry


logger = logging.getLogger('workout_manager.custom')


# ************************
# Misc functions
# ************************
def index(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        return HttpResponseRedirect(reverse('software:features'))


def demo_entries(request):
    '''
    Creates a set of sample entries for guest users
    '''
    if (((not request.user.is_authenticated() or request.user.get_profile().is_temporary)
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
    return HttpResponseRedirect(reverse('dashboard'))


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
        weight = WeightEntry.objects.filter(user=request.user).latest('creation_date')
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

    return render_to_response('index.html',
                              template_data,
                              context_instance=RequestContext(request))


class ContactClassView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(ContactClassView, self).get_context_data(**kwargs)
        context.update({'contribute': reverse('software:contribute'),
                        'issues': reverse('software:issues'),
                        'feedback': reverse('feedback')})
        return context


class FeedbackClass(FormView):
    template_name = 'form.html'
    success_url = reverse_lazy('contact')

    def get_context_data(self, **kwargs):
        '''
        Set necessary template data to correctly render the form
        '''
        context = super(FeedbackClass, self).get_context_data(**kwargs)
        context['title'] = _('Feedback')
        context['form_fields'] = kwargs['form']
        context['form_action'] = reverse('feedback')
        context['submit_text'] = _('Send')
        context['sidebar'] = 'misc/feedback.html'
        context['contribute_url'] = reverse('software:contribute')
        return context

    def get_form_class(self):
        '''
        Load the correct feedback form depending on the user
        (either with reCaptcha field or not)
        '''
        if self.request.user.get_profile().is_temporary:
            return forms.FeedbackAnonymousForm
        else:
            return forms.FeedbackRegisteredForm

    def form_valid(self, form):
        '''
        Send an email to the
        '''
        messages.success(self.request, _('Your feedback was sucessfully sent. Thank you!'))
        message = "Feedback posted by an anonymous user"
        if self.request.user.is_authenticated():
            message = "Feedback posted by {0}".format(self.request.user.username)

        message += ("\n"
                    "Message follows:\n"
                    "----------------\n\n{0}".format(form.cleaned_data['comment']))
        mail.mail_admins(_('New feedback'), message)
        return super(FeedbackClass, self).form_valid(form)
