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

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from django.contrib.auth.decorators import login_required

from django.views.generic import DeleteView
from django.views.generic import UpdateView

from wger.manager.models import Workout
from wger.manager.models import WorkoutLog
from wger.manager.models import Schedule
from wger.manager.models import Day
from wger.manager.forms import WorkoutForm
from wger.manager.forms import WorkoutSessionHiddenFieldsForm
from wger.manager.forms import WorkoutCopyForm

from wger.utils.generic_views import WgerFormMixin
from wger.utils.generic_views import WgerDeleteMixin
from wger.utils.generic_views import WgerPermissionMixin

logger = logging.getLogger('wger.custom')


# ************************
# Workout functions
# ************************
@login_required
def overview(request):
    '''
    An overview of all the user's workouts
    '''

    template_data = {}

    latest_workouts = Workout.objects.filter(user=request.user)
    (current_workout, schedule) = Schedule.objects.get_current_workout(request.user)
    template_data['workouts'] = latest_workouts
    template_data['current_workout'] = current_workout

    return render_to_response('workout/overview.html',
                              template_data,
                              context_instance=RequestContext(request))


@login_required
def view(request, id):
    '''
    Show the workout with the given ID
    '''
    template_data = {}
    workout = get_object_or_404(Workout, pk=id, user=request.user)
    canonical = workout.canonical_representation

    # Create the backgrounds that show what muscles the workout will work on
    muscles_front = []
    muscles_back = []
    for i in canonical['muscles']['front']:
        if not i in muscles_front:
            muscles_front.append('images/muscles/main/muscle-{0}.svg'.format(i))
    for i in canonical['muscles']['back']:
        if not i in muscles_back:
            muscles_back.append('images/muscles/main/muscle-{0}.svg'.format(i))

    # Append the silhouette of the human body as the last entry so the browser
    # renders it in the background
    muscles_front.append('images/muscles/muscular_system_front.svg')
    muscles_back.append('images/muscles/muscular_system_back.svg')

    template_data['workout'] = workout
    template_data['muscle_backgrounds_front'] = muscles_front
    template_data['muscle_backgrounds_back'] = muscles_back

    return render_to_response('workout/view.html',
                              template_data,
                              context_instance=RequestContext(request))


@login_required
def copy_workout(request, pk):
    '''
    Makes a copy of a workout
    '''

    workout = get_object_or_404(Workout, pk=pk, user=request.user)

    # Process request
    if request.method == 'POST':
        workout_form = WorkoutCopyForm(request.POST)

        if workout_form.is_valid():

            # Copy workout
            days = workout.day_set.all()

            workout_copy = workout
            workout_copy.pk = None
            workout_copy.comment = workout_form.cleaned_data['comment']
            workout_copy.save()

            # Copy the days
            for day in days:
                sets = day.set_set.all()

                day_copy = day
                days_of_week = [i for i in day.day.all()]
                day_copy.pk = None
                day_copy.training = workout_copy
                day_copy.save()
                for i in days_of_week:
                    day_copy.day.add(i)
                day_copy.save()

                # Copy the sets
                for current_set in sets:
                    current_set_id = current_set.id
                    exercises = current_set.exercises.all()

                    current_set_copy = current_set
                    current_set_copy.pk = None
                    current_set_copy.exerciseday = day_copy
                    current_set_copy.save()

                    # Exercises has Many2Many relationship
                    current_set_copy.exercises = exercises

                    # Go through the exercises
                    for exercise in exercises:
                        settings = exercise.setting_set.filter(set_id=current_set_id)

                        # Copy the settings
                        for setting in settings:
                            setting_copy = setting
                            setting_copy.pk = None
                            setting_copy.set = current_set_copy
                            setting_copy.save()

            return HttpResponseRedirect(reverse('workout-view',
                                                kwargs={'id': workout.id}))
    else:
        workout_form = WorkoutCopyForm({'comment': workout.comment})

        template_data = {}
        template_data.update(csrf(request))
        template_data['title'] = _('Copy workout')
        template_data['form'] = workout_form
        template_data['form_action'] = reverse('workout-copy', kwargs={'pk': workout.id})
        template_data['form_fields'] = [workout_form['comment']]
        template_data['submit_text'] = _('Copy')

        return render_to_response('form.html',
                                  template_data,
                                  context_instance=RequestContext(request))


@login_required
def add(request):
    '''
    Add a new workout and redirect to its page
    '''
    workout = Workout()
    workout.user = request.user
    workout.save()

    return HttpResponseRedirect(reverse('workout-view', kwargs={'id': workout.id}))


class WorkoutDeleteView(WgerDeleteMixin, DeleteView, WgerPermissionMixin):
    '''
    Generic view to delete a workout routine
    '''

    model = Workout
    success_url = reverse_lazy('workout-overview')
    title = ugettext_lazy('Delete workout')
    form_action_urlname = 'workout-delete'
    messages = ugettext_lazy('Workout was successfully deleted')
    login_required = True


class WorkoutEditView(WgerFormMixin, UpdateView, WgerPermissionMixin):
    '''
    Generic view to update an existing workout routine
    '''

    model = Workout
    form_class = WorkoutForm
    title = ugettext_lazy('Edit workout')
    form_action_urlname = 'workout-edit'
    login_required = True


class LastWeightHelper():
    '''
    Small helper class to retrieve the last workout log for a certain
    user, exercise and repetition combination.
    '''
    user = None
    last_weight_list = {}

    def __init__(self, user):
        self.user = user

    def get_last_weight(self, exercise, reps):
        '''
        Returns an emtpy string if no entry is found

        :param exercise:
        :param reps:
        :return: WorkoutLog or '' if none is found
        '''
        key = '{0}-{1}-{2}'.format(self.user.pk, exercise.pk, reps)

        if self.last_weight_list.get(key) is None:
            last_log = WorkoutLog.objects.filter(user=self.user,
                                                 exercise=exercise,
                                                 reps=reps).order_by('-date')
            weight = last_log[0].weight if last_log.exists() else ''
            self.last_weight_list[key] = weight

        return self.last_weight_list.get(key)


@login_required
def timer(request, day_pk):
    '''
    The timer view ("gym mode") for a workout
    '''

    day = get_object_or_404(Day, pk=day_pk, training__user=request.user)
    canonical_day = day.canonical_representation
    context = {}
    step_list = []
    last_log = LastWeightHelper(request.user)

    # Go through the workout day and create the individual 'pages'
    for set_dict in canonical_day['set_list']:

        if not set_dict['is_superset']:
            for exercise_dict in set_dict['exercise_list']:
                exercise = exercise_dict['obj']
                for reps in exercise_dict['setting_list']:
                    step_list.append({'current_step': uuid.uuid4().hex,
                                      'step_percent': 0,
                                      'step_nr': len(step_list) + 1,
                                      'exercise': exercise,
                                      'type': 'exercise',
                                      'reps': reps,
                                      'weight': last_log.get_last_weight(exercise, reps)})

                    step_list.append({'current_step': uuid.uuid4().hex,
                                      'step_percent': 0,
                                      'step_nr': len(step_list) + 1,
                                      'type': 'pause',
                                      'time': 90})

        # Supersets need extra work to group the exercises and reps together
        else:
            total_reps = len(set_dict['exercise_list'][0]['setting_list'])
            for i in range(0, total_reps):
                for exercise_dict in set_dict['exercise_list']:
                    reps = exercise_dict['setting_list'][i]
                    exercise = exercise_dict['obj']

                    step_list.append({'current_step': uuid.uuid4().hex,
                                      'step_percent': 0,
                                      'step_nr': len(step_list) + 1,
                                      'exercise': exercise,
                                      'type': 'exercise',
                                      'reps': reps,
                                      'weight': last_log.get_last_weight(exercise, reps)})

                step_list.append({'current_step': uuid.uuid4().hex,
                                  'step_percent': 0,
                                  'step_nr': len(step_list) + 1,
                                  'type': 'pause',
                                  'time': 90})

    # Remove the last pause step as it is not needed. If the list is empty,
    # because the user didn't add any repetitions to any exercise, do nothing
    try:
        step_list.pop()
    except IndexError:
        pass

    # Go through the page list and calculate the correct value for step_percent
    for i, s in enumerate(step_list):
        step_list[i]['step_percent'] = (i + 1) * 100.0 / len(step_list)

    # Render template
    context['day'] = day
    context['step_list'] = step_list
    context['canonical_day'] = canonical_day
    context['workout'] = day.training
    context['session_form'] = WorkoutSessionHiddenFieldsForm()
    return render_to_response('workout/timer.html',
                              context,
                              context_instance=RequestContext(request))
