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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.views.generic import UpdateView

from wger.core.models import DaysOfWeek
from wger.manager.models import Workout, Day
from wger.manager.forms import DayForm
from wger.utils.generic_views import WgerFormMixin


logger = logging.getLogger(__name__)


# ************************
# Day functions
# ************************
class DayView(WgerFormMixin, LoginRequiredMixin):
    '''
    Base generic view for exercise day
    '''

    model = Day
    fields = ('description', 'day')

    def get_success_url(self):
        return reverse('manager:workout:view', kwargs={'pk': self.object.training_id})

    def get_form(self, form_class=DayForm):
        '''
        Filter the days of the week that are alreeady used by other days
        '''

        # Get the form
        form = super(DayView, self).get_form(form_class)

        # Calculate the used days ('used' by other days in the same workout)
        if self.object:
            workout = self.object.training
        else:
            workout = Workout.objects.get(pk=self.kwargs['workout_pk'])

        used_days = []
        for day in workout.day_set.all():
            for weekday in day.day.all():
                if not self.object or day.id != self.object.id:
                    used_days.append(weekday.id)
        used_days.sort()

        # Set the queryset for day
        form.fields['day'].queryset = DaysOfWeek.objects.exclude(id__in=used_days)

        return form


class DayEditView(DayView, UpdateView):
    '''
    Generic view to update an existing exercise day
    '''

    form_action_urlname = 'manager:day:edit'

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(DayEditView, self).get_context_data(**kwargs)
        context['title'] = _(u'Edit {0}').format(self.object)
        return context


class DayCreateView(DayView, CreateView):
    '''
    Generic view to add a new exercise day
    '''

    title = ugettext_lazy('Add workout day')
    owner_object = {'pk': 'workout_pk', 'class': Workout}

    def form_valid(self, form):
        '''
        Set the workout this day belongs to
        '''
        form.instance.training = Workout.objects.get(pk=self.kwargs['workout_pk'])
        return super(DayCreateView, self).form_valid(form)

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super(DayCreateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('manager:day:add',
                                         kwargs={'workout_pk': self.kwargs['workout_pk']})
        return context


@login_required
def delete(request, pk):
    '''
    Deletes the given day
    '''
    day = get_object_or_404(Day, training__user=request.user, pk=pk)
    day.delete()
    return HttpResponseRedirect(reverse('manager:workout:view', kwargs={'pk': day.training_id}))


@login_required
def view(request, id):
    '''
    Renders a day as shown in the workout overview.

    This function is to be used with AJAX calls.
    '''
    template_data = {}

    # Load day and check if its workout belongs to the user
    day = get_object_or_404(Day, pk=id, training__user=request.user)

    template_data['day'] = day

    return render(request, 'day/view.html', template_data)
