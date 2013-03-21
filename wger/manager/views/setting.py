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
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required

from wger.manager.models import TrainingSchedule
from wger.manager.models import Set
from wger.manager.models import Setting

from wger.exercises.models import Exercise
from django.views.generic import UpdateView

from wger.workout_manager.generic_views import YamlFormMixin

logger = logging.getLogger('workout_manager.custom')


# TODO: check if we really need to keep this code. All the editing actually
#       happens via AJAX and we don't want to provide a non-JS fallback for
#       all functions.
@login_required
def edit_setting(request, set_id, exercise_id):
    template_data = {}
    template_data.update(csrf(request))

    # Load set and the FormSet
    set_obj = get_object_or_404(Set, pk=set_id)
    if set_obj.get_owner_object().user != request.user:
        return HttpResponseForbidden()
    template_data['set'] = set_obj

    SettingFormSet = modelformset_factory(Setting,
                                          exclude=('set', 'exercise'),
                                          max_num=int(set_obj.sets),
                                          extra=int(set_obj.sets))

    # Load exercise
    exercise = get_object_or_404(Exercise, pk=exercise_id)
    template_data['exercise'] = exercise

    # Load setting
    setting = Setting()
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
                                                kwargs={'id': set_obj.get_owner_object().id}))
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
