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

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.db import models

from django.contrib.auth.decorators import login_required

from wger.manager.models import TrainingSchedule
from wger.manager.models import Day
from wger.manager.models import Set
from wger.manager.models import Setting

from wger.exercises.models import Exercise

from wger.manager.forms import SetForm


logger = logging.getLogger('workout_manager.custom')


# ************************
# Set functions
# ************************
@login_required
def edit_set(request, id, day_id, set_id=None):
    '''
    Edits/creates a set
    '''

    template_data = {}
    template_data.update(csrf(request))

    # Load workout
    workout = get_object_or_404(TrainingSchedule, pk=id, user=request.user)
    template_data['workout'] = workout

    # Load day
    day = get_object_or_404(Day, pk=day_id)
    template_data['day'] = day

    # Load set

    # If the object is new, we will receice a 'None' (string) as the ID
    # from the template, so we check for it (ValueError) and for an actual
    # None (TypeError)
    try:
        int(set_id)
        workout_set = get_object_or_404(Set, pk=set_id)

        # Check if all objects belong to the workout
        if workout_set.exerciseday.id != day.id:
            return HttpResponseForbidden()
    except ValueError, TypeError:
        workout_set = Set()

    template_data['set'] = workout_set

    # Check if all objects belong to the workout
    if day.training.id != workout.id:
        return HttpResponseForbidden()

    # Process request
    if request.method == 'POST':

        set_form = SetForm(request.POST, instance=workout_set)

        # If the data is valid, save and redirect
        if set_form.is_valid():
            workout_set = set_form.save(commit=False)
            workout_set.exerciseday = day

            if not workout_set.order:
                max_order = day.set_set.select_related().aggregate(models.Max('order'))
                workout_set.order = (max_order['order__max'] or 0) + 1
            workout_set.save()

            # The exercises are ManyToMany in DB, so we have to save with this function
            set_form.save_m2m()

            return HttpResponseRedirect(reverse('wger.manager.views.workout.view_workout',
                                                kwargs={'id': id}))
    else:
        set_form = SetForm(instance=workout_set)
    template_data['set_form'] = set_form

    return render_to_response('set/edit.html',
                              template_data,
                              context_instance=RequestContext(request))


@login_required
def delete_set(request, id, day_id, set_id):
    '''
    Deletes the given set
    '''

    # Load the set
    set_obj = get_object_or_404(Set, pk=set_id)

    # Check if the user is the owner of the object
    if set_obj.exerciseday.training.user == request.user:
        set_obj.delete()
        return HttpResponseRedirect(reverse('wger.manager.views.workout.view_workout',
                                            kwargs={'id': id}))
    else:
        return HttpResponseForbidden()


@login_required
def api_edit_set(request):
    '''
    Allows to edit the order of the sets via an AJAX call
    '''

    if request.is_ajax():

        # Set the order of the reps
        if request.GET.get('do') == 'set_order':
            day_id = request.GET.get('day_id')
            new_set_order = request.GET.get('order')

            order = 0
            for i in new_set_order.strip(',').split(','):
                set_id = i.split('-')[1]
                order += 1

                set_obj = get_object_or_404(Set, pk=set_id, exerciseday=day_id)

                # Check if the user is the owner of the object
                if set_obj.exerciseday.training.user == request.user:
                    set_obj.order = order
                    set_obj.save()
                else:
                    return HttpResponseForbidden()

            return HttpResponse(_('Success'))

        # This part is responsible for the in-place editing of the sets and settings
        if request.GET.get('do') == 'edit_set':
            template_data = {}
            template_data.update(csrf(request))

            # Load the objects
            set_id = request.GET.get('set')
            workout_set = get_object_or_404(Set, pk=set_id)
            template_data['set'] = workout_set

            exercise_id = request.GET.get('exercise')
            exercise = get_object_or_404(Exercise, pk=exercise_id)

            # Allow editing settings/repetitions that are not yet associated with the set
            #
            # We calculate here how many are there already [.filter(...)] and how many there could
            # be at all (workout_set.sets)
            current_settings = exercise.setting_set.filter(set_id=set_id).count()
            diff = int(workout_set.sets) - current_settings

            # If there are 'free slots', create some UUIDs for them, this gives them unique form
            # names in the HTML and makes our lifes easier
            new_settings = []
            if diff > 0:

                # Note: use UUIDs version 1 because they are monotonously increasing
                #       and the order of the fields later is important
                new_settings = [uuid.uuid1() for i in range(0, diff)]
            template_data['new_settings'] = new_settings

            # Process request
            if request.method == 'POST':

                new_exercise_id = request.POST.get('current_exercise')
                new_exercise = get_object_or_404(Exercise, pk=new_exercise_id)

                # When there is more than one exercise per set, we need to manually set and replace
                # the IDs here, otherwise they get lost
                request_copy = request.POST
                request_copy = request_copy.copy()

                exercise_list = [i for i in request_copy.getlist('exercises') if i != exercise_id]
                request_copy.setlist('exercises', exercise_list)
                request_copy.update({'exercises': new_exercise_id})

                set_form = SetForm(request_copy, instance=workout_set)

                if set_form.is_valid():
                    set_form.save()

                # Init a counter for the order in case we have to set it for new settings
                # We don't actually care how hight the counter actually is, as long as the new
                # settings get a number that puts them at the end
                order_counter = 1
                new_settings = []

                # input fields for settings  'setting-x, setting-y, etc.',
                #              new settings: 'new-setting-UUID1, new-setting-UUID2, etc.'
                for i in request.POST:
                    order_counter += 1

                    # old settings, update
                    if i.startswith('setting'):
                        setting_id = int(i.split('-')[-1])
                        setting = get_object_or_404(Setting, pk=setting_id)

                        # Check if the new value is empty (the user wants the setting deleted)
                        # We don't check more, if the user enters a string, it won't be converted
                        # and nothing will happen
                        if request.POST[i] == '':
                            setting.delete()
                        else:
                            reps = int(request.POST[i])
                            setting.reps = reps
                            setting.exercise = new_exercise
                            setting.save()

                    # New settings, put in a list, see below
                    if i.startswith('new-setting') and request.POST[i]:

                        new_settings.append(i)

                # new settings, sort by name (important to keep the order as
                # it was inputted in the website),create object and save
                new_settings.sort()
                for i in new_settings:
                    reps = int(request.POST[i])

                    setting = Setting()
                    setting.exercise = new_exercise
                    setting.set = workout_set
                    setting.reps = reps
                    setting.order = order_counter
                    setting.save()

            template_data['exercise'] = exercise

            return render_to_response('setting/ajax_edit.html',
                                      template_data,
                                      context_instance=RequestContext(request))
