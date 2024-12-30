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
import datetime
import logging
import uuid

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import modelformset_factory
from django.http import (
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import reverse
from django.utils.translation import gettext_lazy
from django.views.generic import (
    DeleteView,
    DetailView,
    UpdateView,
)

# wger
from wger.core.models import (
    RepetitionUnit,
    WeightUnit,
)
from wger.manager.forms import (
    HelperWorkoutSessionForm,
    WorkoutLogForm,
    WorkoutLogFormHelper,
)
from wger.manager.models import (
    Day,
    Workout,
    WorkoutLog,
    WorkoutSession,
)
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin,
)
from wger.weight.helpers import process_log_entries


logger = logging.getLogger(__name__)


# ************************
# Log functions
# ************************
class WorkoutLogUpdateView(WgerFormMixin, UpdateView, LoginRequiredMixin):
    """
    Generic view to edit an existing workout log weight entry
    """

    model = WorkoutLog
    form_class = WorkoutLogForm

    def get_success_url(self):
        return reverse('manager:workout:view', kwargs={'pk': self.object.workout_id})


class WorkoutLogDeleteView(WgerDeleteMixin, DeleteView, LoginRequiredMixin):
    """
    Delete a workout log
    """

    model = WorkoutLog
    title = gettext_lazy('Delete workout log')

    def get_success_url(self):
        return reverse('manager:workout:view', kwargs={'pk': self.object.workout_id})


def add(request, pk):
    """
    Add a new workout log
    """

    # NOTE: This function is waaaay too complex and convoluted. While updating
    #       to crispy forms, the template logic could be reduced a lot, but
    #       there is still a lot of optimisations that could happen here.

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
    form_to_exercise_base = {}

    for set_set in day.set_set.all():
        for exercise in set_set.exercise_bases:
            # Maximum possible values
            total_sets += int(set_set.sets)
            counter_before = counter
            counter = counter + int(set_set.sets) - 1
            form_id_range = range(counter_before, counter + 1)

            # Add to list
            exercise_list[exercise.id] = {
                'obj': exercise,
                'sets': int(set_set.sets),
                'form_ids': form_id_range,
            }

            counter += 1
            # Helper mapping form-ID <--> Exercise base
            for id in form_id_range:
                form_to_exercise_base[id] = exercise

    # Define the formset here because now we know the value to pass to 'extra'
    WorkoutLogFormSet = modelformset_factory(
        WorkoutLog,
        form=WorkoutLogForm,
        exclude=('date', 'workout'),
        extra=total_sets,
    )
    # Process the request
    if request.method == 'POST':
        # Make a copy of the POST data and go through it. The reason for this is
        # that the form expects a value for the exercise which is not present in
        # the form (for space and usability reasons)
        post_copy = request.POST.copy()

        for form_id in form_to_exercise_base:
            if post_copy.get('form-%s-weight' % form_id) or post_copy.get('form-%s-reps' % form_id):
                post_copy['form-%s-exercise_base' % form_id] = form_to_exercise_base[form_id].id

        # Pass the new data to the forms
        formset = WorkoutLogFormSet(data=post_copy)
        session_form = HelperWorkoutSessionForm(data=post_copy)

        # If all the data is valid, save and redirect to log overview page
        if session_form.is_valid() and formset.is_valid():
            log_date = session_form.cleaned_data['date']

            if WorkoutSession.objects.filter(user=request.user, date=log_date).exists():
                session = WorkoutSession.objects.get(user=request.user, date=log_date)
                session_form = HelperWorkoutSessionForm(data=post_copy, instance=session)

            # Save the Workout Session only if there is not already one for this date
            log_instance = session_form.save(commit=False)
            if not WorkoutSession.objects.filter(user=request.user, date=log_date).exists():
                log_instance.date = log_date
                log_instance.user = request.user
                log_instance.workout = day.training
            else:
                session = WorkoutSession.objects.get(user=request.user, date=log_date)
                log_instance.instance = session
            log_instance.save()

            # Log entries (only the ones with actual content)
            log_instances = [i for i in formset.save(commit=False) if i.reps]
            for log_instance in log_instances:
                # Set the weight unit in kg
                if not hasattr(log_instance, 'weight_unit'):
                    log_instance.weight_unit = WeightUnit.objects.get(pk=1)

                # Set the unit in reps
                if not hasattr(log_instance, 'repetition_unit'):
                    log_instance.repetition_unit = RepetitionUnit.objects.get(pk=1)

                if not log_instance.weight:
                    log_instance.weight = 0

                log_instance.user = request.user
                log_instance.workout = day.training
                log_instance.date = log_date
                log_instance.save()

            return HttpResponseRedirect(reverse('manager:log:log', kwargs={'pk': day.training_id}))
    else:
        # Initialise the formset with a queryset that won't return any objects
        # (we only add new logs here and that seems to be the fastest way)
        user_weight_unit = 1 if request.user.userprofile.use_metric else 2
        formset = WorkoutLogFormSet(
            queryset=WorkoutLog.objects.none(),
            initial=[
                {'weight_unit': user_weight_unit, 'repetition_unit': 1}
                for x in range(0, total_sets)
            ],
        )

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
        exercise_list[exercise]['forms'] = formset[form_id_from : form_id_to + 1]

    context = {
        'day': day,
        'exercise_list': exercise_list,
        'formset': formset,
        'helper': WorkoutLogFormHelper(),
        'session_form': session_form,
        'form': session_form,
        'form_action': request.path,
    }

    return render(request, 'log/add.html', context)
