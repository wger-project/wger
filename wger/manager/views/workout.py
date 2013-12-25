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
from django.core.cache import cache
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from django.contrib.auth.decorators import login_required

from django.views.generic import DeleteView
from django.views.generic import UpdateView

from wger.manager.models import Workout
from wger.manager.models import WorkoutLog
from wger.manager.models import Schedule
from wger.manager.models import Day
from wger.manager.models import Setting
from wger.manager.forms import WorkoutForm
from wger.manager.forms import WorkoutCopyForm

from wger.utils.generic_views import WgerFormMixin
from wger.utils.generic_views import WgerDeleteMixin
from wger.utils.generic_views import WgerPermissionMixin
from wger.utils.cache import cache_mapper

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
    template_data['workout'] = workout

    # Create the backgrounds that show what muscles the workout will work on
    backgrounds = cache.get(cache_mapper.get_workout_muscle_bg(int(id)))
    if not backgrounds:

        backgrounds_front = []
        backgrounds_back = []
        for day in workout.day_set.select_related():
            for set in day.set_set.select_related():
                for exercise in set.exercises.select_related():
                    for muscle in exercise.muscles.all():
                        muscle_bg = 'images/muscles/main/muscle-%s.svg' % muscle.id

                        # Add the muscles to the background list, but only once.
                        #
                        # While the combining effect (the more often a muscle gets
                        # added, the more intense the colour) is interesting, the
                        # end result is a very unnatural, very bright colour.
                        if muscle.is_front and muscle_bg not in backgrounds_front:
                            backgrounds_front.append(muscle_bg)
                        elif not muscle.is_front and muscle_bg not in backgrounds_back:
                            backgrounds_back.append(muscle_bg)

        # Append the correct "main" background, with the silhouette of the human body
        backgrounds_front.append('images/muscles/muscular_system_front.svg')
        backgrounds_back.append('images/muscles/muscular_system_back.svg')

        backgrounds = (backgrounds_front, backgrounds_back)

        cache.set(cache_mapper.get_workout_muscle_bg(int(id)),
                  (backgrounds_front, backgrounds_back))

    template_data['muscle_backgrounds_front'] = backgrounds[0]
    template_data['muscle_backgrounds_back'] = backgrounds[1]

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

            return HttpResponseRedirect(reverse('wger.manager.views.workout.view',
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

    return HttpResponseRedirect(reverse('wger.manager.views.workout.view',
                                        kwargs={'id': workout.id}))


class WorkoutDeleteView(WgerDeleteMixin, DeleteView, WgerPermissionMixin):
    '''
    Generic view to delete a workout routine
    '''

    model = Workout
    success_url = reverse_lazy('wger.manager.views.workout.overview')
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


def get_last_weight(user, exercise, reps):
    '''
    Helper function to retrieve the last workout log for a certain
    user, exercise and repetition combination. Returns an emtpy string
    if no entry is found

    :param user:
    :param exercise:
    :param reps:
    :return: WorkoutLog or '' if none is found
    '''
    last_log = WorkoutLog.objects.filter(user=user,
                                         exercise=exercise,
                                         reps=reps).order_by('-date')
    if last_log.exists():
        weight = last_log[0].weight
    else:
        weight = ''

    return weight


@login_required
def timer(request, pk):
    '''
    The timer view ("gym mode") for a workout
    '''

    day = Day.objects.get(pk=pk, training__user=request.user)
    canonical_day = day.canonical_representation
    context = {}
    step_list = []

    # Go through the workout day and create the individual 'pages'
    for set_dict in canonical_day:

        if not set_dict['is_superset']:
            for exercise_dict in set_dict['exercise_list']:
                exercise = exercise_dict['obj']
                for reps in exercise_dict['setting_list']:
                    step_list.append({'current_step': uuid.uuid4().hex,
                                      'step_percent': 0,
                                      'exercise': exercise,
                                      'type': 'exercise',
                                      'reps': reps,
                                      'weight': get_last_weight(user=request.user,
                                                                exercise=exercise,
                                                                reps=reps)})

                    step_list.append({'current_step': uuid.uuid4().hex,
                                      'step_percent': 0,
                                      'type': 'pause',
                                      'time': 30})

        # Supersets need extra work to group the exercises and reps together
        else:
            total_reps = len(set_dict['exercise_list'][0]['setting_list'])
            for i in range(0, total_reps):
                for exercise_dict in set_dict['exercise_list']:
                    reps = exercise_dict['setting_list'][i]
                    exercise = exercise_dict['obj']

                    step_list.append({'current_step': uuid.uuid4().hex,
                                      'step_percent': 0,
                                      'exercise': exercise,
                                      'type': 'exercise',
                                      'reps': reps,
                                      'weight': get_last_weight(user=request.user,
                                                                exercise=exercise,
                                                                reps=reps)})

                step_list.append({'current_step': uuid.uuid4().hex,
                                  'step_percent': 0,
                                  'type': 'pause',
                                  'time': 30})

    # Go through the page list and calculate the correct value for step_percent
    for i, s in enumerate(step_list):
        step_list[i]['step_percent'] = (i + 1) * 100.0 / len(step_list),

    context['day'] = day
    context['step_list'] = step_list
    context['canonical_day'] = canonical_day
    context['workout'] = day.training
    return render_to_response('workout/timer.html',
                              context,
                              context_instance=RequestContext(request))
