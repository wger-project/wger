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
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import UpdateView

from wger.manager.models import Schedule
from wger.utils.generic_views import WgerFormMixin
from wger.utils.generic_views import WgerDeleteMixin
from wger.utils.generic_views import WgerPermissionMixin
from wger.utils.helpers import make_token


logger = logging.getLogger('wger.custom')


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


@login_required
def view(request, pk):
    '''
    Show the workout schedule
    '''
    template_data = {}
    user = request.user
    uid, token = make_token(user)

    schedule = get_object_or_404(Schedule, pk=pk, user=user)
    template_data['schedule'] = schedule
    if schedule.is_active:
        template_data['active_workout'] = schedule.get_current_scheduled_workout()
    else:
        template_data['active_workout'] = False

    schedule.get_current_scheduled_workout()

    template_data['uid'] = uid
    template_data['token'] = token

    return render(request, 'schedule/view.html', template_data)


class ScheduleCreateView(WgerFormMixin, CreateView, WgerPermissionMixin):
    '''
    Creates a new workout schedule
    '''

    model = Schedule
    success_url = reverse_lazy('schedule-overview')
    title = ugettext_lazy('Create schedule')
    form_action = reverse_lazy('schedule-add')
    login_required = True

    def form_valid(self, form):
        '''set the submitter'''
        form.instance.user = self.request.user
        return super(ScheduleCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('schedule-view', kwargs={'pk': self.object.id})


class ScheduleDeleteView(WgerDeleteMixin, DeleteView, WgerPermissionMixin):
    '''
    Generic view to delete a schedule
    '''

    model = Schedule
    success_url = reverse_lazy('schedule-overview')
    title = ugettext_lazy('Delete schedule')
    form_action_urlname = 'schedule-delete'
    messages = ugettext_lazy('Schedule was successfully deleted')
    login_required = True


class ScheduleEditView(WgerFormMixin, UpdateView, WgerPermissionMixin):
    '''
    Generic view to update an existing workout routine
    '''

    model = Schedule
    title = ugettext_lazy('Edit schedule')
    form_action_urlname = 'schedule-edit'
    login_required = True
