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
import uuid
import datetime

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.formats import date_format
from django.forms.models import modelformset_factory

from django.views.generic import UpdateView
from django.views.generic import DetailView

from wger.manager.models import TrainingSchedule
from wger.manager.models import Day
from wger.manager.models import WorkoutLog

from wger.manager.forms import HelperDateForm
from wger.manager.forms import WorkoutLogForm

from wger.workout_manager.generic_views import YamlFormMixin


logger = logging.getLogger('workout_manager.custom')


# ************************
# Log functions
# ************************
class WorkoutLogUpdateView(YamlFormMixin, UpdateView):
    '''
    Generic view to edit an existing workout log weight entry
    '''
    model = WorkoutLog
    form_class = WorkoutLogForm
    custom_js = '''$(document).ready(function () {
        init_weight_log_datepicker();
    });'''

    def get_context_data(self, **kwargs):
        context = super(WorkoutLogUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('workout-log-edit', kwargs={'pk': self.object.id})
        context['title'] = _('Edit log entry for %s') % self.object.exercise.name

        return context

    def get_success_url(self):
        return reverse('workout-log', kwargs={'pk': self.object.workout_id})


def add(request, pk):
    '''
    Add a new workout log
    '''

    template_data = {}
    template_data.update(csrf(request))

    # Load the day and check ownership
    day = get_object_or_404(Day, pk=pk)
    if day.get_owner_object().user != request.user:
        return HttpResponseForbidden()

    # We need several lists here because we need to assign specific form to each
    # exercise: the entries for weight and repetitions have no indicator to which
    # exercise they belong besides the form-ID, from Django's formset
    counter = 0
    total_sets = 0
    exercise_list = {}
    form_to_exercise = {}

    for exercise_set in day.set_set.all():
        for exercise in exercise_set.exercises.all():

            # Maximum possible values
            total_sets = total_sets + int(exercise_set.sets)
            counter_before = counter
            counter = counter + int(exercise_set.sets) - 1
            form_id_range = range(counter_before, counter + 1)

            # Add to list
            exercise_list[exercise.id] = {'obj': exercise,
                                          'sets': int(exercise_set.sets),
                                          'form_ids': form_id_range}

            counter = counter + 1
            # Helper mapping form-ID <--> Exercise
            for id in form_id_range:
                form_to_exercise[id] = exercise

    # Define the formset here because now we know the value to pass to 'extra'
    WorkoutLogFormSet = modelformset_factory(WorkoutLog,
                                             form=WorkoutLogForm,
                                             exclude=('user',
                                                      'workout',
                                                      'date'),
                                             extra = total_sets)
    # Process the request
    if request.method == 'POST':

        # Make a copy of the POST data and go through it. The reason for this is
        # that the form expects a value for the exercise which is not present in
        # the form (for space and usability reasons)

        post_copy = request.POST.copy()

        for form_id in form_to_exercise:
            if post_copy.get('form-%s-weight' % form_id) or post_copy.get('form-%s-reps' % form_id):
                post_copy['form-%s-exercise' % form_id] = form_to_exercise[form_id].id

        # Pass the new data to the forms
        formset = WorkoutLogFormSet(data=post_copy)
        dateform = HelperDateForm(data=post_copy)

        if dateform.is_valid():
            log_date = dateform.cleaned_data['date']

            # If the data is valid, save and redirect to log overview page
            if formset.is_valid():
                instances = formset.save(commit=False)
                for instance in instances:

                    instance.user = request.user
                    instance.workout = day.training
                    instance.date = log_date
                    instance.save()

                return HttpResponseRedirect(reverse('workout-log', kwargs={'pk': day.training_id}))
    else:
        # Initialise the formset with a queryset that won't return any objects
        # (we only add new logs here and that seems to be the fastest way)
        formset = WorkoutLogFormSet(queryset=WorkoutLog.objects.filter(exercise=-1))

        formatted_date = date_format(datetime.date.today(), "SHORT_DATE_FORMAT")
        dateform = HelperDateForm(initial={'date': formatted_date})

    # Pass the correct forms to the exercise list
    for exercise in exercise_list:

        form_id_from = min(exercise_list[exercise]['form_ids'])
        form_id_to = max(exercise_list[exercise]['form_ids'])
        exercise_list[exercise]['forms'] = formset[form_id_from:form_id_to + 1]

    template_data['day'] = day
    template_data['exercises'] = exercise_list
    template_data['formset'] = formset
    template_data['dateform'] = dateform
    template_data['form_action'] = reverse('day-log', kwargs={'pk': pk})

    return render_to_response('day/log.html',
                              template_data,
                              context_instance=RequestContext(request))


class WorkoutLogDetailView(DetailView):
    '''
    An overview of the workout's log
    '''

    model = TrainingSchedule
    template_name = 'workout/log.html'
    context_object_name = 'workout'

    def get_context_data(self, **kwargs):

        # Call the base implementation first to get a context
        context = super(WorkoutLogDetailView, self).get_context_data(**kwargs)

        # Prepare the entries for rendering and the D3 chart
        workout_log = {}
        entry = WorkoutLog()

        for day in self.object.day_set.select_related():
            workout_log[day] = {}

            for set in day.set_set.select_related():
                exercise_log = {}

                for exercise in set.exercises.select_related():
                    exercise_log[exercise] = []
                    logs = exercise.workoutlog_set.filter(user=self.request.user)
                    entry_log, chart_data = entry.process_log_entries(logs)
                    if entry_log:
                        exercise_log[exercise].append(entry_log)

                    if exercise_log:
                        workout_log[day][exercise] = {}
                        workout_log[day][exercise]['log_by_date'] = entry_log
                        workout_log[day][exercise]['div_uuid'] = str(uuid.uuid4())
                        workout_log[day][exercise]['chart_data'] = chart_data

        context['workout_log'] = workout_log
        context['reps'] = _("Reps")

        return context

    def dispatch(self, request, *args, **kwargs):
        '''
        Check for ownership
        '''

        workout = TrainingSchedule.objects.get(pk=kwargs['pk'])
        if workout.user != request.user:
            return HttpResponseForbidden()

        # Dispatch normally
        return super(WorkoutLogDetailView, self).dispatch(request, *args, **kwargs)
