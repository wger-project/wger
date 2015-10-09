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

from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy, ugettext as _
from django.views.generic import (
    UpdateView,
    DeleteView,
    CreateView
)

from wger.manager.forms import WorkoutSessionForm
from wger.manager.models import (
    Workout,
    WorkoutSession,
    WorkoutLog
)
from wger.utils.generic_views import (
    WgerFormMixin,
    WgerDeleteMixin,
    WgerPermissionMixin
)


logger = logging.getLogger(__name__)

'''
Workout session
'''


class WorkoutSessionUpdateView(WgerFormMixin, UpdateView, WgerPermissionMixin):
    '''
    Generic view to edit an existing workout session entry
    '''
    model = WorkoutSession
    form_class = WorkoutSessionForm
    login_required = True

    def get_context_data(self, **kwargs):
        context = super(WorkoutSessionUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('manager:session:edit', kwargs={'pk': self.object.id})
        context['title'] = _('Edit workout impression for {0}').format(self.object.date)

        return context

    def get_success_url(self):
        return reverse('manager:workout:calendar')


class WorkoutSessionAddView(WgerFormMixin, CreateView, WgerPermissionMixin):
    '''
    Generic view to add a new workout session entry
    '''
    model = WorkoutSession
    form_class = WorkoutSessionForm
    login_required = True

    def get_date(self):
        '''
        Returns a date object from the URL parameters or None if no date
        could be created
        '''
        try:
            date = datetime.date(int(self.kwargs['year']),
                                 int(self.kwargs['month']),
                                 int(self.kwargs['day']))
        except ValueError:
            date = None

        return date

    def dispatch(self, request, *args, **kwargs):
        '''
        Check for ownership
        '''
        workout = Workout.objects.get(pk=kwargs['workout_pk'])
        if workout.get_owner_object().user != request.user:
            return HttpResponseForbidden()

        if not self.get_date():
            return HttpResponseBadRequest('You need to use a valid date')

        return super(WorkoutSessionAddView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WorkoutSessionAddView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('manager:session:add',
                                         kwargs={'workout_pk': self.kwargs['workout_pk'],
                                                 'year': self.kwargs['year'],
                                                 'month': self.kwargs['month'],
                                                 'day': self.kwargs['day']})
        context['title'] = _('New workout impression for the {0}'.format(self.get_date()))
        return context

    def get_success_url(self):
        return reverse('manager:workout:calendar')

    def form_valid(self, form):
        '''
        Set the workout and the user
        '''

        workout = Workout.objects.get(pk=self.kwargs['workout_pk'])
        form.instance.workout = workout
        form.instance.user = self.request.user
        form.instance.date = self.get_date()
        return super(WorkoutSessionAddView, self).form_valid(form)


class WorkoutSessionDeleteView(WgerDeleteMixin, DeleteView):
    '''
    Generic view to delete a workout routine
    '''

    model = WorkoutSession
    success_url = reverse_lazy('manager:workout:overview')
    messages = ugettext_lazy('Successfully deleted')
    login_required = True

    def delete(self, request, *args, **kwargs):
        '''
        Delete the workout session and, if wished, all associated weight logs as well
        '''
        if self.kwargs['logs'] == 'logs':
            WorkoutLog.objects.filter(user=self.request.user, date=self.get_object().date).delete()

        return super(WorkoutSessionDeleteView, self).delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        logs = '' if not self.kwargs['logs'] else self.kwargs['logs']
        context = super(WorkoutSessionDeleteView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('manager:session:delete', kwargs={'pk': self.object.id,
                                                                           'logs': logs})
        context['title'] = _(u'Delete {0}?').format(self.object)
        if self.kwargs['logs'] == 'logs':
            context['delete_message'] = _('This will delete all weight logs for this day as well.')
        return context
