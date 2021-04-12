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

# Standard Library
import copy
import datetime
import logging
import uuid

# Django
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    HttpResponseForbidden,
    HttpResponseRedirect
)
from django.shortcuts import (
    get_object_or_404,
    render
)
from django.template.context_processors import csrf
from django.urls import (
    reverse,
    reverse_lazy
)
from django.utils.text import slugify
from django.utils.translation import (
    gettext as _,
    gettext_lazy
)
from django.views.generic import (
    DeleteView,
    UpdateView
)

# Third Party
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

# wger
from wger.core.models import (
    RepetitionUnit,
    WeightUnit
)
from wger.manager.forms import (
    WorkoutCopyForm,
    WorkoutForm,
    WorkoutSessionHiddenFieldsForm
)
from wger.manager.models import (
    Day,
    Schedule,
    Workout,
    WorkoutLog,
    WorkoutSession
)
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin
)
from wger.utils.helpers import make_token


logger = logging.getLogger(__name__)


# ************************
# Workout functions
# ************************
@login_required
def overview(request):
    """
    An overview of all the user's workouts
    """

    template_data = {}

    workouts = Workout.objects.filter(user=request.user)
    (current_workout, schedule) = Schedule.objects.get_current_workout(request.user)
    template_data['workouts'] = workouts
    template_data['current_workout'] = current_workout

    return render(request, 'workout/overview.html', template_data)


def view(request, pk):
    """
    Show the workout with the given ID
    """
    template_data = {}
    workout = get_object_or_404(Workout, pk=pk)
    user = workout.user
    is_owner = request.user == user

    if not is_owner and not user.userprofile.ro_access:
        return HttpResponseForbidden()

    canonical = workout.canonical_representation
    uid, token = make_token(user)

    template_data['workout'] = workout
    template_data['muscles'] = canonical['muscles']
    template_data['uid'] = uid
    template_data['token'] = token
    template_data['is_owner'] = is_owner
    template_data['owner_user'] = user
    template_data['show_shariff'] = is_owner

    return render(request, 'workout/view.html', template_data)


@login_required
def copy_workout(request, pk):
    """
    Makes a copy of a workout
    """

    workout = get_object_or_404(Workout, pk=pk)
    user = workout.user
    is_owner = request.user == user

    if not is_owner and not user.userprofile.ro_access:
        return HttpResponseForbidden()

    # Process request
    if request.method == 'POST':
        workout_form = WorkoutCopyForm(request.POST)

        if workout_form.is_valid():

            # Copy workout
            days_original = workout.day_set.all()

            workout_copy = copy.copy(workout)
            workout_copy.pk = None
            workout_copy.comment = workout_form.cleaned_data['comment']
            workout_copy.user = request.user
            workout_copy.save()

            # Copy the days
            for day in days_original:
                sets = day.set_set.all()
                days_of_week = [i for i in day.day.all()]

                day_copy = copy.copy(day)
                day_copy.pk = None
                day_copy.training = workout_copy
                day_copy.save()
                for i in days_of_week:
                    day_copy.day.add(i)
                day_copy.save()

                # Copy the sets
                for current_set in sets:
                    current_set_copy = copy.copy(current_set)
                    current_set_copy.pk = None
                    current_set_copy.exerciseday = day_copy
                    current_set_copy.save()

                    # Copy the settings
                    for current_setting in current_set.setting_set.all():
                        setting_copy = copy.copy(current_setting)
                        setting_copy.pk = None
                        setting_copy.set = current_set_copy
                        setting_copy.save()

            return HttpResponseRedirect(reverse('manager:workout:view',
                                                kwargs={'pk': workout_copy.id}))
    else:
        workout_form = WorkoutCopyForm({'comment': workout.comment})
        workout_form.helper = FormHelper()
        workout_form.helper.form_id = slugify(request.path)
        workout_form.helper.form_method = 'post'
        workout_form.helper.form_action = request.path
        workout_form.helper.add_input(
            Submit('submit', _('Save'), css_class='btn-success btn-block'))
        workout_form.helper.form_class = 'wger-form'

        template_data = {}
        template_data.update(csrf(request))
        template_data['title'] = _('Copy workout')
        template_data['form'] = workout_form
        template_data['form_fields'] = [workout_form['comment']]
        template_data['submit_text'] = _('Copy')

        return render(request, 'form.html', template_data)


@login_required
def add(request):
    """
    Add a new workout and redirect to its page
    """
    workout = Workout()
    workout.user = request.user
    workout.save()

    return HttpResponseRedirect(workout.get_absolute_url())


class WorkoutDeleteView(WgerDeleteMixin, LoginRequiredMixin, DeleteView):
    """
    Generic view to delete a workout routine
    """

    model = Workout
    fields = ('comment',)
    success_url = reverse_lazy('manager:workout:overview')
    messages = gettext_lazy('Successfully deleted')

    def get_context_data(self, **kwargs):
        context = super(WorkoutDeleteView, self).get_context_data(**kwargs)
        context['title'] = _('Delete {0}?').format(self.object)
        return context


class WorkoutEditView(WgerFormMixin, LoginRequiredMixin, UpdateView):
    """
    Generic view to update an existing workout routine
    """

    model = Workout
    form_class = WorkoutForm

    def get_context_data(self, **kwargs):
        context = super(WorkoutEditView, self).get_context_data(**kwargs)
        context['title'] = _('Edit {0}').format(self.object)
        return context


class LastWeightHelper:
    """
    Small helper class to retrieve the last workout log for a certain
    user, exercise and repetition combination.
    """
    user = None
    last_weight_list = {}

    def __init__(self, user):
        self.user = user

    def get_last_weight(self, exercise, reps, default_weight):
        """
        Returns an emtpy string if no entry is found

        :param exercise:
        :param reps:
        :param default_weight:
        :return: WorkoutLog or '' if none is found
        """
        key = (self.user.pk, exercise.pk, reps, default_weight)
        if self.last_weight_list.get(key) is None:
            last_log = WorkoutLog.objects.filter(user=self.user,
                                                 exercise=exercise,
                                                 reps=reps).order_by('-date')
            default_weight = '' if default_weight is None else default_weight
            weight = last_log[0].weight if last_log.exists() else default_weight
            self.last_weight_list[key] = weight

        return self.last_weight_list.get(key)


@login_required
def timer(request, day_pk):
    """
    The timer view ("gym mode") for a workout
    """

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
                for key, element in enumerate(exercise_dict['reps_list']):
                    reps = exercise_dict['reps_list'][key]
                    rep_unit = exercise_dict['repetition_units'][key]
                    weight_unit = exercise_dict['weight_units'][key]
                    default_weight = last_log.get_last_weight(exercise,
                                                              reps,
                                                              exercise_dict['weight_list'][key])

                    step_list.append({'current_step': uuid.uuid4().hex,
                                      'step_percent': 0,
                                      'step_nr': len(step_list) + 1,
                                      'exercise': exercise,
                                      'type': 'exercise',
                                      'reps': reps,
                                      'rep_unit': rep_unit,
                                      'weight': default_weight,
                                      'weight_unit': weight_unit})
                    if request.user.userprofile.timer_active:
                        step_list.append({'current_step': uuid.uuid4().hex,
                                          'step_percent': 0,
                                          'step_nr': len(step_list) + 1,
                                          'type': 'pause',
                                          'time': request.user.userprofile.timer_pause})

        # Supersets need extra work to group the exercises and reps together
        else:
            total_reps = len(set_dict['exercise_list'][0]['reps_list'])
            for i in range(0, total_reps):
                for exercise_dict in set_dict['exercise_list']:
                    reps = exercise_dict['reps_list'][i]
                    rep_unit = exercise_dict['repetition_units'][i]
                    weight_unit = exercise_dict['weight_units'][i]
                    default_weight = exercise_dict['weight_list'][i]
                    exercise = exercise_dict['obj']

                    step_list.append({'current_step': uuid.uuid4().hex,
                                      'step_percent': 0,
                                      'step_nr': len(step_list) + 1,
                                      'exercise': exercise,
                                      'type': 'exercise',
                                      'reps': reps,
                                      'rep_unit': rep_unit,
                                      'weight_unit': weight_unit,
                                      'weight': last_log.get_last_weight(exercise,
                                                                         reps,
                                                                         default_weight)})

                if request.user.userprofile.timer_active:
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

    # Depending on whether there is already a workout session for today, update
    # the current one or create a new one (this will be the most usual case)
    if WorkoutSession.objects.filter(user=request.user, date=datetime.date.today()).exists():
        session = WorkoutSession.objects.get(user=request.user, date=datetime.date.today())
        session_form = WorkoutSessionHiddenFieldsForm(instance=session)
    else:
        session_form = WorkoutSessionHiddenFieldsForm()

    # Render template
    context['day'] = day
    context['step_list'] = step_list
    context['canonical_day'] = canonical_day
    context['workout'] = day.training
    context['session_form'] = session_form
    context['weight_units'] = WeightUnit.objects.all()
    context['repetition_units'] = RepetitionUnit.objects.all()
    return render(request, 'workout/timer.html', context)
