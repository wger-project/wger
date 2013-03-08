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

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.forms.models import modelformset_factory

from django.contrib.auth.decorators import login_required

from wger.manager.models import TrainingSchedule
from wger.manager.models import Set
from wger.manager.models import Setting

from wger.exercises.models import Exercise

logger = logging.getLogger('workout_manager.custom')


# ************************
# Settings functions
# ************************
@login_required
def edit_setting(request, id, set_id, exercise_id, setting_id=None):
    template_data = {}
    template_data.update(csrf(request))

    # Load workout
    workout = get_object_or_404(TrainingSchedule, pk=id, user=request.user)
    template_data['workout'] = workout

    # Load set and the FormSet
    set_obj = get_object_or_404(Set, pk=set_id)
    template_data['set'] = set_obj

    SettingFormSet = modelformset_factory(Setting,
                                          exclude=('set', 'exercise'),
                                          max_num=int(set_obj.sets),
                                          extra=int(set_obj.sets))

    # Load exercise
    exercise = get_object_or_404(Exercise, pk=exercise_id)
    template_data['exercise'] = exercise

    # Check that the set belongs to the workout
    if set_obj.exerciseday.training.id != workout.id:
        return HttpResponseForbidden()

    # Load setting
    if not setting_id:
        setting = Setting()
    else:
        setting = get_object_or_404(Setting, pk=setting_id)
    template_data['setting'] = setting

    # Process request
    if request.method == 'POST':

        # Process the FormSet, setting the set and the exercise
        setting_form = SettingFormSet(request.POST)
        if setting_form.is_valid():

            order = 1
            instances = setting_form.save(commit=False)
            for setting_instance in instances:
                setting_instance.set = set_obj
                setting_instance.exercise = exercise

                # Manualy set the order, the user can later use drag&drop to change this
                if not setting_instance.order:
                    setting_instance.order = order

                setting_instance.save()

                order += 1

            return HttpResponseRedirect(reverse('wger.manager.views.workout.view_workout',
                                                kwargs={'id': id}))
    else:
        setting_form = SettingFormSet(queryset=Setting.objects.filter(exercise_id=exercise.id,
                                                                      set_id=set_obj.id))
    template_data['setting_form'] = setting_form

    return render_to_response('setting/edit.html',
                              template_data,
                              context_instance=RequestContext(request))


@login_required
def api_edit_setting(request):
    '''
    Allows to edit the order of the setting inside a set via an AJAX call
    '''

    if request.is_ajax():
        if request.GET.get('do') == 'set_order':
            new_setting_order = request.GET.get('order')

            order = 0
            for i in new_setting_order.strip(',').split(','):
                setting_id = i.split('-')[1]
                order += 1

                setting_obj = get_object_or_404(Setting, pk=setting_id)

                # Check if the user is the owner of the object
                if setting_obj.set.exerciseday.training.user == request.user:
                    setting_obj.order = order
                    setting_obj.save()
                else:
                    return HttpResponseForbidden()

            return HttpResponse(_('Success'))


@login_required
def delete_setting(request, id, set_id, exercise_id):
    '''
    Deletes all the settings belonging to set_id and exercise_id
    '''

    # Load the workout
    workout = get_object_or_404(TrainingSchedule, pk=id, user=request.user)

    # Delete all settings
    settings = Setting.objects.filter(exercise_id=exercise_id, set_id=set_id)
    settings.delete()

    return HttpResponseRedirect(reverse('wger.manager.views.workout.view_workout',
                                        kwargs={'id': id}))
