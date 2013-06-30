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
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from django.contrib.auth.decorators import login_required

from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import UpdateView

from wger.manager.models import Schedule
from wger.manager.models import ScheduleStep
from wger.manager.models import Workout

from wger.manager.forms import WorkoutForm
from wger.manager.forms import WorkoutCopyForm


from wger.utils.generic_views import YamlFormMixin
from wger.utils.generic_views import YamlDeleteMixin


logger = logging.getLogger('workout_manager.custom')


@login_required
def overview(request):
    '''
    An overview of all the user's schedules
    '''

    template_data = {}
    template_data['schedules'] = (Schedule.objects
                                  .filter(user=request.user)
                                  .order_by('-is_active', '-start_date'))
    return render_to_response('schedule/overview.html',
                              template_data,
                              context_instance=RequestContext(request))


@login_required
def view(request, pk):
    '''
    Show the workout schedule
    '''
    template_data = {}

    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)
    template_data['schedule'] = schedule
    if schedule.is_active:
        template_data['active_workout'] = schedule.get_current_scheduled_workout()
    else:
        template_data['active_workout'] = False

    schedule.get_current_scheduled_workout()

    return render_to_response('schedule/view.html',
                              template_data,
                              context_instance=RequestContext(request))


class ScheduleCreateView(YamlFormMixin, CreateView):
    '''
    Creates a new workout schedule
    '''

    model = Schedule
    success_url = reverse_lazy('schedule-overview')
    title = ugettext_lazy('Create schedule')
    form_action = reverse_lazy('schedule-add')

    def form_valid(self, form):
        '''set the submitter'''
        form.instance.user = self.request.user
        return super(ScheduleCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('schedule-view', kwargs={'pk': self.object.id})


class ScheduleDeleteView(YamlDeleteMixin, DeleteView):
    '''
    Generic view to delete a schedule
    '''

    model = Schedule
    success_url = reverse_lazy('schedule-overview')
    title = ugettext_lazy('Delete schedule')
    form_action_urlname = 'schedule-delete'
    messages = ugettext_lazy('Schedule was successfully deleted')


class ScheduleEditView(YamlFormMixin, UpdateView):
    '''
    Generic view to update an existing workout routine
    '''

    model = Schedule
    title = ugettext_lazy('Edit schedule')
    form_action_urlname = 'schedule-edit'


def edit_step_api(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, user=request.user)

    # Set the order
    if request.GET.get('do') == 'set_order':
        new_set_order = request.GET.get('order')

        order = 0
        for i in new_set_order.strip(',').split(','):
            # If the order items are not well formatted, ignore them
            try:
                step_id = i.split('-')[1]
            except IndexError:
                continue
            order += 1

            # If the step does not exist or belongs to somebody else, ignore it
            try:
                step = ScheduleStep.objects.get(pk=step_id, schedule=schedule)
            except ScheduleStep.DoesNotExist:
                continue

            # Save
            step.order = order
            step.save()

        return HttpResponse(_('Success'))
