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
import datetime

from django.shortcuts import render, get_object_or_404
from django.http import (
    HttpResponseRedirect,
    HttpResponseForbidden,
    HttpResponse
)
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.translation import ugettext_lazy, ugettext as _
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    CreateView,
    DeleteView,
    UpdateView
)

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from wger.manager.models import Schedule
from wger.manager.helpers import render_workout_day
from wger.utils.generic_views import (
    WgerFormMixin,
    WgerDeleteMixin
)
from wger.utils.helpers import make_token, check_token
from wger.utils.pdf import styleSheet, render_footer


logger = logging.getLogger(__name__)


@login_required
def overview(request):
    '''
    An overview of all the user's schedules
    '''

    template_data = {}
    template_data['schedules'] = (Schedule.objects
                                  .filter(user=request.user)
                                  .order_by('-is_active', '-start_date'))
    return render(request, 'schedule/overview.html', template_data)


def view(request, pk):
    '''
    Show the workout schedule
    '''
    template_data = {}
    schedule = get_object_or_404(Schedule, pk=pk)
    user = schedule.user
    is_owner = request.user == user

    if not is_owner and not user.userprofile.ro_access:
        return HttpResponseForbidden()

    uid, token = make_token(user)

    template_data['schedule'] = schedule
    if schedule.is_active:
        template_data['active_workout'] = schedule.get_current_scheduled_workout()
    else:
        template_data['active_workout'] = False

    schedule.get_current_scheduled_workout()

    template_data['uid'] = uid
    template_data['token'] = token
    template_data['is_owner'] = is_owner
    template_data['owner_user'] = user
    template_data['show_shariff'] = is_owner

    return render(request, 'schedule/view.html', template_data)


def export_pdf_log(request, pk, images=False, comments=False, uidb64=None, token=None):
    '''
    Show the workout schedule
    '''
    user = request.user

    comments = bool(int(comments))
    images = bool(int(images))

    # Load the workout
    if uidb64 is not None and token is not None:
        if check_token(uidb64, token):
            schedule = get_object_or_404(Schedule, pk=pk)
        else:
            return HttpResponseForbidden()
    else:
        if request.user.is_anonymous():
            return HttpResponseForbidden()
        schedule = get_object_or_404(Schedule, pk=pk, user=user)

    # Create the HttpResponse object with the appropriate PDF headers.
    # and use it to the create the PDF using it as a file like object
    response = HttpResponse(content_type='application/pdf')
    doc = SimpleDocTemplate(response,
                            pagesize=A4,
                            leftMargin=cm,
                            rightMargin=cm,
                            topMargin=0.5 * cm,
                            bottomMargin=0.5 * cm,
                            title=_('Workout'),
                            author='wger Workout Manager',
                            subject='Schedule for {0}'.format(request.user.username))

    # container for the 'Flowable' objects
    elements = []

    # Set the title
    p = Paragraph(u'<para align="center">{0}</para>'.format(schedule), styleSheet["HeaderBold"])
    elements.append(p)
    elements.append(Spacer(10 * cm, 0.5 * cm))

    # Iterate through the Workout and render the training days
    for step in schedule.schedulestep_set.all():
        p = Paragraph(u'<para>{0} {1}</para>'.format(step.duration, _('Weeks')),
                      styleSheet["HeaderBold"])
        elements.append(p)
        elements.append(Spacer(10 * cm, 0.5 * cm))

        for day in step.workout.canonical_representation['day_list']:
            elements.append(
                render_workout_day(day, images=images, comments=comments, nr_of_weeks=7))
            elements.append(Spacer(10 * cm, 0.5 * cm))

    # Footer, date and info
    elements.append(Spacer(10 * cm, 0.5 * cm))
    url = reverse('manager:schedule:view', kwargs={'pk': schedule.id})
    elements.append(render_footer(request.build_absolute_uri(url)))

    # write the document and send the response to the browser
    doc.build(elements)
    response['Content-Disposition'] = 'attachment; filename=Schedule-{0}-log.pdf'.format(pk)
    response['Content-Length'] = len(response.content)
    return response


def export_pdf_table(request, pk, images=False, comments=False, uidb64=None, token=None):
    '''
    Show the workout schedule
    '''
    user = request.user

    comments = bool(int(comments))
    images = bool(int(images))

    # Load the workout
    if uidb64 is not None and token is not None:
        if check_token(uidb64, token):
            schedule = get_object_or_404(Schedule, pk=pk)
        else:
            return HttpResponseForbidden()
    else:
        if request.user.is_anonymous():
            return HttpResponseForbidden()
        schedule = get_object_or_404(Schedule, pk=pk, user=user)

    # Create the HttpResponse object with the appropriate PDF headers.
    # and use it to the create the PDF using it as a file like object
    response = HttpResponse(content_type='application/pdf')
    doc = SimpleDocTemplate(response,
                            pagesize=A4,
                            leftMargin=cm,
                            rightMargin=cm,
                            topMargin=0.5 * cm,
                            bottomMargin=0.5 * cm,
                            title=_('Workout'),
                            author='wger Workout Manager',
                            subject='Schedule for {0}'.format(request.user.username))

    # container for the 'Flowable' objects
    elements = []

    # Set the title
    p = Paragraph(u'<para align="center">{0}</para>'.format(schedule), styleSheet["HeaderBold"])
    elements.append(p)
    elements.append(Spacer(10 * cm, 0.5 * cm))

    # Iterate through the Workout and render the training days
    for step in schedule.schedulestep_set.all():
        p = Paragraph(u'<para>{0} {1}</para>'.format(step.duration, _('Weeks')),
                      styleSheet["HeaderBold"])
        elements.append(p)
        elements.append(Spacer(10 * cm, 0.5 * cm))

        for day in step.workout.canonical_representation['day_list']:
            elements.append(
                render_workout_day(day, images=images, comments=comments, nr_of_weeks=7,
                                   only_table=True))
            elements.append(Spacer(10 * cm, 0.5 * cm))

    # Footer, date and info
    elements.append(Spacer(10 * cm, 0.5 * cm))
    url = reverse('manager:schedule:view', kwargs={'pk': schedule.id})
    elements.append(render_footer(request.build_absolute_uri(url)))

    # write the document and send the response to the browser
    doc.build(elements)
    response['Content-Disposition'] = 'attachment; filename=Schedule-{0}-table.pdf'.format(pk)
    response['Content-Length'] = len(response.content)
    return response


@login_required
def start(request, pk):
    '''
    Starts a schedule

    This simply sets the start date to today and the schedule is marked as
    being active.
    '''

    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    schedule.is_active = True
    schedule.start_date = datetime.date.today()
    schedule.save()
    return HttpResponseRedirect(reverse('manager:schedule:view', kwargs={'pk': schedule.id}))


class ScheduleCreateView(WgerFormMixin, CreateView, PermissionRequiredMixin):
    '''
    Creates a new workout schedule
    '''

    model = Schedule
    fields = '__all__'
    success_url = reverse_lazy('manager:schedule:overview')
    title = ugettext_lazy('Create schedule')
    form_action = reverse_lazy('manager:schedule:add')

    def form_valid(self, form):
        '''set the submitter'''
        form.instance.user = self.request.user
        return super(ScheduleCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('manager:schedule:view', kwargs={'pk': self.object.id})


class ScheduleDeleteView(WgerDeleteMixin, DeleteView, PermissionRequiredMixin):
    '''
    Generic view to delete a schedule
    '''

    model = Schedule
    fields = ('name', 'start_date', 'is_active', 'is_loop')
    success_url = reverse_lazy('manager:schedule:overview')
    form_action_urlname = 'manager:schedule:delete'
    messages = ugettext_lazy('Successfully deleted')

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(ScheduleDeleteView, self).get_context_data(**kwargs)
        context['title'] = _(u'Delete {0}?').format(self.object)
        return context


class ScheduleEditView(WgerFormMixin, UpdateView, PermissionRequiredMixin):
    '''
    Generic view to update an existing workout routine
    '''

    model = Schedule
    fields = '__all__'
    form_action_urlname = 'manager:schedule:edit'

    def get_context_data(self, **kwargs):
        '''
        Send some additional data to the template
        '''
        context = super(ScheduleEditView, self).get_context_data(**kwargs)
        context['title'] = _(u'Edit {0}').format(self.object)
        return context
