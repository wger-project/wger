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
import uuid
import datetime

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils import formats
from django.utils.translation import ugettext_lazy, ugettext as _
from django.forms.models import modelformset_factory
from django.views.generic import (
    UpdateView,
    CreateView,
    DetailView,
    DeleteView
)

from wger.manager.helpers import WorkoutCalendar
from wger.manager.models import (
    Workout,
    WorkoutSession,
    Day,
    WorkoutLog,
    Schedule
)
from wger.manager.forms import (
    HelperDateForm,
    HelperWorkoutSessionForm,
    WorkoutLogForm
)
from wger.utils.generic_views import (
    WgerFormMixin,
    WgerDeleteMixin,
    WgerPermissionMixin
)
from wger.utils.helpers import check_access
from wger.weight.helpers import process_log_entries, group_log_entries


logger = logging.getLogger(__name__)


# ************************
# Log functions
# ************************
class WorkoutLogUpdateView(WgerFormMixin, UpdateView, WgerPermissionMixin):
    '''
    Generic view to edit an existing workout log weight entry
    '''
    model = WorkoutLog
    form_class = WorkoutLogForm
    success_url = reverse_lazy('manager:workout:calendar')
    login_required = True

    def get_context_data(self, **kwargs):
        context = super(WorkoutLogUpdateView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('manager:log:edit', kwargs={'pk': self.object.id})
        context['title'] = _(u'Edit log entry for %s') % self.object.exercise.name

        return context


class WorkoutLogAddView(WgerFormMixin, CreateView, WgerPermissionMixin):
    '''
    Generic view to add a new workout log weight entry
    '''
    model = WorkoutLog
    login_required = True
    form_class = WorkoutLogForm

    def dispatch(self, request, *args, **kwargs):
        '''
        Check for ownership
        '''
        workout = Workout.objects.get(pk=kwargs['workout_pk'])
        if workout.user != request.user:
            return HttpResponseForbidden()

        return super(WorkoutLogAddView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(WorkoutLogAddView, self).get_context_data(**kwargs)
        context['form_action'] = reverse('manager:log:add',
                                         kwargs={'workout_pk': self.kwargs['workout_pk']})
        context['title'] = _('New log entry')

        return context

    def get_success_url(self):
        return reverse('manager:log:log', kwargs={'pk': self.kwargs['workout_pk']})

    def form_valid(self, form):
        '''
        Set the workout and the user
        '''

        workout = Workout.objects.get(pk=self.kwargs['workout_pk'])
        form.instance.workout = workout
        form.instance.user = self.request.user
        return super(WorkoutLogAddView, self).form_valid(form)


class WorkoutLogDeleteView(WgerDeleteMixin, DeleteView, WgerPermissionMixin):
    '''
    Delete a workout log
    '''

    model = WorkoutLog
    success_url = reverse_lazy('manager:workout:calendar')
    title = ugettext_lazy('Delete workout log')
    form_action_urlname = 'manager:log:delete'
    login_required = True


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
            total_sets += int(exercise_set.sets)
            counter_before = counter
            counter = counter + int(exercise_set.sets) - 1
            form_id_range = range(counter_before, counter + 1)

            # Add to list
            exercise_list[exercise.id] = {'obj': exercise,
                                          'sets': int(exercise_set.sets),
                                          'form_ids': form_id_range}

            counter += 1
            # Helper mapping form-ID <--> Exercise
            for id in form_id_range:
                form_to_exercise[id] = exercise

    # Define the formset here because now we know the value to pass to 'extra'
    WorkoutLogFormSet = modelformset_factory(WorkoutLog,
                                             form=WorkoutLogForm,
                                             exclude=('date', 'workout'),
                                             extra=total_sets)
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
        session_form = HelperWorkoutSessionForm(data=post_copy)

        # If all the data is valid, save and redirect to log overview page
        if dateform.is_valid() and session_form.is_valid() and formset.is_valid():
            log_date = dateform.cleaned_data['date']

            if WorkoutSession.objects.filter(user=request.user, date=log_date).exists():
                session = WorkoutSession.objects.get(user=request.user, date=log_date)
                session_form = HelperWorkoutSessionForm(data=post_copy, instance=session)

            # Save the Workout Session only if there is not already one for this date
            instance = session_form.save(commit=False)
            if not WorkoutSession.objects.filter(user=request.user, date=log_date).exists():
                instance.date = log_date
                instance.user = request.user
                instance.workout = day.training
            else:
                session = WorkoutSession.objects.get(user=request.user, date=log_date)
                instance.instance = session
            instance.save()

            # Log entries
            instances = formset.save(commit=False)
            for instance in instances:

                instance.user = request.user
                instance.workout = day.training
                instance.date = log_date
                instance.save()

            return HttpResponseRedirect(reverse('manager:log:log', kwargs={'pk': day.training_id}))
    else:
        # Initialise the formset with a queryset that won't return any objects
        # (we only add new logs here and that seems to be the fastest way)
        formset = WorkoutLogFormSet(queryset=WorkoutLog.objects.none())

        dateform = HelperDateForm(initial={'date': datetime.date.today()})

        # Depending on whether there is already a workout session for today, update
        # the current one or create a new one (this will be the most usual case)
        if WorkoutSession.objects.filter(user=request.user, date=datetime.date.today()).exists():
            session = WorkoutSession.objects.get(user=request.user, date=datetime.date.today())
            session_form = HelperWorkoutSessionForm(instance=session)
        else:
            session_form = HelperWorkoutSessionForm()

    # Pass the correct forms to the exercise list
    for exercise in exercise_list:

        form_id_from = min(exercise_list[exercise]['form_ids'])
        form_id_to = max(exercise_list[exercise]['form_ids'])
        exercise_list[exercise]['forms'] = formset[form_id_from:form_id_to + 1]

    template_data['day'] = day
    template_data['exercises'] = exercise_list
    template_data['exercise_list'] = exercise_list
    template_data['formset'] = formset
    template_data['dateform'] = dateform
    template_data['session_form'] = session_form
    template_data['form_action'] = reverse('manager:day:log', kwargs={'pk': pk})

    return render(request, 'day/log.html', template_data)


class WorkoutLogDetailView(DetailView, WgerPermissionMixin):
    '''
    An overview of the workout's log
    '''

    model = Workout
    template_name = 'workout/log.html'
    login_required = True
    context_object_name = 'workout'
    owner_user = None

    def get_context_data(self, **kwargs):

        # Call the base implementation first to get a context
        context = super(WorkoutLogDetailView, self).get_context_data(**kwargs)
        is_owner = self.owner_user == self.request.user

        # Prepare the entries for rendering and the D3 chart
        workout_log = {}

        for day_list in self.object.canonical_representation['day_list']:
            day_id = day_list['obj'].id
            workout_log[day_id] = {}
            for set_list in day_list['set_list']:
                exercise_log = {}
                for exercise_list in set_list['exercise_list']:
                    exercise_id = exercise_list['obj'].id
                    exercise_log[exercise_id] = []

                    logs = exercise_list['obj'].workoutlog_set.filter(user=self.owner_user,
                                                                      workout=self.object)
                    entry_log, chart_data = process_log_entries(logs)
                    if entry_log:
                        exercise_log[exercise_list['obj'].id].append(entry_log)

                    if exercise_log:
                        workout_log[day_id][exercise_id] = {}
                        workout_log[day_id][exercise_id]['log_by_date'] = entry_log
                        workout_log[day_id][exercise_id]['div_uuid'] = 'div-' + str(uuid.uuid4())
                        workout_log[day_id][exercise_id]['chart_data'] = chart_data

        context['workout_log'] = workout_log
        context['reps'] = _("Reps")
        context['owner_user'] = self.owner_user
        context['is_owner'] = is_owner
        context['show_shariff'] = is_owner

        return context

    def dispatch(self, request, *args, **kwargs):
        '''
        Check for ownership
        '''

        workout = get_object_or_404(Workout, pk=kwargs['pk'])
        self.owner_user = workout.user
        is_owner = request.user == self.owner_user

        if not is_owner and not self.owner_user.userprofile.ro_access:
            return HttpResponseForbidden()

        # Dispatch normally
        return super(WorkoutLogDetailView, self).dispatch(request, *args, **kwargs)


def calendar(request, username=None, year=None, month=None):
    '''
    Show a calendar with all the workout logs
    '''
    context = {}
    is_owner, user = check_access(request.user, username)
    year = int(year) if year else datetime.date.today().year
    month = int(month) if month else datetime.date.today().month

    (current_workout, schedule) = Schedule.objects.get_current_workout(user)
    grouped_log_entries = group_log_entries(user, year, month)

    context['calendar'] = WorkoutCalendar(grouped_log_entries).formatmonth(year, month)
    context['logs'] = grouped_log_entries
    context['current_year'] = year
    context['current_month'] = month
    context['current_workout'] = current_workout
    context['owner_user'] = user
    context['is_owner'] = is_owner
    context['impressions'] = WorkoutSession.IMPRESSION
    context['month_list'] = WorkoutLog.objects.filter(user=user).dates('date', 'month')
    context['show_shariff'] = is_owner and user.userprofile.ro_access
    return render(request, 'calendar/month.html', context)


def day(request, username, year, month, day):
    '''
    Show the logs for a single day
    '''
    context = {}
    is_owner, user = check_access(request.user, username)

    try:
        date = datetime.date(int(year), int(month), int(day))
    except ValueError as e:
        logger.error("Error on date: {0}".format(e))
        return HttpResponseForbidden()
    context['logs'] = group_log_entries(user, date.year, date.month, date.day)
    context['date'] = date
    context['owner_user'] = user
    context['is_owner'] = is_owner
    context['show_shariff'] = is_owner and user.userprofile.ro_access

    return render(request, 'calendar/day.html', context)
