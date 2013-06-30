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

from django.forms.models import modelformset_factory
from django.forms.models import inlineformset_factory
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.db import models

from django.contrib.auth.decorators import login_required

from django.views.generic import DeleteView
from django.views.generic import CreateView
from django.views.generic import UpdateView

from wger.manager.models import Workout
from wger.manager.models import Day
from wger.manager.models import Set
from wger.manager.models import Setting

from wger.exercises.models import Exercise

from wger.manager.forms import SetForm

from wger.utils.generic_views import YamlFormMixin
from wger.utils.generic_views import YamlDeleteMixin

logger = logging.getLogger('workout_manager.custom')


# ************************
# Set functions
# ************************
SETTING_FORMSET_EXCLUDE = ('comment',)

SettingFormset = modelformset_factory(Setting,
                                      exclude=SETTING_FORMSET_EXCLUDE,
                                      can_delete=True,
                                      can_order=False,
                                      extra=1)


@login_required
def create(request, day_pk):
    '''
    Creates a new set. This view handles both the set form and the corresponding
    settings formsets
    '''
    day = get_object_or_404(Day, pk=day_pk)
    if day.get_owner_object().user != request.user:
        return HttpResponseForbidden()

    context = {}
    formsets = []
    form = SetForm(initial={'sets': Set.DEFAULT_SETS})

    # If the form and all formsets validate, save them
    if request.method == "POST":
        form = SetForm(request.POST)
        if form.is_valid():
            for exercise in form.cleaned_data['exercises']:
                formset = SettingFormset(request.POST,
                                         queryset=Setting.objects.none(),
                                         prefix='exercise{0}'.format(exercise.id))
                formsets.append({'exercise': exercise, 'formset': formset})
        all_valid = True

        for formset in formsets:
            if not formset['formset'].is_valid():
                all_valid = False

        if form.is_valid() and all_valid:
            # Manually take care of the order, TODO: better move this to the model
            max_order = day.set_set.select_related().aggregate(models.Max('order'))
            form.instance.order = (max_order['order__max'] or 0) + 1
            form.instance.exerciseday = day
            set_obj = form.save()

            for formset in formsets:
                instances = formset['formset'].save(commit=False)
                for instance in instances:
                    instance.set = set_obj
                    instance.order = 1
                    instance.exercise = formset['exercise']
                    instance.save()

            return HttpResponseRedirect(reverse('wger.manager.views.workout.view',
                                        kwargs={'id': day.get_owner_object().id}))
        else:
            logger.debug(form.errors)

    # Other context we need
    context['form'] = form
    context['day'] = day
    context['max_sets'] = Set.MAX_SETS
    context['formsets'] = formsets
    context['form_action'] = reverse('set-add', kwargs={'day_pk': day_pk})
    return render_to_response('set/add.html',
                              context,
                              context_instance=RequestContext(request))


@login_required
def get_formset(request, exercise_pk, reps=Set.DEFAULT_SETS):
    '''
    Returns a formset. This is then rendered inside the new set template
    '''
    exercise = Exercise.objects.get(pk=exercise_pk)
    SettingFormSet = inlineformset_factory(Set,
                                           Setting,
                                           can_delete=False,
                                           extra=int(reps),
                                           exclude=SETTING_FORMSET_EXCLUDE)
    formset = SettingFormSet(queryset=Setting.objects.none(),
                             prefix='exercise{0}'.format(exercise_pk))

    return render_to_response("set/formset.html",
                              {'formset': formset,
                               'exercise': exercise},
                              context_instance=RequestContext(request))


@login_required
def delete(request, pk):
    '''
    Deletes the given set
    '''

    # Load the set
    set_obj = get_object_or_404(Set, pk=pk)

    # Check if the user is the owner of the object
    if set_obj.get_owner_object().user == request.user:
        set_obj.delete()
        return HttpResponseRedirect(reverse('wger.manager.views.workout.view',
                                            kwargs={'id': set_obj.get_owner_object().id}))
    else:
        return HttpResponseForbidden()


@login_required
def edit(request, pk):
    '''
    Edit a set (its settings actually)
    '''
    set_obj = get_object_or_404(Set, pk=pk)
    if set_obj.get_owner_object().user != request.user:
        return HttpResponseForbidden()

    formsets = []
    for exercise in set_obj.exercises.all():
        queryset = Setting.objects.filter(set=set_obj, exercise=exercise)
        formset = SettingFormset(queryset=queryset, prefix='exercise{0}'.format(exercise.id))
        formsets.append({'exercise': exercise, 'formset': formset})

    if request.method == "POST":
        formsets = []
        for exercise in set_obj.exercises.all():
            formset = SettingFormset(request.POST,
                                     prefix='exercise{0}'.format(exercise.id))
            formsets.append({'exercise': exercise, 'formset': formset})

        # If all formsets validate, save them
        all_valid = True
        for formset in formsets:
            if not formset['formset'].is_valid():
                all_valid = False

        if all_valid:
            for formset in formsets:
                instances = formset['formset'].save(commit=False)
                for instance in instances:
                    # If the setting has already a set, we are editing...
                    if hasattr(instance, 'set'):

                        # Check that we are allowed to do this
                        if instance.get_owner_object().user != request.user:
                            return HttpResponseForbidden()

                        instance.save()

                    # ...if not, create a new setting
                    else:
                        instance.set = set_obj
                        instance.order = 1
                        instance.exercise = formset['exercise']
                        instance.save()

            return HttpResponseRedirect(reverse('wger.manager.views.workout.view',
                                        kwargs={'id': set_obj.get_owner_object().id}))

    # Other context we need
    context = {}
    context['formsets'] = formsets
    context['form_action'] = reverse('set-edit', kwargs={'pk': pk})
    return render_to_response('set/edit.html',
                              context,
                              context_instance=RequestContext(request))


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
